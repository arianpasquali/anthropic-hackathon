import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.enums import StatusEnum
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.user import User
from src.backend.services.allocation import compute_allocations
from src.backend.services.auth import get_current_user

router = APIRouter(tags=["checkout"])


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    package_id: str
    amount_eur: float
    status: str


def _sub_to_response(sub: FundSubscription) -> SubscriptionResponse:
    return SubscriptionResponse(
        id=str(sub.id),
        user_id=str(sub.user_id),
        package_id=str(sub.package_id),
        amount_eur=sub.amount_eur,
        status=sub.status.value,
    )


@router.post("/packages/{package_id}/checkout", status_code=status.HTTP_201_CREATED, response_model=SubscriptionResponse)
def create_checkout(
    package_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    package = session.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404)
    sub = FundSubscription(
        user_id=user.id,
        package_id=package_id,
        amount_eur=package.price_eur,
        status=StatusEnum.pending,
    )
    session.add(sub)
    session.commit()
    session.refresh(sub)
    return _sub_to_response(sub)


@router.get("/checkout/{sub_id}/confirm", response_model=SubscriptionResponse)
def confirm_page(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    return _sub_to_response(sub)


@router.post("/checkout/{sub_id}/pay", response_model=SubscriptionResponse)
def pay(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    sub.status = StatusEnum.paid
    session.add(sub)
    compute_allocations(session, sub_id, commit=True)
    session.refresh(sub)
    return _sub_to_response(sub)
