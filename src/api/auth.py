from typing import Annotated

from fastapi import APIRouter, Depends, status

from services import AuthService, get_auth_service
from schemas import RegistrationOutputSchema, RegistrationInputSchema, LoginInputSchema

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
)
async def login(
    user: LoginInputSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    """Аутентификация пользователя."""
    await auth_service.login(user)
