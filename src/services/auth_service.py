from abc import ABC, abstractmethod

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from config import app_settings
from db import get_async_session
from repository import AuthRepository
from schemas import RegistrationInputSchema, LoginInputSchema
from tasks import send_email
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

    @abstractmethod
    async def login(self, login_data: LoginInputSchema):
        """Вход пользователя."""
        pass


class AuthService(AuthServiceABC):
    """Сервис аутентификации и регистрации."""

    def __init__(self, session: AsyncSession):
        self.repository = AuthRepository(session)

    async def register(self, user_data: RegistrationInputSchema) -> User:
        """Регистрация пользователя.

        Args:
            user_data (RegistrationInputSchema): Данные пользователя

        Returns:
            User: Пользователь
        """
        new_user = await self.repository.register(user_data.model_dump())
        return new_user

    async def login(self, login_data: LoginInputSchema):
        """Вход в систему

        Args:
            login_data (LoginInputSchema): Данные для входа
        """
        user_id, user_email = await self.repository.login(login_data.model_dump())
        code = await self.repository.generate_user_code(user_id=user_id)
        subject = 'Двухфакторная аутентификация'
        body = f'Код для двухфакторной аутентификации: {code}'
        send_email.delay(
            app_settings.smtp_server,
            app_settings.smtp_port,
            app_settings.smtp_username,
            app_settings.smtp_password,
            user_email,
            subject,
            body
        )


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)
