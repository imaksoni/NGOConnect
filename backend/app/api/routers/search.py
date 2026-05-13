from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user_optional, get_current_user
from app.schemas.ngo import Ngo
from app.schemas.group import Group
from app.schemas.event import Event
from app.models.user import User
from app.services.search import search_service

router = APIRouter(prefix="/search", tags=["Search"])

@router.get("/ngos", response_model=List[Ngo])
def search_ngos(
    q: str = Query(..., min_length=1, description="Search query for NGOs"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search discoverable (public + verified) NGOs.
    """
    return search_service.search_ngos(db, q=q, skip=skip, limit=limit)

@router.get("/groups", response_model=List[Group])
def search_groups(
    q: str = Query(..., min_length=1, description="Search query for Groups"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Search groups. Returns public groups or groups the user has access to.
    """
    user_id = current_user.id if current_user else None
    return search_service.search_groups(db, q=q, user_id=user_id, skip=skip, limit=limit)

@router.get("/events", response_model=List[Event])
def search_events(
    q: str = Query(..., min_length=1, description="Search query for Events"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Search events. Returns events the user has visibility for.
    """
    user_id = current_user.id if current_user else None
    return search_service.search_events(db, q=q, user_id=user_id, skip=skip, limit=limit)
