from fastapi import status as http_status
from fastapi.testclient import TestClient

from src.app import app


def test_root_should_return_ok_and_HelloWord() -> None:
    client = TestClient(app)  # Arrange (arrumar)

    response = client.get('/')  # Act (ação)

    assert response.status_code == http_status.HTTP_200_OK  # Assert (afirmar)
    assert response.json() == {'message': 'Hello World!'}
