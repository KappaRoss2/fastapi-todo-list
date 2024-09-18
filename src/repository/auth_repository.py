from abc import ABC, abstractmethod
from typing import Union

from fastapi import HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from passlib.context import CryptContext

from config import CRYPT_CONTEXT_SCHEMA, CREPT_CONTEXT_DEPRECATED
from models import User


pwd_context = CryptContext(schemes=[CRYPT_CONTEXT_SCHEMA], deprecated=CREPT_CONTEXT_DEPRECATED)


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


class AuthRepository(AuthRepositoryABC):
    """Репозиторий для аутентификации и регистрации."""

    model = User

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def register(self, user_data: dict) -> User:
        username, email, password = user_data.get('username'), user_data.get('email'), user_data.get('password')
        await self._check_existing_user(username, email)
        hashed_password = pwd_context.hash(password)
        user_data['password'] = hashed_password
        new_user = self.model(**user_data)
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
        query = select(self.model).where(
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
