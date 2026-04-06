from abc import ABC, abstractmethod

from schemas import UsersPostDTO, UsersSendDTO, UsersDTO


class IUsersDB(ABC):
    @abstractmethod
    async def create_user(self, new_user: UsersPostDTO, hashed_password: str) -> bool:
        ...

    @abstractmethod
    async def get_user_by_username(self, username: str) -> UsersDTO | None:
        ...

    @abstractmethod
    async def delete_user_by_id(self, user_id) -> bool:
        ...

    @abstractmethod
    async def update_user_by_id(self, user_id: int, new_user_data: UsersPostDTO) -> bool:
        ...

    @abstractmethod
    async def update_password_by_user_id(self, user_id: int, new_hashed_password: str) -> bool:
        ...


class IUsers(ABC):
    @abstractmethod
    async def create_user(self, new_user: UsersPostDTO, password: str) -> bool:
        ...

    @abstractmethod
    async def update_user(self, user_id: int, new_user_date: UsersPostDTO) -> bool:
        ...

    @abstractmethod
    async def update_password(self, user_id: int, new_hashed_password: str) -> bool:
        ...

    @abstractmethod
    async def verify_user(self, username: str, password: str) -> UsersDTO | None:
        ...

    @abstractmethod
    async def delete_user(self, user_id) -> bool:
        ...


class ISynchronizer(ABC):
    @abstractmethod
    async def send_user(self, user: UsersSendDTO, operation: str) -> bool:
        ...
