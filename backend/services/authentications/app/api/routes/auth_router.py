from fastapi.routing import APIRouter
from fastapi import Depends, status

from app.schemas import (
    RegisterRequest,
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    DeleteAccountRequest,
)
from app.api.deps import get_auth_service
from app.services import AuthService


auth_router = APIRouter(
    prefix="/api/v1/auth",
    tags=["auth"],
)


@auth_router.get(
    "/health",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    )
async def health_check():
    return MessageResponse(message="Authentication service is healthy")


@auth_router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.register(request)


@auth_router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.login(request)


@auth_router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(request: LogoutRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.logout(request)


@auth_router.post(
    "/token",
    response_model=RefreshTokenResponse,
    status_code=status.HTTP_200_OK,
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.refresh_token(request)


@auth_router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def delete_account(
    request: DeleteAccountRequest,
    auth_service: AuthService = Depends(get_auth_service),
):
    return await auth_service.delete_account(request)
