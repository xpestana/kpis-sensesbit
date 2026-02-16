from fastapi import APIRouter, Query

from app.core.hubspot_client import fetch_all_bi_data

router = APIRouter(tags=["kpi-test"])


@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para Test."""
    return {"message": "estoy en Test"}


@router.get("/hubspot")
async def hubspot_data(
    limit: int = Query(default=50, ge=1, le=100, description="Límite por objeto CRM"),
):
    """
    Obtiene datos de HubSpot para BI/KPIs: contacts, companies, deals,
    line_items, leads, owners, schemas, pipelines, campaigns (con metrics y revenue).
    Requiere Private App con los scopes CRM y Marketing configurados.
    """
    return fetch_all_bi_data(limit=limit)
