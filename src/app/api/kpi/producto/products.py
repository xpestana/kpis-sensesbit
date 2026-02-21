"KPI Producto"

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.core.database import get_db_session
from app.services.product_services.producto_service import ProductoService

router = APIRouter(tags=["kpi-producto"])


def get_service(db: Session = Depends(get_db_session)) -> ProductoService:
    return ProductoService(db)


@router.get("/test")
async def test_endpoint():
    """Test endpoint: localhost:8000/kpi/Producto/test"""
    return {"message": "KPI Producto"}


@router.get("/sesiones-creadas", response_model=None)
async def sesiones_creadas(service: ProductoService = Depends(get_service)):
    "sessions created by date. localhost:8000/kpi/Producto/sesiones-creadas"
    return {"kpi": "Sesiones Creadas", "datos": service.sesiones_creadas_por_fecha()}


@router.get("/dau", response_model=None)
async def usuarios_activos_diarios(service: ProductoService = Depends(get_service)):
    "daily active users. localhost:8000/kpi/Producto/dau"
    return {"kpi": "DAU", "datos": service.dau()}


@router.get("/mau", response_model=None)
async def usuarios_activos_mensuales(service: ProductoService = Depends(get_service)):
    "monthly active users. localhost:8000/kpi/Producto/mau"
    return {"kpi": "MAU", "datos": service.mau()}


@router.get("/frecuencia-uso", response_model=None)
async def frecuencia_uso(service: ProductoService = Depends(get_service)):
    "frequency of use = sessions per active user. localhost:8000/kpi/Producto/frecuencia-uso"
    return {"kpi": "Frecuencia de Uso", "datos": service.frecuencia_uso()}


@router.get("/exportaciones-generadas", response_model=None)
async def exportaciones_generadas(service: ProductoService = Depends(get_service)):
    "generated exports (PDF and Excel) by file. localhost:8000/kpi/Producto/exportaciones-generadas"
    return {"kpi": "Exportaciones Generadas", "datos": service.exportaciones_generadas()}


@router.get("/porcentaje-usuarios-duplican-sesiones", response_model=None)
async def porcentaje_usuarios_duplican_sesiones(service: ProductoService = Depends(get_service)):
    "% users that duplicate sessions (>= 2 sessions via session->section->question->answer). localhost:8000/kpi/Producto/porcentaje-usuarios-duplican-sesiones"
    return {"kpi": "% usuarios que duplican sesiones", "datos": service.porcentaje_usuarios_duplican_sesiones()}


@router.get("/duracion-media-sesion", response_model=None)
async def duracion_media_sesion(service: ProductoService = Depends(get_service)):
    "average session duration (only sessions with session.end_at). localhost:8000/kpi/Producto/duracion-media-sesion"
    return {"kpi": "Duración media de sesión", "datos": service.duracion_media_sesion()}
