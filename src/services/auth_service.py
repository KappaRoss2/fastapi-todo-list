from abc import ABC, abstractmethod

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from db import get_async_session
from repository import AuthRepository
from schemas import RegistrationInputSchema
from models import User


class AuthServiceABC(ABC):
    """Интерфейс сервиса для аутентификации и регистрации."""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор сервиса для аутентификации и регистрации."""
        pass

    @abstractmethod
    async def register(self, user_data: RegistrationInputSchema) -> User:
        """Регистрация пользователя."""
        pass


class AuthService(AuthServiceABC):
    """Сервис аутентификации и регистрации."""

    def __init__(self, session: AsyncSession):
        self.repository = AuthRepository(session)

    async def register(self, user_data: RegistrationInputSchema) -> User:
        new_user = await self.repository.register(user_data.model_dump())
        return new_user


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)
