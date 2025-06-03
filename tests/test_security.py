from fastapi import status as http_status
from jwt import decode

from src.security import SECRET_KEY, create_access_token


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(token, SECRET_KEY, algorithms=['HS256'])

    assert decoded['test'] == data['test']
    assert 'exp' in decoded


def test_get_current_user_UNAUTHORIZED(client):
    # invalid token DecodeError
    response_invalid_token = client.delete(
        '/user/0',
        headers={'Authorization': 'Bearer invalid-token'},
    )

    # token without sub
    token = create_access_token({'without-sub': 'None'})
    response_without_sub = client.delete(
        '/user/0',
        headers={'Authorization': f'Bearer {token}'},
    )

    # token noneexistent user
    token = create_access_token({'sub': 'noneexistent@mail.com'})
    response_noneexistent_user = client.delete(
        '/user/0',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert (
        response_invalid_token.status_code
        == response_without_sub.status_code
        == response_noneexistent_user.status_code
        == http_status.HTTP_401_UNAUTHORIZED
    )
    assert (
        response_invalid_token.headers.get('www-Authenticate')
        == response_without_sub.headers.get('www-Authenticate')
        == response_noneexistent_user.headers.get('www-Authenticate')
        == 'Bearer'
    )
    assert (
        response_invalid_token.json()
        == response_without_sub.json()
        == response_noneexistent_user.json()
        == {'detail': 'Could not validate credentials'}
    )
