from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from app.models.ngo import Ngo, NgoVisibility, NgoVerificationStatus
from app.models.group import Group, GroupVisibility, GroupMember
from app.models.event import Event, EventVisibility
from app.models.ngo_member import NgoMember

class SearchService:
    def _is_postgresql(self, db: Session) -> bool:
        return db.bind.dialect.name == 'postgresql'

    def search_ngos(self, db: Session, q: str, skip: int = 0, limit: int = 20) -> List[Ngo]:
        query = db.query(Ngo).filter(
            Ngo.visibility == NgoVisibility.public,
            Ngo.verification_status == NgoVerificationStatus.verified
        )

        if self._is_postgresql(db):
            from sqlalchemy import literal_column
            search_vector = func.to_tsvector('english', literal_column("name || ' ' || slug || ' ' || coalesce(about, '')"))
            search_query = func.websearch_to_tsquery('english', q)
            query = query.filter(search_vector.op('@@')(search_query))
        else:
            search_term = f"%{q}%"
            query = query.filter(
                or_(
                    Ngo.name.ilike(search_term),
                    Ngo.slug.ilike(search_term),
                    Ngo.about.ilike(search_term)
                )
            )

        return query.offset(skip).limit(limit).all()

    def search_groups(self, db: Session, q: str, user_id: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Group]:
        base_query = db.query(Group)

        # Visibility logic
        # 1. Public groups
        # 2. Or, if user_id is provided, groups where user is a member or NGO admin/owner
        visibility_conditions = [Group.visibility == GroupVisibility.public]

        if user_id:
            user_is_member = db.query(GroupMember).filter(
                GroupMember.group_id == Group.id,
                GroupMember.user_id == user_id
            ).exists()

            from app.models.ngo_role import NgoRole
            user_is_ngo_admin = db.query(NgoMember).join(NgoRole).filter(
                NgoMember.ngo_id == Group.ngo_id,
                NgoMember.user_id == user_id,
                NgoRole.name.in_(['owner', 'admin'])
            ).exists()

            visibility_conditions.append(user_is_member)
            visibility_conditions.append(user_is_ngo_admin)

        base_query = base_query.filter(or_(*visibility_conditions))

        if self._is_postgresql(db):
            # Use literal_column to match index exactly
            from sqlalchemy import literal_column
            search_vector = func.to_tsvector('english', literal_column("name || ' ' || slug || ' ' || coalesce(about, '')"))
            search_query = func.websearch_to_tsquery('english', q)
            base_query = base_query.filter(search_vector.op('@@')(search_query))
        else:
            search_term = f"%{q}%"
            base_query = base_query.filter(
                or_(
                    Group.name.ilike(search_term),
                    Group.slug.ilike(search_term),
                    Group.about.ilike(search_term)
                )
            )

        return base_query.offset(skip).limit(limit).all()

    def search_events(self, db: Session, q: str, user_id: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Event]:
        base_query = db.query(Event)

        # Event visibility: public events OR events where user is in the group/ngo
        visibility_conditions = [Event.visibility == EventVisibility.public]

        if user_id:
            from app.models.ngo_role import NgoRole
            # User is part of NGO
            user_in_ngo = db.query(NgoMember).filter(
                NgoMember.ngo_id == Event.ngo_id,
                NgoMember.user_id == user_id
            ).exists()

            # User is part of Group
            user_in_group = db.query(GroupMember).filter(
                GroupMember.group_id == Event.group_id,
                GroupMember.user_id == user_id
            ).exists()

            visibility_conditions.append(user_in_ngo)
            visibility_conditions.append(user_in_group)

        base_query = base_query.filter(or_(*visibility_conditions))

        if self._is_postgresql(db):
            from sqlalchemy import literal_column
            search_vector = func.to_tsvector('english', literal_column("title || ' ' || coalesce(description, '') || ' ' || coalesce(location, '')"))
            search_query = func.websearch_to_tsquery('english', q)
            base_query = base_query.filter(search_vector.op('@@')(search_query))
        else:
            search_term = f"%{q}%"
            base_query = base_query.filter(
                or_(
                    Event.title.ilike(search_term),
                    Event.description.ilike(search_term),
                    Event.location.ilike(search_term)
                )
            )

        return base_query.offset(skip).limit(limit).all()

search_service = SearchService()
