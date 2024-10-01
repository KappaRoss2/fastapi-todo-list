from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, status, Path, Security
from fastapi.security import APIKeyHeader

from models import User
from utils import get_current_user
from schemas import (
    TaskCreateOutputSchema, TaskCreateInputSchema, TaskListOutputSchema, TaskRetrieveOutputSchema,
    TaskUpdateOutputSchema, TaskUpdateInputSchema
)
from services import TaskService, get_task_service
from paginators import TaskPaginator


api_key_header = APIKeyHeader(name='Authorization')

router = APIRouter(tags=['TODO карточки'])


@router.post(
    '/tasks',
    description='Создание карточки задания',
    summary='Создание карточки задания',
    status_code=status.HTTP_201_CREATED,
    response_model=TaskCreateOutputSchema,
)
async def create_task(
    task_data: TaskCreateInputSchema,
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: User = Depends(get_current_user),
    api_key: str = Security(api_key_header),
):
    result = await task_service.create(current_user, task_data)
    return result


@router.get(
    '/tasks',
    description='Получение списка карточек',
    summary='Получение списка карточек',
    status_code=status.HTTP_200_OK,
    response_model=List[TaskListOutputSchema],
)
async def get_user_tasks(
    task_service: Annotated[TaskService, Depends(get_task_service)],
    paginator: TaskPaginator = Depends(TaskPaginator),
    current_user: User = Depends(get_current_user),
    api_key: str = Security(api_key_header),
):
    result = await task_service.get_all_by_user(current_user, paginator, (('created_at', 'asc'), ))
    return result


@router.get(
    '/tasks/{task_id}',
    description='Просмотр карточки',
    summary='Просмотр карточки',
    status_code=status.HTTP_200_OK,
    response_model=TaskRetrieveOutputSchema
)
async def get_user_current_task(
    task_id: Annotated[UUID, Path(description='id карточки задания')],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: User = Depends(get_current_user),
    api_key: str = Security(api_key_header),
):
    result = await task_service.get_user_task_by_id(current_user, task_id)
    return result


@router.delete(
    '/tasks/{task_id}',
    description='Удаление карточки задания',
    summary='Удаление карточки задания',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_current_task(
    task_id: Annotated[UUID, Path(description='id карточки задания')],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: User = Depends(get_current_user),
    api_key: str = Security(api_key_header),
):
    await task_service.delete_current_task(current_user, task_id)


@router.put(
    '/tasks/{task_id}',
    description='Обновление карточки задания',
    summary='Обновление карточки задания',
    status_code=status.HTTP_200_OK,
    response_model=TaskUpdateOutputSchema,
)
async def update_current_task(
    task_data: TaskUpdateInputSchema,
    task_id: Annotated[UUID, Path(description='id карточки задания')],
    task_service: Annotated[TaskService, Depends(get_task_service)],
    current_user: User = Depends(get_current_user),
    api_key: str = Security(api_key_header),
):
    result = await task_service.update_current_task(current_user, task_id, task_data)
    return result
