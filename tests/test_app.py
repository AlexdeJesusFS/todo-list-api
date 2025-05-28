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
    user_json = user.model_dump(mode='json', exclude='password')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {'users': [user_json]}


def test_get_user_should_return_OK(client, user):
    response = client.get('/user/1')

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


def test_update_user_should_return_OK(client, user):
    response = client.put(
        '/user/1',
        json={
            'username': 'lexus',
            'email': 'lexus@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'username': 'lexus',
        'email': 'lexus@mail.com',
        'created_at': '2025-01-01T00:00:00',
        'updated_at': '2025-02-02T00:00:00',
    }


def test_update_user_should_return_NOT_FOUND(client, user):
    response = client.put(
        '/user/0',
        json={
            'username': 'lexus',
            'email': 'lexus@mail.com',
            'password': 'n&wp@ssword',
        },
    )
    assert response.status_code == http_status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user_integrity_error(client, user):
    response_username = client.put(
        '/user/1',
        json={
            'username': 'Tester',
            'email': 'tester@test.com',
            'password': 'Test@0',
        },
    )
    response_email = client.put(
        '/user/1',
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


def test_delete_user_should_return_OK(client, user):
    response = client.delete('/user/1')

    assert response.status_code == http_status.HTTP_200_OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_user_should_return_NOT_FOUND(client, user):
    response = client.delete('/user/0')

    assert response.status_code == http_status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
