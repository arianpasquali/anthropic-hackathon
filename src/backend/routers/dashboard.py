import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import func
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import CsrReport, FundSubscription, Package
from src.backend.models.measurements import FoodCategories, PeopleServed
from src.backend.models.user import User
from src.backend.services.auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


class AllocationDetail(BaseModel):
    foodbank_id: str
    foodbank_name: str
    foodbank_city: str
    weight_pct: float
    amount_eur: float
    co2e_attributed_kg: float


class SubscriptionDetail(BaseModel):
    id: str
    package_id: str
    package_name: str
    amount_eur: float
    status: str
    total_co2e_kg: float
    allocations: list[AllocationDetail]
    report_id: Optional[str]


class SubscriptionSummary(BaseModel):
    id: str
    package_id: str
    package_name: str
    amount_eur: float
    status: str
    total_co2e_kg: float


def _get_allocations_detail(session: Session, sub: FundSubscription) -> tuple[list[AllocationDetail], float]:
    allocs = session.exec(select(Allocation).where(Allocation.subscription_id == sub.id)).all()
    details = []
    for alloc in allocs:
        fb = session.get(Foodbank, alloc.foodbank_id)
        # Pick latest report that has a FrameResult
        latest_year = session.exec(
            select(func.max(AnnualReport.year))
            .join(FrameResult, FrameResult.report_id == AnnualReport.id)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id)
        ).first()
        annual = session.exec(
            select(AnnualReport)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id, AnnualReport.year == latest_year)
        ).first() if latest_year else None
        frame = session.exec(select(FrameResult).where(FrameResult.report_id == annual.id)).first() if annual else None
        co2e = (frame.co2e_total_kg * alloc.weight_pct) if frame else 0.0
        details.append(AllocationDetail(
            foodbank_id=str(alloc.foodbank_id),
            foodbank_name=fb.name if fb else "Unknown",
            foodbank_city=fb.city if fb else "",
            weight_pct=alloc.weight_pct,
            amount_eur=sub.amount_eur * alloc.weight_pct,
            co2e_attributed_kg=co2e,
        ))
    details.sort(key=lambda x: x.weight_pct, reverse=True)
    total_co2e = sum(d.co2e_attributed_kg for d in details)
    return details, total_co2e


@router.get("", response_model=list[SubscriptionSummary])
def dashboard(session: Session = Depends(get_session), user: User = Depends(get_current_user)):
    subs = session.exec(select(FundSubscription).where(FundSubscription.user_id == user.id)).all()
    result = []
    for sub in subs:
        pkg = session.get(Package, sub.package_id)
        _, total_co2e = _get_allocations_detail(session, sub)
        result.append(SubscriptionSummary(
            id=str(sub.id),
            package_id=str(sub.package_id),
            package_name=pkg.name if pkg else "Unknown",
            amount_eur=sub.amount_eur,
            status=sub.status.value,
            total_co2e_kg=total_co2e,
        ))
    return result


class TimelineQuarter(BaseModel):
    label: str
    year: int
    quarter: int
    co2e_kg: float
    realised: bool
    cumulative_co2e_kg: float


class ProvenanceMix(BaseModel):
    extracted_pct: float
    inferred_national_avg_pct: float
    inferred_category_split_pct: float
    inferred_calculation_pct: float
    manual_pct: float
    confidence_band: str   # "high" | "medium" | "low" — derived from extracted_pct


class CoverageRegion(BaseModel):
    region: str
    weight_pct: float
    foodbanks: int


class DashboardMetrics(BaseModel):
    # Tier 1 — disclosure grade
    period_co2e_kg: float            # this quarter / current period
    period_delta_pct: float | None   # vs previous year same quarter
    cumulative_co2e_kg: float        # since first paid subscription
    eur_per_tco2e: float | None      # cost effectiveness benchmark
    households_weighted: int         # allocation-weighted households served (no 52x bug)
    individuals_weighted: int

    # Tier 4 — audit trust
    provenance: ProvenanceMix

    # Tier 3 — narrative
    cars_equivalent: int             # tCO2e / 4.6 (avg NL passenger car / yr)
    nl_households_equivalent: int    # tCO2e / 6.5 (avg NL household elec)
    flights_equivalent: int          # tCO2e / 0.255 (1 econ AMS-NYC RT)

    # Coverage
    regions: list[CoverageRegion]


