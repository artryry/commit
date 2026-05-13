import asyncio
import logging
from contextlib import asynccontextmanager

from aiokafka import AIOKafkaProducer
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import chats_router
from config import cfg
from db import Base, async_engine
from kafka.match_consumer import run_match_consumer
from services.chat_room_registry import ChatRoomRegistry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

import models  # noqa: F401


def _kafka_bootstrap_list() -> list[str]:
    return [s.strip() for s in cfg.KAFKA_BOOTSTRAP_SERVERS.split(",") if s.strip()]


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database tables ready")

    producer = AIOKafkaProducer(bootstrap_servers=_kafka_bootstrap_list())
    await producer.start()
    app.state.kafka_producer = producer
    app.state.chat_room_registry = ChatRoomRegistry()

    match_task = asyncio.create_task(run_match_consumer())
    try:
        yield
    finally:
        match_task.cancel()
        try:
            await match_task
        except asyncio.CancelledError:
            pass
        await producer.stop()
        logger.info("shutdown complete")


app = FastAPI(title=cfg.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chats_router, prefix="/api/v1/chats")


@app.get("/health")
async def health():
    return {"status": "ok"}
