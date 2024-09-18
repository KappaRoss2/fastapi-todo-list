from typing import Annotated

from fastapi import APIRouter, Depends

from services import AuthService, get_auth_service
from schemas import RegistrationOutputSchema, RegistrationInputSchema

router = APIRouter(tags=['Аутентификация и регистрация'])


@router.post(
    '/registration',
    description='Регистрация',
    summary='Регистрация',
    response_model=RegistrationOutputSchema
)
async def register(
    user: RegistrationInputSchema,
    auth_service: Annotated[AuthService, Depends(get_auth_service)]
) -> RegistrationOutputSchema:
    """Регистрация пользователя."""
    result = await auth_service.register(user)
    return result
