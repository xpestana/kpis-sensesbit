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


########################################################
# KPI : Calidad y performance
########################################################


# Tiempo de respuesta de API
@router.get("/response-time", response_model=None)
async def response_time():
    from app.core.response_time_monitor import get_state
    return {"kpi": "Response time (api.sensesbit.com/health)", "datos": get_state()}


########################################################
# KPI : Uso e IA
########################################################

# Sesiones creadas por fecha
@router.get("/sesiones-creadas", response_model=None)
async def sesiones_creadas(service: ProductoService = Depends(get_service)):
    return {"kpi": "Sesiones Creadas", "datos": service.sesiones_creadas_por_fecha()}


# Usuarios activos diarios (Logto Management API)
@router.get("/dau", response_model=None)
async def usuarios_activos_diarios(
    service: ProductoService = Depends(get_service),
    date: str | None = None,
):
    """DAU desde Logto GET /api/dashboard/users/active. Opcional: ?date=YYYY-MM-DD."""
    return {"kpi": "DAU", "datos": service.dau(fecha=date)}


# Usuarios activos mensuales (Logto Management API)
@router.get("/mau", response_model=None)
async def usuarios_activos_mensuales(
    service: ProductoService = Depends(get_service),
    date: str | None = None,
):
    """MAU desde Logto GET /api/dashboard/users/active. Opcional: ?date=YYYY-MM-DD."""
    return {"kpi": "MAU", "datos": service.mau(fecha=date)}


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
