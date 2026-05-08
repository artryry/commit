from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.settings import settings
from db.base import Base


def create_engine_and_sessionmaker():
    engine = create_async_engine(
        settings.async_database_url,
        echo=settings.DEBUG,
        pool_pre_ping=True,
    )
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, factory


engine, async_session_maker = create_engine_and_sessionmaker()


async def init_db() -> None:
    import db.models  # noqa: F401 — register models with metadata

    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
