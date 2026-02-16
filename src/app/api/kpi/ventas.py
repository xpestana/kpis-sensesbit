from fastapi import APIRouter

router = APIRouter(tags=["kpi-ventas"])


@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para Ventas."""
    return {"message": "estoy en Ventas"}
