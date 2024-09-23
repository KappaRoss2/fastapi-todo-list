from uuid import uuid4
from datetime import datetime

from sqlalchemy import text, ForeignKey, func
from sqlalchemy import DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


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
    user: Mapped[UUID] = mapped_column(ForeignKey('user.id'), onupdate='CASCADE', nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, doc='Время создания кода', server_default=func.now())
