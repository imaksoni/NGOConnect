from datetime import datetime
import enum
from sqlalchemy import Column, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class EventVisibility(str, enum.Enum):
    public = "public"
    members_only = "members_only"

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True, index=True)
    ngo_id = Column(String, ForeignKey("ngos.id", ondelete="CASCADE"), nullable=True, index=True)
    group_id = Column(String, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    visibility = Column(Enum(EventVisibility), default=EventVisibility.members_only, nullable=False)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ngo = relationship("Ngo")
    group = relationship("Group")
    creator = relationship("User")
