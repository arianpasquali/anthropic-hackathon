"""Public foodbanks endpoint for marketplace + transparency profiles.

Joins Foodbank with the latest AnnualReport per bank and its FrameResult,
FoodCategories, and PeopleServed measurements. Returns shape consumed by
the Next.js frontend (lat/lng injected from a hardcoded coords map keyed
by city name).
"""

from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.measurements import FoodCategories, PeopleServed

router = APIRouter(prefix="/foodbanks", tags=["foodbanks"])


# Hardcoded NL coordinates for the cities we ship data for. Frontend NL map
# pins use these. Extend as new banks are added.
BANK_COORDS: dict[str, tuple[float, float]] = {
    "rotterdam": (51.9225, 4.4792),
    "amsterdam": (52.3676, 4.9041),
    "den haag": (52.0705, 4.3007),
    "haaglanden": (52.0705, 4.3007),
    "utrecht": (52.0907, 5.1214),
    "eindhoven": (51.4416, 5.4697),
    "tilburg": (51.5555, 5.0913),
    "groningen": (53.2194, 6.5665),
    "breda": (51.5719, 4.7683),
    "nijmegen": (51.8126, 5.8372),
    "zwolle": (52.5168, 6.0830),
    "alkmaar": (52.6324, 4.7534),
    "almere": (52.3508, 5.2647),
    "amersfoort": (52.1561, 5.3878),
    "apeldoorn": (52.2112, 5.9699),
    "arnhem": (51.9851, 5.8987),
    "delft": (52.0116, 4.3571),
    "deventer": (52.2551, 6.1639),
    "dordrecht": (51.8133, 4.6901),
    "emmen": (52.7793, 6.9069),
    "enschede": (52.2215, 6.8937),
    "gouda": (52.0115, 4.7105),
    "haarlem": (52.3874, 4.6462),
    "hengelo": (52.2659, 6.7929),
    "hoorn": (52.6425, 5.0597),
    "leeuwarden": (53.2012, 5.7999),
    "leiden": (52.1601, 4.4970),
    "oss": (51.7645, 5.5184),
    "roermond": (51.1942, 5.9870),
    "veenendaal": (52.0286, 5.5589),
    "venlo": (51.3704, 6.1724),
    "bergen op zoom": (51.4946, 4.2872),
}


