"""Handlers for domain events that produce notifications."""

import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from config import cfg
from repositories.notification_repository import NotificationRepository
from services.connection_manager import ConnectionManager
from services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)


async def handle_match_created_envelope(
    session: AsyncSession,
    connection_manager: ConnectionManager,
    envelope: dict[str, Any],
) -> None:
    event_type = envelope.get("event_type") or envelope.get("EventType")
    if event_type != cfg.KAFKA_TOPIC_MATCH_CREATED:
        return

    payload = envelope.get("payload")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        logger.warning("match.created bad payload: %s", envelope)
        return

    first = payload.get("first_user_id")
    sec = payload.get("sec_user_id")
    if first is None or sec is None:
        logger.warning("match.created missing ids: %s", payload)
        return

    msg = "You have a new match!"
    repo = NotificationRepository(session)
    delivery = DeliveryService(repo, connection_manager, session)

    for uid in (int(first), int(sec)):
        await delivery.enqueue_and_try_deliver(uid, "match.created", msg)
