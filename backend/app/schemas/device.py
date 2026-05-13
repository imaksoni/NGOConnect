from pydantic import BaseModel, ConfigDict
from typing import Optional

class DeviceRegisterRequest(BaseModel):
    device_token: str
    platform: str
    app_version: Optional[str] = None

class DeviceUnregisterRequest(BaseModel):
    device_token: str

class DeviceRegistrationResponse(BaseModel):
    id: str
    device_token: str
    platform: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
