from sqlalchemy.orm import Session
from app.models.auth_provider import AuthProvider
from app.schemas.auth_provider import AuthProviderCreate
import uuid

class AuthProviderRepository:
    def get_by_user_and_provider(self, db: Session, user_id: str, provider: str) -> AuthProvider | None:
        return db.query(AuthProvider).filter(
            AuthProvider.user_id == user_id,
            AuthProvider.provider == provider
        ).first()

    def get_by_provider_id(self, db: Session, provider: str, provider_user_id: str) -> AuthProvider | None:
        return db.query(AuthProvider).filter(
            AuthProvider.provider == provider,
            AuthProvider.provider_user_id == provider_user_id
        ).first()

    def create(self, db: Session, auth_provider_in: AuthProviderCreate) -> AuthProvider:
        db_obj = AuthProvider(
            id=str(uuid.uuid4()),
            user_id=auth_provider_in.user_id,
            provider=auth_provider_in.provider,
            provider_user_id=auth_provider_in.provider_user_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

auth_provider_repository = AuthProviderRepository()
