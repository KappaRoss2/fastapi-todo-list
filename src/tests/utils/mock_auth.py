from datetime import datetime, timedelta, timezone

import jwt

import pytest_asyncio
from passlib.context import CryptContext
from sqlalchemy import delete

from config import app_settings
from models import User
from schemas import TokenType


pwd_context = CryptContext(
    schemes=[app_settings.crypt_context_schema],
    deprecated=app_settings.crypt_context_deprecated
)


@pytest_asyncio.fixture(scope='function')
async def mock_user(db_session):  # noqa: F811
    """Фикстура для создания пользователя."""
    hashed_password = pwd_context.hash('testPassword123-')
    user = User(
        username='testuser',
        email='testuser@example.com',
        password=hashed_password,
        is_register=True,
        is_confirmed=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    yield user
    stmt = delete(User)
    await db_session.execute(stmt)
    await db_session.commit()


@pytest_asyncio.fixture(scope='function')
async def mock_token(mock_user):
    """Фикстура для генерации токена аутентификации."""
    token_data = {}
    expiration = datetime.now(timezone.utc) + timedelta(minutes=app_settings.access_token_expire_minutes)
    token_data['user_id'] = str(mock_user.id)
    token_data['expiration'] = datetime.strftime(expiration, '%Y-%m-%d %H:%M:%S.%f+00:00')
    token_value = jwt.encode(token_data, app_settings.secret_key, algorithm=app_settings.algorithm)
    return f'{TokenType.Bearer.value} {token_value}'
