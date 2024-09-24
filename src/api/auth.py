from typing import Annotated

from fastapi import APIRouter, Depends, status

from services import AuthService, get_auth_service
from schemas import (
    RegistrationOutputSchema, RegistrationInputSchema, LoginInputSchema, VerifyInputSchema, TokenSchema,
    LoginOutputSchema
)

router = APIRouter(tags=['Аутентификация и регистрация'])


@router.post(
    '/registration',
    description='Регистрация',
    summary='Регистрация',
    response_model=RegistrationOutputSchema,
    status_code=status.HTTP_201_CREATED
)
async def register(
    user: RegistrationInputSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> RegistrationOutputSchema:
    """Регистрация пользователя."""
    result = await auth_service.register(user)
    return result


@router.post(
    '/login',
    description='Аутентификация',
    summary='Вход',
    status_code=status.HTTP_200_OK,
    response_model=LoginOutputSchema
)
async def login(
    user: LoginInputSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Аутентификация пользователя."""
    result = await auth_service.login(user)
    return result


@router.post(
    '/verify-otp',
    description='Подтверждение из письма',
    summary='Подтверждение из письма',
    response_model=TokenSchema,
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    user: VerifyInputSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Подтверждение кодом из сообщения."""
    result = await auth_service.verify_otp(user)
    return result
