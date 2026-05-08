import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.message import Message, MessageAttachment
from app.schemas.message import MessageCreate, MessageUpdate, MessageAttachmentCreate

class MessageRepository:
    def get(self, db: Session, id: str) -> Optional[Message]:
        return db.query(Message).filter(Message.id == id).first()

    def get_by_channel(self, db: Session, channel_id: str, limit: int = 50, offset: int = 0) -> List[Message]:
        return db.query(Message).filter(Message.channel_id == channel_id).order_by(Message.created_at.desc()).offset(offset).limit(limit).all()

    def create(self, db: Session, obj_in: MessageCreate, channel_id: str, sender_id: str) -> Message:
        db_obj = Message(
            id=str(uuid.uuid4()),
            channel_id=channel_id,
            sender_id=sender_id,
            content=obj_in.content,
            type=obj_in.type
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Message, obj_in: MessageUpdate) -> Message:
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Message) -> None:
        db.delete(db_obj)
        db.commit()

class MessageAttachmentRepository:
    def create(self, db: Session, obj_in: MessageAttachmentCreate, message_id: str, uploader_id: str) -> MessageAttachment:
        db_obj = MessageAttachment(
            id=str(uuid.uuid4()),
            message_id=message_id,
            file_name=obj_in.file_name,
            content_type=obj_in.content_type,
            file_size=obj_in.file_size,
            storage_key=obj_in.storage_key,
            uploaded_by=uploader_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get(self, db: Session, id: str) -> Optional[MessageAttachment]:
        return db.query(MessageAttachment).filter(MessageAttachment.id == id).first()

message_repo = MessageRepository()
message_attachment_repo = MessageAttachmentRepository()
