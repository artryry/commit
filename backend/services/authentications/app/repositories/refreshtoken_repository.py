from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import RefreshToken
from utils import Logger


class RefreshTokenRepository:
    def __init__(self, db_session: Callable[[], AsyncSession]):
        self.__db_session = db_session


    async def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken | None:
        async with self.__db_session() as session:
            try:
                session.add(refresh_token)

                await session.commit()
                await session.refresh(refresh_token)
                Logger.info(f"Refresh token created with id {refresh_token.id}")

                return refresh_token
            except IntegrityError as ex:
                Logger.error(f"func {self.create_refresh_token.__name__}: IntegrityError: {ex}")
                await session.rollback()

                return None


    async def get_refresh_token_by_token(self, token: str) -> RefreshToken | None:
        async with self.__db_session() as session:
            try:
                query = select(RefreshToken).where(RefreshToken.token == token)
                result = await session.execute(query)
                
                return result.scalar_one_or_none()
            except IntegrityError as ex:
                Logger.error(f"func {self.get_refresh_token_by_token.__name__}: IntegrityError: {ex}")
                await session.rollback()

                return None
            
            
    async def delete_refresh_token_by_id(self, token_id: int) -> bool:
        async with self.__db_session() as session:
            try:
                query = select(RefreshToken).where(RefreshToken.id == token_id)
                result = await session.execute(query)
                refresh_token = result.scalar_one_or_none()

                if refresh_token is None:
                    Logger.warning(f"Refresh token with id {token_id} not found for deletion")
                    return False

                await session.delete(refresh_token)
                await session.commit()
                Logger.info(f"Refresh token with id {token_id} deleted")

                return True
            except IntegrityError as ex:
                Logger.error(f"func {self.delete_refresh_token_by_id.__name__}: IntegrityError: {ex}")
                await session.rollback()

                return False
            