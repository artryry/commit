from pydantic import BaseModel
from uuid import UUID


class TokenPayload(BaseModel):
    sub: UUID
    role: str
    exp: int


class AccessTokenPayload(TokenPayload):
    type: str = "access"


class RefreshTokenPayload(BaseModel):
    type: str = "refresh"
    