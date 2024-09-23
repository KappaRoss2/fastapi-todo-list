from uuid import uuid4
from datetime import datetime

from sqlalchemy import func, text, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class User(Base):
    """Модель пользователя."""

    __tablename__ = 'user'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text('gen_random_uuid()'),
    )
    username: Mapped[str] = mapped_column(String, doc='Логин', unique=True)
    password: Mapped[str] = mapped_column(String, doc='Пароль')
    email: Mapped[str] = mapped_column(String, doc='Email', unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, doc='Время регистрации', server_default=func.now())
    is_register: Mapped[bool] = mapped_column(
        Boolean,
        doc='Подтвреждена ли регистрация',
        default=False,
        server_default=text('false')
    )
    is_confirmed: Mapped[bool] = mapped_column(
        Boolean,
        doc='Пройдена ли двухфакторная аутентификация',
        default=False,
        server_default=text('false'),
    )
