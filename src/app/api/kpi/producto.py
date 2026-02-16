from fastapi import APIRouter

router = APIRouter(tags=["kpi-producto"])


@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para Producto."""
    return {"message": "estoy en Producto"}
