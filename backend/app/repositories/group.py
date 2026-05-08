from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.group import Group, GroupMember, GroupRole, GroupJoinRequest, JoinRequestStatus
from app.schemas.group import GroupCreate, GroupUpdate
import uuid

class GroupRepository:
    def get(self, db: Session, group_id: str) -> Optional[Group]:
        return db.query(Group).filter(Group.id == group_id).first()

    def get_by_slug(self, db: Session, slug: str) -> Optional[Group]:
        return db.query(Group).filter(Group.slug == slug).first()

    def get_by_ngo_id(self, db: Session, ngo_id: str, include_invite_only: bool = False) -> List[Group]:
        query = db.query(Group).filter(Group.ngo_id == ngo_id)
        if not include_invite_only:
            query = query.filter(Group.visibility == "public")
        return query.all()

    def create(self, db: Session, obj_in: GroupCreate, ngo_id: str, created_by: str) -> Group:
        db_obj = Group(
            id=str(uuid.uuid4()),
            ngo_id=ngo_id,
            name=obj_in.name,
            slug=obj_in.slug,
            about=obj_in.about,
            visibility=obj_in.visibility,
            created_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Group, obj_in: GroupUpdate) -> Group:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class GroupJoinRequestRepository:
    def get(self, db: Session, id: str) -> Optional[GroupJoinRequest]:
        return db.query(GroupJoinRequest).filter(GroupJoinRequest.id == id).first()

    def get_by_user_and_group(self, db: Session, user_id: str, group_id: str) -> Optional[GroupJoinRequest]:
        return db.query(GroupJoinRequest).filter(
            GroupJoinRequest.user_id == user_id,
            GroupJoinRequest.group_id == group_id
        ).order_by(GroupJoinRequest.requested_at.desc()).first()

    def get_all_for_group(self, db: Session, group_id: str, status: Optional[str] = None) -> List[GroupJoinRequest]:
        query = db.query(GroupJoinRequest).filter(GroupJoinRequest.group_id == group_id)
        if status:
            query = query.filter(GroupJoinRequest.status == status)
        return query.all()

    def create(self, db: Session, user_id: str, group_id: str) -> GroupJoinRequest:
        db_obj = GroupJoinRequest(
            id=str(uuid.uuid4()),
            user_id=user_id,
            group_id=group_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: GroupJoinRequest, status: JoinRequestStatus, reviewer_id: str, admin_comment: Optional[str] = None) -> GroupJoinRequest:
        db_obj.status = status
        db_obj.reviewed_by = reviewer_id
        db_obj.reviewed_at = datetime.utcnow()
        if admin_comment is not None:
            db_obj.admin_comment = admin_comment

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

class GroupMemberRepository:
    def get(self, db: Session, user_id: str, group_id: str) -> Optional[GroupMember]:
        return db.query(GroupMember).filter(GroupMember.user_id == user_id, GroupMember.group_id == group_id).first()

    def get_all_for_group(self, db: Session, group_id: str) -> List[GroupMember]:
        return db.query(GroupMember).filter(GroupMember.group_id == group_id).all()

    def create(self, db: Session, user_id: str, group_id: str, role_id: str, status: str = "active") -> GroupMember:
        db_obj = GroupMember(user_id=user_id, group_id=group_id, role_id=role_id, status=status)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: GroupMember):
        db.delete(db_obj)
        db.commit()

class GroupRoleRepository:
    def get(self, db: Session, role_id: str) -> Optional[GroupRole]:
        return db.query(GroupRole).filter(GroupRole.id == role_id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[GroupRole]:
        return db.query(GroupRole).filter(GroupRole.name == name).first()

    def create(self, db: Session, name: str, description: str = None) -> GroupRole:
        db_obj = GroupRole(id=str(uuid.uuid4()), name=name, description=description)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

group_repo = GroupRepository()
group_member_repo = GroupMemberRepository()
group_role_repo = GroupRoleRepository()
group_join_request_repo = GroupJoinRequestRepository()
