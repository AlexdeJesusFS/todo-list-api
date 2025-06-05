from fastapi import status as http_status


def test_get_token(client, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user['user'].email,
            'password': user['clean_password'],
        },
    )
    token = response.json()

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
