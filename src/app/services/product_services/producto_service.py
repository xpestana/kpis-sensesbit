"""Servicio: orquestación y transformación de datos para KPIs de producto."""

from datetime import date, datetime

from sqlmodel import Session

from app.repositories.product_repositories.producto_repository import ProductoRepository


class ProductoService:
    def __init__(self, db: Session) -> None:
        self._repo = ProductoRepository(db)

    def sesiones_creadas_por_fecha(
        self,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> list[dict]:
        rows = self._repo.sesiones_creadas_por_fecha(date_from=date_from, date_to=date_to)
        if not rows:
            label = date_from.strftime("%d/%m/%Y") if date_from else datetime.now().strftime("%d/%m/%Y")
            return [{"time": label, "value": 0}]
        return [
            {
                "time": f.strftime("%d/%m/%Y") if isinstance(f, date) else str(f),
                "value": c,
            }
            for f, c in rows
        ]

    def frecuencia_uso(self) -> dict:
        """KPI 11: Frecuencia de uso = media de sesiones por cliente activo (por tenant)."""
        total_sesiones, usuarios_activos = self._repo.total_sesiones_y_usuarios_activos()
        if usuarios_activos == 0:
            return {"media_sesiones_por_usuario_activo": 0.0, "total_sesiones": 0, "usuarios_activos": 0}
        media = round(total_sesiones / usuarios_activos, 2)
        return {
            "media_sesiones_por_usuario_activo": media,
            "total_sesiones": total_sesiones,
            "usuarios_activos": usuarios_activos,
        }

    def exportaciones_generadas(self) -> dict:
        """KPI 16: Exportaciones generadas (PDF y Excel) — por file."""
        por_tipo = self._repo.exportaciones_por_tipo()
        total = self._repo.total_exportaciones()
        return {
            "total": total,
            "por_tipo": [{"tipo": t or "sin_tipo", "count": c} for t, c in por_tipo],
        }

    def porcentaje_usuarios_duplican_sesiones(self) -> dict:
        """KPI 18: % usuarios que duplican sesiones (>= 2 sesiones)."""
        total_usuarios = self._repo.total_usuarios()
        usuarios_duplican = self._repo.usuarios_con_al_menos_dos_sesiones()
        if total_usuarios == 0:
            return {"porcentaje": 0.0, "usuarios_duplican_sesiones": 0, "total_usuarios": 0}
        pct = round(100.0 * usuarios_duplican / total_usuarios, 2)
        return {
            "porcentaje": pct,
            "usuarios_duplican_sesiones": usuarios_duplican,
            "total_usuarios": total_usuarios,
        }

    def duracion_media_sesion(self) -> dict:
        """KPI 19: Duración media de sesión (solo sesiones con end_at)."""
        segundos = self._repo.duracion_media_sesion_segundos()
        if segundos is None:
            return {"duracion_media_segundos": None, "duracion_media_minutos": None}
        return {
            "duracion_media_segundos": round(segundos, 2),
            "duracion_media_minutos": round(segundos / 60, 2),
        }

    # --- KPIs IA (tabla report) ---

    def analisis_ia_ejecutados(self) -> list[dict]:
        TIPOS = ["DualSense", "JAR", "Ranking", "Verbatim", "Drivers"]
        por_tipo = {tipo: n for tipo, n in self._repo.reports_by_tipo()}
        return [{"tipo": t, "total": por_tipo.get(t, 0)} for t in TIPOS]

    def tiempo_procesamiento_ia(self) -> dict:
        por_tipo = self._repo.avg_duration_seconds_by_tipo()
        return {
            "por_tipo": [
                {
                    "tipo": tipo,
                    "segundos": seg,
                    "minutos": round(seg / 60, 2),
                }
                for tipo, seg in por_tipo
            ],
        }

    def adopcion_funcionalidades_ia(self) -> dict:
        total_sesiones = self._repo.total_sessions()
        sesiones_con_ia = self._repo.sessions_with_ai_count()
        if total_sesiones == 0:
            return {
                "porcentaje": 0.0,
                "sesiones_con_analisis_ia": 0,
                "total_sesiones": 0,
            }
        pct = round(100.0 * sesiones_con_ia / total_sesiones, 2)
        return {
            "porcentaje": pct,
            "sesiones_con_analisis_ia": sesiones_con_ia,
            "total_sesiones": total_sesiones,
        }

    # --- KPIs shared.organizations (Credits / Credits IA) ---

    def consumo_muestras(self) -> dict:
        """KPI: Consumo de Muestras (Credits) — totales y por plan. Fuente: shared.organizations.credits."""
        total, por_plan = self._repo.consumo_credits_por_plan()
        return {
            "total": total,
            "por_plan": [{"plan": plan, "Creditos": n} for plan, n in por_plan],
        }

    def consumo_credits_ia(self) -> dict:
        """KPI: Consumo de Créditos IA — totales y por plan. Fuente: shared.organizations.credits_ia."""
        total, por_plan = self._repo.consumo_credits_ia_por_plan()
        return {
            "total": total,
            "por_plan": [{"plan": plan, "Creditos": n} for plan, n in por_plan],
        }
