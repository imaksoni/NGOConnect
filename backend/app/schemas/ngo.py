from datetime import datetime
from typing import Optional
from pydantic import BaseModel, constr

class NgoBase(BaseModel):
    name: str
    slug: constr(min_length=3, max_length=50)
    about: Optional[str] = None
    visibility: Optional[str] = "private"

class NgoCreate(NgoBase):
    pass

class NgoUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[constr(min_length=3, max_length=50)] = None
    about: Optional[str] = None
    visibility: Optional[str] = None

class Ngo(NgoBase):
    id: str
    verification_status: str
    invite_code: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
