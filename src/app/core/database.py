from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlmodel import Session as SessionDB
from sqlmodel import SQLModel

from app.core.config import settings
from app.models.organization import OrganizationBase

# Primera organización: todos los endpoints usan este schema (hardcoded por ahora)
FIRST_ORG_SCHEMA = "org_n74hvy7njcmb"

engine: Engine = create_engine(
    settings.POSTGRES_URL, pool_size=20, max_overflow=20, pool_timeout=30
)


def get_db_session() -> Generator[SessionDB, None, None]:
    """Sesión de BD sobre la primera organización (hardcoded). Todos los KPIs usan este tenant."""
    db = SessionDB(
        engine.execution_options(schema_translate_map={None: FIRST_ORG_SCHEMA})
    )
    try:
        yield db
    finally:
        db.close()


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
