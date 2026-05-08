from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ngo_member import NgoMember
from app.schemas.ngo_member import NgoMemberCreate
from app.repositories.ngo_member import ngo_member_repo
from app.services.ngo_role import ngo_role_service

class NgoMemberService:
    def get_member(self, db: Session, user_id: str, ngo_id: str) -> Optional[NgoMember]:
        return ngo_member_repo.get(db, user_id, ngo_id)

    def add_owner(self, db: Session, user_id: str, ngo_id: str) -> NgoMember:
        ngo_role_service.ensure_default_roles(db)
        owner_role = ngo_role_service.get_role_by_name(db, "owner")
        return ngo_member_repo.create(
            db,
            obj_in=NgoMemberCreate(user_id=user_id, ngo_id=ngo_id, role_id=owner_role.id)
        )

ngo_member_service = NgoMemberService()
