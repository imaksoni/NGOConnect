from datetime import datetime
from pydantic import BaseModel

class NgoMemberBase(BaseModel):
    user_id: str
    ngo_id: str
    role_id: str

class NgoMemberCreate(NgoMemberBase):
    pass

class NgoMember(NgoMemberBase):
    joined_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
