from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.device import DeviceRegistration
from app.schemas.device import DeviceRegisterRequest, DeviceUnregisterRequest, DeviceRegistrationResponse

router = APIRouter(prefix="/devices", tags=["Devices"])

@router.post("/register", response_model=DeviceRegistrationResponse)
def register_device(
    request: DeviceRegisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if token already registered for this user
    existing = db.query(DeviceRegistration).filter(
        DeviceRegistration.device_token == request.device_token
    ).first()

    if existing:
        if existing.user_id != current_user.id:
            # Token might have belonged to another user previously, update ownership
            existing.user_id = current_user.id

        existing.is_active = True
        existing.platform = request.platform
        existing.app_version = request.app_version
        db.commit()
        db.refresh(existing)
        return existing

    device_id = str(uuid.uuid4())
    new_device = DeviceRegistration(
        id=device_id,
        user_id=current_user.id,
        device_token=request.device_token,
        platform=request.platform,
        app_version=request.app_version,
        is_active=True
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.post("/unregister")
def unregister_device(
    request: DeviceUnregisterRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device = db.query(DeviceRegistration).filter(
        DeviceRegistration.device_token == request.device_token,
        DeviceRegistration.user_id == current_user.id
    ).first()

    if device:
        device.is_active = False
        db.commit()

    return {"status": "success"}
