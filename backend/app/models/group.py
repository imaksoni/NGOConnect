from datetime import datetime
import enum
from sqlalchemy import Column, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base

class GroupVisibility(str, enum.Enum):
    public = "public"
    invite_only = "invite_only"

class Group(Base):
    __tablename__ = "groups"

    id = Column(String, primary_key=True, index=True)
    ngo_id = Column(String, ForeignKey("ngos.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    about = Column(Text, nullable=True)
    visibility = Column(Enum(GroupVisibility), default=GroupVisibility.invite_only, nullable=False)
    created_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    ngo = relationship("Ngo")
    members = relationship("GroupMember", back_populates="group", cascade="all, delete-orphan")
    channels = relationship("Channel", back_populates="group", cascade="all, delete-orphan")

class GroupRole(Base):
    __tablename__ = "group_roles"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # group_admin, group_moderator, member
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    members = relationship("GroupMember", back_populates="role")

class GroupMember(Base):
    __tablename__ = "group_members"

    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    group_id = Column(String, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(String, ForeignKey("group_roles.id", ondelete="RESTRICT"), nullable=False)
    status = Column(String, default="active") # active, pending, etc
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User")
    group = relationship("Group", back_populates="members")
    role = relationship("GroupRole", back_populates="members")
