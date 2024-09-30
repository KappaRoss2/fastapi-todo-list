from typing import Annotated

from fastapi import APIRouter, Depends, status
from models import User
from utils import get_current_user
from schemas import TaskCreateOutputSchema, TaskCreateInputSchema
from services import TaskService, get_task_service


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
):
    result = await task_service.create_task(current_user, task_data)
    return result
