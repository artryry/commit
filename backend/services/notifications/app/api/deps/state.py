from fastapi import WebSocket

from services.connection_manager import ConnectionManager


def get_connection_manager(websocket: WebSocket) -> ConnectionManager:
    return websocket.app.state.connection_manager
