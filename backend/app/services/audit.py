import uuid
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from typing import Optional, Dict, Any

class AuditService:
    def log_action(
        self,
        db: Session,
        action_type: str,
        entity_type: str,
        entity_id: str,
        actor_user_id: Optional[str] = None,
        target_user_id: Optional[str] = None,
        ngo_id: Optional[str] = None,
        group_id: Optional[str] = None,
        metadata_json: Optional[Dict[str, Any]] = None,
        commit: bool = True
    ) -> AuditLog:
        log = AuditLog(
            id=str(uuid.uuid4()),
            actor_user_id=actor_user_id,
            action_type=action_type,
            entity_type=entity_type,
            entity_id=entity_id,
            target_user_id=target_user_id,
            ngo_id=ngo_id,
            group_id=group_id,
            metadata_json=metadata_json,
        )
        db.add(log)
        if commit:
            db.commit()
            db.refresh(log)
        return log

audit_service = AuditService()
