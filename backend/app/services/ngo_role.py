import uuid
from typing import Optional
from sqlalchemy.orm import Session
from app.models.ngo_role import NgoRole
from app.schemas.ngo_role import NgoRoleCreate
from app.repositories.ngo_role import ngo_role_repo

class NgoRoleService:
    def get_role(self, db: Session, role_id: str) -> Optional[NgoRole]:
        return ngo_role_repo.get(db, role_id)

    def get_role_by_name(self, db: Session, name: str) -> Optional[NgoRole]:
        return ngo_role_repo.get_by_name(db, name)

    def create_role(self, db: Session, role_in: NgoRoleCreate) -> NgoRole:
        role_id = str(uuid.uuid4())
        return ngo_role_repo.create(db, obj_in=role_in, id=role_id)

    def ensure_default_roles(self, db: Session):
        owner_role = self.get_role_by_name(db, "owner")
        if not owner_role:
            self.create_role(db, NgoRoleCreate(name="owner", description="Owner of the NGO"))

        admin_role = self.get_role_by_name(db, "admin")
        if not admin_role:
            self.create_role(db, NgoRoleCreate(name="admin", description="Admin of the NGO"))

        member_role = self.get_role_by_name(db, "member")
        if not member_role:
            self.create_role(db, NgoRoleCreate(name="member", description="Member of the NGO"))

ngo_role_service = NgoRoleService()
