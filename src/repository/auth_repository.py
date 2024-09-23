from abc import ABC, abstractmethod
from typing import Union, Tuple
from random import randint

from fastapi import HTTPException, status

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import UUID

from passlib.context import CryptContext

from config import app_settings
from models import User, UsersCode


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
    async def login(self, user_data: dict) -> Tuple[int, str]:
        """Аутентификация пользователя."""
        pass


class AuthRepository(AuthRepositoryABC):
    """Репозиторий для аутентификации и регистрации."""

    model = User

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
            self.model.username == username
            or self.model.email == email
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

    async def login(self, user_data: dict) -> Tuple[int, str]:
        """Аутентификация пользователя.

        Args:
            user_data (dict): Данные пользователя для входа.
        """
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Неверные учетные данные'
        )
        login, password = user_data.get('login'), user_data.get('password')
        query = select(self.model).where(
                or_(self.model.username == login, self.model.email == login),
        )
        result = await self.session.execute(query)
        current_user = result.scalar_one_or_none()
        if not current_user:
            raise http_exception
        is_password_correct = pwd_context.verify(password, current_user.password)
        if not is_password_correct:
            raise http_exception
        code = await self._generate_user_code(current_user.id)
        return code, current_user.email

    async def _generate_user_code(self, user_id: UUID) -> int:
        """Генерация случайного 6-ти значного числа для пользователя.

        Args:
            current_user (User): Пользователь для которого генирируем код.
        """
        code = randint(100000, 999999)
        users_code_data = {
            'code': randint(100000, 999999),
            'user': user_id,
        }
        users_code = UsersCode(**users_code_data)
        self.session.add(users_code)
        await self.session.commit()
        await self.session.refresh(users_code)
        return code
