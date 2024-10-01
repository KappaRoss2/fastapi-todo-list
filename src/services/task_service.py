from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession

from db.database import get_async_session
from models import User, Task
from schemas import TaskCreateInputSchema, TaskUpdateInputSchema
from paginators import TaskPaginator
from repository import TaskRepository
from utils import prepare_ordering


class TaskServiceABC(ABC):
    """Интерфейс сервиса для карточек."""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор для сервиса карточек."""
        pass

    @abstractmethod
    async def create(self, user: User, data: TaskCreateInputSchema) -> Task:
        """Создание карточки."""
        pass

    @abstractmethod
    async def get_all_by_user(self, user: User, paginator: TaskPaginator, ordering: tuple) -> List[Task]:
        """Получения карточек заданий пользователя."""
        pass

    @abstractmethod
    async def get_user_task_by_id(self, user: User, task_id: UUID) -> Task:
        """Получаем конкретную карточку задания пользователя."""
        pass

    @abstractmethod
    async def delete_current_task(self, user: User, task_id: UUID) -> None:
        """Удаляем конкретную карточку задания пользователя."""
        pass

    @abstractmethod
    async def update_current_task(self, user: User, task_id: UUID, task_data: TaskUpdateInputSchema) -> Task:
        """Обновляем конкретную карточку задания пользователя."""
        pass


class TaskService(TaskServiceABC):
    """Сервис для карточек."""

    def __init__(self, session: AsyncSession):
        """Конструктор для сервиса карточек.

        Args:
            session (AsyncSession): Сессия БД.
        """
        self.repository = TaskRepository(session)

    async def create(self, user: User, data: TaskCreateInputSchema) -> Task:
        """Создание карточки.

        Args:
            user (User): Текущий пользователь.
            data (TaskCreateInputSchema): Данные для создания карточки задания.

        Returns:
            Task: Карточка задания.
        """
        created_data = data.model_dump()
        created_data['user_id'] = user.id
        result = await self.repository.create(created_data)
        return result

    async def get_all_by_user(self, user: User, paginator: TaskPaginator, ordering: tuple) -> List[Task]:
        """Получения карточек заданий пользователя.

        Args:
            user (User): Текущий пользователь.
            paginator (TaskPaginator): Пагинатор.
            ordering (tuple): Правило сортировки.
        Returns:
            List[Task]: Карточки заданий.
        """
        if ordering is None:
            ordering = tuple()
        prepared_ordering = prepare_ordering(ordering)
        result = await self.repository.get_all_by_user(user.id, paginator.limit, paginator.offset, prepared_ordering)
        return result

    async def get_user_task_by_id(self, user: User, task_id: UUID) -> Task:
        """Получаем конкретную карточку задания пользователя.

        Args:
            user (User): Текущий пользователь.
            task_id (UUID): id карточки задания.

        Returns:
            Task: Карточка задания.
        """
        result = await self.repository.get_user_task_by_id(user.id, task_id)
        return result

    async def delete_current_task(self, user: User, task_id: UUID) -> None:
        """Удаляем конкретную карточку задания пользователя.

        Args:
            user (User): Текущий пользователь.
            task_id (UUID): id карточки задания.
        """
        await self.repository.delete_current_task(user.id, task_id)

    async def update_current_task(self, user: User, task_id: UUID, task_data: TaskUpdateInputSchema) -> Task:
        """Обновляем конкретную карточку задания пользователя.

        Args:
            user (User): Текущий пользователь.
            task_id (UUID): id Карточки задания.
            task_data (TaskUpdateInputSchema): Обновляемые данные.

        Returns:
            Task: Карточка задания.
        """
        result = await self.repository.update_current_task(user.id, task_id, task_data.model_dump())
        return result


def get_task_service(
    session: AsyncSession = Depends(get_async_session),
) -> TaskService:
    return TaskService(session)
