from fastapi import status as http_status

# TODO: test para get_users_list com offset e limit


def test_create_user(client):
    response = client.post(
        '/users/',
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
    _user = user['user']

    response_username = client.post(
        '/users/',
        json={
            'username': _user.username,
            'email': 'tester@test.com',
            'password': 'Test@0',
        },
    )
    response_email = client.post(
        '/users/',
        json={
            'username': 'Tester0',
            'email': _user.email,
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
    _user = user['user']
    response = client.get(f'/users/{user["user"].id}')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {
        'id': _user.id,
        'username': _user.username,
        'email': _user.email,
        'created_at': '2025-01-01T00:00:00',
        'updated_at': '2025-01-01T00:00:00',
    }


def test_get_user_should_return_NOT_FOUND(client, user):
    response = client.get('/users/0')

    assert response.status_code == http_status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_should_return_OK(client, user, token):
    user_id = user['user'].id
    response = client.put(
        f'/users/{user_id}',
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
        f'/users/{user_id}',
        json={
            'username': 'lele',
            'email': 'lele@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_update_user_should_return_FORBIDDEN(client, other_user, token):
    _other_user = other_user['user']

    response = client.put(
        f'/users/{_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'lele',
            'email': 'lele@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_integrity_error_username(client, user, other_user, token):
    _user = user['user']
    _other_user = other_user['user']

    response = client.put(
        f'/users/{_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': _other_user.username,
            'email': 'tester@test.com',
            'password': 'Test@0',
        },
    )
    assert response.status_code == http_status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'username already exists'}


def test_update_user_integrity_error_email(client, user, other_user, token):
    _user = user['user']
    _other_user = other_user['user']

    response = client.put(
        f'/users/{_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'Tester',
            'email': _other_user.email,
            'password': 'Test@0',
        },
    )
    assert response.status_code == http_status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'email already exists'}


def test_delete_user_should_return_OK(client, user, token):
    user_id = user['user'].id

    response = client.delete(
        f'/users/{user_id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_should_return_UNAUTHORIZED(client, user):
    response = client.delete('/users/0')

    assert response.status_code == http_status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Not authenticated'}


def test_delete_user_should_return_FORBIDDEN(client, other_user, token):
    _other_user = other_user['user']

    response = client.delete(
        f'/users/{_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == http_status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}
