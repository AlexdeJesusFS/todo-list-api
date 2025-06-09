from contextlib import asynccontextmanager
from datetime import datetime

import factory
import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import SQLModel, StaticPool

from src.app import app
from src.database import get_session
from src.models.user import User
from src.security import get_password_hash


class UserFactory(factory.Factory):
    class Meta:
        model = User  # type: ignore

    username = factory.Sequence(lambda n: f'test{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')
    password = factory.LazyAttribute(lambda obj: f'{obj.username}@')


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def session(mock_db_time):
    engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with mock_db_time(model=User):
        async with AsyncSession(engine, expire_on_commit=False) as session:
            yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@asynccontextmanager
async def _mock_db_time(
    *,
    model,
    create_time=datetime(2025, 1, 1),
    update_time=datetime(2025, 2, 2),
):
    def fake_created_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = create_time
        if hasattr(target, 'updated_at'):
            target.updated_at = create_time

    def fake_updated_time_hook(mapper, connection, target):
        if hasattr(target, 'updated_at'):
            target.updated_at = update_time

    event.listen(model, 'before_insert', fake_created_time_hook)
    event.listen(model, 'before_update', fake_updated_time_hook)

    try:
        yield create_time, update_time
    finally:
        event.remove(model, 'before_insert', fake_created_time_hook)
        event.remove(model, 'before_update', fake_updated_time_hook)


@pytest_asyncio.fixture
def mock_db_time():
    return _mock_db_time


@pytest_asyncio.fixture
async def user(session):
    password = 'Test@'
    user = UserFactory(
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {'user': user, 'clean_password': password}


@pytest_asyncio.fixture
async def other_user(session):
    password = 'Test@'
    user = UserFactory(
        password=get_password_hash(password),
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {'user': user, 'clean_password': password}


@pytest.fixture
def token(client, user):
    _user = user['user']
    clean_password = user['clean_password']

    response = client.post(
        '/auth/token',
        data={
            'username': _user.email,
            'password': clean_password,
        },
    )
    return response.json()['access_token']
