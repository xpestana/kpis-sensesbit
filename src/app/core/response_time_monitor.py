"""
Health check cada 30s a api.sensesbit.com/health.
Cada 30s actualiza el registro de la hora actual (1ª, 2ª, … 10ª hora).
Al pasar a la hora 11 se elimina el registro más antiguo; siempre hay como máximo 10 registros.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Any

import requests

HEALTH_URL = "https://api.sensesbit.com/health"
CHECK_INTERVAL_SECONDS = 30
RETENTION_HOURS = 10
TIMEOUT_SECONDS = 10

# Máximo 10 registros en memoria (uno por hora); sin fuga.
MAX_REGISTROS_EN_MEMORIA = RETENTION_HOURS
_history: list[dict[str, Any]] = []
_last_check_at: datetime | None = None
_last_error: str | None = None


def _do_http_get() -> None:
    requests.get(HEALTH_URL, timeout=TIMEOUT_SECONDS)


def _hour_key(now: datetime) -> str:
    """Clave de la hora actual para agrupar (ej. 2025-02-16T14)."""
    return now.strftime("%Y-%m-%dT%H")


async def _check_once() -> None:
    global _last_check_at, _last_error
    now = datetime.now(timezone.utc)
    start = time.perf_counter()
    hour = _hour_key(now)
    at_iso = now.isoformat().replace("+00:00", "Z")

    try:
        await asyncio.to_thread(_do_http_get)
        elapsed_ms = (time.perf_counter() - start) * 1000
        _last_check_at = now
        _last_error = None
        entry = {
            "hour": hour,
            "at": at_iso,
            "response_time_ms": round(elapsed_ms, 2),
            "response_time_sec": round(elapsed_ms / 1000, 4),
            "error": None,
        }
    except Exception as e:  # noqa: BLE001
        _last_error = str(e)
        _last_check_at = now
        entry = {
            "hour": hour,
            "at": at_iso,
            "response_time_ms": None,
            "response_time_sec": None,
            "error": str(e),
        }

    # Actualizar el registro de la hora actual o añadir uno nuevo
    if _history and _history[-1].get("hour") == hour:
        _history[-1] = entry
    else:
        _history.append(entry)
        _history[:] = _history[-MAX_REGISTROS_EN_MEMORIA:]


_background_task: asyncio.Task | None = None


async def run_loop() -> None:
    """Bucle: health check cada 30s; actualiza el registro de la hora actual."""
    while True:
        await _check_once()
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)


def start_background_task() -> None:
    """Arranca el health check en background. Llamar desde lifespan de la app."""
    global _background_task
    if _background_task is None or _background_task.done():
        _background_task = asyncio.create_task(run_loop())


def get_state() -> dict[str, Any]:
    """
    Devuelve las últimas 10 h (un registro por hora, actualizado cada 30s).
    Cada punto: at, response_time_ms, response_time_sec.
    """
    return {
        "ultimas_10_horas": [
            {
                "at": e["at"],
                "response_time_ms": e.get("response_time_ms"),
                "response_time_sec": e.get("response_time_sec"),
                "error": e.get("error"),
            }
            for e in _history
        ],
        "last_check_at": _last_check_at.isoformat().replace("+00:00", "Z") if _last_check_at else None,
        "last_error": _last_error,
    }
