from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings
from logger import Logger
from .ORM_models import Base

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(async_engine)


async def delete_tables():
    async with async_engine.begin() as conn:
        Logger.info("Start deleting tables")
        await conn.run_sync(Base.metadata.drop_all)
        Logger.info("Tables deleted")


async def create_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        Logger.info("Tables created")
