from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.channel import Channel
from app.models.group import Group
from app.schemas.channel import ChannelCreate, ChannelUpdate
from app.repositories.channel import channel_repo

class ChannelService:
    def get_channel(self, db: Session, channel_id: str) -> Optional[Channel]:
        return channel_repo.get(db, channel_id)

    def get_channels_by_group_id(self, db: Session, group_id: str) -> List[Channel]:
        return channel_repo.get_by_group_id(db, group_id)

    def create_channel(self, db: Session, obj_in: ChannelCreate, group_id: str, user_id: str) -> Channel:
        # Enforce max 5 channels per group with a robust check against race conditions
        # We lock the group row to ensure sequential processing for this group's channels
        try:
            group = db.query(Group).filter(Group.id == group_id).with_for_update().first()
            if not group:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

            # Count current channels
            current_count = channel_repo.count_by_group_id(db, group_id)
            if current_count >= 5:
                db.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A group can have a maximum of 5 channels")

            # Create channel
            channel = channel_repo.create(db, obj_in, group_id, user_id)
            db.commit() # release lock and finalize creation
            return channel
        except Exception as e:
            db.rollback()
            raise e

    def update_channel(self, db: Session, db_obj: Channel, obj_in: ChannelUpdate) -> Channel:
        return channel_repo.update(db, db_obj, obj_in)

    def delete_channel(self, db: Session, db_obj: Channel):
        channel_repo.delete(db, db_obj)

channel_service = ChannelService()
