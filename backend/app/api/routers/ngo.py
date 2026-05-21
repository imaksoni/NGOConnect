from typing import Optional, List
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.schemas.ngo import Ngo, NgoCreate, NgoUpdate
from app.services.ngo import ngo_service
from app.models.user import User

router = APIRouter(prefix="/ngos", tags=["NGOs"])

from app.services.ngo_member import ngo_member_service

@router.post("", response_model=Ngo, status_code=status.HTTP_201_CREATED)
def create_ngo(
    ngo_in: NgoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing_ngo = ngo_service.get_ngo_by_slug(db, ngo_in.slug)
    if existing_ngo:
        raise HTTPException(status_code=400, detail="NGO with this slug already exists.")

    ngo = ngo_service.create_ngo(db, ngo_in, creator_user_id=current_user.id)
    ngo_member_service.add_owner(db, current_user.id, ngo.id)
    return ngo

@router.get("/discover", response_model=List[Ngo])
def list_discoverable_ngos(db: Session = Depends(get_db)):
    """Returns only public and verified NGOs"""
    return ngo_service.list_discoverable(db)

@router.get("/slug/{slug}", response_model=Ngo)
def get_ngo_by_slug(slug: str, db: Session = Depends(get_db)):
    ngo = ngo_service.get_ngo_by_slug(db, slug)
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")
    return ngo

@router.put("/{ngo_id}", response_model=Ngo)
def update_ngo(
    ngo_id: str,
    ngo_in: NgoUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ngo = ngo_service.get_ngo(db, ngo_id)
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")

    member = ngo_member_service.get_member(db, current_user.id, ngo_id)
    if not member or member.role.name not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    if ngo_in.slug and ngo_in.slug != ngo.slug:
        existing_ngo = ngo_service.get_ngo_by_slug(db, ngo_in.slug)
        if existing_ngo:
            raise HTTPException(status_code=400, detail="NGO with this slug already exists.")

    return ngo_service.update_ngo(db, db_obj=ngo, ngo_in=ngo_in)

@router.post("/{ngo_id}/verify", response_model=Ngo)
def submit_verification_request(
    ngo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ngo = ngo_service.get_ngo(db, ngo_id)
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")

    member = ngo_member_service.get_member(db, current_user.id, ngo_id)
    if not member or member.role.name not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return ngo_service.submit_verification_request(db, db_obj=ngo)

from app.schemas.event import Event, EventCreate
from app.services.event import event_service

@router.post("/{ngo_id}/events", response_model=Event, status_code=status.HTTP_201_CREATED)
def create_ngo_event(
    ngo_id: str,
    event_in: EventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return event_service.create_ngo_event(db, ngo_id, event_in, current_user.id)

@router.get("/{ngo_id}/events", response_model=List[Event])
def get_ngo_events(
    ngo_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional),
):
    user_id = current_user.id if current_user else None
    return event_service.get_ngo_events(db, ngo_id, user_id)
