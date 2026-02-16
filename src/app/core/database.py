from sqlalchemy import Engine, create_engine
from sqlmodel import SQLModel

from app.core.config import settings
from app.models.organization import OrganizationBase

engine: Engine = create_engine(
    settings.POSTGRES_URL, pool_size=20, max_overflow=20, pool_timeout=30
)


def init_global_schema() -> None:
    """Crea el schema global y las tablas (organizations)."""
    from sqlalchemy import Connection, text
    from sqlalchemy.schema import CreateSchema

    global_schema = settings.GLOBAL_SCHEMA
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"
            ),
            {"schema": global_schema},
        ).fetchone()
        if result is None:
            conn.execute(CreateSchema(global_schema, if_not_exists=True))
            conn.commit()
        OrganizationBase.metadata.create_all(engine)
