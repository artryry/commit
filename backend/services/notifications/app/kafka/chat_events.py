"""Handlers for chat-related domain events."""

import json
import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from config import cfg
from repositories.notification_repository import NotificationRepository
from services.connection_manager import ConnectionManager
from services.delivery_service import DeliveryService

logger = logging.getLogger(__name__)


async def handle_chat_deleted_envelope(
    session: AsyncSession,
    connection_manager: ConnectionManager,
    envelope: dict[str, Any],
) -> None:
    event_type = envelope.get("event_type") or envelope.get("EventType")
    if event_type != cfg.KAFKA_TOPIC_CHAT_DELETED:
        return

    payload = envelope.get("payload")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        logger.warning("chat.deleted bad payload: %s", envelope)
        return

    first = payload.get("first_user_id")
    sec = payload.get("sec_user_id")
    if first is None or sec is None:
        logger.warning("chat.deleted missing ids: %s", payload)
        return

    text = "The chat was deleted."
    repo = NotificationRepository(session)
    delivery = DeliveryService(repo, connection_manager, session)

    for uid in (int(first), int(sec)):
        await delivery.enqueue_and_try_deliver(uid, "chat.deleted", text)


async def handle_chat_message_envelope(
    session: AsyncSession,
    connection_manager: ConnectionManager,
    envelope: dict[str, Any],
) -> None:
    event_type = envelope.get("event_type") or envelope.get("EventType")
    if event_type != cfg.KAFKA_TOPIC_CHAT_MESSAGE:
        return

    payload = envelope.get("payload")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        logger.warning("chat.message bad payload: %s", envelope)
        return

    recipient = payload.get("recipient_id")
    preview = payload.get("preview")
    if recipient is None:
        logger.warning("chat.message missing recipient_id: %s", payload)
        return

    line = (preview or "New message").strip() or "New message"
    repo = NotificationRepository(session)
    delivery = DeliveryService(repo, connection_manager, session)
    await delivery.enqueue_and_try_deliver(int(recipient), "chat.message", line)
