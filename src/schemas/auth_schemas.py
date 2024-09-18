from uuid import UUID
from typing import Union

from fastapi import HTTPException, status
from password_validator import PasswordValidator

from pydantic import BaseModel, EmailStr, field_validator


class RegistrationInputSchema(BaseModel):
    """Схема входных данных для регистрации."""

    username: str
    password: str
    email: EmailStr

    @field_validator('password')
    def validate_password(cls, password: str) -> Union[str, HTTPException]:
        """Валидация пароля.

        Args:
            password (str): Пароль.
        """
        password_validator = PasswordValidator()
        password_validator.min(8).max(20).has().uppercase().has().lowercase().has().digits().has().symbols()
        if password_validator.validate(password):
            return password
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Пароль недостаточно надежен',
        )


class RegistrationOutputSchema(BaseModel):
    """Схема выходных данных для регистрации."""

    id: UUID
    username: str
    email: EmailStr
