# mypy: disable-error-code="no-untyped-def"

from fastapi import FastAPI, HTTPException
from fastapi import status as http_status
from fastapi.responses import HTMLResponse

from src.schemas import user as user_schemas

app = FastAPI()


@app.get('/')
def root() -> dict[str, str]:
    return {'message': 'Hello World!'}


@app.get('/html', response_class=HTMLResponse)
def html() -> str:
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
    </head>
    <body>
        <h1>Hello World!</h1>
    </body>
    </html>
    """


# user routers:
database = []  # type: ignore  # ignora o erro "var-annotated"


@app.post(
    '/users/',
    status_code=http_status.HTTP_201_CREATED,
    response_model=user_schemas.UserResponse,
)
def create_user(user: user_schemas.UserInput):
    user_with_id = user_schemas.UserDB(
        **user.model_dump(), id=len(database) + 1
    )

    database.append(user_with_id)

    return user_with_id


@app.get(
    '/user/{user_id}',
    status_code=http_status.HTTP_200_OK,
    response_model=user_schemas.UserResponse,
)
def get_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]


@app.get('/users/', response_model=user_schemas.ListUserResponse)
def get_users():
    return {'users': database}


@app.put('/users/{user_id}', response_model=user_schemas.UserResponse)
def update_user(user_id: int, user: user_schemas.UserInput):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    user_with_id = user_schemas.UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id

    return user_with_id


@app.delete('/users/{user_id}', response_model=user_schemas.Message)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]

    return {'message': f'User {user_id} deleted'}
