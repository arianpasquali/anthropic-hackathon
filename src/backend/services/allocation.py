import uuid
from sqlalchemy import func
from sqlmodel import Session, select

from src.backend.models.allocation import Allocation
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import PeopleServed
from src.backend.models.profile import ImpactProfile


def _score(
    co2e_kg: float,
    households: int,
    co2_weight: float,
    social_weight: float,
    max_co2: float,
    max_households: float,
) -> float:
    norm_co2 = co2e_kg / max_co2 if max_co2 > 0 else 0.0
    norm_social = households / max_households if max_households > 0 else 0.0
    return co2_weight * norm_co2 + social_weight * norm_social


def _get_profile_weights(session: Session, profile_key: str) -> tuple[float, float]:
    profile = session.exec(
        select(ImpactProfile).where(ImpactProfile.key == profile_key)
    ).first()
    if profile:
        return profile.co2_weight, profile.social_weight
    return 0.5, 0.5


def compute_allocations(
    session: Session,
    subscription_id: uuid.UUID,
    commit: bool = False,
) -> list[Allocation]:
    sub = session.get(FundSubscription, subscription_id)
    package = session.get(Package, sub.package_id)

    co2_weight, social_weight = _get_profile_weights(session, package.impact_profile.value)

    # Subquery: latest year per foodbank that has a FrameResult
    latest_year_sq = (
        select(AnnualReport.foodbank_id, func.max(AnnualReport.year).label("max_year"))
        .join(FrameResult, FrameResult.report_id == AnnualReport.id)
        .group_by(AnnualReport.foodbank_id)
        .subquery()
    )
    rows = session.exec(
        select(Foodbank, FrameResult, PeopleServed)
        .join(AnnualReport, AnnualReport.foodbank_id == Foodbank.id)
        .join(
            latest_year_sq,
            (latest_year_sq.c.foodbank_id == AnnualReport.foodbank_id)
            & (latest_year_sq.c.max_year == AnnualReport.year),
        )
        .join(FrameResult, FrameResult.report_id == AnnualReport.id)
        .join(PeopleServed, PeopleServed.report_id == AnnualReport.id)
    ).all()

    if not rows:
        return []

    co2_values = [frame.co2e_total_kg for _, frame, _ in rows]
    social_values = [float(people.households_weekly or 0) for _, _, people in rows]
    max_co2 = max(co2_values) if co2_values else 1.0
    max_social = max(social_values) if social_values else 1.0

    scored = [
        (fb, _score(frame.co2e_total_kg, people.households_weekly or 0,
                    co2_weight, social_weight, max_co2, max_social))
        for fb, frame, people in rows
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:package.top_n]

    total = sum(score for _, score in top)
    allocations = [
        Allocation(
            subscription_id=subscription_id,
            foodbank_id=fb.id,
            weight_pct=score / total if total > 0 else 1.0 / len(top),
        )
        for fb, score in top
    ]

    if commit:
        for alloc in allocations:
            session.add(alloc)
        session.commit()
        for alloc in allocations:
            session.refresh(alloc)

    return allocations
