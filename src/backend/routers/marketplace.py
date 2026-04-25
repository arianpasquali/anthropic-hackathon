import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.enums import ImpactProfileEnum
from src.backend.models.marketplace import Package

router = APIRouter(prefix="/packages", tags=["packages"])


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
def list_packages(
    request: Request,
    profile: Optional[str] = None,
    session: Session = Depends(get_session),
):
    q = select(Package).where(Package.is_active == True)
    if profile:
        try:
            q = q.where(Package.impact_profile == ImpactProfileEnum(profile))
        except ValueError:
            pass
    packages = [_pkg_to_response(p) for p in session.exec(q).all()]

    if "text/markdown" in request.headers.get("accept", ""):
        lines = ["## Impact Packages\n"]
        for p in packages:
            lines.append(f"### {p.name}")
            lines.append(f"- **Region:** {p.region}")
            lines.append(f"- **Price:** €{p.price_eur:.0f}")
            lines.append(f"- **CO₂e claim:** {p.co2e_claim_kg:,.0f} kg")
            lines.append(f"- **Impact profile:** {p.impact_profile}")
            lines.append(f"- {p.description if p.description else ''}")
            lines.append("")
        return PlainTextResponse(
            content="\n".join(lines),
            media_type="text/markdown; charset=utf-8",
        )

    return packages


@router.get("/{package_id}", response_model=PackageResponse)
def get_package(package_id: uuid.UUID, session: Session = Depends(get_session)):
    pkg = session.get(Package, package_id)
    if not pkg:
        raise HTTPException(status_code=404)
    return _pkg_to_response(pkg)
