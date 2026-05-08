from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr
from app.schemas.user import User

class GroupBase(BaseModel):
    name: str
    slug: constr(min_length=3, max_length=50)
    about: Optional[str] = None
    visibility: Optional[str] = "invite_only"

class GroupCreate(GroupBase):
    pass

class GroupUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[constr(min_length=3, max_length=50)] = None
    about: Optional[str] = None
    visibility: Optional[str] = None

class Group(GroupBase):
    id: str
    ngo_id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class GroupRoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class GroupRole(GroupRoleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class GroupMemberBase(BaseModel):
    user_id: str
    group_id: str
    role_id: str
    status: str

class GroupMember(GroupMemberBase):
    joined_at: datetime
    role: GroupRole
    user: User

    class Config:
        orm_mode = True
        from_attributes = True
