from abc import ABC, abstractmethod

from fastapi import Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

from config import app_settings
from db import get_async_session
from repository import AuthRepository
from schemas import RegistrationInputSchema, LoginInputSchema, VerifyInputSchema
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
    async def login(self, login_data: LoginInputSchema) -> User:
        """Вход пользователя."""
        pass

    @abstractmethod
    async def verify_otp(self, user_data: VerifyInputSchema) -> dict:
        """Подтверждение входа кодом из почты."""
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

    async def login(self, login_data: LoginInputSchema) -> User:
        """Вход в систему

        Args:
            login_data (LoginInputSchema): Данные для входа
        """
        current_user = await self.repository.login(login_data.model_dump())
        await self.repository.delete_user_code(current_user.id)
        code = await self.repository.generate_user_code(user_id=current_user.id)
        subject = 'Двухфакторная аутентификация'
        body = f'Код для двухфакторной аутентификации: {code}'
        send_email.delay(
            app_settings.smtp_server,
            app_settings.smtp_port,
            app_settings.smtp_username,
            app_settings.smtp_password,
            current_user.email,
            subject,
            body
        )
        return current_user

    async def verify_otp(self, user_data: VerifyInputSchema) -> dict:
        is_verified = await self.repository.verify_otp(user_data.model_dump())
        if is_verified:
            updated_data = {
                'is_register': True,
                'is_confirmed': True
            }
            await self.repository.update_user(user_id=user_data.user_id, update_data=updated_data)
            token = self.repository.create_jwt_token(user_data.user_id)
            return token
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Неверный код или вы не успели ввести код!'
            )


def get_auth_service(
    session: AsyncSession = Depends(get_async_session),
) -> AuthService:
    return AuthService(session)
