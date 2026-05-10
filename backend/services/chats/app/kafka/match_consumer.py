import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer

from config import cfg
from db.session import AsyncSessionLocal
from repositories.chat_repository import ChatRepository

logger = logging.getLogger(__name__)


def _bootstrap_servers() -> list[str]:
    return [s.strip() for s in cfg.KAFKA_BOOTSTRAP_SERVERS.split(",") if s.strip()]


async def handle_match_envelope(raw: dict[str, Any]) -> None:
    event_type = raw.get("event_type") or raw.get("EventType")
    if event_type != cfg.KAFKA_TOPIC_MATCH_CREATED:
        return

    payload = raw.get("payload")
    if isinstance(payload, str):
        payload = json.loads(payload)
    if not isinstance(payload, dict):
        logger.warning("match.created invalid payload: %s", raw)
        return

    mid = payload.get("match_id")
    first = payload.get("first_user_id")
    sec = payload.get("sec_user_id")
    if mid is None or first is None or sec is None:
        logger.warning("match.created missing fields: %s", payload)
        return

    async with AsyncSessionLocal() as session:
        try:
            repo = ChatRepository(session)
            await repo.ensure_chat_for_match(int(mid), int(first), int(sec))
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("failed to create chat from match.created")


async def run_match_consumer() -> None:
    consumer = AIOKafkaConsumer(
        cfg.KAFKA_TOPIC_MATCH_CREATED,
        bootstrap_servers=_bootstrap_servers(),
        group_id=cfg.KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    await consumer.start()
    logger.info("chats match.created consumer started")
    try:
        async for msg in consumer:
            await handle_match_envelope(msg.value)
    except asyncio.CancelledError:
        logger.info("match consumer cancelled")
        raise
    finally:
        await consumer.stop()
