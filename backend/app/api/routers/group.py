from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.api.deps import get_db, get_current_user
from app.schemas.group import Group, GroupCreate, GroupUpdate, GroupMember, GroupJoinRequest, GroupJoinRequestReview
from app.services.group import group_service, group_member_service, group_role_service, group_join_request_service
from app.services.ngo import ngo_service
from app.services.ngo_member import ngo_member_service
from app.repositories.group import group_join_request_repo
from app.models.user import User

router = APIRouter(tags=["Groups"])

class RoleAssignRequest(BaseModel):
    user_id: str
    role_name: str

class RoleRemoveRequest(BaseModel):
    user_id: str

@router.post("/ngos/{ngo_id}/groups", response_model=Group, status_code=status.HTTP_201_CREATED)
def create_group(
    ngo_id: str,
    group_in: GroupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ngo = ngo_service.get_ngo(db, ngo_id)
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")

    member = ngo_member_service.get_member(db, current_user.id, ngo_id)
    if not member or member.role.name not in ["owner", "admin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions to create groups for this NGO")

    return group_service.create_group(db, obj_in=group_in, ngo_id=ngo_id, user_id=current_user.id)

@router.get("/ngos/{ngo_id}/groups", response_model=List[Group])
def list_ngo_groups(
    ngo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ngo = ngo_service.get_ngo(db, ngo_id)
    if not ngo:
        raise HTTPException(status_code=404, detail="NGO not found")

    member = ngo_member_service.get_member(db, current_user.id, ngo_id)
    include_invite_only = False

    # NGO owners/admins can see all groups, other members can also see invite_only groups if they belong to the NGO?
    # For simplicity, if they are NGO members, they can see them.
    # Otherwise, they only see public groups
    if member:
        include_invite_only = True

    return group_service.get_groups_by_ngo_id(db, ngo_id, include_invite_only=include_invite_only)

@router.get("/groups/{group_id}", response_model=Group)
def get_group(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if group.visibility == "invite_only":
        group_member = group_member_service.get_member(db, current_user.id, group_id)
        ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)

        if not group_member and not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
             raise HTTPException(status_code=403, detail="Not authorized to view this group")

    return group

@router.patch("/groups/{group_id}", response_model=Group)
def update_group(
    group_id: str,
    group_in: GroupUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group_member = group_member_service.get_member(db, current_user.id, group_id)
    if not group_member or group_member.role.name != "group_admin":
        ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)
        if not ngo_member or ngo_member.role.name not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Not enough permissions to update this group")

    return group_service.update_group(db, db_obj=group, obj_in=group_in)

@router.get("/groups/{group_id}/members/me", response_model=Optional[GroupMember])
def get_my_group_member(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return group_member_service.get_member(db, current_user.id, group_id)

@router.get("/groups/{group_id}/members", response_model=List[GroupMember])
def list_group_members(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    group_member = group_member_service.get_member(db, current_user.id, group_id)
    if not group_member and group.visibility == "invite_only":
        ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)
        if not ngo_member or ngo_member.role.name not in ["owner", "admin"]:
            raise HTTPException(status_code=403, detail="Not authorized to view members")

    return group_member_service.get_all_members(db, group_id)

@router.post("/groups/{group_id}/roles/assign", response_model=GroupMember)
def assign_role(
    group_id: str,
    request: RoleAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Only group admins or ngo admins/owners can assign roles
    current_group_member = group_member_service.get_member(db, current_user.id, group_id)
    is_group_admin = current_group_member and current_group_member.role.name == "group_admin"

    ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)
    is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

    if not is_group_admin and not is_ngo_admin:
        raise HTTPException(status_code=403, detail="Not authorized to assign roles")

    target_member = group_member_service.get_member(db, request.user_id, group_id)
    if target_member:
        # Update role (simplification: we just update it here or delete and re-add)
        role = group_role_service.get_role_by_name(db, request.role_name)
        if not role:
            raise HTTPException(status_code=400, detail="Role not found")
        target_member.role_id = role.id
        db.add(target_member)
        db.commit()
        db.refresh(target_member)
        return target_member
    else:
        return group_member_service.add_member(db, request.user_id, group_id, request.role_name)

@router.post("/groups/{group_id}/roles/remove", status_code=status.HTTP_204_NO_CONTENT)
def remove_role(
    group_id: str,
    request: RoleRemoveRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Only group admins or ngo admins/owners can remove roles
    current_group_member = group_member_service.get_member(db, current_user.id, group_id)
    is_group_admin = current_group_member and current_group_member.role.name == "group_admin"

    ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)
    is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

    if not is_group_admin and not is_ngo_admin:
        raise HTTPException(status_code=403, detail="Not authorized to remove roles")

    # Prevent self-removal if only group admin? Let's just allow removal for now
    group_member_service.remove_member(db, request.user_id, group_id)
    return

@router.get("/groups/{group_id}/join-request/me", response_model=Optional[GroupJoinRequest])
def get_my_join_request(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    return group_join_request_repo.get_by_user_and_group(db, current_user.id, group_id)

@router.post("/groups/{group_id}/join-request", response_model=GroupJoinRequest, status_code=status.HTTP_201_CREATED)
def create_join_request(
    group_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # If invite_only, you might want to prevent join requests if it's strictly invite only
    # But product rule: "For invite_only groups, direct join requests may still be allowed"
    return group_join_request_service.create_request(db, current_user.id, group_id)

@router.get("/groups/{group_id}/join-requests", response_model=List[GroupJoinRequest])
def list_join_requests(
    group_id: str,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    group = group_service.get_group(db, group_id)
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    current_group_member = group_member_service.get_member(db, current_user.id, group_id)
    is_group_admin = current_group_member and current_group_member.role.name == "group_admin"
    ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)
    is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

    if not is_group_admin and not is_ngo_admin:
        raise HTTPException(status_code=403, detail="Not authorized to view join requests")

    return group_join_request_service.get_requests_for_group(db, group_id, status)

@router.post("/join-requests/{request_id}/approve", response_model=GroupJoinRequest)
def approve_join_request(
    request_id: str,
    review: GroupJoinRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    join_request = group_join_request_repo.get(db, request_id)
    if not join_request:
        raise HTTPException(status_code=404, detail="Join request not found")

    group = group_service.get_group(db, join_request.group_id)

    current_group_member = group_member_service.get_member(db, current_user.id, group.id)
    is_group_admin = current_group_member and current_group_member.role.name == "group_admin"
    ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)
    is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

    if not is_group_admin and not is_ngo_admin:
        raise HTTPException(status_code=403, detail="Not authorized to approve join requests")

    return group_join_request_service.approve_request(db, request_id, current_user.id, review.admin_comment)

@router.post("/join-requests/{request_id}/reject", response_model=GroupJoinRequest)
def reject_join_request(
    request_id: str,
    review: GroupJoinRequestReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    join_request = group_join_request_repo.get(db, request_id)
    if not join_request:
        raise HTTPException(status_code=404, detail="Join request not found")

    group = group_service.get_group(db, join_request.group_id)

    current_group_member = group_member_service.get_member(db, current_user.id, group.id)
    is_group_admin = current_group_member and current_group_member.role.name == "group_admin"
    ngo_member = ngo_member_service.get_member(db, current_user.id, group.ngo_id)
    is_ngo_admin = ngo_member and ngo_member.role.name in ["owner", "admin"]

    if not is_group_admin and not is_ngo_admin:
        raise HTTPException(status_code=403, detail="Not authorized to reject join requests")

    return group_join_request_service.reject_request(db, request_id, current_user.id, review.admin_comment)
