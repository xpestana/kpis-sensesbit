from app.api.kpi.customer_success import router as customer_success_router
from app.api.kpi.management import router as management_router
from app.api.kpi.marketing import router as marketing_router
from app.api.kpi.producto import router as producto_router
from app.api.kpi.test import router as test_router
from app.api.kpi.ventas import router as ventas_router

__all__ = [
    "management_router",
    "producto_router",
    "marketing_router",
    "ventas_router",
    "customer_success_router",
    "test_router",
]
