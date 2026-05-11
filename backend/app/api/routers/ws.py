from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.core.security import verify_token
from app.repositories.user import user_repository
from app.services.channel import channel_service
from app.services.group import group_service, group_member_service
from app.services.ngo_member import ngo_member_service
from app.core.websockets import manager
import logging

router = APIRouter(tags=["WebSockets"])
logger = logging.getLogger(__name__)

async def get_current_user_ws(token: str, db: Session):
    if not token:
        return None
    payload = verify_token(token, "access")
    if payload is None:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    user = user_repository.get_by_id(db, user_id=user_id)
    if not user or not user.is_active:
        return None
    return user

def _check_ws_channel_access(db: Session, user_id: str, channel_id: str):
    channel = channel_service.get_channel(db, channel_id)
    if not channel:
        return False

    group = group_service.get_group(db, channel.group_id)
    if not group:
        return False

    group_member = group_member_service.get_member(db, user_id, group.id)
    ngo_member = ngo_member_service.get_member(db, user_id, group.ngo_id)

    if group.visibility.value == "invite_only":
        if not group_member and not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
            return False

    if channel.visibility.value == "invite_only" and not group_member:
        if not (ngo_member and ngo_member.role.name in ["owner", "admin"]):
            return False

    return True

@router.websocket("/ws/channels/{channel_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    channel_id: str,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    # Authenticate User
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid or missing token")
        return

    # Authorize Channel Access
    has_access = _check_ws_channel_access(db, user.id, channel_id)
    if not has_access:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Not authorized to access this channel")
        return

    await manager.connect(websocket, channel_id)
    try:
        while True:
            # We don't currently support sending messages directly through the socket,
            # only receiving broadcasts of REST-created messages.
            # But we need to receive to keep connection open and handle disconnects.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, channel_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket, channel_id)
