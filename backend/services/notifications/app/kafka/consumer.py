"""Kafka consumer: match.created → persist + optional live push."""

import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer

from config import cfg
from db.session import AsyncSessionLocal
from kafka.chat_events import handle_chat_deleted_envelope, handle_chat_message_envelope
from kafka.match_events import handle_match_created_envelope
from kafka.swipe_events import handle_swipe_created_envelope
from services.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


def _bootstrap_servers() -> list[str]:
    return [s.strip() for s in cfg.KAFKA_BOOTSTRAP_SERVERS.split(",") if s.strip()]


async def _process_record(connection_manager: ConnectionManager, topic: str, raw: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as session:
        try:
            if topic == cfg.KAFKA_TOPIC_MATCH_CREATED:
                await handle_match_created_envelope(session, connection_manager, raw)
            elif topic == cfg.KAFKA_TOPIC_SWIPE_CREATED:
                await handle_swipe_created_envelope(session, connection_manager, raw)
            elif topic == cfg.KAFKA_TOPIC_CHAT_DELETED:
                await handle_chat_deleted_envelope(session, connection_manager, raw)
            elif topic == cfg.KAFKA_TOPIC_CHAT_MESSAGE:
                await handle_chat_message_envelope(session, connection_manager, raw)
            else:
                return
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("kafka notification handling failed")


async def run_kafka_consumer(connection_manager: ConnectionManager) -> None:
    consumer = AIOKafkaConsumer(
        cfg.KAFKA_TOPIC_MATCH_CREATED,
        cfg.KAFKA_TOPIC_SWIPE_CREATED,
        cfg.KAFKA_TOPIC_CHAT_DELETED,
        cfg.KAFKA_TOPIC_CHAT_MESSAGE,
        bootstrap_servers=_bootstrap_servers(),
        group_id=cfg.KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    await consumer.start()
    logger.info(
        "kafka consumer started topics=%s,%s,%s,%s",
        cfg.KAFKA_TOPIC_MATCH_CREATED,
        cfg.KAFKA_TOPIC_SWIPE_CREATED,
        cfg.KAFKA_TOPIC_CHAT_DELETED,
        cfg.KAFKA_TOPIC_CHAT_MESSAGE,
    )
    try:
        async for msg in consumer:
            raw = msg.value or {}
            et = raw.get("event_type") or raw.get("EventType")
            logger.info("kafka rx topic=%s event_type=%s", msg.topic, et)
            await _process_record(connection_manager, msg.topic, raw)
    except asyncio.CancelledError:
        logger.info("kafka consumer cancelled")
        raise
    finally:
        await consumer.stop()
