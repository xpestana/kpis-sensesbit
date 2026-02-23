"""
Cliente para la API de gestión de Logto.
Solo consumo de GET /api/dashboard/users/active (DAU, MAU, WAU, dauCurve).
Ver: https://openapi.logto.io/operation/operation-getactiveusercounts
"""

from typing import Any

import requests

from app.core.config import settings

TIMEOUT = 15


def get_active_users(date: str) -> dict[str, Any]:
    """
    GET active user data (DAU, WAU, MAU, dauCurve).
    date: YYYY-MM-DD.
    Requiere LOGTO_ACCESS_TOKEN (Bearer) en config.
    """
    base = settings.LOGTO_API_BASE.rstrip("/")
    url = f"{base}/api/dashboard/users/active"
    headers = {"Authorization": f"Bearer {settings.LOGTO_ACCESS_TOKEN}"}
    params = {"date": date}
    try:
        r = requests.get(url, headers=headers, params=params, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        status = getattr(getattr(e, "response", None), "status_code", None)
        return {"error": str(e), "status": status}
    except Exception as e:
        return {"error": str(e), "status": None}
