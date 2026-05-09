from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.event import Event

class EventRepository:
    def get(self, db: Session, event_id: str) -> Optional[Event]:
        return db.query(Event).filter(Event.id == event_id).first()

    def get_ngo_events(self, db: Session, ngo_id: str, public_only: bool = False) -> List[Event]:
        query = db.query(Event).filter(Event.ngo_id == ngo_id)
        if public_only:
            query = query.filter(Event.visibility == "public")
        return query.order_by(Event.start_time.asc()).all()

    def get_group_events(self, db: Session, group_id: str, public_only: bool = False) -> List[Event]:
        query = db.query(Event).filter(Event.group_id == group_id)
        if public_only:
            query = query.filter(Event.visibility == "public")
        return query.order_by(Event.start_time.asc()).all()

    def create(self, db: Session, *, obj_in, event_id: str, creator_id: str, ngo_id: Optional[str] = None, group_id: Optional[str] = None) -> Event:
        db_obj = Event(
            id=event_id,
            ngo_id=ngo_id,
            group_id=group_id,
            title=obj_in.title,
            description=obj_in.description,
            start_time=obj_in.start_time,
            end_time=obj_in.end_time,
            location=obj_in.location,
            visibility=obj_in.visibility,
            created_by=creator_id
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Event, obj_in) -> Event:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, event_id: str) -> None:
        obj = db.query(Event).filter(Event.id == event_id).first()
        if obj:
            db.delete(obj)
            db.commit()

event_repo = EventRepository()
