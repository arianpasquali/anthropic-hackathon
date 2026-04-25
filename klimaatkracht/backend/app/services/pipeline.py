"""End-to-end pipeline orchestrator.

Connects ingested operations data to a buyer commitment via the allocation
engine and attribution service. Persists all derived rows into the database
and returns a summary for the caller. The functions are deliberately small
so each is independently testable: `compute_allocations_for_commitment`
mints rows in the `allocations` table, `attribute_commitment` produces rows
in `attributions`.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    Allocation,
    AttributionRow,
    Chapter,
    Commitment,
    OperationsRecord,
    Report,
)
from app.services.allocation_engine import (
    AllocationPreferences,
    AllocationResult,
    ChapterSnapshot,
    compute_allocation,
)
from app.services.attribution import compute_attribution, DateRange
from app.services.impact_calculator import ImpactResult, calculate_avoided_emissions
from app.services.llm_client import LLMClient
from app.services.report_generator import (
    BuyerInfo,
    ChapterAttributionRow,
    ReportData,
    ReportTotals,
    generate_executive_summary,
    render_full_report_markdown,
)


@dataclass
class ChapterPeriodImpact:
    chapter: Chapter
    operations: OperationsRecord
    impact: ImpactResult
    quarterly_cost_eur: float


@dataclass
class PipelineResult:
    commitment_id: str
    period_start: date
    period_end: date
    total_food_rescued_kg: float
    total_net_avoided_kgco2e: float
    total_households_supported: float
    report_id: str
    report_markdown: str


def load_chapter_period_impacts(
    db: Session,
    coefficients: dict[str, float],
    period_start: date,
    period_end: date,
) -> list[ChapterPeriodImpact]:
    """For each chapter that submitted data covering the period, compute the
    impact result via the impact calculator and the quarterly operational
    cost via the chapter's stored cost-per-household-week rate.
    """
    chapters = db.execute(select(Chapter)).scalars().all()

    impacts: list[ChapterPeriodImpact] = []
    for chapter in chapters:
        ops = db.execute(
            select(OperationsRecord).where(
                OperationsRecord.chapter_id == chapter.id,
                OperationsRecord.period_start == period_start,
                OperationsRecord.period_end == period_end,
            )
        ).scalar_one_or_none()
        if ops is None:
            continue
        impact = calculate_avoided_emissions(
            category_kg=dict(ops.category_breakdown),
            coefficients=coefficients,
            operational_footprint_per_tonne=float(
                chapter.operational_footprint_kgco2e_per_tonne
            ),
        )
        # Prefer the chapter's stated quarterly service cost when the ops
        # record provides it; otherwise fall back to households × per-week
        # rate × calendar weeks. The two should agree for canonical 13-week
        # quarters; the override matters when periods are non-standard.
        if ops.operational_cost_eur is not None:
            quarterly_cost = float(ops.operational_cost_eur)
        else:
            weeks = max((period_end - period_start).days // 7 + 1, 1)
            quarterly_cost = (
                float(chapter.households_served_per_week)
                * float(chapter.cost_per_household_per_week_eur)
                * weeks
            )
        impacts.append(
            ChapterPeriodImpact(
                chapter=chapter,
                operations=ops,
                impact=impact,
                quarterly_cost_eur=quarterly_cost,
            )
        )
    return impacts


def _snapshot(impact: ChapterPeriodImpact) -> ChapterSnapshot:
    return ChapterSnapshot(
        id=impact.chapter.id,
        net_avoided_tco2e=impact.impact.net_avoided_kgco2e / 1000,
        households_served_quarter=float(impact.operations.households_served),
        needs_score=float(impact.chapter.needs_score),
        regional_bonus=float(impact.chapter.regional_bonus),
        total_tonnes=sum(impact.operations.category_breakdown.values()) / 1000,
    )


def compute_allocations_for_commitment(
    db: Session,
    commitment: Commitment,
    impacts: list[ChapterPeriodImpact],
) -> dict[str, AllocationResult]:
    """Run the allocation engine and persist `allocations` rows."""
    snapshots = [_snapshot(i) for i in impacts]
    prefs = AllocationPreferences(
        max_climate_impact=commitment.allocation_preferences["max_climate_impact"],
        max_social_need=commitment.allocation_preferences["max_social_need"],
        balanced_distribution=commitment.allocation_preferences["balanced_distribution"],
    )
    results = compute_allocation(snapshots, prefs, float(commitment.amount_eur))

    for chapter_id, result in results.items():
        db.add(
            Allocation(
                commitment_id=commitment.id,
                chapter_id=chapter_id,
                weight=result.weight,
                amount_eur=result.amount_eur,
                axis_weights=result.axis_weights,
            )
        )
    db.flush()
    return results


def attribute_commitment(
    db: Session,
    commitment: Commitment,
    impacts: list[ChapterPeriodImpact],
    allocations: dict[str, AllocationResult],
    period_start: date,
    period_end: date,
) -> list[AttributionRow]:
    """Compute attributions per chapter and persist them."""
    period = DateRange(start=period_start, end=period_end)
    rows: list[AttributionRow] = []
    for impact in impacts:
        allocation = allocations[impact.chapter.id]
        households_quarter = float(impact.operations.households_served)
        attr = compute_attribution(
            commitment_id=commitment.id,
            chapter_id=impact.chapter.id,
            allocation_eur=allocation.amount_eur,
            chapter_quarterly_cost_eur=impact.quarterly_cost_eur,
            chapter_total_food_kg=sum(impact.operations.category_breakdown.values()),
            chapter_net_avoided_kgco2e=impact.impact.net_avoided_kgco2e,
            chapter_households_served_quarter=households_quarter,
            period=period,
        )
        row = AttributionRow(
            commitment_id=commitment.id,
            chapter_id=impact.chapter.id,
            period_start=period_start,
            period_end=period_end,
            attribution_factor=attr.attribution_factor,
            attributed_food_kg=attr.attributed_food_kg,
            attributed_net_avoided_kgco2e=attr.attributed_net_avoided_kgco2e,
            attributed_households_supported=attr.attributed_households_supported,
            chapter_total_food_kg=attr.chapter_total_food_kg,
            chapter_total_avoided_kgco2e=attr.chapter_total_avoided_kgco2e,
            chapter_quarterly_op_cost_eur=attr.chapter_quarterly_op_cost_eur,
        )
        db.add(row)
        rows.append(row)
    db.flush()
    return rows


def assemble_report_from_db(
    db: Session,
    commitment: Commitment,
    period_start: date,
    period_end: date,
    methodology_version: str,
) -> ReportData:
    """Build ReportData from persisted attribution rows + chapter metadata.

    This is the DB-backed counterpart to assemble_report_data_from_seed.
    Reading from `attributions` (not recomputing from operations) means
    the historical figures stay frozen, which is the audit-stability
    invariant the schema is designed for.
    """
    from app.models import Buyer

    buyer = db.get(Buyer, commitment.buyer_id)
    attribution_rows = (
        db.execute(
            select(AttributionRow, Chapter)
            .join(Chapter, AttributionRow.chapter_id == Chapter.id)
            .where(
                AttributionRow.commitment_id == commitment.id,
                AttributionRow.period_start == period_start,
                AttributionRow.period_end == period_end,
            )
            .order_by(Chapter.id)
        )
    ).all()
    if not attribution_rows:
        raise ValueError(
            f"No attribution rows for commitment {commitment.id} in period "
            f"{period_start}..{period_end}"
        )

    rows: list[ChapterAttributionRow] = []
    for attr, chapter in attribution_rows:
        # Find the matching allocation for amount_eur
        allocation = db.execute(
            select(Allocation).where(
                Allocation.commitment_id == commitment.id,
                Allocation.chapter_id == chapter.id,
            )
        ).scalar_one()
        rows.append(
            ChapterAttributionRow(
                chapter_id=chapter.id,
                chapter_name=chapter.name,
                period_start=attr.period_start,
                period_end=attr.period_end,
                allocation_eur=float(allocation.amount_eur),
                chapter_total_food_kg=float(attr.chapter_total_food_kg),
                chapter_net_avoided_kgco2e=float(attr.chapter_total_avoided_kgco2e),
                chapter_quarterly_op_cost_eur=float(attr.chapter_quarterly_op_cost_eur),
                attribution_factor=float(attr.attribution_factor),
                attributed_food_kg=float(attr.attributed_food_kg),
                attributed_net_avoided_kgco2e=float(attr.attributed_net_avoided_kgco2e),
                attributed_households_supported=float(attr.attributed_households_supported),
            )
        )

    totals = ReportTotals(
        total_food_rescued_kg=sum(r.attributed_food_kg for r in rows),
        total_net_avoided_tco2e=sum(r.attributed_net_avoided_kgco2e for r in rows) / 1000,
        total_households_supported=sum(r.attributed_households_supported for r in rows),
        total_operational_kgco2e=sum(
            (r.chapter_net_avoided_kgco2e * 0)  # operational was already netted
            for r in rows
        ),
    )

    return ReportData(
        buyer=BuyerInfo(
            id=buyer.id,
            name=buyer.name,
            industry=buyer.industry or "",
            csr_framework=buyer.csr_framework,
        ),
        period_start=period_start,
        period_end=period_end,
        methodology_version=methodology_version,
        totals=totals,
        attributions=rows,
    )


def run_full_pipeline(
    db: Session,
    commitment: Commitment,
    coefficients: dict[str, float],
    period_start: date,
    period_end: date,
    methodology_version: str,
    llm_client: LLMClient | None = None,
) -> PipelineResult:
    """Orchestrate ops → allocation → attribution → report."""
    impacts = load_chapter_period_impacts(db, coefficients, period_start, period_end)
    if not impacts:
        raise ValueError(
            f"No operations records found for period {period_start}..{period_end}"
        )

    allocations = compute_allocations_for_commitment(db, commitment, impacts)
    attribute_commitment(db, commitment, impacts, allocations, period_start, period_end)

    report_data = assemble_report_from_db(
        db, commitment, period_start, period_end, methodology_version
    )
    summary = generate_executive_summary(report_data, llm_client=llm_client)
    markdown = render_full_report_markdown(report_data, summary)

    report = Report(
        commitment_id=commitment.id,
        period_start=period_start,
        period_end=period_end,
        markdown_content=markdown,
        json_data={
            "totals": {
                "total_food_rescued_kg": report_data.totals.total_food_rescued_kg,
                "total_net_avoided_tco2e": report_data.totals.total_net_avoided_tco2e,
                "total_households_supported": report_data.totals.total_households_supported,
            },
            "chapter_count": len(report_data.attributions),
        },
        llm_model="stub" if llm_client is None else llm_client.__class__.__name__,
        llm_prompt_version="exec-summary-v1",
        methodology_version=methodology_version,
    )
    db.add(report)
    db.commit()

    return PipelineResult(
        commitment_id=commitment.id,
        period_start=period_start,
        period_end=period_end,
        total_food_rescued_kg=report_data.totals.total_food_rescued_kg,
        total_net_avoided_kgco2e=report_data.totals.total_net_avoided_tco2e * 1000,
        total_households_supported=report_data.totals.total_households_supported,
        report_id=report.id,
        report_markdown=markdown,
    )
