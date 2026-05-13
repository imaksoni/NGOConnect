import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.event import Event, EventVisibility
from app.models.ngo import NgoVerificationStatus
from app.schemas.event import EventCreate, EventUpdate
from app.services.notification import notification_service
from app.models.ngo_member import NgoMember
from app.models.group import GroupMember
from app.repositories.event import event_repo
from app.services.ngo import ngo_service
from app.services.group import group_service
from app.services.ngo_member import ngo_member_service
from app.services.group import group_member_service

class EventService:
    def get_event(self, db: Session, event_id: str) -> Optional[Event]:
        return event_repo.get(db, event_id)

    def create_ngo_event(self, db: Session, ngo_id: str, event_in: EventCreate, creator_id: str) -> Event:
        ngo = ngo_service.get_ngo(db, ngo_id)
        if not ngo:
            raise HTTPException(status_code=404, detail="NGO not found")

        ngo_member = ngo_member_service.get_member(db, creator_id, ngo_id)
        if not ngo_member or ngo_member.role.name not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Not enough permissions to create events for this NGO")

        if event_in.visibility == EventVisibility.public and ngo.verification_status != NgoVerificationStatus.verified:
            raise HTTPException(status_code=403, detail="Non-verified NGOs cannot publish public events")

        event_id = str(uuid.uuid4())
        event = event_repo.create(db, obj_in=event_in, event_id=event_id, creator_id=creator_id, ngo_id=ngo_id)

        # Notify NGO members
        if not event.is_private:
            members = db.query(NgoMember).filter(NgoMember.ngo_id == ngo_id).all()
            for member in members:
                if member.user_id != creator_id:
                    notification_service.send_push_notification(
                        db=db,
                        user_id=member.user_id,
                        title="New NGO Event",
                        body=f"A new event '{event.title}' was created by '{ngo.name}'.",
                        data={"type": "new_event", "event_id": event.id}
                    )

        return event

    def create_group_event(self, db: Session, group_id: str, event_in: EventCreate, creator_id: str) -> Event:
        group = group_service.get_group(db, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        ngo = ngo_service.get_ngo(db, group.ngo_id)

        group_member = group_member_service.get_member(db, creator_id, group_id)
        is_group_admin = group_member and group_member.role.name == "group_admin"

        ngo_member = ngo_member_service.get_member(db, creator_id, group.ngo_id)
        is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

        if not is_group_admin and not is_ngo_admin:
            raise HTTPException(status_code=403, detail="Not enough permissions to create events for this group")

        if event_in.visibility == EventVisibility.public and ngo.verification_status != NgoVerificationStatus.verified:
            raise HTTPException(status_code=403, detail="Groups under non-verified NGOs cannot publish public events")

        event_id = str(uuid.uuid4())
        event = event_repo.create(db, obj_in=event_in, event_id=event_id, creator_id=creator_id, group_id=group_id)

        # Notify Group members
        members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
        for member in members:
            if member.user_id != creator_id:
                notification_service.send_push_notification(
                    db=db,
                    user_id=member.user_id,
                    title="New Group Event",
                    body=f"A new event '{event.title}' was created in group '{group.name}'.",
                    data={"type": "new_event", "event_id": event.id}
                )

        return event

    def update_event(self, db: Session, event_id: str, event_in: EventUpdate, user_id: str) -> Event:
        event = event_repo.get(db, event_id)
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.ngo_id:
            ngo_member = ngo_member_service.get_member(db, user_id, event.ngo_id)
            if not ngo_member or ngo_member.role.name not in ["owner", "admin"]:
                raise HTTPException(status_code=403, detail="Not enough permissions to edit this event")
            ngo = ngo_service.get_ngo(db, event.ngo_id)

            if event_in.visibility == EventVisibility.public and ngo.verification_status != NgoVerificationStatus.verified:
                raise HTTPException(status_code=403, detail="Non-verified NGOs cannot publish public events")

        elif event.group_id:
            group = group_service.get_group(db, event.group_id)
            group_member = group_member_service.get_member(db, user_id, event.group_id)
            is_group_admin = group_member and group_member.role.name == "group_admin"
            ngo_member = ngo_member_service.get_member(db, user_id, group.ngo_id)
            is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

            if not is_group_admin and not is_ngo_admin:
                raise HTTPException(status_code=403, detail="Not enough permissions to edit this event")

            ngo = ngo_service.get_ngo(db, group.ngo_id)
            if event_in.visibility == EventVisibility.public and ngo.verification_status != NgoVerificationStatus.verified:
                raise HTTPException(status_code=403, detail="Groups under non-verified NGOs cannot publish public events")

        return event_repo.update(db, db_obj=event, obj_in=event_in)

    def get_ngo_events(self, db: Session, ngo_id: str, user_id: Optional[str] = None) -> List[Event]:
        ngo = ngo_service.get_ngo(db, ngo_id)
        if not ngo:
            raise HTTPException(status_code=404, detail="NGO not found")

        public_only = True
        if user_id:
            ngo_member = ngo_member_service.get_member(db, user_id, ngo_id)
            if ngo_member:
                public_only = False

        return event_repo.get_ngo_events(db, ngo_id, public_only=public_only)

    def get_group_events(self, db: Session, group_id: str, user_id: Optional[str] = None) -> List[Event]:
        group = group_service.get_group(db, group_id)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")

        public_only = True
        if user_id:
            group_member = group_member_service.get_member(db, user_id, group_id)
            if group_member:
                public_only = False
            else:
                ngo_member = ngo_member_service.get_member(db, user_id, group.ngo_id)
                if ngo_member and ngo_member.role.name in ["owner", "admin"]:
                    public_only = False

        return event_repo.get_group_events(db, group_id, public_only=public_only)

event_service = EventService()
