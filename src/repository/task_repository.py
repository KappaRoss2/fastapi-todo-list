from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from models import Task


class TaskRepositoryABC(ABC):
    """Интерфейс для репозитория карточек."""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор для репозитория карточек."""
        pass

    @abstractmethod
    async def create_task(self, data: dict) -> Task:
        """Метод создания карточки."""
        pass


class TaskRepository(TaskRepositoryABC):
    """Репозиторий карточек."""

    def __init__(self, session: AsyncSession):
        """Конструктор для репозитория карточек.

        Args:
            session (AsyncSession): Сессия БД.
        """
        self.session = session

    async def create_task(self, data: dict) -> Task:
        """Метод создания карточки.

        Args:
            data (dict): Данные для создания.

        Returns:
            Task: Новая карточка.
        """
        new_task = Task(**data)
        self.session.add(new_task)
        await self.session.commit()
        await self.session.refresh(new_task)
        return new_task
