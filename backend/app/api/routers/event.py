from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.event import Event, EventUpdate
from app.services.event import event_service

router = APIRouter(prefix="/events", tags=["Events"])

@router.get("/{event_id}", response_model=Event)
def get_event(
    event_id: str,
    db: Session = Depends(get_db),
):
    event = event_service.get_event(db, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event

@router.patch("/{event_id}", response_model=Event)
def update_event(
    event_id: str,
    event_in: EventUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.update_event(db, event_id, event_in, current_user.id)
