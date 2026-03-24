import pytest_asyncio
import pytest
from aiokafka import AIOKafkaConsumer, TopicPartition
import json
import asyncio

from database.models import UsersDB
from database.database import create_tables, delete_tables
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from schemas import UsersDTO, UsersPostDTO, UsersSendDTO
from controllers import Users
from synchronizer import Synchronizer
from config import settings
from logger import Logger


# Base fake user
fake_user = UsersPostDTO(**{
    "username": "test_user_1",
    "email": "testuser1@gmail.com",
})
fake_user_pwd = "test_user_1"
fake_user_full = UsersDTO(id=1, **fake_user.model_dump(), hashed_password=fake_user_pwd)
fake_user_token = ""

# New fake user data for update
new_fake_user = UsersPostDTO(**{
    "username": "new_test_user_1",
    "email": "newtestuser1@gmail.com",
})
new_fake_user_pwd = "new_test_user_1"
new_fake_user_full_new_pwd = UsersDTO(id=1, **new_fake_user.model_dump(), hashed_password=new_fake_user_pwd)
new_fake_user_full = UsersDTO(id=1, **new_fake_user.model_dump(), hashed_password=fake_user_pwd)
new_fake_user_token = ""


@pytest_asyncio.fixture(scope="module", autouse=True)
async def set_db_tables():
    await create_tables()
    yield
    await delete_tables()


@pytest_asyncio.fixture
async def users_db() -> UsersDB:
    async_engine = create_async_engine(
        url=settings.DATABASE_URL,
        echo=False,
        pool_size=5,
        max_overflow=10,
    )

    async_session_factory = async_sessionmaker(async_engine)

    return UsersDB(async_session_factory)


async def get_user_from_kafka() -> UsersSendDTO | None:
    topic = settings.KAFKA_USERS_TOPIC
    consumer = AIOKafkaConsumer(
        settings.KAFKA_USERS_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="test_controllers_group",
    )

    await consumer.start()
    try:
        partitions = consumer.partitions_for_topic(topic)
        if not partitions:
            return None

        tp = TopicPartition(topic, 0)
        end_offsets = await consumer.end_offsets([tp])
        last_offset = end_offsets[tp] - 1
        if last_offset < 0:
            return None
        consumer.seek(tp, last_offset)
        msg = await consumer.getone()
        if msg.value is not None:
            user_data = json.loads(msg.value.decode())
            return UsersSendDTO(**user_data)
    finally:
        await consumer.stop()
        

@pytest_asyncio.fixture
async def users(users_db: UsersDB) -> Users:
    synchronizer = Synchronizer()
    return Users(users_db, synchronizer)


async def test_create_user(users: Users):
    assert await users.create_user(fake_user, fake_user_pwd)
    await asyncio.sleep(2)
    assert await get_user_from_kafka() == UsersSendDTO(**fake_user_full.model_dump())
    assert await users.create_user(fake_user, fake_user_pwd) is False


async def test_update_user(users: Users):
    assert await users.update_user(1, new_fake_user)
    await asyncio.sleep(2)
    assert await get_user_from_kafka() == UsersSendDTO(**new_fake_user_full.model_dump())
    assert await users.update_user(1, new_fake_user) is False


async def test_update_password(users: Users):
    assert await users.update_password(1,  new_fake_user_pwd)


async def test_delete_user(users: Users):
    assert await users.delete_user(1)
    assert await users._get_user(new_fake_user.username) == UsersDTO(id=1, disabled=True, **new_fake_user.model_dump(), hashed_password=new_fake_user_pwd)


