import asyncio
import contextlib
import json
import logging

import redis.asyncio as redis
from aiokafka import AIOKafkaConsumer

from config.settings import settings
from db.redis_factory import create_redis
from db.session import async_session_maker
from services.profile_ingestion import ProfileIngestionService

logger = logging.getLogger(__name__)


def _bootstrap_servers() -> list[str]:
    return [s.strip() for s in settings.KAFKA_BOOTSTRAP_SERVERS.split(",") if s.strip()]


async def run_kafka_loop(redis_client: redis.Redis, ingestion: ProfileIngestionService) -> None:
    consumer = AIOKafkaConsumer(
        settings.KAFKA_TOPIC_PROFILE_UPDATED,
        settings.KAFKA_TOPIC_USER_DELETED,
        bootstrap_servers=_bootstrap_servers(),
        group_id=settings.KAFKA_GROUP_ID,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda b: json.loads(b.decode("utf-8")),
    )
    await consumer.start()
    logger.info("Kafka consumer running")
    try:
        async for msg in consumer:
            async with async_session_maker() as session:
                try:
                    await ingestion.handle_kafka_envelope(session, redis_client, msg.value)
                    await session.commit()
                except Exception:
                    await session.rollback()
                    logger.exception("kafka message failed")
    finally:
        await consumer.stop()


async def run_all(ingestion: ProfileIngestionService) -> None:
    from transport.grpc.handlers.recommendation_grpc import create_and_start_grpc_server

    redis_client = create_redis()
    grpc_server = await create_and_start_grpc_server(redis_client)
    kafka_task = asyncio.create_task(run_kafka_loop(redis_client, ingestion))
    try:
        await grpc_server.wait_for_termination()
    finally:
        kafka_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await kafka_task
