import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.enums import ImpactProfileEnum
from src.backend.models.foodbank import AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import Package
from src.backend.routers.foodbanks import FoodbankResponse, TimelinePoint, _build_response, _foodbank_timeline
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


@router.get("/{package_id}/timeline", response_model=list[TimelinePoint])
def get_package_timeline(package_id: uuid.UUID, session: Session = Depends(get_session)):
    """Aggregate timeline across the fund's projected top-N foodbanks.

    Sums per-year CO2e and kg rescued over the banks the fund would currently
    allocate to. Years are taken from the union of report years across the set.
    """
    pkg = session.get(Package, package_id)
    if not pkg:
        raise HTTPException(status_code=404)
    scored = score_foodbanks(session, pkg)
    if not scored:
        return []
    per_bank = [(row, _foodbank_timeline(row.foodbank, session)) for row in scored]
    years = sorted({pt.year for _, pts in per_bank for pt in pts})
    out: list[TimelinePoint] = []
    for y in years:
        co2 = 0.0
        kg = 0.0
        hh = 0
        for row, pts in per_bank:
            pt = next((p for p in pts if p.year == y), None)
            if not pt:
                continue
            co2 += pt.co2e_kg * row.weight_pct
            if pt.annual_kg_rescued:
                kg += pt.annual_kg_rescued * row.weight_pct
            if pt.households_weekly:
                hh += int(pt.households_weekly * row.weight_pct)
        out.append(TimelinePoint(
            year=y,
            co2e_kg=co2,
            annual_kg_rescued=kg or None,
            households_weekly=hh or None,
        ))
    return out
