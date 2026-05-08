from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.channel import Channel
from app.schemas.channel import ChannelCreate, ChannelUpdate
import uuid

class ChannelRepository:
    def get(self, db: Session, channel_id: str) -> Optional[Channel]:
        return db.query(Channel).filter(Channel.id == channel_id).first()

    def get_by_group_id(self, db: Session, group_id: str) -> List[Channel]:
        return db.query(Channel).filter(Channel.group_id == group_id).all()

    def count_by_group_id(self, db: Session, group_id: str) -> int:
        return db.query(Channel).filter(Channel.group_id == group_id).count()

    def create(self, db: Session, obj_in: ChannelCreate, group_id: str, created_by: str) -> Channel:
        db_obj = Channel(
            id=str(uuid.uuid4()),
            group_id=group_id,
            name=obj_in.name,
            slug=obj_in.slug,
            description=obj_in.description,
            visibility=obj_in.visibility,
            type=obj_in.type,
            created_by=created_by,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, db_obj: Channel, obj_in: ChannelUpdate) -> Channel:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, db_obj: Channel):
        db.delete(db_obj)
        db.commit()

channel_repo = ChannelRepository()
