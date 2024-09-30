from abc import ABC, abstractmethod

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from models import User
from schemas import TaskCreateInputSchema
from repository import TaskRepository


class TaskServiceABC(ABC):
    """Интерфейс сервиса для карточек."""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор для сервиса карточек."""
        pass

    @abstractmethod
    async def create_task(self, user: User, data: TaskCreateInputSchema) -> User:
        """Создание карточки."""
        pass


class TaskService(TaskServiceABC):
    """Сервис для карточек."""

    def __init__(self, session: AsyncSession):
        """Конструктор для сервиса карточек.

        Args:
            session (AsyncSession): Сессия БД.
        """
        self.repository = TaskRepository(session)

    async def create_task(self, user: User, data: TaskCreateInputSchema) -> User:
        created_data = data.model_dump()
        created_data['user_id'] = user.id
        result = await self.repository.create_task(created_data)
        return result


def get_task_service(
    session: AsyncSession = Depends(get_async_session),
) -> TaskService:
    return TaskService(session)
