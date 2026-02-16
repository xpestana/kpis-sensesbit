from fastapi import APIRouter

router = APIRouter(tags=["kpi-marketing"])


@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para Marketing."""
    return {"message": "estoy en Marketing"}
