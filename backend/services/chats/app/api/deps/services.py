from aiokafka import AIOKafkaProducer
from fastapi import Depends, Request

from api.deps.db import get_db
from services.chat_app_service import ChatAppService
from services.chat_room_registry import ChatRoomRegistry
from services.minio_storage import ChatImageStorage

_storage_singleton: ChatImageStorage | None = None


def get_kafka_producer(request: Request) -> AIOKafkaProducer:
    return request.app.state.kafka_producer


def get_chat_room_registry(request: Request) -> ChatRoomRegistry:
    return request.app.state.chat_room_registry


def get_image_storage() -> ChatImageStorage:
    global _storage_singleton
    if _storage_singleton is None:
        _storage_singleton = ChatImageStorage()
    return _storage_singleton


async def get_chat_service(
    session=Depends(get_db),
    producer: AIOKafkaProducer = Depends(get_kafka_producer),
    storage: ChatImageStorage = Depends(get_image_storage),
    rooms: ChatRoomRegistry = Depends(get_chat_room_registry),
) -> ChatAppService:
    return ChatAppService(session, producer, storage, rooms)
