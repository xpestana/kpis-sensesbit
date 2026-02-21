from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Section(SQLModel, table=True):
    __tablename__ = "section"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    session_id: UUID = Field(foreign_key="session.id", index=True)
    repeated_by_sample: bool = Field(default=False)
