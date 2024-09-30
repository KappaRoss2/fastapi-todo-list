from uuid import uuid4
from datetime import datetime
from typing import List, TYPE_CHECKING

from sqlalchemy import func, text, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


if TYPE_CHECKING:
    from .task import Task


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
    code: Mapped['UsersCode'] = relationship(back_populates='user')
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
    tasks: Mapped[List['Task']] = relationship('Task', back_populates='user')


class UsersCode(Base):
    """Модель кодов подтверждения."""

    __tablename__ = 'users_code'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text('gen_random_uuid()'),
    )
    code: Mapped[int] = mapped_column(Integer, doc='Код подтверждения', nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'), onupdate='CASCADE', nullable=False)
    user: Mapped['User'] = relationship(back_populates='code')
    created_at: Mapped[datetime] = mapped_column(DateTime, doc='Время создания кода', server_default=func.now())
