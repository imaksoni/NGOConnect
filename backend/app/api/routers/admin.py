from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.ngo import Ngo, NgoVerificationStatus
from app.models.audit_log import AuditLog
from app.core.authorization import check_platform_admin
from app.services.audit import audit_service
from app.schemas.admin import AuditLogBase, VerificationRequestResponse

router = APIRouter(prefix="/admin", tags=["Admin Moderation"])

@router.get("/audit-logs", response_model=List[AuditLogBase])
def get_audit_logs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    check_platform_admin(db, current_user.id)
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs

@router.get("/moderation/verification-requests", response_model=List[VerificationRequestResponse])
def get_verification_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    check_platform_admin(db, current_user.id)
    ngos = db.query(Ngo).filter(Ngo.verification_status == NgoVerificationStatus.pending).offset(skip).limit(limit).all()
    return ngos

@router.post("/ngos/{ngo_id}/verify")
def verify_ngo(
    ngo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_platform_admin(db, current_user.id)
    ngo = db.query(Ngo).filter(Ngo.id == ngo_id).with_for_update().first()
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")
    if ngo.verification_status == NgoVerificationStatus.verified:
        raise HTTPException(status_code=400, detail="NGO already verified")

    ngo.verification_status = NgoVerificationStatus.verified

    audit_service.log_action(
        db=db,
        action_type="verify_ngo",
        entity_type="ngo",
        entity_id=ngo.id,
        actor_user_id=current_user.id,
        ngo_id=ngo.id,
        metadata_json={"status": "verified"},
        commit=False
    )

    db.commit()
    db.refresh(ngo)

    # Send push notification to NGO creator
    notification_service.send_push_notification(
        db=db,
        user_id=ngo.creator_id,
        title="NGO Verified",
        body=f"Your NGO '{ngo.name}' has been successfully verified.",
        data={"type": "ngo_verified", "ngo_id": ngo.id}
    )

    return {"status": "success", "ngo_id": ngo.id, "verification_status": ngo.verification_status}

@router.post("/ngos/{ngo_id}/reject-verification")
def reject_ngo_verification(
    ngo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    check_platform_admin(db, current_user.id)
    ngo = db.query(Ngo).filter(Ngo.id == ngo_id).with_for_update().first()
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")
    if ngo.verification_status == NgoVerificationStatus.rejected:
        raise HTTPException(status_code=400, detail="NGO already rejected")

    ngo.verification_status = NgoVerificationStatus.rejected

    audit_service.log_action(
        db=db,
        action_type="reject_ngo_verification",
        entity_type="ngo",
        entity_id=ngo.id,
        actor_user_id=current_user.id,
        ngo_id=ngo.id,
        metadata_json={"status": "rejected"},
        commit=False
    )

    db.commit()
    db.refresh(ngo)

    # Send push notification to NGO creator
    notification_service.send_push_notification(
        db=db,
        user_id=ngo.creator_id,
        title="NGO Verification Rejected",
        body=f"Your NGO verification request for '{ngo.name}' was rejected.",
        data={"type": "ngo_verification_rejected", "ngo_id": ngo.id}
    )

    return {"status": "success", "ngo_id": ngo.id, "verification_status": ngo.verification_status}
