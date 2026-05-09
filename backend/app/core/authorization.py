from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.services.group import group_member_service, group_service
from app.services.ngo_member import ngo_member_service
from app.services.ngo import ngo_service

def check_ngo_admin(db: Session, user_id: str, ngo_id: str):
    ngo_member = ngo_member_service.get_member(db, user_id, ngo_id)
    if not ngo_member or ngo_member.role.name not in ["owner", "admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this NGO")
    return True

def check_group_admin_or_ngo_admin(db: Session, user_id: str, group_id: str, ngo_id: str):
    group_member = group_member_service.get_member(db, user_id, group_id)
    is_group_admin = group_member and group_member.role.name == "group_admin"

    ngo_member = ngo_member_service.get_member(db, user_id, ngo_id)
    is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

    if not is_group_admin and not is_ngo_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions to manage this group")
    return True

def check_group_view_access(db: Session, user_id: str, group_id: str, ngo_id: str, group_visibility: str):
    group_member = group_member_service.get_member(db, user_id, group_id)
    ngo_member = ngo_member_service.get_member(db, user_id, ngo_id)

    if group_visibility == "invite_only":
        if not group_member and not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this group or its channels")
    return True

def check_channel_view_access(db: Session, user_id: str, group_id: str, ngo_id: str, channel_visibility: str, group_visibility: str):
    check_group_view_access(db, user_id, group_id, ngo_id, group_visibility)

    group_member = group_member_service.get_member(db, user_id, group_id)
    ngo_member = ngo_member_service.get_member(db, user_id, ngo_id)

    if channel_visibility == "invite_only" and not group_member:
        if not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this channel")
    return True
