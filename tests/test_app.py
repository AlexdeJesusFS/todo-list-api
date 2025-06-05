from fastapi import status as http_status


def test_root_should_return_ok_and_HelloWord(client):
    response = client.get('/')  # Act (ação)

    assert response.status_code == http_status.HTTP_200_OK  # Assert (afirmar)
    assert response.json() == {'message': 'Hello World!'}


def test_html_should_return_ok_and_HTML(client):
    response = client.get('html')

    assert response.status_code == http_status.HTTP_200_OK
    assert '<h1>Hello World!</h1>' in response.text
