from datetime import datetime

from pydantic import EmailStr
from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class UserInput(SQLModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(SQLModel):
    id: int
    username: str
    email: EmailStr


class ListUserResponse(SQLModel):
    users: list[UserResponse]


class Message(SQLModel):
    message: str


# DB Class
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
