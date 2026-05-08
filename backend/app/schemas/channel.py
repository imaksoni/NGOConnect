from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr
from app.models.channel import ChannelVisibility, ChannelType

class ChannelBase(BaseModel):
    name: str
    slug: Optional[constr(max_length=50)] = None
    description: Optional[str] = None
    visibility: Optional[ChannelVisibility] = ChannelVisibility.public
    type: Optional[ChannelType] = ChannelType.general

class ChannelCreate(ChannelBase):
    pass

class ChannelUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[constr(max_length=50)] = None
    description: Optional[str] = None
    visibility: Optional[ChannelVisibility] = None
    type: Optional[ChannelType] = None

class Channel(ChannelBase):
    id: str
    group_id: str
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
