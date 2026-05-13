from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.websockets import WebSocketDisconnect

from api.deps.auth import get_current_user_id
from api.deps.db import get_db
from api.deps.services import get_chat_service, get_image_storage
from api.routes.ws_chat import handle_chat_ws_text
from api.schemas.message import SendTextMessageBody
from db.session import AsyncSessionLocal
from models.message import Message
from repositories.chat_repository import ChatRepository
from repositories.message_repository import MessageRepository
from services.chat_app_service import ChatAppService
from services.chat_room_registry import ChatRoomRegistry
from utils.message_serialization import message_to_public_dict

router = APIRouter()


def _message_to_dict(m: Message) -> dict:
    return message_to_public_dict(m)


@router.get("")
async def list_chats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ChatRepository(db)
    return await repo.list_chats_summary(user_id)


@router.websocket("/{peer_user_id}/ws")
async def chat_room_websocket(websocket: WebSocket, peer_user_id: int) -> None:
    """Bidirectional chat room: JSON frames to send; ``chat.new_message`` broadcasts for delivery."""
    raw_uid = websocket.headers.get("x-user-id")
    if not raw_uid:
        await websocket.close(code=4401, reason="missing user")
        return
    try:
        user_id = int(raw_uid)
    except ValueError:
        await websocket.close(code=4401, reason="invalid user")
        return
    if peer_user_id == user_id:
        await websocket.close(code=4400, reason="invalid peer")
        return

    async with AsyncSessionLocal() as db:
        repo = ChatRepository(db)
        chat = await repo.get_chat_between(user_id, peer_user_id)
        if chat is None:
            await websocket.close(code=4404, reason="chat not found")
            return

    registry: ChatRoomRegistry = websocket.app.state.chat_room_registry
    producer = websocket.app.state.kafka_producer
    storage = get_image_storage()

    await websocket.accept()
    await registry.attach(user_id, peer_user_id, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            await handle_chat_ws_text(
                raw,
                user_id=user_id,
                peer_user_id=peer_user_id,
                websocket=websocket,
                registry=registry,
                producer=producer,
                storage=storage,
            )
    except WebSocketDisconnect:
        pass
    finally:
        await registry.detach(user_id, peer_user_id, websocket)


@router.post("/{peer_user_id}/messages", status_code=201)
async def send_message(
    request: Request,
    peer_user_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChatAppService = Depends(get_chat_service),
):
    """JSON `{"body":"..."}` or multipart with optional `body` (caption) and/or `file` (image)."""
    content_type = (request.headers.get("content-type") or "").lower()
    if content_type.startswith("multipart/form-data"):
        form = await request.form()
        raw_body = form.get("body")
        body: str | None = None
        if raw_body is not None:
            body = str(raw_body).strip() or None
        file_item = form.get("file")
        image_bytes: bytes | None = None
        image_ct: str | None = None
        if file_item is not None and hasattr(file_item, "read"):
            image_bytes = await file_item.read()
            if image_bytes:
                image_ct = file_item.content_type
        msg = await svc.send_chat_message(
            user_id,
            peer_user_id,
            body=body,
            image_bytes=image_bytes if image_bytes else None,
            image_content_type=image_ct,
        )
        return _message_to_dict(msg)

    try:
        raw = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=422, detail="invalid json body") from exc
    payload = SendTextMessageBody.model_validate(raw)
    msg = await svc.send_text_message(user_id, peer_user_id, payload.body)
    return _message_to_dict(msg)


@router.get("/{peer_user_id}")
async def get_chat_with_user(
    peer_user_id: int,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ChatRepository(db)
    msg_repo = MessageRepository(db)
    chat = await repo.get_chat_between(user_id, peer_user_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="chat not found")
    messages = await msg_repo.list_for_chat(chat.id)
    return {
        "chat_id": str(chat.id),
        "peer_user_id": peer_user_id,
        "messages": [_message_to_dict(m) for m in messages],
    }


@router.delete("/{peer_user_id}", status_code=204)
async def delete_chat(
    peer_user_id: int,
    user_id: int = Depends(get_current_user_id),
    svc: ChatAppService = Depends(get_chat_service),
):
    await svc.delete_chat_for_both_users(user_id, peer_user_id)
