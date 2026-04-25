import uuid
from sqlmodel import Session, select

from src.backend.models.allocation import Allocation
from src.backend.models.enums import ImpactProfileEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import PeopleServed


def _score(
    co2e_kg: float,
    households: int,
    profile: ImpactProfileEnum,
    max_co2: float,
    max_households: float,
) -> float:
    if profile == ImpactProfileEnum.co2_focus:
        return co2e_kg
    if profile == ImpactProfileEnum.social_focus:
        return float(households)
    norm_co2 = co2e_kg / max_co2 if max_co2 > 0 else 0.0
    norm_social = households / max_households if max_households > 0 else 0.0
    return 0.5 * norm_co2 + 0.5 * norm_social


def compute_allocations(
    session: Session,
    subscription_id: uuid.UUID,
    commit: bool = False,
) -> list[Allocation]:
    sub = session.get(FundSubscription, subscription_id)
    package = session.get(Package, sub.package_id)

    rows = session.exec(
        select(Foodbank, FrameResult, PeopleServed)
        .join(AnnualReport, AnnualReport.foodbank_id == Foodbank.id)
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
                    package.impact_profile, max_co2, max_social))
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
