# mypy: disable-error-code="no-untyped-def"

from fastapi import Depends, FastAPI, HTTPException
from fastapi import status as http_status
from fastapi.responses import HTMLResponse
from sqlmodel import Session, or_, select

from src.database import get_session
from src.models import user as user_models

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
@app.post(
    '/user/',
    status_code=http_status.HTTP_201_CREATED,
    response_model=user_models.UserResponse,
)
def create_user(
    user: user_models.UserInput, session: Session = Depends(get_session)
):
    db_user = session.scalar(
        select(user_models.User).where(
            or_(
                user_models.User.username == user.username,
                user_models.User.email == user.email,
            )
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail='username already exists',
            )
        else:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail='email already exists',
            )

    db_user = user_models.User(**user.model_dump())
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.get(
    '/user/{user_id}',
    status_code=http_status.HTTP_200_OK,
    response_model=user_models.UserResponse,
)
def get_one_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(user_models.User).where(user_models.User.id == user_id)
    )
    if not db_user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    return db_user


@app.get('/users/', response_model=user_models.ListUserResponse)
def get_users(
    skip: int = 0, limit: int = 100, session: Session = Depends(get_session)
):
    users = session.exec(
        select(user_models.User).offset(skip).limit(limit)
    ).all()

    return {'users': users}


@app.put('/user/{user_id}', response_model=user_models.UserResponse)
def update_user(
    user_id: int,
    user: user_models.UserInput,
    session: Session = Depends(get_session),
):
    db_user = session.scalar(
        select(user_models.User).where(
            or_(
                user_models.User.username == user.username,
                user_models.User.email == user.email,
            )
        )
    )
    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail='username already exists',
            )
        else:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail='email already exists',
            )

    db_user = session.scalar(
        select(user_models.User).where(user_models.User.id == user_id)
    )
    if not db_user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail='User not found',
        )

    for key, value in user.model_dump().items():
        setattr(db_user, key, value)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@app.delete('/user/{user_id}', response_model=user_models.Message)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.scalar(
        select(user_models.User).where(user_models.User.id == user_id)
    )
    if not db_user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    session.delete(db_user)
    session.commit()

    return {'message': 'User deleted'}
