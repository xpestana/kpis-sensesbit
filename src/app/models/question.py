from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Question(SQLModel, table=True):
    __tablename__ = "question"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    section_id: UUID = Field(foreign_key="section.id", index=True)
    type: str | None = Field(max_length=50)
