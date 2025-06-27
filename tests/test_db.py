from datetime import datetime

import pytest
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.models.tag import Tag
from src.models.task import Task, TaskStatus
from src.models.user import User


@pytest.mark.asyncio
async def test_create_user(session, mock_db_time):
    async with mock_db_time(model=User) as (create_time, _):
        new_user = User(
            username='Lex', password='s&cret', email='lex@mail.com'
        )
        session.add(new_user)
        await session.commit()

    user = await session.scalar(select(User).where(User.username == 'Lex'))

    assert user.to_dict() == {
        'id': 1,
        'username': 'Lex',
        'password': 's&cret',
        'email': 'lex@mail.com',
        'created_at': create_time,
        'updated_at': create_time,
        'tasks': [],
    }


@pytest.mark.asyncio
async def test_update_user(session, mock_db_time):
    async with mock_db_time(model=User) as (create_time, update_time):
        # criando user
        new_user = User(
            username='Lex', password='s&cret', email='lex@mail.com'
        )
        session.add(new_user)
        await session.commit()

        user = await session.scalar(select(User))

        # atualizando user
        user_updates = {
            'username': 'Lexus',
            'password': 'NewP@ss',
            'email': 'lexus@mail.com',
        }

        # cada attr do user recebe como novo valor o que está no
        # dict user_updates
        for attr, value in user_updates.items():
            setattr(user, attr, value)

        session.add(user)
        await session.commit()

        # assert
        updated_user = await session.scalar(select(User))

        assert updated_user.to_dict() == {
            'id': 1,
            'username': 'Lexus',
            'password': 'NewP@ss',
            'email': 'lexus@mail.com',
            'created_at': create_time,
            'updated_at': update_time,
            'tasks': [],
        }


@pytest.mark.asyncio
async def test_create_simple_task(session, user, mock_db_time):
    async with mock_db_time(model=Task) as (created_time, _):
        user_obj = user['user']
        task = Task(
            title='Test Task',
            status=TaskStatus.draft,
            user_id=user_obj.id,
        )

        session.add(task)
        await session.commit()

        task = await session.scalar(
            select(Task).options(
                selectinload(Task.children), selectinload(Task.tags)
            )
        )

        assert task.to_dict() == {
            'id': 1,
            'title': 'Test Task',
            'description': None,
            'status': TaskStatus.draft,
            'created_at': created_time,
            'updated_at': created_time,
            'due': None,
            'completed_at': None,
            'parent_id': None,
            'children': [],
            'tags': [],
            'user_id': user_obj.id,
        }


@pytest.mark.asyncio
async def test_create_complete_task(session, user, task, tag, mock_db_time):
    async with mock_db_time(model=Task) as (created_time, _):
        user_obj = user['user']
        parent_task = task['parent_task']
        children_task = task['children_task']

        task_obj = Task(
            title='Test Task',
            description='Test description',
            status=TaskStatus.done,
            due=datetime(2025, 7, 1),
            completed_at=datetime(2025, 6, 30),
            parent_id=parent_task.id,
            children=[children_task],
            tags=[tag],
            user_id=user_obj.id,
        )

        session.add(task_obj)
        await session.commit()

        task_db = await session.scalar(
            select(Task).where(Task.id == task_obj.id)
        )

        assert task_db.to_dict() == {
            'id': task_obj.id,
            'title': 'Test Task',
            'description': 'Test description',
            'status': TaskStatus.done,
            'created_at': created_time,
            'updated_at': created_time,
            'due': datetime(2025, 7, 1),
            'completed_at': datetime(2025, 6, 30),
            'parent_id': parent_task.id,
            'children': [children_task],
            'tags': [tag],
            'user_id': user_obj.id,
        }


@pytest.mark.asyncio
async def test_update_taks(session, user, mock_db_time):
    async with mock_db_time(model=Task) as (created_time, updated_time):
        user_obj = user['user']
        new_task = Task(
            title='Task',
            description='description',
            status=TaskStatus.draft,
            user_id=user_obj.id,
        )

        session.add(new_task)
        await session.commit()

        task = await session.scalar(select(Task))

        task_updates = {
            'title': 'New Task',
            'description': 'New description',
            'status': TaskStatus.todo,
        }

        for attr, value in task_updates.items():
            setattr(task, attr, value)

        session.add(task)
        await session.commit()

        task_updated = await session.scalar(
            select(Task).options(
                selectinload(Task.children), selectinload(Task.tags)
            )
        )

        assert task_updated.to_dict() == {
            'id': 1,
            'title': 'New Task',
            'description': 'New description',
            'status': TaskStatus.todo,
            'created_at': created_time,
            'updated_at': updated_time,
            'due': None,
            'completed_at': None,
            'parent_id': None,
            'children': [],
            'tags': [],
            'user_id': user_obj.id,
        }


@pytest.mark.asyncio
async def test_create_tag(session, mock_db_time):
    async with mock_db_time(model=Tag) as (created_time, _):
        tag = Tag(
            title='Test Tag',
            description='Test description',
        )

        session.add(tag)
        await session.commit()

        tag = await session.scalar(select(Tag))

        assert tag.to_dict() == {
            'id': 1,
            'title': 'Test Tag',
            'description': 'Test description',
            'text_color': '#FFFFFF',
            'background_color': '#000000',
            'created_at': created_time,
            'updated_at': created_time,
            'is_active': True,
            'owner_id': None,
        }


@pytest.mark.asyncio
async def test_update_tag(session, mock_db_time):
    async with mock_db_time(model=Tag) as (created_time, updated_time):
        new_tag = Tag(
            title='Tag',
        )

        session.add(new_tag)
        await session.commit()

        tag = await session.scalar(select(Tag))

        tag_updates = {
            'title': 'New Tag',
        }

        for attr, value in tag_updates.items():
            setattr(tag, attr, value)

        session.add(tag)
        await session.commit()

        tag_updated = await session.scalar(select(Tag))

        assert tag_updated.to_dict() == {
            'id': 1,
            'title': 'New Tag',
            'description': None,
            'text_color': '#FFFFFF',
            'background_color': '#000000',
            'created_at': created_time,
            'updated_at': updated_time,
            'is_active': True,
            'owner_id': None,
        }


@pytest.mark.asyncio
async def test_user_task_relationship(session, user):
    user_obj = user['user']
    task = Task(
        title='Test Taks',
        description='Test description',
        status=TaskStatus.draft,
        user_id=user_obj.id,
    )

    session.add(task)
    await session.commit()
    await session.refresh(user_obj)

    user = await session.scalar(select(User).where(User.id == user_obj.id))

    assert user.tasks == [task]


@pytest.mark.asyncio
async def test_task_tag_relationship(session, user, tag):
    user_obj = user['user']

    task = Task(
        title='Test Task',
        status=TaskStatus.draft,
        user_id=user_obj.id,
        tags=[tag],
    )

    session.add(task)
    await session.commit()
    await session.refresh(task)

    task = await session.scalar(select(Task).where(Task.id == task.id))

    assert task.tags == [tag]
