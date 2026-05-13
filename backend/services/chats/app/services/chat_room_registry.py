"""In-memory chat rooms: WebSocket lists per (viewer, peer), broadcast + Kafka skip.

When recipient has an active socket for (recipient, sender), ``chat.message`` Kafka is **not**
published (notifications are skipped — user already receives the payload over this chat WS).

Multi-process deployments need a shared store (e.g. Redis) instead of this registry.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ChatRoomRegistry:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._sockets: dict[tuple[int, int], list[WebSocket]] = {}

    async def attach(self, viewer_id: int, peer_user_id: int, ws: WebSocket) -> None:
        async with self._lock:
            self._sockets.setdefault((viewer_id, peer_user_id), []).append(ws)

    async def detach(self, viewer_id: int, peer_user_id: int, ws: WebSocket) -> None:
        async with self._lock:
            lst = self._sockets.get((viewer_id, peer_user_id))
            if not lst:
                return
            try:
                lst.remove(ws)
            except ValueError:
                return
            if not lst:
                self._sockets.pop((viewer_id, peer_user_id), None)

    async def recipient_in_room(self, recipient_id: int, sender_id: int) -> bool:
        async with self._lock:
            return bool(self._sockets.get((recipient_id, sender_id)))

    async def broadcast(self, viewer_id: int, peer_user_id: int, payload: dict[str, Any]) -> None:
        async with self._lock:
            sockets = list(self._sockets.get((viewer_id, peer_user_id)) or [])
        for ws in sockets:
            try:
                await ws.send_json(payload)
            except Exception:
                logger.debug("chat room ws send failed", exc_info=True)
