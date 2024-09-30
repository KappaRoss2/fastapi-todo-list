from datetime import datetime
from uuid import uuid4
from typing import TYPE_CHECKING

from sqlalchemy import func, text, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base


if TYPE_CHECKING:
    from .user import User


class Task(Base):
    """Модель для карточки задания."""

    __tablename__ = 'task'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text('gen_random_uuid()'),
    )
    title: Mapped[str] = mapped_column(String, doc='Заголовок карточки', nullable=False)
    description: Mapped[str] = mapped_column(String, doc='Описание карточки', nullable=False)
    status: Mapped[bool] = mapped_column(
        Boolean,
        doc='Выполнено/Не выполнено',
        default=False,
        server_default=text('false')
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, doc='Дата создания карточки', server_default=func.now())
    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'), nullable=False)
    user: Mapped['User'] = relationship('User', back_populates='tasks')
