"""Kafka consumer: match.created → persist + optional live push."""

import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer

from config import cfg
from db.session import AsyncSessionLocal
from kafka.match_events import handle_match_created_envelope
from services.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


def _bootstrap_servers() -> list[str]:
    return [s.strip() for s in cfg.KAFKA_BOOTSTRAP_SERVERS.split(",") if s.strip()]


async def _process_envelope(connection_manager: ConnectionManager, raw: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as session:
        try:
            await handle_match_created_envelope(session, connection_manager, raw)
            await session.commit()
        except Exception:
            await session.rollback()
            logger.exception("kafka notification handling failed")


async def run_kafka_consumer(connection_manager: ConnectionManager) -> None:
    consumer = AIOKafkaConsumer(
        cfg.KAFKA_TOPIC_MATCH_CREATED,
        bootstrap_servers=_bootstrap_servers(),
        group_id=cfg.KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    await consumer.start()
    logger.info("kafka consumer started topic=%s", cfg.KAFKA_TOPIC_MATCH_CREATED)
    try:
        async for msg in consumer:
            await _process_envelope(connection_manager, msg.value)
    except asyncio.CancelledError:
        logger.info("kafka consumer cancelled")
        raise
    finally:
        await consumer.stop()
