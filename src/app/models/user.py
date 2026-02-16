from datetime import datetime
from enum import IntEnum
from uuid import UUID, uuid4

from sqlalchemy import Integer
from sqlmodel import Field, SQLModel


class UserRole(IntEnum):
    ADMIN = 1
    USER = 2


class User(SQLModel, table=True):
    id: UUID = Field(primary_key=True, default_factory=uuid4)
    name: str | None = Field(index=True, max_length=100)
    email: str | None = Field(index=True, max_length=100, unique=True)
    role: int = Field(default=UserRole.USER, sa_type=Integer)

    created: datetime = Field(default_factory=datetime.now)
    updated: datetime = Field(
        default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}
    )
    deleted: datetime | None = Field(default=None)
