from datetime import datetime
from typing import TypedDict

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class TagDict(TypedDict):
    id: int | None
    title: str
    description: str | None
    text_color: str
    background_color: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    owner_id: int | None


class Tag(SQLModel, table=True):
    __tablename__ = 'tags'

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False, max_length=50, unique=True)
    description: str | None = Field(max_length=255)
    text_color: str = Field(max_length=7, default='#FFFFFF')
    background_color: str = Field(max_length=7, default='#000000')
    created_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.now(),
            nullable=False,
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )
    is_active: bool = Field(index=True, default=True)
    owner_id: int | None = Field(foreign_key='users.id')

    def to_dict(
        self,
    ) -> dict[str, TagDict]:
        return self.model_dump()
