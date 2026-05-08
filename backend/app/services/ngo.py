import uuid
import secrets
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ngo import Ngo, NgoVerificationStatus
from app.schemas.ngo import NgoCreate, NgoUpdate
from app.repositories.ngo import ngo_repo

class NgoService:
    def get_ngo(self, db: Session, ngo_id: str) -> Optional[Ngo]:
        return ngo_repo.get(db, ngo_id)

    def get_ngo_by_slug(self, db: Session, slug: str) -> Optional[Ngo]:
        return ngo_repo.get_by_slug(db, slug)

    def list_discoverable(self, db: Session) -> List[Ngo]:
        return ngo_repo.list_discoverable(db)

    def create_ngo(self, db: Session, ngo_in: NgoCreate) -> Ngo:
        ngo_id = str(uuid.uuid4())
        invite_code = secrets.token_urlsafe(8)
        return ngo_repo.create(db, obj_in=ngo_in, id=ngo_id, invite_code=invite_code)

    def update_ngo(self, db: Session, db_obj: Ngo, ngo_in: NgoUpdate) -> Ngo:
        return ngo_repo.update(db, db_obj=db_obj, obj_in=ngo_in)

    def submit_verification_request(self, db: Session, db_obj: Ngo) -> Ngo:
        return ngo_repo.set_verification_status(db, db_obj=db_obj, status=NgoVerificationStatus.pending)

ngo_service = NgoService()
