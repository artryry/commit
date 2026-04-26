from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.repositories import UserRepository, RefreshTokenRepository
from .db import get_db


async def get_user_repository(db_session: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db_session)


async def get_refresh_token_repository(db_session: AsyncSession = Depends(get_db)) -> RefreshTokenRepository:
    return RefreshTokenRepository(db_session)