def _slugify(value: str) -> str:
    """City → URL slug. 'Bergen op Zoom' -> 'bergen-op-zoom'."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug


def _coords_for(city: str) -> tuple[Optional[float], Optional[float]]:
    key = city.lower()
    if key in BANK_COORDS:
        return BANK_COORDS[key]
    return (None, None)


# --- response shapes ------------------------------------------------------

class CategoryMix(BaseModel):
    produce: float
    dry_goods: float
    dairy: float
    bakery: float
    meat: float
    prepared: float
    eggs: float


class ProvenanceRecord(BaseModel):
    field: str
    source: str
    method: str


class FoodbankResponse(BaseModel):
    id: str
    slug: str
    name: str
    region: str
    city: str
    lat: Optional[float] = None
    lng: Optional[float] = None
    is_regional_dc: bool
    rdc_satellite_count: Optional[int] = None
    annual_kg_rescued: Optional[float] = None
    annual_tco2e: Optional[float] = None
    weighted_emission_factor: Optional[float] = None
    households_weekly: Optional[int] = None
    people_served: Optional[int] = None
    category_mix: Optional[CategoryMix] = None
    source_url: Optional[str] = None
    provenance: list[ProvenanceRecord] = []


# --- helpers --------------------------------------------------------------

def _category_mix(cats: Optional[FoodCategories]) -> Optional[CategoryMix]:
    if not cats:
        return None
    total = sum(
        v for v in (
            cats.kg_produce, cats.kg_dry_goods, cats.kg_dairy_eggs,
            cats.kg_bread_bakery, cats.kg_meat_fish, cats.kg_prepared,
        ) if v
    )
    if not total:
        return None
    return CategoryMix(
        produce=(cats.kg_produce or 0.0) / total,
        dry_goods=(cats.kg_dry_goods or 0.0) / total,
        # dairy/eggs are stored together; split is reported as combined "dairy"
        # for the frontend; eggs contribution is approximated downstream.
        dairy=(cats.kg_dairy_eggs or 0.0) / total,
        bakery=(cats.kg_bread_bakery or 0.0) / total,
        meat=(cats.kg_meat_fish or 0.0) / total,
        prepared=(cats.kg_prepared or 0.0) / total,
        eggs=0.0,
    )


def _provenance(cats: Optional[FoodCategories], people: Optional[PeopleServed]) -> list[ProvenanceRecord]:
    records: list[ProvenanceRecord] = []
    for model, fields in (
        (cats, ["kg_produce", "kg_meat_fish", "kg_dairy_eggs", "kg_dry_goods", "kg_bread_bakery", "kg_prepared"]),
        (people, ["households_weekly", "individuals_total", "children_count"]),
    ):
        if not model:
            continue
        for field in fields:
            value = getattr(model, field, None)
            source = getattr(model, f"{field}_source", None)
            method = getattr(model, f"{field}_method", None)
            if value is not None and source is not None:
                records.append(ProvenanceRecord(
                    field=field,
                    source=source.value if hasattr(source, "value") else str(source),
                    method=method or "",
                ))
    return records


def _build_response(fb: Foodbank, session: Session) -> FoodbankResponse:
    # Latest AnnualReport for this foodbank
    report = session.exec(
        select(AnnualReport)
        .where(AnnualReport.foodbank_id == fb.id)
        .order_by(AnnualReport.year.desc())
    ).first()

    frame: Optional[FrameResult] = None
    cats: Optional[FoodCategories] = None
    people: Optional[PeopleServed] = None
    annual_kg = None

    if report:
        frame = session.exec(select(FrameResult).where(FrameResult.report_id == report.id)).first()
        cats = session.exec(select(FoodCategories).where(FoodCategories.report_id == report.id)).first()
        people = session.exec(select(PeopleServed).where(PeopleServed.report_id == report.id)).first()
        if cats:
            annual_kg = sum(
                v for v in (
                    cats.kg_produce, cats.kg_dry_goods, cats.kg_dairy_eggs,
                    cats.kg_bread_bakery, cats.kg_meat_fish, cats.kg_prepared,
                ) if v
            ) or None

    weighted_ef = None
    if frame and annual_kg:
        weighted_ef = frame.co2e_total_kg / annual_kg if annual_kg > 0 else None

    lat, lng = _coords_for(fb.city)

    return FoodbankResponse(
        id=str(fb.id),
        slug=_slugify(fb.city),
        name=fb.name,
        region=fb.region.value,
        city=fb.city,
        lat=lat,
        lng=lng,
        is_regional_dc=fb.is_regional_dc,
        rdc_satellite_count=None,
        annual_kg_rescued=annual_kg,
        annual_tco2e=(frame.co2e_total_kg / 1000.0) if frame else None,
        weighted_emission_factor=weighted_ef,
        households_weekly=people.households_weekly if people else None,
        people_served=people.individuals_total if people else None,
        category_mix=_category_mix(cats),
        source_url=report.raw_file_path if report else None,
        provenance=_provenance(cats, people),
    )


# --- endpoints ------------------------------------------------------------

@router.get("", response_model=list[FoodbankResponse])
def list_foodbanks(session: Session = Depends(get_session)):
    foodbanks = session.exec(select(Foodbank).order_by(Foodbank.name)).all()
    return [_build_response(fb, session) for fb in foodbanks]


@router.get("/{slug}", response_model=FoodbankResponse)
def get_foodbank(slug: str, session: Session = Depends(get_session)):
    foodbanks = session.exec(select(Foodbank)).all()
    for fb in foodbanks:
        if _slugify(fb.city) == slug:
            return _build_response(fb, session)
    raise HTTPException(status_code=404, detail="foodbank not found")
