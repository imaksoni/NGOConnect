from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.group import Group, GroupMember, GroupRole
from app.schemas.group import GroupCreate, GroupUpdate
from app.repositories.group import group_repo, group_role_repo, group_member_repo
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
