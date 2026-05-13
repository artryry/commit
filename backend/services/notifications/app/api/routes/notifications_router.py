"""WebSocket endpoint + workers."""

import logging

from fastapi import APIRouter, Depends, WebSocket
from api.deps.state import get_connection_manager
from db.session import AsyncSessionLocal
from repositories.notification_repository import NotificationRepository
from services.connection_manager import ConnectionManager
from services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)

router = APIRouter()


async def flush_pending_on_connect(cm: ConnectionManager, user_id: int) -> None:
    """Deliver queued rows while the socket is registered (separate DB session).

    **Do not** use Starlette ``BackgroundTasks`` here: for WebSocket handlers those tasks run only
    after the handler returns (i.e. on disconnect), when the client is no longer connected — so
    pending notifications would never flush during a normal session.
    """
    async with AsyncSessionLocal() as session:
        try:
            repo = NotificationRepository(session)
            delivery = DeliveryService(repo, cm, session)
            await delivery.flush_pending_for_user(user_id)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("flush pending notifications failed user_id=%s", user_id)


@router.websocket("/ws")
async def notifications_websocket(
    websocket: WebSocket,
    cm: ConnectionManager = Depends(get_connection_manager),
) -> None:
    # Identity comes from api-gateway after JWT verification (X-User-Id).
    raw_uid = websocket.headers.get("x-user-id")
    if not raw_uid:
        await websocket.close(code=4401, reason="missing user")
        return
    try:
        user_id = int(raw_uid)
    except ValueError:
        await websocket.close(code=4401, reason="invalid user")
        return

    await websocket.accept()
    await cm.connect(user_id, websocket)

    # Rows with `delivered_at` IS NULL (user was offline). Must run while this socket is registered.
    await flush_pending_on_connect(cm, user_id)

    try:
        while True:
            await websocket.receive_text()
    finally:
        cm.disconnect(user_id, websocket)
