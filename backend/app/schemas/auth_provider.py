from datetime import datetime
from pydantic import BaseModel

class AuthProviderBase(BaseModel):
    provider: str
    provider_user_id: str

class AuthProviderCreate(AuthProviderBase):
    user_id: str

class AuthProviderInDBBase(AuthProviderBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class AuthProvider(AuthProviderInDBBase):
    pass
