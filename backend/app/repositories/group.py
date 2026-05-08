from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.group import Group, GroupMember, GroupRole
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
