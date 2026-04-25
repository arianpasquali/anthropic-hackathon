import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.enums import ImpactProfileEnum
from src.backend.models.marketplace import Package

router = APIRouter(prefix="/packages")


class PackageResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    region: str
    price_eur: float
    co2e_claim_kg: float
    impact_profile: str
    top_n: int
    is_active: bool


def _pkg_to_response(pkg: Package) -> PackageResponse:
    return PackageResponse(
        id=str(pkg.id),
        name=pkg.name,
        description=pkg.description,
        region=pkg.region.value,
        price_eur=pkg.price_eur,
        co2e_claim_kg=pkg.co2e_claim_kg,
        impact_profile=pkg.impact_profile.value,
        top_n=pkg.top_n,
        is_active=pkg.is_active,
    )


@router.get("", response_model=list[PackageResponse])
def list_packages(profile: Optional[str] = None, session: Session = Depends(get_session)):
    q = select(Package).where(Package.is_active == True)
    if profile:
        try:
            q = q.where(Package.impact_profile == ImpactProfileEnum(profile))
        except ValueError:
            pass
    return [_pkg_to_response(p) for p in session.exec(q).all()]


@router.get("/{package_id}", response_model=PackageResponse)
def get_package(package_id: uuid.UUID, session: Session = Depends(get_session)):
    pkg = session.get(Package, package_id)
    if not pkg:
        raise HTTPException(status_code=404)
    return _pkg_to_response(pkg)
