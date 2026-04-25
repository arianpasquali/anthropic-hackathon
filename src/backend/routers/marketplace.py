import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.enums import ImpactProfileEnum
from src.backend.models.marketplace import Package
from src.backend.routers.foodbanks import FoodbankResponse, _build_response
from src.backend.services.allocation import score_foodbanks

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


class ProjectedAllocationResponse(BaseModel):
    foodbank: FoodbankResponse
    weight_pct: float
    attributed_kg: float
    attributed_tco2e: float
    attributed_eur: float


class PackageDetailResponse(PackageResponse):
    projected_allocations: list[ProjectedAllocationResponse] = []


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


@router.get("/{package_id}", response_model=PackageDetailResponse)
def get_package(package_id: uuid.UUID, session: Session = Depends(get_session)):
    pkg = session.get(Package, package_id)
    if not pkg:
        raise HTTPException(status_code=404)

    scored = score_foodbanks(session, pkg)
    total_co2e_kg = sum(row.co2e_total_kg for row in scored) or 1.0
    projected = []
    for row in scored:
        attributed_kg_share = row.weight_pct * pkg.co2e_claim_kg
        # tCO2e attributed proportional to weight × bank's own per-bank CO2e contribution
        attributed_tco2e = (row.co2e_total_kg * row.weight_pct) / 1000.0
        projected.append(ProjectedAllocationResponse(
            foodbank=_build_response(row.foodbank, session),
            weight_pct=row.weight_pct,
            attributed_kg=attributed_kg_share,
            attributed_tco2e=attributed_tco2e,
            attributed_eur=row.weight_pct * pkg.price_eur,
        ))

    base = _pkg_to_response(pkg)
    return PackageDetailResponse(
        **base.model_dump(),
        projected_allocations=projected,
    )
