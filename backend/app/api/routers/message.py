from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.message import Message, MessageCreate, MessageAttachment, MessageAttachmentCreate
from app.services.message import message_service
from app.models.user import User

router = APIRouter(tags=["Messages"])

@router.get("/channels/{channel_id}/messages", response_model=List[Message])
def list_messages(
    channel_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return message_service.get_messages(db, channel_id, current_user.id, limit, offset)

@router.post("/channels/{channel_id}/messages", response_model=Message, status_code=status.HTTP_201_CREATED)
def create_message(
    channel_id: str,
    message_in: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return message_service.create_message(db, message_in, channel_id, current_user.id)

@router.post("/messages/{message_id}/attachments", response_model=MessageAttachment, status_code=status.HTTP_201_CREATED)
def create_attachment(
    message_id: str,
    attachment_in: MessageAttachmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return message_service.create_attachment(db, attachment_in, message_id, current_user.id)
