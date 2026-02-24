from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import INTERVAL, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.core.config import settings


class Base(DeclarativeBase):
    pass


class AIReportModel(Base):
    __tablename__ = "report"
    __table_args__ = {"schema": settings.ORG_SCHEMA}

    id: Mapped[int] = mapped_column(
        sa.Integer,
        sa.Identity(always=False),
        primary_key=True,
    )
    session_id: Mapped[Optional[UUID]] = mapped_column(
        sa.Uuid,
        sa.ForeignKey(f"{settings.ORG_SCHEMA}.session.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(sa.Text, nullable=False)
    params: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    status: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    ai_engine: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    language: Mapped[str] = mapped_column(sa.String(8), nullable=False)

    advanced: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    essential: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)
    annexes: Mapped[Optional[str]] = mapped_column(sa.Text, nullable=True)

    input_tokens: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default=sa.text("0"))
    output_tokens: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default=sa.text("0"))
    reasoning_tokens: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default=sa.text("0"))

    started: Mapped[Optional[dt.datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
    completed: Mapped[Optional[dt.datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)

    generation_duration: Mapped[dt.timedelta] = mapped_column(
        INTERVAL,
        sa.Computed(
            "CASE "
            "WHEN started IS NOT NULL AND completed IS NOT NULL THEN completed - started "
            "ELSE INTERVAL '0 seconds' "
            "END",
            persisted=True,
        ),
        nullable=False,
    )

    provider_cost_usd: Mapped[Decimal] = mapped_column(sa.Numeric(12, 4), nullable=False, server_default=sa.text("0"))
    provider_cost_eur: Mapped[Decimal] = mapped_column(sa.Numeric(12, 4), nullable=False, server_default=sa.text("0"))

    credits_charged: Mapped[int] = mapped_column(sa.Integer, nullable=False, server_default=sa.text("0"))
    credit_unit_price: Mapped[Decimal] = mapped_column(sa.Numeric(12, 4), nullable=False, server_default=sa.text("0.7500"))

    created: Mapped[dt.datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    updated: Mapped[dt.datetime] = mapped_column(sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()"))
    deleted: Mapped[Optional[dt.datetime]] = mapped_column(sa.DateTime(timezone=True), nullable=True)
