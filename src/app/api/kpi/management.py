from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from app.core.database import engine
from app.models.user import User

router = APIRouter(tags=["kpi-management"])

# TODO: Reemplazar con lógica multitenant real
HARDCODED_ORG_SCHEMA = "org_n74hvy7njcmb"


def get_db_session() -> Session:
    """Obtiene sesión de base de datos sin autenticación (hardcoded a un schema)."""
    db = Session(
        engine.execution_options(schema_translate_map={None: HARDCODED_ORG_SCHEMA})
    )
    try:
        yield db
    finally:
        db.close()


@router.get("/test")
async def test_endpoint():
    """Test endpoint for Management."""
    return {"message": "estoy en Management"}


@router.get("/all-users-active-total")
async def all_users_active_total(
    db: Session = Depends(get_db_session),
):
    """
    KPI 1 — All Users Active Total

    Definition: Total number of users registered in the system.
    Source: user
    Strategic level: Current size of installed base.
    """
    query = select(func.count(User.id)).where(User.deleted.is_(None))
    result = db.exec(query).one()

    return {
        "kpi": "All Users Active Total",
        "valor": result,
        "descripcion": "Total number of users registered in the system",
    }
