from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
import uuid

class UserRepository:
    def get_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def get_by_id(self, db: Session, user_id: str) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def create(self, db: Session, user_in: UserCreate) -> User:
        db_obj = User(
            id=str(uuid.uuid4()),
            email=user_in.email,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
            hashed_password=get_password_hash(user_in.password) if user_in.password else None
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repository = UserRepository()
