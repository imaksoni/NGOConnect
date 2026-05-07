from sqlalchemy.orm import Session
from app.schemas.user import UserCreate, UserLogin
from app.repositories.user import user_repository
from app.core.security import verify_password
from fastapi import HTTPException, status

class AuthService:
    def authenticate(self, db: Session, user_in: UserLogin):
        user = user_repository.get_by_email(db, email=user_in.email)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password(user_in.password, user.hashed_password):
            return None
        return user

auth_service = AuthService()
