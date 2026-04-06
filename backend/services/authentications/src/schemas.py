from pydantic import BaseModel, EmailStr


class UsersPostDTO(BaseModel):
    username: str
    email: EmailStr


class UsersDTO(UsersPostDTO):
    id: int | None = None
    hashed_password: str
    disabled: bool = False


class UsersSendDTO(UsersPostDTO):
    id: int
    disabled: bool = False


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int
