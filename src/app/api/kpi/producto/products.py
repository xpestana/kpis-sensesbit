"KPI Producto"

from datetime import datetime, timezone

import requests
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_db_session
from app.services.product_services.producto_service import ProductoService

router = APIRouter(tags=["kpi-producto"])

TIMEOUT = 15


def get_service(db: Session = Depends(get_db_session)) -> ProductoService:
    return ProductoService(db)


@router.get("/test")
async def test_endpoint():
    """Test endpoint: localhost:8000/kpi/Producto/test"""
    return {"message": "KPI Producto"}


@router.get("/test-logto", response_model=None)
async def test_logto():
    """GET a la raíz de LOGTO_API_BASE para ver qué devuelve (sin oidc/token)."""
    base = settings.LOGTO_API_BASE.rstrip("/")
    url = f"{base}/"
    try:
        r = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
        return {
            "url": url,
            "status_code": r.status_code,
            "content_type": r.headers.get("Content-Type", ""),
            "body": r.text[:4000] if r.text else "(vacío)",
        }
    except requests.RequestException as e:
        return {"url": url, "error": str(e)}


########################################################
# KPI : Calidad y performance
########################################################


# Tiempo de respuesta de API
@router.get("/response-time", response_model=None)
async def response_time():
    from datetime import timedelta
    from app.core.response_time_monitor import _history

    now = datetime.now(timezone.utc)

    history_map = {e["hour"]: e for e in _history}

    result = {}
    for i in range(9, -1, -1):
        slot_dt = now - timedelta(hours=i)
        hour_key = slot_dt.strftime("%Y-%m-%dT%H")
        label = slot_dt.strftime("%d/%m/%Y %H:00 UTC")

        if hour_key in history_map:
            samples = history_map[hour_key].get("samples", [])
            avg = round(sum(samples) / len(samples), 4) if samples else 0
        else:
            avg = 0

        result[label] = avg

    return result


########################################################
# KPI : Uso e IA
########################################################

# Sesiones creadas por fecha
@router.get("/sesiones-creadas", response_model=None)
async def sesiones_creadas(
    from_ms: int | None = Query(default=None, alias="from"),
    to_ms: int | None = Query(default=None, alias="to"),
    service: ProductoService = Depends(get_service),
):
    today = datetime.now(tz=timezone.utc).date()
    date_from = datetime.fromtimestamp(from_ms / 1000, tz=timezone.utc) if from_ms is not None else datetime(today.year, today.month, today.day, 0, 0, 0, tzinfo=timezone.utc)
    date_to = datetime.fromtimestamp(to_ms / 1000, tz=timezone.utc) if to_ms is not None else datetime(today.year, today.month, today.day, 23, 59, 59, tzinfo=timezone.utc)
    return service.sesiones_creadas_por_fecha(date_from=date_from, date_to=date_to)

#falta dau
#falta mau

# Análisis IA ejecutados + por tipo (DualSense, JAR, Ranking, Verbatim, Drivers)
@router.get("/analisis-ia-ejecutados", response_model=None)
async def analisis_ia_ejecutados(service: ProductoService = Depends(get_service)):
    return service.analisis_ia_ejecutados()


# Consumo de Créditos IA — totales y por plan — shared.organizations
@router.get("/consumo-credits-ia", response_model=None)
async def consumo_credits_ia(service: ProductoService = Depends(get_service)):
    return service.consumo_credits_ia()

# Consumo de Muestras (Credits) — totales y por plan — shared.organizations
@router.get("/consumo-muestras", response_model=None)
async def consumo_muestras(service: ProductoService = Depends(get_service)):
    return service.consumo_muestras()

# Tiempo medio de procesamiento IA por tipo de análisis (segundos/minutos)
@router.get("/tiempo-procesamiento-ia", response_model=None)
async def tiempo_procesamiento_ia(service: ProductoService = Depends(get_service)):
    return service.tiempo_procesamiento_ia()


########################################################
# KPI : Adopción y Features
########################################################


@router.get("/frecuencia-uso", response_model=None)
async def frecuencia_uso(service: ProductoService = Depends(get_service)):
    "frequency of use = sessions per active user. localhost:8000/kpi/Producto/frecuencia-uso"
    return {"kpi": "Frecuencia de Uso", "datos": service.frecuencia_uso()}


# % clientes (sesiones) que utilizan análisis IA
@router.get("/adopcion-funcionalidades-ia", response_model=None)
async def adopcion_funcionalidades_ia(service: ProductoService = Depends(get_service)):
    return service.adopcion_funcionalidades_ia()


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
