from datetime import datetime
from uuid import UUID

import pytest
import pytest_asyncio

from fastapi import status
from sqlalchemy import select, func, delete, asc
from sqlalchemy.ext.asyncio import AsyncSession
from httpx import AsyncClient

from models import User, Task
from schemas import TaskCreateInputSchema, TaskListOutputSchema, TaskRetrieveOutputSchema, TaskUpdateInputSchema

from ..conftest import client, db_session  # noqa: F401
from ..utils.mock_auth import mock_token, mock_user  # noqa: F401


@pytest_asyncio.fixture(scope='function')
async def mock_task(db_session: AsyncSession, mock_user: User):  # noqa: F811
    """Фикстура для создания карточек заданий."""
    task1 = Task(
        title='title1',
        description='description1',
        user_id=mock_user.id,
        created_at=datetime.now()
    )
    task2 = Task(
        title='title2',
        description='description2',
        user_id=mock_user.id,
        created_at=datetime.now()
    )
    task3 = Task(
        title='title3',
        description='description3',
        user_id=mock_user.id,
        created_at=datetime.now()
    )
    db_session.add_all([task1, task2, task3])
    yield await db_session.commit()
    stmt = delete(Task)
    await db_session.execute(stmt)
    await db_session.commit()


@pytest.mark.asyncio()
async def test_create_task(db_session: AsyncSession, client: AsyncClient, mock_token: str, mock_task):  # noqa: F811
    """Тест создания карточки задания."""
    task_data = TaskCreateInputSchema(title='title4', description='description4')
    response = await client.post('/api/tasks', json=task_data.model_dump(), headers={'Authorization': mock_token})
    assert response.status_code == status.HTTP_201_CREATED
    result = response.json()
    assert result['title'] == task_data.title
    assert result['description'] == task_data.description
    query = select(func.count(Task.id))
    result = await db_session.execute(query)
    count = result.scalar()
    assert count == 4


@pytest.mark.asyncio()
async def test_get_list_tasks(db_session: AsyncSession, client: AsyncClient, mock_token: str, mock_task):  # noqa: F811
    """Тест получения списка карточек задания."""
    response = await client.get('/api/tasks', headers={'Authorization': mock_token})
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert len(result) == 3
    query = select(Task).order_by(asc('created_at'))
    query_result = await db_session.execute(query)
    tasks = query_result.scalars().all()
    output_schemas = []
    for task in tasks:
        output_schemas.append(TaskListOutputSchema.model_validate(task))
    for result_task, schema in zip(result, output_schemas):
        result_task['id'] = UUID(result_task['id'])
        output_schema = schema.model_dump()
        output_schema['created_at'] = datetime.isoformat(output_schema['created_at'])
        assert result_task == output_schema


@pytest.mark.asyncio()
async def test_get_retrieve_task(
    db_session: AsyncSession,  # noqa: F811
    client: AsyncClient,  # noqa: F811
    mock_token: str,  # noqa: F811
    mock_task
):
    """Тест получения конкретной карточки задания."""
    query = select(Task).order_by(asc('created_at'))
    query_result = await db_session.execute(query)
    task = query_result.scalars().first()
    response = await client.get(f'/api/tasks/{task.id}', headers={'Authorization': mock_token})
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    output = TaskRetrieveOutputSchema.model_validate(result).model_dump()
    result['id'] = UUID(result['id'])
    output['created_at'] = datetime.isoformat(output['created_at'])
    assert result == output


@pytest.mark.asyncio()
async def test_delete_task(db_session: AsyncSession, client: AsyncClient, mock_token: str, mock_task):  # noqa: F811
    """Тест удаления конкретной карточки задания."""
    query = select(Task).order_by(asc('created_at'))
    query_result = await db_session.execute(query)
    task = query_result.scalars().first()
    response = await client.delete(f'/api/tasks/{task.id}', headers={'Authorization': mock_token})
    assert response.status_code == status.HTTP_204_NO_CONTENT
    query = select(func.count(Task.id))
    result = await db_session.execute(query)
    count = result.scalar()
    assert count == 2


@pytest.mark.asyncio()
async def test_update_task(db_session: AsyncSession, client: AsyncClient, mock_token: str, mock_task):  # noqa: F811
    """Тест обновления конкретной карточки задания."""
    query = select(Task).order_by(asc('created_at'))
    query_result = await db_session.execute(query)
    task = query_result.scalars().first()
    payload = TaskUpdateInputSchema(title='New title', description='New description', status=False)
    response = await client.put(
        f'/api/tasks/{task.id}', json=payload.model_dump(), headers={'Authorization': mock_token}
    )
    assert response.status_code == status.HTTP_200_OK
    result = response.json()
    assert result['title'] == payload.title
    assert result['description'] == payload.description
    assert result['status'] == payload.status
