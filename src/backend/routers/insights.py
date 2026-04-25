"""Aggregate stats and per-bank data insights for the frontend."""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.foodbank import AnnualReport, Foodbank, FoodbankLocation
from src.backend.models.frame import FrameResult
from src.backend.models.measurements import FoodCategories, FoodVolume, PeopleServed

router = APIRouter(prefix="/insights", tags=["insights"])


class AggregateStats(BaseModel):
    banks_count: int
    total_tco2e_yr: float
    total_kg_rescued_yr: float
    total_households_wk: int


class CategoryMix(BaseModel):
    produce: float
    meat_fish: float
    dairy_eggs: float
    dry_goods: float
    bread_bakery: float
    prepared: float


class FrameSummary(BaseModel):
    co2e_total_kg: float
    co2e_produce_kg: float
    co2e_meat_fish_kg: float
    co2e_dairy_eggs_kg: float
    co2e_dry_goods_kg: float
    co2e_bread_kg: float
    co2e_prepared_kg: Optional[float]
    methodology_version: str


class BankSummary(BaseModel):
    id: str
    name: str
    city: str
    region: str
    is_regional_dc: bool
    annual_tco2e: Optional[float]
    annual_kg_rescued: Optional[float]
    households_weekly: Optional[int]
    people_served: Optional[int]
    lat: Optional[float]
    lng: Optional[float]
    category_mix: Optional[CategoryMix]
    frame: Optional[FrameSummary]
    report_year: Optional[int]


def _latest_report(session: Session, foodbank_id: uuid.UUID) -> Optional[AnnualReport]:
    reports = session.exec(
        select(AnnualReport).where(AnnualReport.foodbank_id == foodbank_id)
    ).all()
    return max(reports, key=lambda r: r.year) if reports else None


def _category_mix(fc: FoodCategories) -> Optional[CategoryMix]:
    vals = {
        "produce": fc.kg_produce,
        "meat_fish": fc.kg_meat_fish,
        "dairy_eggs": fc.kg_dairy_eggs,
        "dry_goods": fc.kg_dry_goods,
        "bread_bakery": fc.kg_bread_bakery,
        "prepared": fc.kg_prepared,
    }
    total = sum(v for v in vals.values() if v is not None)
    if total == 0:
        return None
    return CategoryMix(**{k: (v or 0) / total for k, v in vals.items()})


def _build_bank_summary(session: Session, fb: Foodbank) -> BankSummary:
    report = _latest_report(session, fb.id)

    loc = session.exec(
        select(FoodbankLocation).where(FoodbankLocation.foodbank_id == fb.id)
    ).first()

    frame: Optional[FrameResult] = None
    fv: Optional[FoodVolume] = None
    ps: Optional[PeopleServed] = None
    fc: Optional[FoodCategories] = None

    if report:
        frame = session.exec(
            select(FrameResult).where(FrameResult.report_id == report.id)
        ).first()
        fv = session.exec(
            select(FoodVolume).where(FoodVolume.report_id == report.id)
        ).first()
        ps = session.exec(
            select(PeopleServed).where(PeopleServed.report_id == report.id)
        ).first()
        fc = session.exec(
            select(FoodCategories).where(FoodCategories.report_id == report.id)
        ).first()

    frame_summary = None
    if frame:
        frame_summary = FrameSummary(
            co2e_total_kg=frame.co2e_total_kg,
            co2e_produce_kg=frame.co2e_produce_kg,
            co2e_meat_fish_kg=frame.co2e_meat_fish_kg,
            co2e_dairy_eggs_kg=frame.co2e_dairy_eggs_kg,
            co2e_dry_goods_kg=frame.co2e_dry_goods_kg,
            co2e_bread_kg=frame.co2e_bread_kg,
            co2e_prepared_kg=frame.co2e_prepared_kg,
            methodology_version=frame.methodology_version,
        )

    return BankSummary(
        id=str(fb.id),
        name=fb.name,
        city=fb.city,
        region=fb.region.value,
        is_regional_dc=fb.is_regional_dc,
        annual_tco2e=frame.co2e_total_kg / 1000 if frame else None,
        annual_kg_rescued=fv.kg_received_total if fv else None,
        households_weekly=ps.households_weekly if ps else None,
        people_served=ps.individuals_total if ps else None,
        lat=loc.lat if loc else None,
        lng=loc.lng if loc else None,
        category_mix=_category_mix(fc) if fc else None,
        frame=frame_summary,
        report_year=report.year if report else None,
    )


@router.get("/aggregate", response_model=AggregateStats)
def aggregate_stats(request: Request, session: Session = Depends(get_session)) -> AggregateStats:
    """Platform-wide totals: tCO₂e, kg rescued, households, bank count."""
    banks = session.exec(select(Foodbank)).all()

    total_tco2e = 0.0
    total_kg = 0.0
    total_hh = 0

    for fb in banks:
        report = _latest_report(session, fb.id)
        if not report:
            continue

        frame = session.exec(
            select(FrameResult).where(FrameResult.report_id == report.id)
        ).first()
        if frame:
            total_tco2e += frame.co2e_total_kg / 1000

        fv = session.exec(
            select(FoodVolume).where(FoodVolume.report_id == report.id)
        ).first()
        if fv and fv.kg_received_total:
            total_kg += fv.kg_received_total

        ps = session.exec(
            select(PeopleServed).where(PeopleServed.report_id == report.id)
        ).first()
        if ps and ps.households_weekly:
            total_hh += ps.households_weekly

    stats = AggregateStats(
        banks_count=len(banks),
        total_tco2e_yr=round(total_tco2e, 1),
        total_kg_rescued_yr=round(total_kg, 0),
        total_households_wk=total_hh,
    )

    if "text/markdown" in request.headers.get("accept", ""):
        md = (
            "## Klimaatkracht Platform Stats\n\n"
            f"- **Foodbanks tracked:** {stats.banks_count}\n"
            f"- **Total CO₂e avoided:** {stats.total_tco2e_yr:,.1f} tCO₂e/year\n"
            f"- **Food rescued:** {stats.total_kg_rescued_yr:,.0f} kg/year\n"
            f"- **Households served weekly:** {stats.total_households_wk:,}\n"
        )
        return PlainTextResponse(content=md, media_type="text/markdown; charset=utf-8")

    return stats


@router.get("/banks", response_model=list[BankSummary])
def list_banks(session: Session = Depends(get_session)) -> list[BankSummary]:
    """All banks with latest FRAME data, coordinates, and category mix."""
    banks = session.exec(select(Foodbank)).all()
    results = [_build_bank_summary(session, fb) for fb in banks]
    return sorted(results, key=lambda b: b.annual_tco2e or 0, reverse=True)


@router.get("/banks/{bank_id}", response_model=BankSummary)
def get_bank(bank_id: uuid.UUID, session: Session = Depends(get_session)) -> BankSummary:
    """Single bank with latest FRAME data, coordinates, and category mix."""
    fb = session.get(Foodbank, bank_id)
    if not fb:
        raise HTTPException(status_code=404, detail="Bank not found")
    return _build_bank_summary(session, fb)
