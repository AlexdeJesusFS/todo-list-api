from datetime import datetime
from typing import TYPE_CHECKING, TypedDict

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

from src.models.task import Task

if TYPE_CHECKING:
    from .task import Task


class UserRequest(SQLModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(SQLModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime
    tasks: list[Task]


class ListUserResponse(SQLModel):
    users: list[UserResponse]


class Message(SQLModel):
    message: str


class UserDict(TypedDict):
    id: int | None
    username: str
    email: str
    password: str
    created_at: datetime
    updated_at: datetime
    tasks: list[Task]


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        index=True, max_length=50, nullable=False, unique=True
    )
    email: EmailStr = Field(index=True, nullable=False, unique=True)
    password: str = Field(nullable=False, max_length=128)

    created_at: datetime = Field(
        sa_column=Column(DateTime, server_default=func.now(), nullable=False)
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )

    tasks: list['Task'] = Relationship(
        back_populates='user',
        sa_relationship_kwargs={
            'cascade': 'all, delete-orphan',
            'lazy': 'selectin',
        },
    )

    def to_dict(
        self,
    ) -> UserDict:
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'password': self.password,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'tasks': self.tasks,
        }
