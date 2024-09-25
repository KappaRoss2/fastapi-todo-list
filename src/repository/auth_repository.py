from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from typing import Union

from fastapi import HTTPException, status

from sqlalchemy import select, or_, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID

import jwt

from passlib.context import CryptContext

from config import app_settings
from models import User, UsersCode
from schemas import TokenType


pwd_context = CryptContext(
    schemes=[app_settings.crypt_context_schema],
    deprecated=app_settings.crypt_context_deprecated
)


class AuthRepositoryABC(ABC):
    """Интерфейс для аутентификации и регистрации."""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор репозитории для аутентификации и регистрации."""
        pass

    @abstractmethod
    async def register(self, user_data: dict) -> User:
        """Регистрация пользователя."""
        pass

    @abstractmethod
    async def login(self, user_data: dict) -> User:
        """Аутентификация пользователя."""
        pass

    @abstractmethod
    async def verify_otp(self, user_data: dict) -> bool:
        """Подтверждение входа кодом из почты."""
        pass


class AuthRepository(AuthRepositoryABC):
    """Репозиторий для аутентификации и регистрации."""

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def register(self, user_data: dict) -> User:
        """Регистрация пользователя.

        Args:
            user_data (dict): Данные пользователя

        Returns:
            User: Пользователь
        """
        username, email, password = user_data.get('username'), user_data.get('email'), user_data.get('password')
        await self._check_existing_user(username, email)
        hashed_password = pwd_context.hash(password)
        user_data['password'] = hashed_password
        new_user = User(**user_data)
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def _check_existing_user(self, username: str, email: str) -> Union[HTTPException, None]:
        """Проверяем существует ли такой пользователь уже в системе.

        Args:
            username (str): Логин
            email (str): Email

        Returns:
            bool: Существует(True)/Не существует(False)
        """
        query = select(User).where(
            User.username == username
            or User.email == email
        )
        result = await self.session.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user:
            if existing_user.username == username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Пользователь с таким логином уже существует'
                )
            if existing_user.email == email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Пользователь с таким email уже существует'
                )

    async def login(self, user_data: dict) -> User:
        """Аутентификация пользователя.

        Args:
            user_data (dict): Данные пользователя для входа.
        """
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверные учетные данные'
        )
        login, password = user_data.get('login'), user_data.get('password')
        query = select(User).where(
                or_(User.username == login, User.email == login),
        )
        result = await self.session.execute(query)
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise http_exception
        is_password_correct = pwd_context.verify(password, current_user.password)
        if not is_password_correct:
            raise http_exception
        return current_user

    async def delete_user_code(self, user_id: UUID):
        """Удаляем прошлые коды пользователя.

        Args:
            user_id (UUID): id юзера.
        """
        stmt = delete(UsersCode).where(UsersCode.user_id == user_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def create_user_code(self, data: dict) -> UsersCode:
        """Генерация случайного 6-ти значного числа для пользователя.

        Args:
            current_user (User): Пользователь для которого генирируем код.
        """
        users_code = UsersCode(**data)
        self.session.add(users_code)
        await self.session.commit()
        await self.session.refresh(users_code)
        return users_code

    async def verify_otp(self, user_data: dict) -> bool:
        """Подтверждение входа из почты.

        Args:
            user_data (dict): Данные пользователя.

        Returns:
            bool: Подтвержден/Не подтвержден.
        """
        user_id, code = user_data.get('user_id'), user_data.get('code')
        query = select(UsersCode.code, UsersCode.created_at).where(UsersCode.user_id == user_id)
        result = await self.session.execute(query)
        verify_data = result.fetchone()
        if not verify_data:
            return False
        expired_datetime = verify_data.created_at.replace(tzinfo=timezone.utc) + timedelta(minutes=5)
        return verify_data.code == code and expired_datetime >= datetime.now(timezone.utc)

    async def update_user(self, user_id: UUID, update_data: dict):
        """Обновляем пользователя.

        Args:
            user_id (UUID): id Пользователя.
        """
        stmt = update(User).where(User.id == user_id).values(**update_data)
        await self.session.execute(stmt)
        await self.session.commit()

    def create_jwt_token(self, user_id: UUID) -> dict:
        """Создаем jwt токен.

        Returns:
            dict: JWT токен.
        """
        token = {}
        token_data = {}
        expiration = datetime.now(timezone.utc) + timedelta(minutes=app_settings.access_token_expire_minutes)
        token_data['user_id'] = str(user_id)
        token_data['expiration'] = datetime.strftime(expiration, '%Y-%m-%d %H:%M:%S.%f+00:00')
        token_value = jwt.encode(token_data, app_settings.secret_key, algorithm=app_settings.algorithm)
        token['access_token'] = token_value
        token['token_type'] = TokenType.Bearer.value
        return token
