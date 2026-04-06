from typing import Callable

from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from logger import Logger
from .ORM_models import UsersOrm
from schemas import UsersDTO, UsersPostDTO
from interfaces import IUsersDB


class UsersDB(IUsersDB):
    def __init__(self, a_session_factory: Callable[[], AsyncSession]):
        self.__a_session_factory = a_session_factory

    async def create_user(self, new_user: UsersPostDTO, hashed_password: str) -> bool:
        new_user_dto = UsersDTO(**new_user.model_dump(), hashed_password=hashed_password)
        async with self.__a_session_factory() as session:
            try:
                if not await self.__check_duplication_user_data(new_user):
                    return False
                new_user_orm = UsersOrm(**new_user_dto.model_dump())
                session.add(new_user_orm)
                await session.commit()
            except IntegrityError as ex:
                Logger.error(f"IntegrityError: {ex}")
                await session.rollback()
                return False
        return True

    async def get_user_by_username(self, username: str) -> UsersDTO | None:
        query = (
            select(UsersOrm)
            .select_from(UsersOrm)
            .filter_by(username=username)
        )
        user = None
        async with self.__a_session_factory() as session:
            try:
                exec_result = await session.execute(query)
                result = exec_result.scalars().first()
                if result is None or result.disabled:
                    return None
                user = UsersDTO.model_validate(result, from_attributes=True)
            except IntegrityError as ex:
                Logger.error(f"IntegrityError: {ex}")
                await session.rollback()
        return user
    
    async def update_user_by_id(self, user_id: int, new_user_data: UsersPostDTO) -> bool:
        async with self.__a_session_factory() as session:
            try:
                if not await self.__check_duplication_user_data(new_user_data, user_id=user_id):
                    return False
                user_orm = await session.get(UsersOrm, user_id)
                if user_orm is None or user_orm.disabled:
                    return False
                for key, item in new_user_data.model_dump().items():
                    setattr(user_orm, key, item)
                await session.commit()
            except IntegrityError as ex:
                Logger.error(f"IntegrityError: {ex}")
                await session.rollback()
                return False
        return True

    async def delete_user_by_id(self, user_id) -> bool:
        async with self.__a_session_factory() as session:
            try:
                user_orm = await session.get(UsersOrm, user_id)
                if user_orm is None or user_orm.disabled:
                    return False
                user_orm.disabled = True
                await session.commit()
            except IntegrityError as ex:
                Logger.error(f"IntegrityError: {ex}")
                await session.rollback()
                return False
        return True

    async def __check_duplication_user_data(self, new_user_data: UsersPostDTO, user_id: int | None = None) -> bool:
        query = (
                    select(UsersOrm)
                    .select_from(UsersOrm)
                    .filter(or_(
                        UsersOrm.username == new_user_data.username,
                        UsersOrm.email == new_user_data.email,
                    ))
                )
                
        async with self.__a_session_factory() as session:
            try:
                exec_result = await session.execute(query)
                results = exec_result.scalars().fetchall()
                if not results:
                    return True
                if user_id is None:
                    if results:
                        return False
                for record in results:
                    if record.id == user_id:
                        continue
                    if new_user_data.username == record.username:
                        return False
                    if new_user_data.email == record.email:
                        return False
            except IntegrityError as ex:
                Logger.error(f"IntegrityError: {ex}")
                await session.rollback()
        return True

    async def update_password_by_user_id(self, user_id: int, new_hashed_password: str) -> bool:
        async with self.__a_session_factory() as session:
            try:
                user_orm = await session.get(UsersOrm, user_id)
                if user_orm is None or user_orm.disabled:
                    return False
                user_orm.hashed_password = new_hashed_password
                await session.commit()
            except IntegrityError as ex:
                Logger.error(f"IntegrityError: {ex}")
                await session.rollback()
                return False
        return True
