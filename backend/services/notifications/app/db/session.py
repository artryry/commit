from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config import cfg

async_engine = create_async_engine(cfg.DATABASE_URL, echo=cfg.DB_ECHO, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
