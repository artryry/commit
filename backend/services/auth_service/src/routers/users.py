from datetime import datetime, timezone, timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Form, Body, Path
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status
from fastapi import Response

from config import settings
from logger import Logger
from schemas import Token, UsersDTO, UsersPostDTO, TokenData
from dependencies import get_user_post_form, get_token_data, GetUsers


router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "User not found"}},
)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.PRIVATE_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    users: GetUsers,
) -> Token:
    user = await users.verify_user(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    Logger.info(f"Token was issued for user <id: {user.id}>")
    return Token(access_token=access_token, token_type="bearer")


@router.post("")
async def create_user(
        user_post: Annotated[UsersPostDTO, Depends(get_user_post_form)],
        password: Annotated[str, Form()],
        users: GetUsers,
):
    if not await users.create_user(user_post, password):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already used"
        )
    return Response(status_code=status.HTTP_201_CREATED)


@router.put("")
async def update_user(
        token_data: Annotated[TokenData, Depends(get_token_data)],
        new_user_data: Annotated[UsersPostDTO, Depends(get_user_post_form)],
        users: GetUsers,
):
    if not await users.update_user(token_data.id, new_user_data):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email is already used",
        )
    return Response(status_code=status.HTTP_200_OK)


@router.put("/password")
async def update_password(
        token_data: Annotated[TokenData, Depends(get_token_data)],
        password: Annotated[str, Form()],
        users: GetUsers,
):
    if not await users.update_password(token_data.id, password):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )
    return Response(status_code=status.HTTP_200_OK)


@router.delete("")
async def delete_user(
    token_data: Annotated[TokenData, Depends(get_token_data)],
    users: GetUsers,
):
    if not await users.delete_user(token_data.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
