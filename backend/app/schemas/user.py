from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserInDBBase(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class User(UserInDBBase):
    pass
