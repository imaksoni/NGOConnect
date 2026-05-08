from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.message import Message, MessageAttachment
from app.schemas.message import MessageCreate, MessageAttachmentCreate
from app.repositories.message import message_repo, message_attachment_repo
from app.services.channel import channel_service
from app.services.group import group_service, group_member_service
from app.services.ngo_member import ngo_member_service

class MessageService:
    def _check_channel_access(self, db: Session, user_id: str, channel_id: str):
        channel = channel_service.get_channel(db, channel_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")

        group = group_service.get_group(db, channel.group_id)
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        group_member = group_member_service.get_member(db, user_id, group.id)
        ngo_member = ngo_member_service.get_member(db, user_id, group.ngo_id)

        # Basic access logic: if group is invite_only, must be member or ngo admin
        if group.visibility.value == "invite_only":
            if not group_member and not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
                 raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this channel")

        if channel.visibility.value == "invite_only" and not group_member:
            if not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this channel")

        return channel

    def get_message(self, db: Session, message_id: str) -> Optional[Message]:
        return message_repo.get(db, message_id)

    def get_messages(self, db: Session, channel_id: str, user_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        self._check_channel_access(db, user_id, channel_id)
        messages = message_repo.get_by_channel(db, channel_id, limit, offset)
        # Reverse to show chronological order if needed, but usually frontend handles it.
        # API returns newest first due to desc() in repo.
        return messages

    def create_message(self, db: Session, obj_in: MessageCreate, channel_id: str, user_id: str) -> Message:
        self._check_channel_access(db, user_id, channel_id)
        return message_repo.create(db, obj_in, channel_id, user_id)

    def create_attachment(self, db: Session, obj_in: MessageAttachmentCreate, message_id: str, user_id: str) -> MessageAttachment:
        message = message_repo.get(db, message_id)
        if not message:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

        # User must have access to the channel to attach files to a message in it
        self._check_channel_access(db, user_id, message.channel_id)

        # Optionally restrict to the sender
        if message.sender_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add attachments to this message")

        return message_attachment_repo.create(db, obj_in, message_id, user_id)

message_service = MessageService()
