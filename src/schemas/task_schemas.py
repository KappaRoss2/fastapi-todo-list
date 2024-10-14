from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .user_schemas import UserSchema


class BaseTaskInputSchema(BaseModel):
    """Базовая схема входных данных для карточки задания."""

    title: str
    description: str


class BaseTaskOutputSchema(BaseModel):
    """Базовая схема выходных данных для карточки задания."""

    id: UUID
    title: str
    description: str
    status: bool
    created_at: datetime


class TaskCreateInputSchema(BaseTaskInputSchema):
    """Схема входных данных для карточки задания при ее создании."""

    pass


class TaskCreateOutputSchema(BaseTaskOutputSchema):
    """Схема выходных данных для карточки задания при ее создании."""

    pass


class TaskListOutputSchema(BaseTaskOutputSchema):
    """Схема списка выходных данных для карточки задания."""

    model_config = ConfigDict(from_attributes=True)
    user: UserSchema


class TaskRetrieveOutputSchema(BaseTaskOutputSchema):
    """Схема выходных данных конкретной карточки задания."""

    model_config = ConfigDict(from_attributes=True)
    user: UserSchema


class TaskUpdateInputSchema(BaseTaskInputSchema):
    """Схема входных данных при обновлении конкретной карточки задания."""

    status: bool


class TaskUpdateOutputSchema(BaseTaskOutputSchema):
    """Схема выходных данных при обновлении конкретной карточки задания."""

    model_config = ConfigDict(from_attributes=True)
