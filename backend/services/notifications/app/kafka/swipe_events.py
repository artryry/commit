"""Handlers for swipe.created → notify the liked user (not on mutual match — match.created covers that)."""

import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from config import cfg
from repositories.notification_repository import NotificationRepository
from services.connection_manager import ConnectionManager
from services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)


async def handle_swipe_created_envelope(
    session: AsyncSession,
    connection_manager: ConnectionManager,
    envelope: dict[str, Any],
) -> None:
    event_type = envelope.get("event_type") or envelope.get("EventType")
    if event_type != cfg.KAFKA_TOPIC_SWIPE_CREATED:
        return

    payload = envelope.get("payload")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        logger.warning("swipe.created bad payload: %s", envelope)
        return

    if not payload.get("liked"):
        return

    if payload.get("mutual_match"):
        return

    target = payload.get("target_user_id")
    viewer = payload.get("viewer_id")
    if target is None or viewer is None:
        logger.warning("swipe.created missing ids: %s", payload)
        return

    msg = "Someone liked you!"
    repo = NotificationRepository(session)
    delivery = DeliveryService(repo, connection_manager, session)
    ws_payload: dict[str, Any] = {
        "type": "swipe.created",
        "message": msg,
        "viewer_id": int(viewer),
    }
    await delivery.enqueue_and_try_deliver(
        int(target),
        "swipe.created",
        msg,
        websocket_payload=ws_payload,
    )
