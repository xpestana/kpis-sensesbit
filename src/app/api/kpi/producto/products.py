"""Products KPI: endpoints delegados al servicio."""

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_db_session
from app.services.product_services.producto_service import ProductoService

router = APIRouter(tags=["kpi-producto"])


def get_service(db: Session = Depends(get_db_session)) -> ProductoService:
    return ProductoService(db)


@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para Producto."""
    return {"message": "estoy en Producto"}


@router.get("/sesiones-creadas", response_model=None)
async def sesiones_creadas(service: ProductoService = Depends(get_service)):
    """KPI 4: Sesiones creadas por fecha (count por fecha en session.created)."""
    return {"kpi": "Sesiones Creadas", "datos": service.sesiones_creadas_por_fecha()}


@router.get("/dau", response_model=None)
async def usuarios_activos_diarios(service: ProductoService = Depends(get_service)):
    """KPI 5: Usuarios activos diarios (DAU) — por answer.created (si respondió está activo)."""
    return {"kpi": "DAU", "datos": service.dau()}


@router.get("/mau", response_model=None)
async def usuarios_activos_mensuales(service: ProductoService = Depends(get_service)):
    """KPI 6: Usuarios activos mensuales (MAU) — por answer.created por mes."""
    return {"kpi": "MAU", "datos": service.mau()}


@router.get("/frecuencia-uso", response_model=None)
async def frecuencia_uso(service: ProductoService = Depends(get_service)):
    """KPI 11: Frecuencia de uso = media de sesiones por cliente activo (por tenant)."""
    return {"kpi": "Frecuencia de Uso", "datos": service.frecuencia_uso()}


@router.get("/exportaciones-generadas", response_model=None)
async def exportaciones_generadas(service: ProductoService = Depends(get_service)):
    """KPI 16: Exportaciones generadas (PDF y Excel) — por file."""
    return {"kpi": "Exportaciones Generadas", "datos": service.exportaciones_generadas()}


@router.get("/porcentaje-usuarios-duplican-sesiones", response_model=None)
async def porcentaje_usuarios_duplican_sesiones(service: ProductoService = Depends(get_service)):
    """KPI 18: % usuarios que duplican sesiones (>= 2 sesiones vía session->section->question->answer)."""
    return {"kpi": "% usuarios que duplican sesiones", "datos": service.porcentaje_usuarios_duplican_sesiones()}


@router.get("/duracion-media-sesion", response_model=None)
async def duracion_media_sesion(service: ProductoService = Depends(get_service)):
    """KPI 19: Duración media de sesión (solo sesiones con session.end_at)."""
    return {"kpi": "Duración media de sesión", "datos": service.duracion_media_sesion()}
