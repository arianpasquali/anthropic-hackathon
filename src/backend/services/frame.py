"""FRAME-aligned CO2e calculation from extracted measurement tables."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from src.backend.models.enums import CounterfactualEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.measurements import FoodCategories, FoodVolume

# kg CO2e avoided per kg of food rescued (production + counterfactual disposal)
# Source: FAO Food Wastage Footprint (2013) + WRAP UK 2022 + RIVM Afvalmonitor 2024
_FACTORS: dict[str, float] = {
    "produce":    1.0,
    "bakery":     1.5,
    "dairy":      3.2,
    "meat_fish":  8.5,
    "dry_goods":  2.0,
    "prepared":   3.0,
}

# NL counterfactual: incineration-with-energy-recovery (vs US-default landfill)
_COUNTERFACTUAL = 0.93

_EMISSION_FACTOR_SOURCE = (
    "FAO Food Wastage Footprint 2013 + WRAP UK 2022; "
    "NL counterfactual: RIVM Afvalmonitor 2024"
)
_METHODOLOGY_VERSION = "FRAME-NL-v1.0"

# Fallback category split when FoodCategories is absent (national NL averages)
_DEFAULT_SPLIT: dict[str, float] = {
    "produce":   0.365,
    "meat_fish": 0.240,
    "dairy":     0.151,
    "dry_goods": 0.144,
    "bakery":    0.100,
    "prepared":  0.000,
}


def _co2e(kg: float, factor_key: str) -> float:
    return kg * _FACTORS[factor_key] * _COUNTERFACTUAL


def compute_frame(
    session: Session,
    report: AnnualReport,
) -> FrameResult:
    """Compute FrameResult for a report. Raises ValueError if no weight data available."""
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report.id)).first()
    fc = session.exec(select(FoodCategories).where(FoodCategories.report_id == report.id)).first()

    _CAT_FIELDS = ("kg_produce", "kg_meat_fish", "kg_dairy_eggs", "kg_dry_goods", "kg_bread_bakery", "kg_prepared")
    # Require ≥3 non-zero categories to trust the breakdown; a single non-null field is likely
    # a partial supplier figure extracted from a callout, not the bank's full category split.
    _cat_populated = sum(1 for f in _CAT_FIELDS if getattr(fc, f, None) not in (None, 0.0)) if fc else 0
    if fc and _cat_populated >= 3:
        produce    = fc.kg_produce     or 0.0
        meat_fish  = fc.kg_meat_fish   or 0.0
        dairy      = fc.kg_dairy_eggs  or 0.0
        dry_goods  = fc.kg_dry_goods   or 0.0
        bakery     = fc.kg_bread_bakery or 0.0
        prepared   = fc.kg_prepared    or 0.0
    elif fv and (fv.kg_received_total or (fv.kg_direct or 0) + (fv.kg_via_national_dc or 0)):
        # Fall back to national average split over best available total weight
        total = float(
            fv.kg_received_total
            or (fv.kg_direct or 0.0) + (fv.kg_via_national_dc or 0.0)
        )
        produce   = total * _DEFAULT_SPLIT["produce"]
        meat_fish = total * _DEFAULT_SPLIT["meat_fish"]
        dairy     = total * _DEFAULT_SPLIT["dairy"]
        dry_goods = total * _DEFAULT_SPLIT["dry_goods"]
        bakery    = total * _DEFAULT_SPLIT["bakery"]
        prepared  = total * _DEFAULT_SPLIT["prepared"]
    else:
        raise ValueError("No weight data (FoodCategories or FoodVolume.kg_received_total)")

    co2e_produce   = _co2e(produce,   "produce")
    co2e_meat_fish = _co2e(meat_fish, "meat_fish")
    co2e_dairy     = _co2e(dairy,     "dairy")
    co2e_dry_goods = _co2e(dry_goods, "dry_goods")
    co2e_bakery    = _co2e(bakery,    "bakery")
    co2e_prepared  = _co2e(prepared,  "prepared")

    return FrameResult(
        report_id=report.id,
        co2e_total_kg=co2e_produce + co2e_meat_fish + co2e_dairy + co2e_dry_goods + co2e_bakery + co2e_prepared,
        co2e_produce_kg=co2e_produce,
        co2e_meat_fish_kg=co2e_meat_fish,
        co2e_dairy_eggs_kg=co2e_dairy,
        co2e_dry_goods_kg=co2e_dry_goods,
        co2e_bread_kg=co2e_bakery,
        co2e_prepared_kg=co2e_prepared,
        counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
        emission_factor_source=_EMISSION_FACTOR_SOURCE,
        methodology_version=_METHODOLOGY_VERSION,
        computed_at=datetime.now(timezone.utc),
    )
