from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.auth import get_current_user_id
from api.deps.db import get_db
from api.deps.services import get_chat_service
from api.schemas.message import SendTextMessageBody
from models.message import Message
from repositories.chat_repository import ChatRepository
from repositories.message_repository import MessageRepository
from services.chat_app_service import ChatAppService

router = APIRouter()


def _message_to_dict(m: Message) -> dict:
    return {
        "id": str(m.id),
        "sender_id": m.sender_id,
        "body": m.body,
        "image_storage_key": m.image_storage_key,
        "created_at": m.created_at.isoformat(),
    }


@router.get("")
async def list_chats(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    repo = ChatRepository(db)
    return await repo.list_chats_summary(user_id)


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
