from sqlalchemy.ext.asyncio import (
    create_async_engine, 
    async_sessionmaker, 
    AsyncSession,
)

from config import cfg

async_engine = create_async_engine(
    url=cfg.DATABASE_URL,
    echo=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
