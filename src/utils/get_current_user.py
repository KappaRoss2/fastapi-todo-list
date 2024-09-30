from datetime import datetime, timezone

from fastapi import Request, HTTPException, status, Depends

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jwt import decode
from jwt.exceptions import DecodeError

from config import app_settings
from db.database import get_async_session
from models import User


def get_token(request: Request) -> str:
    """Получаем токен из запроса.

    Args:
        request (Request): Запрос.

    Raises:
        HTTPException: Токена нет в запросе.

    Returns:
        str: Токен.
    """
    token = request.headers.get('Authorization')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token not found')
    return token


async def get_current_user(token: str = Depends(get_token), session: AsyncSession = Depends(get_async_session)) -> User:
    """Получаем текущего пользователя.

    Args:
        token (str, optional): Получаем токен из заголовков. Defaults to Depends(get_token).
        session (AsyncSession, optional): Получаем сессию. Defaults to Depends(get_async_session).

    Raises:
        HTTPException: Не нашли токен в заголовке.
        HTTPException: Ошибка при декодировании токена.

    Returns:
        User: Текущий пользователь.
    """
    _, token_data = token.split()
    try:
        payload = decode(token_data, app_settings.secret_key, algorithms=[app_settings.algorithm])
    except (DecodeError, ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Invalid token'
        )
    expire = datetime.strptime(payload.get('expiration'), '%Y-%m-%d %H:%M:%S.%f+00:00').replace(tzinfo=timezone.utc)
    current_datetime = datetime.now(tz=timezone.utc)
    if current_datetime >= expire:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token is expired'
        )
    user_id = payload.get('user_id')
    query = select(User).where(User.id == user_id)
    result = await session.execute(query)
    user = result.scalar_one_or_none()
    return user
