"""Repositorio: solo acceso a datos para KPIs de producto. Sin lógica de negocio."""

from datetime import date

from sqlalchemy import func, select
from sqlmodel import Session

from app.models.answer import Answer
from app.models.file import File
from app.models.organization import Organization
from app.models.question import Question
from app.models.report import AIReportModel
from app.models.section import Section
from app.models.session import Session as SessionModel
from app.models.user import User


class ProductoRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def sesiones_creadas_por_fecha(self) -> list[tuple[date, int]]:
        stmt = (
            select(func.date(SessionModel.created).label("fecha"), func.count(SessionModel.id))
            .group_by(func.date(SessionModel.created))
            .order_by(func.date(SessionModel.created))
        )
        rows = self._db.exec(stmt).all()
        return [(r[0], r[1]) for r in rows] if rows else []

    def total_sesiones_y_usuarios_activos(self) -> tuple[int, int]:
        """Para KPI 11: total sesiones y total usuarios con al menos una respuesta (activos)."""
        total_sesiones = self._db.exec(select(func.count(SessionModel.id))).one()
        usuarios_activos = self._db.exec(
            select(func.count(func.distinct(Answer.user_id)))
        ).one()
        return total_sesiones or 0, usuarios_activos or 0

    def exportaciones_por_tipo(self) -> list[tuple[str | None, int]]:
        """KPI 16: count de files por tipo (pdf, xlsx, etc.). file_type o inferido por name."""
        stmt = (
            select(File.file_type, func.count(File.id))
            .group_by(File.file_type)
            .order_by(func.count(File.id).desc())
        )
        rows = self._db.exec(stmt).all()
        return [(r[0], r[1]) for r in rows] if rows else []

    def total_exportaciones(self) -> int:
        """KPI 16: total de archivos (exportaciones)."""
        r = self._db.exec(select(func.count(File.id))).one()
        return r or 0

    def total_usuarios(self) -> int:
        """Total usuarios (no borrados) para porcentajes."""
        r = self._db.exec(select(func.count(User.id)).where(User.deleted.is_(None))).one()
        return r or 0

    def usuarios_con_al_menos_dos_sesiones(self) -> int:
        """KPI 18: usuarios que tienen >= 2 sesiones (vía answer -> question -> section -> session)."""
        subq = (
            select(Answer.user_id, Section.session_id)
            .join(Question, Answer.question_id == Question.id)
            .join(Section, Question.section_id == Section.id)
            .distinct()
        ).subquery()
        agrupado = (
            select(subq.c.user_id)
            .group_by(subq.c.user_id)
            .having(func.count(subq.c.session_id) >= 2)
        ).subquery()
        r = self._db.exec(select(func.count(agrupado.c.user_id)).select_from(agrupado)).one()
        return r or 0

    def duracion_media_sesion_segundos(self) -> float | None:
        """KPI 19: media de (end_at - created) en segundos, solo sesiones con end_at."""
        stmt = select(
            func.avg(
                func.extract("epoch", SessionModel.end_at) - func.extract("epoch", SessionModel.created)
            )
        ).where(SessionModel.end_at.isnot(None))
        r = self._db.exec(stmt).one()
        return float(r) if r is not None else None

    # --- KPIs IA (tabla report) ---

    def total_reports(self) -> int:
        """Total de análisis IA ejecutados (report sin borrar)."""
        stmt = select(func.count(AIReportModel.id)).where(AIReportModel.deleted.is_(None))
        r = self._db.execute(stmt).scalar()
        return r or 0

    def reports_by_tipo(self) -> list[tuple[str, int]]:
        """Análisis IA por tipo (ai_engine): DualSense, JAR, Ranking, Verbatim, Drivers, etc."""
        stmt = (
            select(AIReportModel.ai_engine, func.count(AIReportModel.id))
            .where(AIReportModel.deleted.is_(None))
            .group_by(AIReportModel.ai_engine)
            .order_by(func.count(AIReportModel.id).desc())
        )
        rows = self._db.execute(stmt).all()
        return [(row[0], row[1]) for row in rows] if rows else []

    def avg_duration_seconds_by_tipo(self) -> list[tuple[str, float]]:
        """Tiempo medio de procesamiento (segundos) por tipo de análisis. Solo report con started y completed."""
        stmt = (
            select(
                AIReportModel.ai_engine,
                func.avg(func.extract("epoch", AIReportModel.generation_duration)).label("avg_sec"),
            )
            .where(
                AIReportModel.deleted.is_(None),
                AIReportModel.started.isnot(None),
                AIReportModel.completed.isnot(None),
            )
            .group_by(AIReportModel.ai_engine)
            .order_by(AIReportModel.ai_engine)
        )
        rows = self._db.execute(stmt).all()
        return [(row[0], round(float(row[1] or 0), 2)) for row in rows] if rows else []

    def sessions_with_ai_count(self) -> int:
        """Sesiones distintas que tienen al menos un report (análisis IA)."""
        stmt = (
            select(func.count(func.distinct(AIReportModel.session_id)))
            .where(AIReportModel.deleted.is_(None), AIReportModel.session_id.isnot(None))
        )
        r = self._db.execute(stmt).scalar()
        return r or 0

    def total_sessions(self) -> int:
        """Total de sesiones (para % adopción)."""
        r = self._db.execute(select(func.count(SessionModel.id))).scalar()
        return r or 0

    # --- KPIs shared.organizations (Credits / Credits IA) ---

    def consumo_credits_por_plan(self) -> tuple[int, list[tuple[str, int]]]:
        """Consumo de Muestras (credits): total y por plan (license_type). shared.organizations."""
        total_stmt = select(func.coalesce(func.sum(Organization.credits), 0)).select_from(Organization)
        total = int(self._db.execute(total_stmt).scalar() or 0)
        por_plan_stmt = (
            select(Organization.license_type, func.sum(Organization.credits))
            .group_by(Organization.license_type)
            .order_by(func.sum(Organization.credits).desc())
        )
        rows = self._db.execute(por_plan_stmt).all()
        por_plan = [(row[0], int(row[1] or 0)) for row in rows] if rows else []
        return total, por_plan

    def consumo_credits_ia_por_plan(self) -> tuple[int, list[tuple[str, int]]]:
        """Consumo de Créditos IA (credits_ia): total y por plan (license_type). shared.organizations."""
        total_stmt = select(func.coalesce(func.sum(Organization.credits_ia), 0)).select_from(Organization)
        total = int(self._db.execute(total_stmt).scalar() or 0)
        por_plan_stmt = (
            select(Organization.license_type, func.sum(Organization.credits_ia))
            .group_by(Organization.license_type)
            .order_by(func.sum(Organization.credits_ia).desc())
        )
        rows = self._db.execute(por_plan_stmt).all()
        por_plan = [(row[0], int(row[1] or 0)) for row in rows] if rows else []
        return total, por_plan
