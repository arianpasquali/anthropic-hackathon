"""Fund: allocation preview + commitment creation.

`POST /api/fund/allocation-preview` runs the allocation engine without
persisting — used by the buyer dashboard for live slider feedback.

`POST /api/fund/commit` persists a commitment, runs the full pipeline,
and returns the resulting attribution summary.
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import Buyer, Chapter, Commitment, Fund, OperationsRecord
from app.services.allocation_engine import (
    AllocationPreferences,
    ChapterSnapshot,
    compute_allocation,
)
from app.services.impact_calculator import calculate_avoided_emissions
from app.services.pipeline import run_full_pipeline

router = APIRouter(prefix="/api/fund", tags=["fund"])


class AllocationPreferencesIn(BaseModel):
    max_climate_impact: float = Field(ge=0, le=1)
    max_social_need: float = Field(ge=0, le=1)
    balanced_distribution: float = Field(ge=0, le=1)


class AllocationPreviewIn(BaseModel):
    amount_eur: float = Field(gt=0)
    period_start: date
    period_end: date
    preferences: AllocationPreferencesIn


class CommitIn(BaseModel):
    buyer_id: str
    fund_id: str
    amount_eur: float = Field(gt=0)
    preferences: AllocationPreferencesIn
    rationale: str | None = None
    period_start: date
    period_end: date


def _coefficient_lookup() -> dict[str, float]:
    """Inline default coefficients — production would query co2e_coefficients."""
    return {
        "fresh_produce": 1.4,
        "bread_bakery": 1.1,
        "dairy": 3.2,
        "meat_processed": 6.0,
        "ready_meals": 2.5,
        "dry_goods": 1.0,
        "canned": 1.5,
        "frozen": 2.0,
    }


def _snapshots_for_period(
    db: Session, period_start: date, period_end: date
) -> list[ChapterSnapshot]:
    chapters = db.execute(select(Chapter).order_by(Chapter.id)).scalars().all()
    coefficients = _coefficient_lookup()
    snapshots: list[ChapterSnapshot] = []
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
        snapshots.append(
            ChapterSnapshot(
                id=chapter.id,
                net_avoided_tco2e=impact.net_avoided_kgco2e / 1000,
                households_served_quarter=float(ops.households_served),
                needs_score=float(chapter.needs_score),
                regional_bonus=float(chapter.regional_bonus),
                total_tonnes=sum(ops.category_breakdown.values()) / 1000,
            )
        )
    return snapshots


@router.post("/allocation-preview")
def allocation_preview(
    payload: AllocationPreviewIn, db: Session = Depends(get_db)
) -> dict:
    snapshots = _snapshots_for_period(db, payload.period_start, payload.period_end)
    if not snapshots:
        raise HTTPException(
            status_code=400,
            detail=f"No operations data for {payload.period_start}..{payload.period_end}",
        )

    try:
        prefs = AllocationPreferences(
            max_climate_impact=payload.preferences.max_climate_impact,
            max_social_need=payload.preferences.max_social_need,
            balanced_distribution=payload.preferences.balanced_distribution,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    results = compute_allocation(snapshots, prefs, payload.amount_eur)
    return {
        "amount_eur": payload.amount_eur,
        "period_start": payload.period_start.isoformat(),
        "period_end": payload.period_end.isoformat(),
        "allocations": [
            {
                "chapter_id": cid,
                "weight": round(r.weight, 6),
                "amount_eur": round(r.amount_eur, 2),
                "axis_weights": {k: round(v, 6) for k, v in r.axis_weights.items()},
            }
            for cid, r in results.items()
        ],
    }


@router.post("/commit")
def create_commitment(payload: CommitIn, db: Session = Depends(get_db)) -> dict:
    buyer = db.get(Buyer, payload.buyer_id)
    if buyer is None:
        raise HTTPException(status_code=404, detail=f"Buyer {payload.buyer_id} not found")
    fund = db.get(Fund, payload.fund_id)
    if fund is None:
        raise HTTPException(status_code=404, detail=f"Fund {payload.fund_id} not found")

    try:
        prefs = AllocationPreferences(
            max_climate_impact=payload.preferences.max_climate_impact,
            max_social_need=payload.preferences.max_social_need,
            balanced_distribution=payload.preferences.balanced_distribution,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    commitment = Commitment(
        buyer_id=buyer.id,
        fund_id=fund.id,
        amount_eur=payload.amount_eur,
        allocation_preferences={
            "max_climate_impact": prefs.max_climate_impact,
            "max_social_need": prefs.max_social_need,
            "balanced_distribution": prefs.balanced_distribution,
        },
        rationale=payload.rationale,
    )
    db.add(commitment)
    db.commit()
    db.refresh(commitment)

    result = run_full_pipeline(
        db=db,
        commitment=commitment,
        coefficients=_coefficient_lookup(),
        period_start=payload.period_start,
        period_end=payload.period_end,
        methodology_version=settings.methodology_version,
    )

    return {
        "commitment_id": result.commitment_id,
        "report_id": result.report_id,
        "total_food_rescued_kg": result.total_food_rescued_kg,
        "total_net_avoided_tco2e": result.total_net_avoided_kgco2e / 1000,
        "total_households_supported": result.total_households_supported,
    }
