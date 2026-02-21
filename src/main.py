from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.kpi import producto_router
from app.core.auth import verify_bearer_token
from app.core.config import settings
from app.core.database import init_global_schema

app = FastAPI(
    title="KPIs API",
    version="0.1.0",
    redirect_slashes=False,
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/doc",
    on_startup=[init_global_schema],
)

origins = [o.strip() for o in settings.ORIGIN_HOSTS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas KPI: exigen header Authorization: Bearer <TOKEN_GRAFANA>
bearer_dep = [Depends(verify_bearer_token)]
app.include_router(
    producto_router, prefix="/kpi/Producto", tags=["kpi-producto"], dependencies=bearer_dep
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
