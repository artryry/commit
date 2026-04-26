from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

from schemas import AccessTokenPayload
from app.services import TokenService
from app.models import UserRole
from app.repositories import UserRepository, RefreshTokenRepository
from app.services import AuthService
from .services import get_user_repository, get_refresh_token_repository


security = HTTPBearer()


async def get_access_token_payload(
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> AccessTokenPayload:

    token = credentials.credentials

    return TokenService.verify_access_token(token)


async def get_auth_service(
    user_repository: UserRepository = Depends(get_user_repository),
    refresh_token_repository: RefreshTokenRepository = Depends(get_refresh_token_repository),
) -> AuthService:
    return AuthService(
        user_repository=user_repository,
        refresh_token_repository=refresh_token_repository,
    )


def require_role(
    roles: list[UserRole],
):

    async def dependency(
        payload: AccessTokenPayload = Depends(
            get_access_token_payload
        ),
    ):

        if payload.role not in roles:
            raise HTTPException(
                status_code=403,
                detail="Forbidden",
            )

    return dependency
