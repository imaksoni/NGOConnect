from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class NgoMember(Base):
    __tablename__ = "ngo_members"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    ngo_id = Column(String, ForeignKey("ngos.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String, ForeignKey("ngo_roles.id", ondelete="RESTRICT"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    ngo = relationship("Ngo", back_populates="members")
    role = relationship("NgoRole", back_populates="members")
