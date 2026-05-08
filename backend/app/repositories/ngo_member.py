from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ngo_member import NgoMember
from app.schemas.ngo_member import NgoMemberCreate

class NgoMemberRepository:
    def get(self, db: Session, user_id: str, ngo_id: str) -> Optional[NgoMember]:
        return db.query(NgoMember).filter(
            NgoMember.user_id == user_id,
            NgoMember.ngo_id == ngo_id
        ).first()

    def list_by_ngo(self, db: Session, ngo_id: str) -> List[NgoMember]:
        return db.query(NgoMember).filter(NgoMember.ngo_id == ngo_id).all()

    def create(self, db: Session, *, obj_in: NgoMemberCreate) -> NgoMember:
        db_obj = NgoMember(
            user_id=obj_in.user_id,
            ngo_id=obj_in.ngo_id,
            role_id=obj_in.role_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

ngo_member_repo = NgoMemberRepository()
