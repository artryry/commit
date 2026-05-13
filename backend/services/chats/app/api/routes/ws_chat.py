"""Handle incoming JSON frames on the chat-room WebSocket."""

from __future__ import annotations

import base64
import binascii
import json
import logging

from fastapi import HTTPException, WebSocket

from db.session import AsyncSessionLocal
from services.chat_app_service import ChatAppService
from services.chat_room_registry import ChatRoomRegistry
from services.minio_storage import ChatImageStorage

logger = logging.getLogger(__name__)


async def handle_chat_ws_text(
    raw: str,
    *,
    user_id: int,
    peer_user_id: int,
    websocket: WebSocket,
    registry: ChatRoomRegistry,
    producer,
    storage: ChatImageStorage,
) -> None:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        await websocket.send_json({"type": "error", "detail": "invalid json"})
        return
    if not isinstance(data, dict):
        await websocket.send_json({"type": "error", "detail": "invalid body"})
        return

    msg_type = data.get("type")
    async with AsyncSessionLocal() as session:
        svc = ChatAppService(session, producer, storage, registry)
        try:
            if msg_type == "text":
                body = data.get("body")
                if body is None or not str(body).strip():
                    await websocket.send_json({"type": "error", "detail": "body required"})
                    return
                await svc.send_chat_message(
                    user_id,
                    peer_user_id,
                    body=str(body).strip(),
                    image_bytes=None,
                    image_content_type=None,
                )
            elif msg_type == "image":
                caption = data.get("body")
                cap = str(caption).strip() if caption is not None else None
                cap = cap or None
                b64 = data.get("image_base64")
                if not b64 or not isinstance(b64, str):
                    await websocket.send_json({"type": "error", "detail": "image_base64 required"})
                    return
                b64 = "".join(b64.split())
                try:
                    img_bytes = base64.b64decode(b64, validate=False)
                except (ValueError, binascii.Error):
                    await websocket.send_json({"type": "error", "detail": "invalid base64"})
                    return
                raw_ct = data.get("content_type")
                ct = str(raw_ct).strip() if raw_ct else None
                ct = ct or None
                await svc.send_chat_message(
                    user_id,
                    peer_user_id,
                    body=cap,
                    image_bytes=img_bytes,
                    image_content_type=ct,
                )
            else:
                await websocket.send_json({"type": "error", "detail": "unknown type (use text or image)"})
                return
        except HTTPException as e:
            detail = e.detail
            if isinstance(detail, str):
                await websocket.send_json({"type": "error", "detail": detail})
            else:
                await websocket.send_json({"type": "error", "detail": "request failed"})
            return
        except Exception:
            logger.exception("chat ws send failed")
            await websocket.send_json({"type": "error", "detail": "internal error"})
            return
