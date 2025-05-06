# mypy: disable-error-code="no-untyped-def"

from fastapi import status as http_status


def test_root_should_return_ok_and_HelloWord(client) -> None:
    response = client.get('/')  # Act (ação)

    assert response.status_code == http_status.HTTP_200_OK  # Assert (afirmar)
    assert response.json() == {'message': 'Hello World!'}


def test_html_should_return_ok_and_HTML(client) -> None:
    response = client.get('html')

    assert response.status_code == http_status.HTTP_200_OK
    assert '<h1>Hello World!</h1>' in response.text


def test_create_user(client) -> None:
    response = client.post(
        '/users/',
        json={'username': 'lex', 'email': 'lex@dev.com', 'password': 'secr&t'},
    )

    assert response.status_code == http_status.HTTP_201_CREATED
    assert response.json() == {
        'username': 'lex',
        'email': 'lex@dev.com',
        'id': 1,
    }


def test_get_users(client) -> None:
    response = client.get('/users/')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {
        'users': [
            {
                'username': 'lex',
                'email': 'lex@dev.com',
                'id': 1,
            }
        ]
    }


def test_get_user_should_return_OK(client) -> None:
    response = client.get('/user/1')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {
        'username': 'lex',
        'email': 'lex@dev.com',
        'id': 1,
    }


def test_get_user_should_return_NOT_FOUND(client) -> None:
    response = client.get('/user/0')

    assert response.status_code == http_status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_should_return_OK(client):
    response = client.put(
        '/users/1',
        json={
            'username': 'lexus',
            'email': 'lexus@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {
        'username': 'lexus',
        'email': 'lexus@mail.com',
        'id': 1,
    }


def test_update_user_should_return_NOT_FOUND(client):
    response = client.put(
        '/users/0',
        json={
            'username': 'lexus',
            'email': 'lexus@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user_should_return_OK(client):
    response = client.delete('/users/1')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {'message': 'User 1 deleted'}


def test_delete_user_should_return_NOT_FOUND(client):
    response = client.delete('/users/0')

    assert response.status_code == http_status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
