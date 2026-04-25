"""SQLAlchemy ORM models matching the schema in the implementation plan.

Postgres-specific features (GEOGRAPHY column, generated columns) are kept
optional so the same models work against SQLite for in-memory tests. When a
column is Postgres-only, the model carries it as a plain JSON or numeric
column and the migration generates the typed counterpart.
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Chapter(Base):
    __tablename__ = "chapters"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    households_served_per_week: Mapped[int] = mapped_column(Integer, nullable=False)
    needs_score: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    regional_bonus: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False, default=1.0)
    operational_footprint_kgco2e_per_tonne: Mapped[float] = mapped_column(Numeric, nullable=False)
    cost_per_household_per_week_eur: Mapped[float] = mapped_column(Numeric, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    operations: Mapped[list[OperationsRecord]] = relationship(back_populates="chapter")


class OperationsRecord(Base):
    __tablename__ = "operations_records"
    __table_args__ = (
        UniqueConstraint("chapter_id", "period_start", "period_end", name="uq_ops_chapter_period"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    submission_method: Mapped[str] = mapped_column(String(20), nullable=False)
    total_kg: Mapped[float] = mapped_column(Numeric, nullable=False)
    category_breakdown: Mapped[dict] = mapped_column(JSON, nullable=False)
    households_served: Mapped[int] = mapped_column(Integer, nullable=False)
    distribution_count: Mapped[int | None] = mapped_column(Integer)
    transport_km: Mapped[float | None] = mapped_column(Numeric)
    refrigeration_kwh: Mapped[float | None] = mapped_column(Numeric)
    operational_cost_eur: Mapped[float | None] = mapped_column(Numeric)
    raw_input_url: Mapped[str | None] = mapped_column(Text)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    chapter: Mapped[Chapter] = relationship(back_populates="operations")


class CO2eCoefficient(Base):
    __tablename__ = "co2e_coefficients"

    category: Mapped[str] = mapped_column(String(50), primary_key=True)
    version: Mapped[str] = mapped_column(String(20), primary_key=True)
    coefficient_kgco2e_per_kg: Mapped[float] = mapped_column(Numeric, nullable=False)
    source: Mapped[str] = mapped_column(Text, nullable=False)
    effective_from: Mapped[date] = mapped_column(Date, nullable=False)
    effective_to: Mapped[date | None] = mapped_column(Date)


class Buyer(Base):
    __tablename__ = "buyers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    industry: Mapped[str | None] = mapped_column(String(50))
    csr_framework: Mapped[str] = mapped_column(String(20), nullable=False, default="CSRD")
    contact_email: Mapped[str] = mapped_column(Text, nullable=False)
    employees_count: Mapped[int | None] = mapped_column(Integer)
    turnover_eur_m: Mapped[int | None] = mapped_column(Integer)
    csrd_in_scope: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Fund(Base):
    __tablename__ = "funds"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    methodology_version: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Commitment(Base):
    __tablename__ = "commitments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    buyer_id: Mapped[str] = mapped_column(ForeignKey("buyers.id"), nullable=False)
    fund_id: Mapped[str] = mapped_column(ForeignKey("funds.id"), nullable=False)
    amount_eur: Mapped[float] = mapped_column(Numeric, nullable=False)
    allocation_preferences: Mapped[dict] = mapped_column(JSON, nullable=False)
    rationale: Mapped[str | None] = mapped_column(Text)
    committed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="active")


class Allocation(Base):
    __tablename__ = "allocations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    commitment_id: Mapped[str] = mapped_column(ForeignKey("commitments.id"), nullable=False)
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric, nullable=False)
    amount_eur: Mapped[float] = mapped_column(Numeric, nullable=False)
    axis_weights: Mapped[dict] = mapped_column(JSON, nullable=False)
    allocated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AttributionRow(Base):
    __tablename__ = "attributions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    commitment_id: Mapped[str] = mapped_column(ForeignKey("commitments.id"), nullable=False)
    chapter_id: Mapped[str] = mapped_column(ForeignKey("chapters.id"), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    attribution_factor: Mapped[float] = mapped_column(Numeric, nullable=False)
    attributed_food_kg: Mapped[float] = mapped_column(Numeric, nullable=False)
    attributed_net_avoided_kgco2e: Mapped[float] = mapped_column(Numeric, nullable=False)
    attributed_households_supported: Mapped[float] = mapped_column(Numeric, nullable=False)
    chapter_total_food_kg: Mapped[float] = mapped_column(Numeric, nullable=False)
    chapter_total_avoided_kgco2e: Mapped[float] = mapped_column(Numeric, nullable=False)
    chapter_quarterly_op_cost_eur: Mapped[float] = mapped_column(Numeric, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    commitment_id: Mapped[str] = mapped_column(ForeignKey("commitments.id"), nullable=False)
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    period_end: Mapped[date] = mapped_column(Date, nullable=False)
    pdf_url: Mapped[str | None] = mapped_column(Text)
    markdown_content: Mapped[str | None] = mapped_column(Text)
    json_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    llm_model: Mapped[str | None] = mapped_column(String(50))
    llm_prompt_version: Mapped[str | None] = mapped_column(String(20))
    methodology_version: Mapped[str | None] = mapped_column(String(20))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AuditLogEntry(Base):
    __tablename__ = "audit_log"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    actor_type: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(Text)
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_table: Mapped[str | None] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(Text)
    details: Mapped[dict | None] = mapped_column(JSON)
