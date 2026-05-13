from typing import List, Optional
from app.services.notification import notification_service
from app.models.ngo import Ngo
from sqlalchemy.orm import Session
from app.models.group import Group, GroupMember, GroupRole, GroupJoinRequest, JoinRequestStatus
from app.schemas.group import GroupCreate, GroupUpdate
from app.repositories.group import group_repo, group_role_repo, group_member_repo, group_join_request_repo
from fastapi import HTTPException

class GroupRoleService:
    def ensure_default_roles(self, db: Session):
        roles = [
            {"name": "group_admin", "description": "Group Administrator"},
            {"name": "group_moderator", "description": "Group Moderator"},
            {"name": "member", "description": "Regular Group Member"},
        ]
        for role_data in roles:
            role = group_role_repo.get_by_name(db, role_data["name"])
            if not role:
                group_role_repo.create(db, name=role_data["name"], description=role_data["description"])

    def get_role_by_name(self, db: Session, name: str) -> Optional[GroupRole]:
        return group_role_repo.get_by_name(db, name)

group_role_service = GroupRoleService()

class GroupMemberService:
    def get_member(self, db: Session, user_id: str, group_id: str) -> Optional[GroupMember]:
        return group_member_repo.get(db, user_id, group_id)

    def get_all_members(self, db: Session, group_id: str) -> List[GroupMember]:
        return group_member_repo.get_all_for_group(db, group_id)

    def add_member(self, db: Session, user_id: str, group_id: str, role_name: str = "member") -> GroupMember:
        group_role_service.ensure_default_roles(db)
        role = group_role_service.get_role_by_name(db, role_name)
        if not role:
            raise HTTPException(status_code=500, detail="Role not found")
        existing_member = self.get_member(db, user_id, group_id)
        if existing_member:
            raise HTTPException(status_code=400, detail="User is already a member of this group")
        return group_member_repo.create(db, user_id=user_id, group_id=group_id, role_id=role.id)

    def remove_member(self, db: Session, user_id: str, group_id: str):
        member = self.get_member(db, user_id, group_id)
        if not member:
            raise HTTPException(status_code=404, detail="Member not found")
        group_member_repo.delete(db, member)

group_member_service = GroupMemberService()

class GroupService:
    def get_group(self, db: Session, group_id: str) -> Optional[Group]:
        return group_repo.get(db, group_id)

    def get_group_by_slug(self, db: Session, slug: str) -> Optional[Group]:
        return group_repo.get_by_slug(db, slug)

    def get_groups_by_ngo_id(self, db: Session, ngo_id: str, include_invite_only: bool = False) -> List[Group]:
        return group_repo.get_by_ngo_id(db, ngo_id, include_invite_only)

    def create_group(self, db: Session, obj_in: GroupCreate, ngo_id: str, user_id: str) -> Group:
        existing_group = self.get_group_by_slug(db, obj_in.slug)
        if existing_group:
            raise HTTPException(status_code=400, detail="Group with this slug already exists.")

        group = group_repo.create(db, obj_in, ngo_id, user_id)
        # Add creator as group_admin
        group_member_service.add_member(db, user_id, group.id, "group_admin")
        return group

    def update_group(self, db: Session, db_obj: Group, obj_in: GroupUpdate) -> Group:
        if obj_in.slug and obj_in.slug != db_obj.slug:
            existing_group = self.get_group_by_slug(db, obj_in.slug)
            if existing_group:
                raise HTTPException(status_code=400, detail="Group with this slug already exists.")
        return group_repo.update(db, db_obj, obj_in)

group_service = GroupService()

class GroupJoinRequestService:
    def create_request(self, db: Session, user_id: str, group_id: str) -> GroupJoinRequest:
        group = group_repo.get(db, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        # Check if already a member
        member = group_member_service.get_member(db, user_id, group_id)
        if member:
            raise HTTPException(status_code=400, detail="User is already a member of this group")

        # Check if a pending request already exists
        existing_request = group_join_request_repo.get_by_user_and_group(db, user_id, group_id)
        if existing_request and existing_request.status == JoinRequestStatus.pending:
            raise HTTPException(status_code=400, detail="A pending join request already exists")

        # Note: Depending on rules, you might allow re-requesting if rejected, or disallow it. We'll allow if not pending.

        return group_join_request_repo.create(db, user_id=user_id, group_id=group_id)

    def get_requests_for_group(self, db: Session, group_id: str, status: Optional[str] = None) -> List[GroupJoinRequest]:
        return group_join_request_repo.get_all_for_group(db, group_id, status)

    def approve_request(self, db: Session, request_id: str, reviewer_id: str, admin_comment: Optional[str] = None) -> GroupJoinRequest:
        from datetime import datetime
        # Use with_for_update() to prevent race conditions during approval
        db_obj = db.query(GroupJoinRequest).filter(GroupJoinRequest.id == request_id).with_for_update().first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Join request not found")

        if db_obj.status != JoinRequestStatus.pending:
            raise HTTPException(status_code=400, detail=f"Cannot approve a request with status: {db_obj.status}")

        db_obj.status = JoinRequestStatus.approved
        db_obj.reviewed_by = reviewer_id
        db_obj.reviewed_at = datetime.utcnow()
        if admin_comment is not None:
            db_obj.admin_comment = admin_comment

        db.add(db_obj)

        group_role_service.ensure_default_roles(db)
        role = group_role_service.get_role_by_name(db, "member")
        if not role:
            raise HTTPException(status_code=500, detail="Role not found")

        # Grant membership.
        # Note on Channel Access: Public channel access is implicitly derived
        # from group membership. When a user becomes a GroupMember here, they
        # automatically gain access to view all public channels within this group
        # (as enforced by channel view logic checking group membership).
        existing_member = db.query(GroupMember).filter(GroupMember.user_id == db_obj.user_id, GroupMember.group_id == db_obj.group_id).first()
        if not existing_member:
            member = GroupMember(user_id=db_obj.user_id, group_id=db_obj.group_id, role_id=role.id, status="active")
            db.add(member)

        db.commit()
        db.refresh(db_obj)

        # Trigger push notification
        group = db.query(Group).filter(Group.id == db_obj.group_id).first()
        if group:
            notification_service.send_push_notification(
                db=db,
                user_id=db_obj.user_id,
                title="Join Request Approved",
                body=f"Your request to join '{group.name}' has been approved.",
                data={"type": "group_join_approved", "group_id": group.id}
            )

        return db_obj

    def reject_request(self, db: Session, request_id: str, reviewer_id: str, admin_comment: Optional[str] = None) -> GroupJoinRequest:
        db_obj = db.query(GroupJoinRequest).filter(GroupJoinRequest.id == request_id).with_for_update().first()
        if not db_obj:
            raise HTTPException(status_code=404, detail="Join request not found")

        if db_obj.status != JoinRequestStatus.pending:
            raise HTTPException(status_code=400, detail=f"Cannot reject a request with status: {db_obj.status}")

        updated_obj = group_join_request_repo.update(
            db, db_obj=db_obj, status=JoinRequestStatus.rejected, reviewer_id=reviewer_id, admin_comment=admin_comment
        )

        # Trigger push notification
        group = db.query(Group).filter(Group.id == updated_obj.group_id).first()
        if group:
            notification_service.send_push_notification(
                db=db,
                user_id=updated_obj.user_id,
                title="Join Request Rejected",
                body=f"Your request to join '{group.name}' was rejected.",
                data={"type": "group_join_rejected", "group_id": group.id}
            )

        return updated_obj

group_join_request_service = GroupJoinRequestService()
