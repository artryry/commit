from app.kafka import KafkaProducerService
from fastapi import Request, Depends
from aiokafka import AIOKafkaProducer


async def get_kafka_producer(request: Request) -> KafkaProducerService:
    return request.app.state.kafka_producer


async def get_kafka_producer_service(kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer)):
    return KafkaProducerService(kafka_producer)
