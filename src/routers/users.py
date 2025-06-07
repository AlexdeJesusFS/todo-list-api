# mypy: disable-error-code="no-untyped-def"

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi import status as http_status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import or_, select

from src.database import get_session
from src.models import user as user_models
from src.models.pagination import FilterPage
from src.security import (
    get_current_user,
    get_password_hash,
)

router = APIRouter(prefix='/users', tags=['users'])

SessionDep = Annotated[AsyncSession, Depends(get_session)]
CurrentUserDep = Annotated[user_models.User, Depends(get_current_user)]


@router.post(
    '/',
    status_code=http_status.HTTP_201_CREATED,
    response_model=user_models.UserResponse,
)
async def create_user(user: user_models.UserInput, session: SessionDep):
    db_user = await session.scalar(
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

    hashed_password = get_password_hash(user.password)
    user_dict = user.model_dump()
    user_dict['password'] = hashed_password

    db_user = user_models.User(**user_dict)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user


@router.get(
    '/{user_id}',
    status_code=http_status.HTTP_200_OK,
    response_model=user_models.UserResponse,
)
async def get_one_user(user_id: int, session: SessionDep):
    db_user = await session.scalar(
        select(user_models.User).where(user_models.User.id == user_id)
    )
    if not db_user:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    return db_user


@router.get('/', response_model=user_models.ListUserResponse)
async def get_users_list(
    session: SessionDep, filter_users: Annotated[FilterPage, Query()]
):
    query = await session.scalars(
        select(user_models.User)
        .offset(filter_users.offset)
        .limit(filter_users.limit)
    )
    users = query.all()

    return {'users': users}


@router.put('/{user_id}', response_model=user_models.UserResponse)
async def update_user(
    user_id: int,
    user: user_models.UserInput,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )

    for key, value in user.model_dump().items():
        setattr(current_user, key, value)

    current_user.password = get_password_hash(user.password)

    try:
        session.add(current_user)
        await session.commit()
        await session.refresh(current_user)

        return current_user
    except IntegrityError as err:
        await session.rollback()
        if 'username' in err._message():
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail='username already exists',
            )
        else:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail='email already exists',
            )


@router.delete('/{user_id}', response_model=user_models.Message)
async def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail='Not enough permissions',
        )

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
