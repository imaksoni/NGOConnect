from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.ngo import Ngo, NgoVisibility, NgoVerificationStatus
from app.schemas.ngo import NgoCreate, NgoUpdate

class NgoRepository:
    def get(self, db: Session, id: str) -> Optional[Ngo]:
        return db.query(Ngo).filter(Ngo.id == id).first()

    def get_by_slug(self, db: Session, slug: str) -> Optional[Ngo]:
        return db.query(Ngo).filter(Ngo.slug == slug).first()

    def list_discoverable(self, db: Session) -> List[Ngo]:
        return db.query(Ngo).filter(
            Ngo.visibility == NgoVisibility.public,
            Ngo.verification_status == NgoVerificationStatus.verified
        ).all()

    def create(self, db: Session, *, obj_in: NgoCreate, id: str, invite_code: str) -> Ngo:
        db_obj = Ngo(
            id=id,
            name=obj_in.name,
            slug=obj_in.slug,
            about=obj_in.about,
            visibility=obj_in.visibility,
            invite_code=invite_code
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Ngo, obj_in: NgoUpdate) -> Ngo:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def set_verification_status(self, db: Session, *, db_obj: Ngo, status: NgoVerificationStatus) -> Ngo:
        db_obj.verification_status = status
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

ngo_repo = NgoRepository()
