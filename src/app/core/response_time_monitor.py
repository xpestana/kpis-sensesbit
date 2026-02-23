"""
Health check cada 30s a api.sensesbit.com/health.
Guarda un valor por hora; el endpoint expone las últimas 10 h en ms y en segundos.
"""

import asyncio
import time
from collections import deque
from datetime import datetime, timezone, timedelta
from typing import Any

import requests

HEALTH_URL = "https://api.sensesbit.com/health"
CHECK_INTERVAL_SECONDS = 30
SAVE_INTERVAL_SECONDS = 3600  # 1 hora
RETENTION_HOURS = 10
TIMEOUT_SECONDS = 10

# Límite fijo en memoria: 1 entrada por hora × RETENTION_HOURS. Sin límite habría fuga.
# deque(maxlen=N) descarta el más antiguo al append; nunca hay más de N entradas.
MAX_REGISTROS_EN_MEMORIA = RETENTION_HOURS  # 10
_history: deque[dict[str, Any]] = deque(maxlen=MAX_REGISTROS_EN_MEMORIA)
_last_saved_at: datetime | None = None
_last_check_at: datetime | None = None
_last_error: str | None = None


def _do_http_get() -> None:
    requests.get(HEALTH_URL, timeout=TIMEOUT_SECONDS)


def _prune_old() -> None:
    """Elimina entradas con más de 10 horas."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=RETENTION_HOURS)
    while _history and _history[0].get("at"):
        try:
            at = datetime.fromisoformat(_history[0]["at"].replace("Z", "+00:00"))
            if at < cutoff:
                _history.popleft()
            else:
                break
        except (ValueError, TypeError):
            _history.popleft()


async def _check_once() -> None:
    global _last_saved_at, _last_check_at, _last_error
    now = datetime.now(timezone.utc)
    start = time.perf_counter()
    try:
        await asyncio.to_thread(_do_http_get)
        elapsed_ms = (time.perf_counter() - start) * 1000
        _last_check_at = now
        _last_error = None

        # Guardar solo cada hora
        if _last_saved_at is None or (now - _last_saved_at).total_seconds() >= SAVE_INTERVAL_SECONDS:
            _last_saved_at = now
            _prune_old()
            _history.append({
                "at": now.isoformat().replace("+00:00", "Z"),
                "response_time_ms": round(elapsed_ms, 2),
                "response_time_sec": round(elapsed_ms / 1000, 4),
            })
    except Exception as e:  # noqa: BLE001
        _last_error = str(e)
        _last_check_at = now
        if _last_saved_at is None or (now - _last_saved_at).total_seconds() >= SAVE_INTERVAL_SECONDS:
            _last_saved_at = now
            _prune_old()
            _history.append({
                "at": now.isoformat().replace("+00:00", "Z"),
                "response_time_ms": None,
                "response_time_sec": None,
                "error": str(e),
            })


_background_task: asyncio.Task | None = None


async def run_loop() -> None:
    """Bucle: health check cada 30s; persiste un valor por hora."""
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
    Devuelve las últimas 10 h de datos (un punto por hora).
    Cada punto incluye at, response_time_ms y response_time_sec.
    """
    _prune_old()
    list_snapshot = list(_history)
    return {
        "ultimas_10_horas": [
            {
                "at": e["at"],
                "response_time_ms": e.get("response_time_ms"),
                "response_time_sec": e.get("response_time_sec"),
                "error": e.get("error"),
            }
            for e in list_snapshot
        ],
        "last_check_at": _last_check_at.isoformat().replace("+00:00", "Z") if _last_check_at else None,
        "last_error": _last_error,
    }
