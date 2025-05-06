# mypy: disable-error-code="no-untyped-def"

import pytest  # type: ignore[import-not-found]
from fastapi.testclient import TestClient

from src.app import app


@pytest.fixture
def client():
    return TestClient(app)
