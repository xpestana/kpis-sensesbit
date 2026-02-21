from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class File(SQLModel, table=True):
    __tablename__ = "file"

    id: UUID = Field(primary_key=True, default_factory=uuid4)
    created: datetime = Field(default_factory=datetime.now)
    name: str | None = Field(max_length=255)
    # Tipo o extensión para distinguir PDF/Excel (ej. "pdf", "xlsx")
    file_type: str | None = Field(max_length=20, default=None)
