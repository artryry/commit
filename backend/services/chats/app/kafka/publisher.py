import json
import logging

from aiokafka import AIOKafkaProducer

from config import cfg
from kafka.envelope import build_envelope

logger = logging.getLogger(__name__)


async def publish_chat_deleted(
    producer: AIOKafkaProducer,
    *,
    chat_id: str,
    user_low: int,
    user_high: int,
) -> None:
    payload = {
        "chat_id": chat_id,
        "first_user_id": user_low,
        "sec_user_id": user_high,
    }
    env = build_envelope(cfg.KAFKA_TOPIC_CHAT_DELETED, payload)
    data = json.dumps(env).encode("utf-8")
    await producer.send_and_wait(cfg.KAFKA_TOPIC_CHAT_DELETED, data)
    logger.info("published chat.deleted chat_id=%s", chat_id)


async def publish_chat_message(
    producer: AIOKafkaProducer,
    *,
    chat_id: str,
    message_id: str,
    sender_id: int,
    recipient_id: int,
    preview: str,
) -> None:
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "sender_id": sender_id,
        "recipient_id": recipient_id,
        "preview": preview,
    }
    env = build_envelope(cfg.KAFKA_TOPIC_CHAT_MESSAGE, payload)
    data = json.dumps(env).encode("utf-8")
    await producer.send_and_wait(cfg.KAFKA_TOPIC_CHAT_MESSAGE, data)
    logger.info(
        "published chat.message chat_id=%s message_id=%s recipient_id=%s",
        chat_id,
        message_id,
        recipient_id,
    )
