from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from aiokafka import AIOKafkaProducer

from config import cfg
from api.routes import auth_router
from utils import Logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = AIOKafkaProducer(bootstrap_servers=cfg.KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    Logger.info("Kafka producer started")

    app.state.kafka_producer = producer

    yield

    await producer.stop()
    Logger.info("Kafka producer stopped")


app = FastAPI(lifespan=lifespan, root_path="/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_router)
