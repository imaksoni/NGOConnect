import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class NgoVisibility(str, enum.Enum):
    public = "public"
    private = "private"

class NgoVerificationStatus(str, enum.Enum):
    pending = "pending"
    verified = "verified"
    rejected = "rejected"

class Ngo(Base):
    __tablename__ = "ngos"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    about = Column(Text, nullable=True)
    visibility = Column(Enum(NgoVisibility), default=NgoVisibility.private, nullable=False)
    verification_status = Column(Enum(NgoVerificationStatus), default=NgoVerificationStatus.pending, nullable=False)
    invite_code = Column(String, unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = relationship("NgoMember", back_populates="ngo", cascade="all, delete-orphan")
