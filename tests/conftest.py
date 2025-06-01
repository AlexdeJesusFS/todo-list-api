from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlmodel import Session, SQLModel, StaticPool, create_engine

from src.app import app
from src.database import get_session
from src.models import user as user_models
from src.security import get_password_hash


@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def session(mock_db_time):
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    with mock_db_time(model=user_models.User):
        with Session(engine) as session:
            yield session

    SQLModel.metadata.drop_all(engine)


@contextmanager
def _mock_db_time(
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

    yield create_time, update_time

    event.remove(model, 'before_insert', fake_created_time_hook)
    event.remove(model, 'before_update', fake_updated_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
def user(session):
    password = 'Test@'
    user = user_models.User(
        username='Tester',
        email='tester@test.com',
        password=get_password_hash(password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    return {'user': user, 'clean_password': password}


@pytest.fixture
def token(client, user):
    response = client.post(
        '/token',
        data={
            'username': user['user'].email,
            'password': user['clean_password'],
        },
    )
    return response.json()['access_token']
