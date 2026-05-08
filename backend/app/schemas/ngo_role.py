from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NgoRoleBase(BaseModel):
    name: str
    description: Optional[str] = None

class NgoRoleCreate(NgoRoleBase):
    pass

class NgoRoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class NgoRole(NgoRoleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
