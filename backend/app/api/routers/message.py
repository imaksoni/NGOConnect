from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.storage import storage_provider

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

@router.post("/channels/{channel_id}/attachments/upload", response_model=Message, status_code=status.HTTP_201_CREATED)
def upload_attachment(
    channel_id: str,
    file: UploadFile = File(...),
    content: Optional[str] = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Verify channel access
    message_service._check_channel_access(db, current_user.id, channel_id)

    # Validate file size (rough check before reading everything if possible, or read and check)
    # Using a simple check based on file.size if provided, otherwise check after reading
    if file.size and file.size > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE_MB}MB.")

    # Create the message first
    message_in = MessageCreate(content=content, type="file")
    message = message_service.create_message(db, message_in, channel_id, current_user.id)

    # Save the file
    try:
        storage_key = storage_provider.upload_file(file.file, file.filename, file.content_type)
    except Exception as e:
        # We might want to delete the created message here to keep DB clean if upload fails
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")

    # Create attachment metadata
    attachment_in = MessageAttachmentCreate(
        file_name=file.filename,
        content_type=file.content_type,
        file_size=file.size or 0,
        storage_key=storage_key
    )
    message_service.create_attachment(db, attachment_in, message.id, current_user.id)

    # Return updated message with attachments
    return message_service.get_message(db, message.id)

@router.get("/attachments/{attachment_id}/download")
def download_attachment(
    attachment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attachment = message_service.get_attachment(db, attachment_id, current_user.id)

    if settings.STORAGE_BACKEND == "s3":
        url = storage_provider.get_download_url(attachment.storage_key, attachment.file_name)
        if not url:
            raise HTTPException(status_code=404, detail="Could not generate download URL")
        return RedirectResponse(url=url)
    else:
        file_path = storage_provider.get_file_path(attachment.storage_key)
        if not file_path:
             raise HTTPException(status_code=404, detail="File path not found")
        return FileResponse(
            path=file_path,
            filename=attachment.file_name,
            media_type=attachment.content_type or "application/octet-stream"
        )
