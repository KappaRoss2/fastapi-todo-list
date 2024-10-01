from abc import ABC, abstractmethod
from typing import List
from uuid import UUID

from fastapi import HTTPException, status

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from models import Task


class TaskRepositoryABC(ABC):
    """Интерфейс для репозитория карточек."""

    @abstractmethod
    def __init__(self, session: AsyncSession):
        """Конструктор для репозитория карточек."""
        pass

    @abstractmethod
    async def create(self, data: dict) -> Task:
        """Метод создания карточки."""
        pass

    @abstractmethod
    async def get_all_by_user(
        self,
        user_id: UUID,
        pagination_limit: int,
        pagination_offset: int,
        ordering: tuple
    ) -> List[Task]:
        """Получаем все записи карточек заданий с заданным user_id."""
        pass

    @abstractmethod
    async def get_user_task_by_id(self, user_id: UUID, task_id: UUID) -> Task:
        """Получаем конкретную карточку задания пользователя."""
        pass

    @abstractmethod
    async def delete_current_task(self, user_id: UUID, task_id: UUID) -> None:
        """Удаляем конкретную карточку задания пользователя."""
        pass

    @abstractmethod
    async def update_current_task(self, user_id: UUID, task_id: UUID, task_data: dict) -> Task:
        """Обновляем конкретную карточку задания пользователя."""
        pass


class TaskRepository(TaskRepositoryABC):
    """Репозиторий карточек."""

    def __init__(self, session: AsyncSession):
        """Конструктор для репозитория карточек.

        Args:
            session (AsyncSession): Сессия БД.
        """
        self.session = session

    async def create(self, data: dict) -> Task:
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

    async def get_all_by_user(
        self,
        user_id: UUID,
        pagination_limit: int,
        pagination_offset: int,
        ordering: list
    ) -> List[Task]:
        """Получаем все записи карточек заданий с заданным user_id.

        Args:
            user_id (UUID): id Пользователя.
            pagination_limit (int): Количество элементов на странице.
            pagination_offset (int): Номер страницы.
            ordering (list): Порядок сортировки.

        Returns:
            List[Task]: Список карточек заданий.
        """
        query = select(
            Task
        ).where(
            Task.user_id == user_id
        ).order_by(
            *ordering
        ).limit(
            pagination_limit
        ).offset(
            pagination_offset
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_user_task_by_id(self, user_id: UUID, task_id: UUID) -> Task:
        """Получаем конкретную карточку задания пользователя.

        Args:
            user_id (UUID): id пользователя.
            task_id (UUID): id карточки задания.

        Raises:
            HTTPException: Карточка не найдена.

        Returns:
            Task: Карточка задания.
        """
        query = select(Task).where(Task.user_id == user_id, Task.id == task_id)
        result = await self.session.execute(query)
        task = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND
            )
        return task

    async def delete_current_task(self, user_id: UUID, task_id: UUID) -> None:
        """Удаляем конкретную карточку задания пользователя.

        Args:
            user_id (UUID): id Пользователя.
            task_id (UUID): id карточки задания.
        """
        stmt = delete(Task).where(Task.user_id == user_id, Task.id == task_id)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_current_task(self, user_id: UUID, task_id: UUID, task_data: dict) -> Task:
        """Обновляем конкретную карточку задания пользователя.

        Args:
            user_id (UUID): id Пользователя.
            task_id (UUID): id карточки задания.
            task_data (dict): Данные для обновления.

        Returns:
            Task: карточка задания.
        """
        stmt = update(Task).where(Task.user_id == user_id, Task.id == task_id).values(**task_data).returning(Task)
        result = await self.session.execute(stmt)
        await self.session.commit()
        task = result.scalar_one_or_none()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found'
            )
        return task
