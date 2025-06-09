from fastapi import status as http_status
from freezegun import freeze_time


def test_get_token(client, user):
    _user = user['user']
    clean_password = user['clean_password']

    response = client.post(
        '/auth/token',
        data={
            'username': _user.email,
            'password': clean_password,
        },
    )
    token = response.json()
    print('token aqui: ', token)

    assert response.status_code == http_status.HTTP_200_OK
    assert 'access_token' in token
    assert 'token_type' in token


def test_token_should_return_UNAUTHORIZED(client, user):
    # without user
    response_without_user = client.post(
        '/auth/token',
        data={'username': 'lele@mail.com', 'password': 'pass123'},
    )

    # incorrect password
    response_incorrect = client.post(
        '/auth/token',
        data={'username': user['user'].email, 'password': 'pass123'},
    )

    assert (
        response_without_user.status_code
        == response_incorrect.status_code
        == http_status.HTTP_401_UNAUTHORIZED
    )
    assert (
        response_without_user.json()
        == response_incorrect.json()
        == {'detail': 'Incorrect email or password'}
    )


def test_token_expired_after_time(client, user):
    _user = user['user']
    clean_password = user['clean_password']

    with freeze_time('2025-06-01 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': _user.email, 'password': clean_password},
        )
        assert response.status_code == http_status.HTTP_200_OK
        token = response.json()['access_token']

    with freeze_time('2025-06-01 12:31:00'):
        response = client.put(
            f'/users/{_user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'Mr. Wrong',
                'email': 'wrong@wrong.com',
                'password': 'wrong',
            },
        )
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}


def test_refresh_token(client, user, token):
    response = client.post(
        '/auth/refresh-token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == http_status.HTTP_200_OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'bearer'


def test_token_expired_dont_refresh(client, user):
    _user = user['user']
    clean_password = user['clean_password']
    with freeze_time('2025-06-01 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': _user.email, 'password': clean_password},
        )
        assert response.status_code == http_status.HTTP_200_OK
        token = response.json()['access_token']

    with freeze_time('2025-06-01 12:31:00'):
        response = client.post(
            '/auth/refresh-token',
            headers={'Authorization': f'Bearer {token}'},
        )
        assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Could not validate credentials'}
