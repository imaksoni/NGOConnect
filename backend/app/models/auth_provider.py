from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from app.models.base import Base

class AuthProvider(Base):
    __tablename__ = "auth_providers"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String, nullable=False)  # e.g., 'email', 'google'
    provider_user_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
