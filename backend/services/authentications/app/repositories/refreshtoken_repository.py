from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import RefreshToken
from utils import Logger


class RefreshTokenRepository:
    def __init__(self, db_session: AsyncSession):
        self.__db_session = db_session


    async def create_refresh_token(self, refresh_token: RefreshToken) -> RefreshToken:
        try:
            self.__db_session.add(refresh_token)

            await self.__db_session.commit()
            await self.__db_session.refresh(refresh_token)
            Logger.info(f"Refresh token created with id {refresh_token.id}")

            return refresh_token
        except IntegrityError as ex:
            Logger.error(f"func {self.create_refresh_token.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise


    async def get_refresh_token_by_token(self, token: str) -> RefreshToken | None:
        try:
            query = select(RefreshToken).where(RefreshToken.token == token)
            result = await self.__db_session.execute(query)
            
            return result.scalar_one_or_none()
        except IntegrityError as ex:
            Logger.error(f"func {self.get_refresh_token_by_token.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise


    async def delete_refresh_token_by_id(self, token_id: int) -> bool:
        try:
            query = select(RefreshToken).where(RefreshToken.id == token_id)
            result = await self.__db_session.execute(query)
            refresh_token = result.scalar_one_or_none()

            if refresh_token is None:
                Logger.warning(f"Refresh token with id {token_id} not found for deletion")
                return False

            await self.__db_session.delete(refresh_token)
            await self.__db_session.commit()
            Logger.info(f"Refresh token with id {token_id} deleted")

            return True
        except IntegrityError as ex:
            Logger.error(f"func {self.delete_refresh_token_by_id.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise
            