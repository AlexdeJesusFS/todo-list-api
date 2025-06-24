from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, TypedDict

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from src.models.tag import Tag
    from src.models.user import User


class TaskTagLink(SQLModel, table=True):
    __tablename__ = 'task_tags'

    task_id: int = Field(foreign_key='tasks.id', primary_key=True)
    tag_id: int = Field(foreign_key='tags.id', primary_key=True)


class TaskStatus(str, Enum):
    draft = 'draft'
    todo = 'todo'
    doing = 'doing'
    done = 'done'
    trash = 'trash'


class TaskRequest(SQLModel):
    title: str
    description: str | None = None
    status: TaskStatus
    due: datetime | None = None
    completed_at: datetime | None = None
    parent_id: int | None = None
    tags: list['Tag'] = []


class TaskDict(TypedDict):
    id: int | None
    title: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime
    due: datetime | None
    completed_at: datetime | None
    parent_id: int | None
    children: list['Task']
    tags: list['Tag']
    user_id: int


class Task(SQLModel, table=True):
    __tablename__ = 'tasks'

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False, max_length=100)
    description: str | None = Field(max_length=1000)
    status: TaskStatus = Field(index=True)
    created_at: datetime = Field(
        sa_column=Column(DateTime, server_default=func.now(), nullable=False),
    )
    updated_at: datetime = Field(
        sa_column=Column(
            DateTime,
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
    )
    due: datetime | None = Field(index=True, default=None)
    completed_at: datetime | None = Field(index=True, default=None)
    parent_id: int | None = Field(foreign_key='tasks.id', index=True)

    parent: Optional['Task'] = Relationship(
        back_populates='children',
        sa_relationship_kwargs={
            'remote_side': 'Task.id',
            'lazy': 'selectin',
        },
    )
    children: list['Task'] = Relationship(
        back_populates='parent',
        sa_relationship_kwargs={
            'cascade': 'all, delete-orphan',
            'lazy': 'selectin',
        },
    )

    user_id: int = Field(foreign_key='users.id', nullable=False)
    user: Optional['User'] = Relationship(
        back_populates='tasks',
        sa_relationship_kwargs={
            'lazy': 'selectin',
        },
    )
    tags: list['Tag'] = Relationship(
        link_model=TaskTagLink,
        sa_relationship_kwargs={
            'cascade': 'all',
            'lazy': 'selectin',
        },
    )

    def to_dict(
        self,
    ) -> TaskDict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'due': self.due,
            'completed_at': self.completed_at,
            'parent_id': self.parent_id,
            'children': self.children,
            'tags': self.tags,
            'user_id': self.user_id,
        }
