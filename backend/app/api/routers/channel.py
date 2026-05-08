from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.schemas.channel import Channel, ChannelCreate, ChannelUpdate
from app.services.channel import channel_service
from app.services.group import group_service, group_member_service
from app.services.ngo import ngo_service
from app.services.ngo_member import ngo_member_service
from app.models.user import User

router = APIRouter(tags=["Channels"])

def check_group_admin_or_ngo_admin(db: Session, user_id: str, group_id: str, ngo_id: str):
    group_member = group_member_service.get_member(db, user_id, group_id)
    is_group_admin = group_member and group_member.role.name == "group_admin"
    ngo_member = ngo_member_service.get_member(db, user_id, ngo_id)
    is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]
    if not is_group_admin and not is_ngo_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions to manage channels for this group")

def check_channel_view_access(db: Session, user_id: str, group_id: str, ngo_id: str, channel_visibility: str, group_visibility: str):
    # Base logic from group view:
    group_member = group_member_service.get_member(db, user_id, group_id)
    ngo_member = ngo_member_service.get_member(db, user_id, ngo_id)

    if group_visibility == "invite_only":
        if not group_member and not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
             raise HTTPException(status_code=403, detail="Not authorized to view this group or its channels")

    # Check channel level visibility
    if channel_visibility == "invite_only" and not group_member:
        # Assuming invite_only channels require group membership at minimum (maybe a specific channel role later)
        # We will require group membership to view invite_only channels.
        if not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
            raise HTTPException(status_code=403, detail="Not authorized to view this channel")

@router.post("/groups/{group_id}/channels", response_model=Channel, status_code=status.HTTP_201_CREATED)
def create_channel(
    group_id: str,
    channel_in: ChannelCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    check_group_admin_or_ngo_admin(db, current_user.id, group.id, group.ngo_id)

    return channel_service.create_channel(db, obj_in=channel_in, group_id=group_id, user_id=current_user.id)

@router.get("/groups/{group_id}/channels", response_model=List[Channel])
def list_group_channels(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Verify if user can see the group at all
    group_member = group_member_service.get_member(db, current_user.id, group_id)
    ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)

    if group.visibility == "invite_only":
        if not group_member and not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
             raise HTTPException(status_code=403, detail="Not authorized to view channels for this group")

    channels = channel_service.get_channels_by_group_id(db, group_id)

    # Filter channels based on visibility
    result = []
    for ch in channels:
        if ch.visibility == "public" or group_member or (ngo_member and ngo_member.role.name in ["owner", "admin"]):
            result.append(ch)

    return result

@router.get("/channels/{channel_id}", response_model=Channel)
def get_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    channel = channel_service.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    group = group_service.get_group(db, channel.group_id)

    check_channel_view_access(db, current_user.id, group.id, group.ngo_id, channel.visibility.value, group.visibility.value)

    return channel

@router.patch("/channels/{channel_id}", response_model=Channel)
def update_channel(
    channel_id: str,
    channel_in: ChannelUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    channel = channel_service.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    group = group_service.get_group(db, channel.group_id)
    check_group_admin_or_ngo_admin(db, current_user.id, group.id, group.ngo_id)

    return channel_service.update_channel(db, db_obj=channel, obj_in=channel_in)

@router.delete("/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_channel(
    channel_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    channel = channel_service.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    group = group_service.get_group(db, channel.group_id)
    check_group_admin_or_ngo_admin(db, current_user.id, group.id, group.ngo_id)

    channel_service.delete_channel(db, db_obj=channel)
    return
