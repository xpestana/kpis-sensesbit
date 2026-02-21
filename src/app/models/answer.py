from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Answer(SQLModel, table=True):
    __tablename__ = "answer"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
    user_id: UUID = Field(foreign_key="user.id", index=True)
    question_id: UUID = Field(foreign_key="question.id", index=True)
