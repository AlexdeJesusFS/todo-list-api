from fastapi import status as http_status


def test_root_should_return_ok_and_HelloWord(client):
    response = client.get('/')  # Act (ação)

    assert response.status_code == http_status.HTTP_200_OK  # Assert (afirmar)
    assert response.json() == {'message': 'Hello World!'}


def test_html_should_return_ok_and_HTML(client):
    response = client.get('html')

    assert response.status_code == http_status.HTTP_200_OK
    assert '<h1>Hello World!</h1>' in response.text


def test_create_user(client):
    response = client.post(
        '/user/',
        json={'username': 'lex', 'email': 'lex@dev.com', 'password': 'secr&t'},
    )

    assert response.status_code == http_status.HTTP_201_CREATED
    assert response.json() == {
        'id': 1,
        'username': 'lex',
        'email': 'lex@dev.com',
        'created_at': '2025-01-01T00:00:00',
        'updated_at': '2025-01-01T00:00:00',
    }


def test_create_user_integrity_error(client, user):
    response_username = client.post(
        '/user/',
        json={
            'username': 'Tester',
            'email': 'tester@test.com',
            'password': 'Test@0',
        },
    )
    response_email = client.post(
        '/user/',
        json={
            'username': 'Tester0',
            'email': 'tester@test.com',
            'password': 'Test@0',
        },
    )

    assert (
        response_username.status_code
        == response_email.status_code
        == http_status.HTTP_409_CONFLICT
    )
    assert response_username.json() == {'detail': 'username already exists'}
    assert response_email.json() == {'detail': 'email already exists'}


def test_get_user_list_empty(client):
    response = client.get('/users/')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {'users': []}


def test_get_user_list_with_users(client, user):
    response = client.get('/users/')
    user_json = user['user'].model_dump(mode='json', exclude='password')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {'users': [user_json]}


def test_get_user_should_return_OK(client, user):
    response = client.get(f'/user/{user["user"].id}')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'username': 'Tester',
        'email': 'tester@test.com',
        'created_at': '2025-01-01T00:00:00',
        'updated_at': '2025-01-01T00:00:00',
    }


def test_get_user_should_return_NOT_FOUND(client, user):
    response = client.get('/user/0')

    assert response.status_code == http_status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_should_return_OK(client, user, token):
    user_id = user['user'].id
    response = client.put(
        f'/user/{user_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'lele',
            'email': 'lele@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {
        'id': user_id,
        'username': 'lele',
        'email': 'lele@mail.com',
        'created_at': '2025-01-01T00:00:00',
        'updated_at': '2025-02-02T00:00:00',
    }


def test_update_user_should_return_UNAUTHORIZED(client, user):
    user_id = user['user'].id
    response = client.put(
        f'/user/{user_id}',
        json={
            'username': 'lele',
            'email': 'lele@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_user_should_return_FORBIDDEN(client, user, token):
    response = client.put(
        '/user/0',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'lele',
            'email': 'lele@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_integrity_error(client, user, token):
    client.post(
        '/user/',
        json={
            'username': 'lele',
            'email': 'lele@mail.com',
            'password': 'pass',
        },
    )

    user_id = user['user'].id

    response_username = client.put(
        f'/user/{user_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'lele',
            'email': 'tester@test.com',
            'password': 'Test@0',
        },
    )
    response_email = client.put(
        f'/user/{user_id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Tester',
            'email': 'lele@mail.com',
            'password': 'Test@0',
        },
    )

    assert (
        response_username.status_code
        == response_email.status_code
        == http_status.HTTP_409_CONFLICT
    )
    assert response_username.json() == {'detail': 'username already exists'}
    assert response_email.json() == {'detail': 'email already exists'}


def test_delete_user_should_return_OK(client, user, token):
    user_id = user['user'].id

    response = client.delete(
        f'/user/{user_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_should_return_UNAUTHORIZED(client, user):
    response = client.delete('/user/0')

    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_delete_user_should_return_FORBIDDEN(client, user, token):
    response = client.delete(
        '/user/0',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == http_status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_token(client, user):
    response = client.post(
        '/token',
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
        '/token',
        data={'username': 'lele@mail.com', 'password': 'pass123'},
    )

    # incorrect password
    response_incorrect = client.post(
        '/token',
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
