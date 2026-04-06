from passlib.context import CryptContext
from passlib.exc import InvalidHashError, UnknownHashError

from interfaces import IUsers, IUsersDB, ISynchronizer
from schemas import UsersDTO, UsersPostDTO, UsersSendDTO
from logger import Logger


class Users(IUsers):
    def __init__(self, users_db: IUsersDB, synchronizer: ISynchronizer):
        self.users_db = users_db
        self.synchronizer = synchronizer
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def create_user(self, new_user: UsersPostDTO, password: str) -> bool:
        if not await self.users_db.create_user(new_user, self._hash_password(password)):
            return False
        Logger.info(f"User <username: {new_user.username} created>")
        # Sending new user to other services
        if (user := await self._get_user(new_user.username)) is None:
            return False
        await self._synchronize_user(user, "create")
        return True
    
    async def update_user(self, user_id: int, new_user_date: UsersPostDTO) -> bool:
        if not await self.users_db.update_user_by_id(user_id, new_user_date):
            return False
        Logger.info(f"User <id: {user_id}> updated")
        # Sending updated user to other services
        if (user := await self._get_user(new_user_date.username)) is None:
            return False
        await self._synchronize_user(user, "update")
        return True

    async def update_password(self, user_id: int, new_hashed_password: str) -> bool:
        if not await self.users_db.update_password_by_user_id(user_id, self._hash_password(new_hashed_password)):
            return False
        Logger.info(f"User's <id: {user_id}> password updated")
        return True
    
    async def verify_user(self, username: str, password: str) -> UsersDTO | None:
        if (user := await self._get_user(username)) is None:
            return None
        Logger.info(f"User <username: {username}> verified")
        try:
            if not self.pwd_context.verify(password, user.hashed_password):
                return None
        except (InvalidHashError, UnknownHashError) as ex:
            Logger.error(f"HashError: {ex}")
        return user
    
    async def delete_user(self, user_id) -> bool:
        if not await self.users_db.delete_user_by_id(user_id):
            return False
        Logger.info(f"User <id: {user_id}> deleted")
        user = UsersDTO(id=user_id, username="", email="deleteuser@del.ru", hashed_password="")
        await self._synchronize_user(user, "update")
        return True
    
    async def _get_user(self, username: str) -> UsersDTO | None:
        return await self.users_db.get_user_by_username(username)

    async def _synchronize_user(self, user: UsersDTO, operation: str) -> bool:
        user_for_sending = UsersSendDTO(**user.model_dump())
        if not await self.synchronizer.send_user(user_for_sending, operation):
            Logger.warning(f"User <id: {user.id}> was not sent to other services")
            return False
        Logger.info(f"User <id: {user.id}> sent to other services ")
        return True
        
    def _hash_password(self, password: str) -> str:
        return self.pwd_context.hash(password)
