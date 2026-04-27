from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer

from config import cfg
from api.routes import auth_router
from utils import Logger
from api.middleware import logging_middleware
from db import Base
from db import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Logger.info("Database tables created")
    
    # Start Kafka producer
    producer = AIOKafkaProducer(bootstrap_servers=cfg.KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    Logger.info("Kafka producer started")

    app.state.kafka_producer = producer

    yield

    await producer.stop()
    Logger.info("Kafka producer stopped")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(logging_middleware)
app.include_router(auth_router)
