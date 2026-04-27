from uuid import uuid4
from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from schemas import (
    RegisterRequest,
    LoginRequest,
    LogoutRequest,
    AuthResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    DeleteAccountRequest,
    MessageResponse
)
from repositories import UserRepository, RefreshTokenRepository
from models import User
from utils import Logger
from .password_service import PasswordService
from .token_service import TokenService
from kafka import KafkaProducerService, Event, UserCreatedPayload, UserDeletedPayload
from config import cfg


class AuthService:
    def __init__(
        self, 
        user_repository: UserRepository, 
        refresh_token_repository: RefreshTokenRepository,
        kafka_producer_service: KafkaProducerService
    ):
        self.__user_repository = user_repository
        self.__refresh_token_repository = refresh_token_repository
        self.__kafka_producer_service = kafka_producer_service


    async def register(self, request: RegisterRequest) -> AuthResponse:
        if not PasswordService.check_password_strength(request.password):
            Logger.info(f"Password strength is not met")
            raise HTTPException(
                status_code=422,
                detail="Password does not meet strength requirements"
            )

        user = User(
            email=request.email,
            password_hash=PasswordService.hash_password(request.password),
        )

        try:
            user = await self.__user_repository.create_user(user)
        except IntegrityError as ex:
            Logger.error(f"func {self.register.__name__}: IntegrityError: {ex}")
            if "users_email_key" in str(ex.orig):
                raise HTTPException(
                    status_code=409,
                    detail="User with this email already exists"
                )
            
            raise

        # Send user created event to Kafka
        event = Event(
            event_id=str(uuid4()),
            event_type=cfg.KAFKA_USER_CREATED_TOPIC,
            occurred_at=datetime.now(timezone.utc),
            payload=UserCreatedPayload(
                id=user.id,
                email=user.email,
            ).model_dump(),
        )

        await self.__kafka_producer_service.send_event(
            cfg.KAFKA_USER_CREATED_TOPIC,
            event,
        )
        Logger.info(f"UserCreated event <id: {event.event_id}, type: {event.event_type}> was sent for user: {user.id}")

        refresh_token = await TokenService.generate_refresh_token(
            self.__refresh_token_repository,
            user.id,
        )

        access_token = TokenService.generate_access_token(user)

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,            
        )
    

    async def login(self, request: LoginRequest) -> AuthResponse:
        user = await self.__user_repository.get_user_by_email(request.email)

        if not user or not PasswordService.verify_password(request.password, user.password_hash):
            Logger.info(f"Invalid login attempt for email: {request.email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password"
            )
        
        refresh_token = await TokenService.generate_refresh_token(
            self.__refresh_token_repository,
            user.id,
        )
        access_token = TokenService.generate_access_token(user)

        return AuthResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        

    async def logout(self, request: LogoutRequest) -> MessageResponse:
        refresh_token = await TokenService.verify_refresh_token(
            self.__refresh_token_repository,
            request.refresh_token
        )

        await TokenService.delete_refresh_token_by_id(
            self.__refresh_token_repository,
            refresh_token.id,
        )
        Logger.info(f"User {refresh_token.user_id} logged out successfully")

        return MessageResponse(message="Logged out successfully")


    async def refresh_token(self, request: RefreshTokenRequest) -> RefreshTokenResponse:
        refresh_token = await TokenService.verify_refresh_token(
            self.__refresh_token_repository,
            request.refresh_token
        )

        user = await self.__user_repository.get_user_by_id(refresh_token.user_id)
        if not user:
            Logger.info(f"User with id {refresh_token.user_id} not found")
            raise HTTPException(
                status_code=401,
                detail="Invalid refresh token"
            )
        
        access_token = TokenService.generate_access_token(user)

        return RefreshTokenResponse(access_token=access_token)


    async def delete_account(self, request: DeleteAccountRequest) -> MessageResponse:
        refresh_token = await TokenService.verify_refresh_token(
            self.__refresh_token_repository,
            request.refresh_token
        )
        
        await self.__user_repository.delete_user(refresh_token.user_id)

        # Send user deleted event to Kafka
        event = Event(
            event_id=str(uuid4()),
            event_type=cfg.KAFKA_USER_DELETED_TOPIC,
            occurred_at=datetime.now(timezone.utc),
            payload=UserDeletedPayload(
                id=refresh_token.user_id,
            ).model_dump(),
        )

        await self.__kafka_producer_service.send_event(
            cfg.KAFKA_USER_DELETED_TOPIC,
            event,
        )
        Logger.info(f"UserDeleted event <id: {event.event_id}, type: {event.event_type}> was sent for user: {refresh_token.user_id}")


        return MessageResponse(message="Account deleted successfully")
    