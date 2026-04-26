import datetime

from pydantic import BaseModel


class TokenPayload(BaseModel):
    sub: int
    role: str
    exp: datetime.datetime


class AccessTokenPayload(TokenPayload):
    type: str = "access"


class RefreshTokenPayload(BaseModel):
    type: str = "refresh"
    