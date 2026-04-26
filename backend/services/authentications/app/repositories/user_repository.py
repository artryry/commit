from typing import Callable

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import User
from services.authentications.app.db import session
from utils import Logger


class UserRepository:
    def __init__(self, db_session: AsyncSession):
        self.__db_session = db_session


    async def get_user_by_id(self, user_id: int) -> User | None:
        try:
            query = select(User).where(User.id == user_id)
            result = await self.__db_session.execute(query)
            
            return result.scalar_one_or_none()
        except IntegrityError as ex:
            Logger.error(f"func {self.get_user_by_id.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise

    
    async def get_user_by_email(self, email: str) -> User | None:
        try:
            query = select(User).where(User.email == email)
            result = await self.__db_session.execute(query)
            
            return result.scalar_one_or_none()
        except IntegrityError as ex:
            Logger.error(f"func {self.get_user_by_email.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise


    async def create_user(self, new_user: User) -> User:
        try:
            self.__db_session.add(new_user)

            await self.__db_session.commit()
            await self.__db_session.refresh(new_user)
            Logger.info(f"User created with id {new_user.id}")

            return new_user
        except IntegrityError as ex:
            Logger.error(f"func {self.create_user.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise


    async def update_user(self, user_id: int, user_data: User) -> User | None:
        try:
            query = select(User).where(User.id == user_id)
            result = await self.__db_session.execute(query)
            user = result.scalar_one_or_none()

            if user is None:
                Logger.warning(f"User with id {user_id} not found for update")
                return None

            for column in user_data.__table__.columns:
                key = column.name
                value = getattr(user_data, key)
                setattr(user, key, value)

            await self.__db_session.commit()
            await self.__db_session.refresh(user)
            Logger.info(f"User with id {user_id} updated")

            return user
        except IntegrityError as ex:
            Logger.error(f"func {self.update_user.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise


    async def delete_user(self, user_id: int) -> bool:
        try:
            query = select(User).where(User.id == user_id)
            result = await self.__db_session.execute(query)
            user = result.scalar_one_or_none()

            if user is None:
                Logger.warning(f"User with id {user_id} not found for deletion")
                return False

            await self.__db_session.delete(user)
            await self.__db_session.commit()
            Logger.info(f"User with id {user_id} deleted")

            return True
        except IntegrityError as ex:
            Logger.error(f"func {self.delete_user.__name__}: IntegrityError: {ex}")
            await self.__db_session.rollback()

            raise
            