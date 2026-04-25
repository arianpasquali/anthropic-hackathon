import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import CsrReport, FundSubscription, Package
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
        annual = session.exec(select(AnnualReport).where(AnnualReport.foodbank_id == alloc.foodbank_id)).first()
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
