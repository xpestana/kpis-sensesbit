from fastapi import APIRouter

router = APIRouter(tags=["kpi-customer-success"])


@router.get("/test")
async def test_endpoint():
    """Endpoint de prueba para CustomerSuccess."""
    return {"message": "estoy en CustomerSuccess"}
