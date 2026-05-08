from typing import Optional
from sqlalchemy.orm import Session
from app.models.ngo_role import NgoRole
from app.schemas.ngo_role import NgoRoleCreate

class NgoRoleRepository:
    def get(self, db: Session, id: str) -> Optional[NgoRole]:
        return db.query(NgoRole).filter(NgoRole.id == id).first()

    def get_by_name(self, db: Session, name: str) -> Optional[NgoRole]:
        return db.query(NgoRole).filter(NgoRole.name == name).first()

    def create(self, db: Session, *, obj_in: NgoRoleCreate, id: str) -> NgoRole:
        db_obj = NgoRole(
            id=id,
            name=obj_in.name,
            description=obj_in.description
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

ngo_role_repo = NgoRoleRepository()
