from uuid import UUID

from pydantic import BaseModel, EmailStr


class BaseUserSchema(BaseModel):
    """Базовая схема пользователя"""

    username: str
    email: EmailStr


class UserSchema(BaseUserSchema):
    """Схема пользователя."""

    id: UUID