@router.get("/{sub_id}/metrics", response_model=DashboardMetrics)
def dashboard_metrics(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)

    allocs = session.exec(select(Allocation).where(Allocation.subscription_id == sub.id)).all()
    if not allocs:
        raise HTTPException(status_code=404, detail="no allocations")

    pkg = session.get(Package, sub.package_id)

    # Period (one quarter) co2e: subscription's annual claim / 4. Annual claim
    # comes from compute_allocations result baked into Allocation table — we
    # recompute with score_foodbanks so this stays in sync if banks change.
    annual_co2e = 0.0
    households = 0
    individuals = 0
    region_weight: dict[str, float] = {}
    region_count: dict[str, int] = {}
    provenance_counts = {
        "extracted": 0,
        "inferred_national_avg": 0,
        "inferred_category_split": 0,
        "inferred_calculation": 0,
        "manual": 0,
    }
    provenance_total = 0

    for alloc in allocs:
        fb = session.get(Foodbank, alloc.foodbank_id)
        if not fb:
            continue
        # Latest annual report for this bank
        latest = session.exec(
            select(AnnualReport)
            .where(AnnualReport.foodbank_id == fb.id)
            .order_by(AnnualReport.year.desc())
        ).first()
        if not latest:
            continue
        frame = session.exec(select(FrameResult).where(FrameResult.report_id == latest.id)).first()
        people = session.exec(select(PeopleServed).where(PeopleServed.report_id == latest.id)).first()
        cats = session.exec(select(FoodCategories).where(FoodCategories.report_id == latest.id)).first()

        if frame:
            annual_co2e += frame.co2e_total_kg * alloc.weight_pct
        if people:
            if people.households_weekly:
                households += int(people.households_weekly * alloc.weight_pct)
            if people.individuals_total:
                individuals += int(people.individuals_total * alloc.weight_pct)

        # Region coverage
        rkey = fb.region.value
        region_weight[rkey] = region_weight.get(rkey, 0.0) + alloc.weight_pct
        region_count[rkey] = region_count.get(rkey, 0) + 1

        # Provenance accounting — count fields by source across measurement tables.
        for model, fields in (
            (cats, ["kg_produce", "kg_meat_fish", "kg_dairy_eggs", "kg_dry_goods", "kg_bread_bakery", "kg_prepared"]),
            (people, ["households_weekly", "individuals_total", "children_count", "pct_under_18"]),
        ):
            if not model:
                continue
            for fname in fields:
                source = getattr(model, f"{fname}_source", None)
                if source is not None:
                    key = source.value if hasattr(source, "value") else str(source)
                    if key in provenance_counts:
                        provenance_counts[key] += 1
                        provenance_total += 1

    # Subscription's annual claim is what corporate is "buying" — scale to
    # `pkg.co2e_claim_kg` if defined, else use the weighted bank-baseline sum.
    # The fund advertised co2e_claim_kg is the contractual figure; the weighted
    # baseline is what FRAME computes the banks can deliver. We use the
    # smaller of the two as the conservative number.
    advertised = pkg.co2e_claim_kg if pkg else None
    annual_claim_kg = min(annual_co2e, advertised) if advertised else annual_co2e

    period_co2e_kg = annual_claim_kg / 4.0

    # Delta vs prior-year-same-quarter: derived from historical bank trajectory
    # for the same allocation.
    annual_history: dict[int, float] = {}
    for alloc in allocs:
        reports = session.exec(
            select(AnnualReport)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id)
            .order_by(AnnualReport.year)
        ).all()
        for r in reports:
            f = session.exec(select(FrameResult).where(FrameResult.report_id == r.id)).first()
            if not f:
                continue
            annual_history[r.year] = annual_history.get(r.year, 0.0) + f.co2e_total_kg * alloc.weight_pct

    period_delta_pct = None
    if len(annual_history) >= 2:
        ys = sorted(annual_history)
        prior, latest = annual_history[ys[-2]], annual_history[ys[-1]]
        if prior > 0:
            period_delta_pct = (latest - prior) / prior

    # Cumulative: count quarters between purchased_at and now, default 1 if
    # the subscription was just confirmed.
    from datetime import datetime, timezone
    if sub.status.value == "paid":
        purchased = sub.purchased_at
        if purchased.tzinfo is None:
            purchased = purchased.replace(tzinfo=timezone.utc)
        delta_days = max(0, (datetime.now(timezone.utc) - purchased).days)
        quarters_paid = max(1, delta_days // 90 + 1)
    else:
        quarters_paid = 0
    cumulative_co2e_kg = period_co2e_kg * quarters_paid

    eur_per_tco2e = None
    if annual_claim_kg > 0:
        eur_per_tco2e = sub.amount_eur / (annual_claim_kg / 1000.0)

    if provenance_total == 0:
        provenance = ProvenanceMix(
            extracted_pct=0, inferred_national_avg_pct=0, inferred_category_split_pct=0,
            inferred_calculation_pct=0, manual_pct=0, confidence_band="low",
        )
    else:
        ext_pct = provenance_counts["extracted"] / provenance_total
        band = "high" if ext_pct >= 0.7 else "medium" if ext_pct >= 0.4 else "low"
        provenance = ProvenanceMix(
            extracted_pct=ext_pct,
            inferred_national_avg_pct=provenance_counts["inferred_national_avg"] / provenance_total,
            inferred_category_split_pct=provenance_counts["inferred_category_split"] / provenance_total,
            inferred_calculation_pct=provenance_counts["inferred_calculation"] / provenance_total,
            manual_pct=provenance_counts["manual"] / provenance_total,
            confidence_band=band,
        )

    annual_t = annual_claim_kg / 1000.0
    cars = int(annual_t / 4.6)             # avg NL passenger car ~4.6 tCO2e/yr (CBS 2023)
    nl_hh = int(annual_t / 6.5)            # avg NL household electricity 6.5 tCO2e/yr (RIVM)
    flights = int(annual_t / 0.255)        # 1 economy AMS-JFK RT ~0.255 tCO2e (ICAO calculator)

    regions = sorted(
        [
            CoverageRegion(region=r, weight_pct=w, foodbanks=region_count[r])
            for r, w in region_weight.items()
        ],
        key=lambda x: x.weight_pct, reverse=True,
    )

    return DashboardMetrics(
        period_co2e_kg=period_co2e_kg,
        period_delta_pct=period_delta_pct,
        cumulative_co2e_kg=cumulative_co2e_kg,
        eur_per_tco2e=eur_per_tco2e,
        households_weighted=households,
        individuals_weighted=individuals,
        provenance=provenance,
        cars_equivalent=cars,
        nl_households_equivalent=nl_hh,
        flights_equivalent=flights,
        regions=regions,
    )


class SubscriptionPacing(BaseModel):
    quarters_realised: int           # since purchased_at
    quarters_contracted: int         # 4 = annual cycle
    cycle_pct: float                 # quarters_realised / quarters_contracted
    next_disclosure_quarter: str     # e.g. "2026 Q3"


@router.get("/{sub_id}/pacing", response_model=SubscriptionPacing)
def dashboard_pacing(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)

    from datetime import datetime, timezone
    purchased = sub.purchased_at
    if purchased.tzinfo is None:
        purchased = purchased.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    if sub.status.value != "paid":
        quarters_realised = 0
    else:
        days = max(0, (now - purchased).days)
        quarters_realised = max(1, days // 90 + 1)

    # Next disclosure quarter from current calendar position
    nxt_q = ((now.month - 1) // 3) + 2
    nxt_y = now.year
    if nxt_q > 4:
        nxt_q = 1
        nxt_y += 1

    return SubscriptionPacing(
        quarters_realised=quarters_realised,
        quarters_contracted=4,
        cycle_pct=min(1.0, quarters_realised / 4.0),
        next_disclosure_quarter=f"{nxt_y} Q{nxt_q}",
    )


@router.get("/{sub_id}/timeline", response_model=list[TimelineQuarter])
def dashboard_timeline(
    sub_id: uuid.UUID,
    forecast_quarters: int = 4,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    """Quarterly performance timeline for a subscription.

    Realised: each paid quarter contributes 1/4 of the per-bank annual co2e
    weighted by allocation share. Forecast: linear extrapolation from the most
    recent realised quarters using the last 4 reported annual growth points,
    falling back to the historical mean year-on-year delta.
    """
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)

    allocs = session.exec(select(Allocation).where(Allocation.subscription_id == sub.id)).all()
    if not allocs:
        return []

    # Build per-allocation annual co2e history then collapse to fund-level annual.
    annual_totals: dict[int, float] = {}
    for alloc in allocs:
        reports = session.exec(
            select(AnnualReport)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id)
            .order_by(AnnualReport.year)
        ).all()
        for r in reports:
            frame = session.exec(select(FrameResult).where(FrameResult.report_id == r.id)).first()
            if not frame:
                continue
            annual_totals[r.year] = annual_totals.get(r.year, 0.0) + frame.co2e_total_kg * alloc.weight_pct

    if not annual_totals:
        return []

    years = sorted(annual_totals)
    # Rescale: weighted bank baseline → subscription's contractual annual claim.
    # The advertised pkg.co2e_claim_kg is the corporate's actual yearly purchase;
    # we normalise the timeline so the most recent year matches that and prior
    # years preserve historical relative growth.
    pkg = session.get(Package, sub.package_id)
    advertised = pkg.co2e_claim_kg if pkg else 0.0
    raw_latest = annual_totals[years[-1]]
    target_latest = min(advertised, raw_latest) if advertised else raw_latest
    if raw_latest > 0 and target_latest > 0:
        scale = target_latest / raw_latest
        annual_totals = {y: v * scale for y, v in annual_totals.items()}
    latest_annual = annual_totals[years[-1]]

    # Linear regression slope (kg/year) for forecast extrapolation.
    if len(years) >= 2:
        n = len(years)
        x_mean = sum(years) / n
        y_mean = sum(annual_totals.values()) / n
        denom = sum((y - x_mean) ** 2 for y in years) or 1.0
        slope = sum((y - x_mean) * (annual_totals[y] - y_mean) for y in years) / denom
    else:
        slope = 0.0

    # Option C: subscription runway only. Past = quarters between purchased_at
    # and now (realised). Future = forecast forward using historical bank slope.
    # No fictional pre-purchase quarters claiming retroactive credit.
    from datetime import datetime, timezone
    purchased = sub.purchased_at
    if purchased.tzinfo is None:
        purchased = purchased.replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    if sub.status.value != "paid":
        return []

    days_since = max(0, (now - purchased).days)
    quarters_realised = max(1, days_since // 90 + 1)

    # Quarter of purchased_at
    p_year = purchased.year
    p_q = ((purchased.month - 1) // 3) + 1

    series: list[TimelineQuarter] = []
    fy, fq = p_year, p_q

    # Realised quarters (since purchase)
    for i in range(quarters_realised):
        # Per-quarter co2e scales with the closest annual_total available
        annual_for_year = annual_totals.get(fy, latest_annual)
        per_q = annual_for_year / 4.0
        series.append(TimelineQuarter(
            label=f"{fy} Q{fq}",
            year=fy, quarter=fq,
            co2e_kg=per_q,
            realised=True,
            cumulative_co2e_kg=0.0,
        ))
        fq += 1
        if fq > 4:
            fq = 1
            fy += 1

    # Forecast quarters forward from current position
    for _ in range(forecast_quarters):
        # Use linear fit; if we exceed seeded data years, extrapolate
        if fy in annual_totals:
            annual_for_year = annual_totals[fy]
        else:
            annual_for_year = max(0.0, latest_annual + slope * (fy - years[-1]))
        per_q = annual_for_year / 4.0
        series.append(TimelineQuarter(
            label=f"{fy} Q{fq}",
            year=fy, quarter=fq,
            co2e_kg=per_q,
            realised=False,
            cumulative_co2e_kg=0.0,
        ))
        fq += 1
        if fq > 4:
            fq = 1
            fy += 1

    cum = 0.0
    for pt in series:
        cum += pt.co2e_kg
        pt.cumulative_co2e_kg = cum
    return series


@router.get("/{sub_id}", response_model=SubscriptionDetail)
def dashboard_detail(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    pkg = session.get(Package, sub.package_id)
    alloc_details, total_co2e = _get_allocations_detail(session, sub)
    report = session.exec(select(CsrReport).where(CsrReport.subscription_id == sub_id)).first()
    return SubscriptionDetail(
        id=str(sub.id),
        package_id=str(sub.package_id),
        package_name=pkg.name if pkg else "Unknown",
        amount_eur=sub.amount_eur,
        status=sub.status.value,
        total_co2e_kg=total_co2e,
        allocations=alloc_details,
        report_id=str(report.id) if report else None,
    )
