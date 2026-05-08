from datetime import datetime
import enum
from sqlalchemy import Column, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class ChannelVisibility(str, enum.Enum):
    public = "public"
    invite_only = "invite_only"

class ChannelType(str, enum.Enum):
    chat = "chat"
    announcements = "announcements"
    files = "files"
    general = "general"

class Channel(Base):
    __tablename__ = "channels"

    id = Column(String, primary_key=True, index=True)
    group_id = Column(String, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, index=True, nullable=True)
    description = Column(Text, nullable=True)
    visibility = Column(Enum(ChannelVisibility), default=ChannelVisibility.public, nullable=False)
    type = Column(Enum(ChannelType), default=ChannelType.general, nullable=False)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    group = relationship("Group", back_populates="channels")
    creator = relationship("User")
