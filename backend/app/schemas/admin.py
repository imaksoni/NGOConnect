from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class AuditLogBase(BaseModel):
    id: str
    actor_user_id: Optional[str] = None
    action_type: str
    entity_type: str
    entity_id: str
    target_user_id: Optional[str] = None
    ngo_id: Optional[str] = None
    group_id: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class VerificationRequestResponse(BaseModel):
    id: str
    name: str
    slug: str
    verification_status: str

    model_config = ConfigDict(from_attributes=True)
