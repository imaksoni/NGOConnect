from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, constr

class MessageAttachmentBase(BaseModel):
    file_name: str
    content_type: Optional[str] = None
    file_size: Optional[int] = None
    storage_key: str

class MessageAttachmentCreate(MessageAttachmentBase):
    pass

class MessageAttachment(MessageAttachmentBase):
    id: str
    message_id: str
    uploaded_by: Optional[str] = None
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class MessageBase(BaseModel):
    content: str
    type: Optional[str] = "text"

class MessageCreate(MessageBase):
    pass

class MessageUpdate(BaseModel):
    content: Optional[str] = None

class Message(MessageBase):
    id: str
    channel_id: str
    sender_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    attachments: List[MessageAttachment] = []

    class Config:
        orm_mode = True
        from_attributes = True
