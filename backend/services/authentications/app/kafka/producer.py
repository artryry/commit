from aiokafka import AIOKafkaProducer

from kafka.events import Event


class KafkaProducerService:
    def __init__(self, producer: AIOKafkaProducer) -> None:
        self.producer = producer

    
    async def send_event(
        self,
        topic: str,
        event: Event,
    ):

        await self.producer.send_and_wait(
            topic,
            event.model_dump_json().encode(),
        )
        