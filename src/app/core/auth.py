"""Validación de Bearer token (TOKEN_GRAFANA) en header Authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

security = HTTPBearer(auto_error=False)


def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> None:
    """
    Exige que la petición traiga header Authorization: Bearer <TOKEN_GRAFANA>.
    Si TOKEN_GRAFANA está vacío en .env, no se exige token (desarrollo).
    """
    if not settings.TOKEN_GRAFANA:
        return
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta header Authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if credentials.credentials != settings.TOKEN_GRAFANA:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
