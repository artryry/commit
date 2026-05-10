import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import notifications_router
from config import cfg
from db import Base, async_engine
from kafka.consumer import run_kafka_consumer
from services.connection_manager import ConnectionManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register models on Base.metadata
import models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database tables ready")

    cm = ConnectionManager()
    app.state.connection_manager = cm

    kafka_task = asyncio.create_task(run_kafka_consumer(cm))
    try:
        yield
    finally:
        kafka_task.cancel()
        try:
            await kafka_task
        except asyncio.CancelledError:
            pass
        logger.info("shutdown complete")


app = FastAPI(title=cfg.APP_NAME, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(notifications_router, prefix="/api/v1/notifications")


@app.get("/health")
async def health():
    return {"status": "ok"}
