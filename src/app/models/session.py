from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Session(SQLModel, table=True):
    __tablename__ = "session"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    code: str | None = Field(index=True, max_length=100)
    created: datetime = Field(default_factory=datetime.now)
    end_at: datetime | None = Field(default=None)
