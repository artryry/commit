import datetime
import secrets

import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from fastapi import HTTPException

from repositories import RefreshTokenRepository
from models import RefreshToken, User
from schemas import RefreshTokenPayload, AccessTokenPayload
from utils import Logger
from config import cfg


class TokenService:
    @staticmethod
    def generate_access_token(user: User) -> str:
        token_payload = AccessTokenPayload(
            sub=user.id,
            role=user.role,
            exp=(
                datetime.datetime.now(
                datetime.timezone.utc) + 
                datetime.timedelta(minutes=cfg.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
            )
        )

        accesses_token = jwt.encode(
            token_payload.model_dump(), 
            cfg.JWT_PRIVATE_KEY,
            algorithm=cfg.JWT_ALGORITHM,
        )

        return accesses_token

    @staticmethod
    def verify_access_token(token: str) -> AccessTokenPayload:
        try:
            accesses_token_payload = AccessTokenPayload.model_validate(
                jwt.decode(
                    token,
                    cfg.JWT_PUBLIC_KEY,
                    algorithms=[cfg.JWT_ALGORITHM],
                )
            )
        except ExpiredSignatureError:
            Logger.info(f"Access token expired")
            raise HTTPException(
                status_code=401,
                detail="Access token expired"
            )
        except InvalidTokenError:
            Logger.info(f"Invalid access token")
            raise HTTPException(
                status_code=401,
                detail="Invalid access token"
            )
        
        Logger.info(f"Access token verified for user_id {accesses_token_payload.sub}")

        return accesses_token_payload

    @staticmethod
    async def generate_refresh_token(
        refreshtoken_repository: RefreshTokenRepository,
        user_id: int
    ) -> str:
        token = secrets.token_urlsafe(32)

        refresh_token = RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=(
                datetime.datetime.now(datetime.timezone.utc) + 
                datetime.timedelta(days=cfg.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
            )
        )

        await refreshtoken_repository.create_refresh_token(refresh_token)

        return token

    @staticmethod
    async def verify_refresh_token(
        refreshtoken_repository: RefreshTokenRepository,
        token: str
    ) -> RefreshToken:
        refresh_token = await refreshtoken_repository.get_refresh_token_by_token(token)

        if not refresh_token:
            Logger.info(f"Refresh token not found")
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )

        if refresh_token.expires_at < datetime.datetime.now(datetime.timezone.utc):
            Logger.info(f"Refresh token expired")
            await refreshtoken_repository.delete_refresh_token_by_id(refresh_token.id)
            Logger.info(f"Refresh token with id {refresh_token.id} deleted due to expiration")
            raise HTTPException(
                status_code=401,
                detail="Refresh token expired"
            )

        return refresh_token
    

    @staticmethod
    async def delete_refresh_token_by_id(
        refreshtoken_repository: RefreshTokenRepository,
        refresh_token_id: int
    ) -> None:
        await refreshtoken_repository.delete_refresh_token_by_id(refresh_token_id)
        Logger.info(f"Refresh token with id {refresh_token_id} deleted")
    