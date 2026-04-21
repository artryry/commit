import pytest_asyncio
import pytest
import os

from database.models import UsersDB
from database.database import create_tables, delete_tables
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from schemas import UsersDTO, UsersPostDTO
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


async def test_create_user(users_db):
    assert await users_db.create_user(fake_user, fake_user_pwd)
    assert await users_db.get_user_by_username(fake_user.username) == fake_user_full
    assert await users_db.create_user(fake_user, fake_user_pwd) is False


@pytest.mark.asyncio
async def test_get_user(users_db: UsersDB):
    assert await users_db.get_user_by_username(fake_user.username) == fake_user_full
    assert await users_db.get_user_by_username("fake_name") is None


@pytest.mark.asyncio
async def test_update_user(users_db: UsersDB):
    assert await users_db.update_user_by_id(1, new_fake_user)
    assert await users_db.get_user_by_username(new_fake_user.username) == new_fake_user_full
    assert await users_db.update_user_by_id(1, new_fake_user) is False


@pytest.mark.asyncio
async def test_update_password(users_db: UsersDB):
    assert await users_db.update_password_by_user_id(1, new_fake_user_pwd)
    assert await users_db.get_user_by_username(new_fake_user.username) == new_fake_user_full_new_pwd


@pytest.mark.asyncio
async def test_delete_user(users_db: UsersDB):
    assert await users_db.delete_user_by_id(1)
    user = await users_db.get_user_by_username(new_fake_user.username)
    if user is not None:
        assert user.disabled
    else:
        assert 0


