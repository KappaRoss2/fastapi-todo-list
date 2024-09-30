from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


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
