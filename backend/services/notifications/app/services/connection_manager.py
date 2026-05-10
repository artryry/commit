"""In-memory registry of active WebSocket connections per user (tabs)."""

import logging
from typing import Dict, List

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self) -> None:
        self._by_user: Dict[int, List[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        self._by_user.setdefault(user_id, []).append(websocket)

    def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self._by_user.get(user_id)
        if not sockets:
            return
        try:
            sockets.remove(websocket)
        except ValueError:
            pass
        if not sockets:
            del self._by_user[user_id]

    def is_online(self, user_id: int) -> bool:
        return bool(self._by_user.get(user_id))

    async def send_json_to_user(self, user_id: int, data: dict) -> bool:
        sockets = list(self._by_user.get(user_id, []))
        if not sockets:
            return False
        dead: List[WebSocket] = []
        any_ok = False
        for ws in sockets:
            try:
                await ws.send_json(data)
                any_ok = True
            except Exception:
                logger.debug("send failed for user %s", user_id, exc_info=True)
                dead.append(ws)
        for ws in dead:
            self.disconnect(user_id, ws)
        return any_ok
