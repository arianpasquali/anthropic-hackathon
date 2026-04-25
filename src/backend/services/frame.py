"""Full FRAME (Food Recovery to Avoid Methane Emissions) CO2e calculation.

Methodology: GFN + Carbon Trust, August 2024.
Reference: docs/methodology/FRAME-Methodology-GFN-2024.pdf

AE = BE − LE
  BE = Σ_category (kg_wet × DM_fraction × EF_NL_weighted)  [kgCO2e]
  LE = kg_received × waste_pct × DM_avg × EF_NL_weighted   [kgCO2e]
  AE = avoided emissions (the reportable claim)
"""
from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Session, select

from src.backend.models.enums import CounterfactualEnum
from src.backend.models.foodbank import AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.measurements import FoodCategories, FoodVolume

# ---------------------------------------------------------------------------
# NL destination mix (CBS Afvalmonitor 2023) — Table 1 from FRAME spec
# EFs in tCO2e/t DM (same numeric value as kgCO2e/kg DM)
# ---------------------------------------------------------------------------
_NL_DESTINATION_MIX: dict[str, tuple[float, float]] = {
    "incineration":          (0.56, 0.131),
    "composting":            (0.20, 0.392),
    "anaerobic_digestion":   (0.19, 0.359),
    "landfill_with_flaring": (0.05, 2.222),
}

# Weighted NL EF: kgCO2e per kg dry matter
_NL_EF_KG_PER_KG_DM: float = sum(
    share * ef for share, ef in _NL_DESTINATION_MIX.values()
)

# ---------------------------------------------------------------------------
# Dry matter fractions per food category (USDA FoodData Central defaults)
# DM = 1 − water_content
# ---------------------------------------------------------------------------
_DM: dict[str, float] = {
    "produce":   0.10,  # fruit, veg, potatoes — ~90% water
    "dairy":     0.13,  # dairy & eggs
    "meat_fish": 0.35,  # meat and fish
    "dry_goods": 0.88,  # pasta, rice, canned, dry pantry
    "bakery":    0.65,  # bread and bakery
    "prepared":  0.30,  # ready meals
}

# NL national average category split (Voedselbanken NL Feiten & Cijfers 2024)
_DEFAULT_SPLIT: dict[str, float] = {
    "produce":   0.365,
    "meat_fish": 0.240,
    "dairy":     0.151,
    "dry_goods": 0.144,
    "bakery":    0.100,
    "prepared":  0.000,
}

_EMISSION_FACTOR_SOURCE = (
    "GFN FRAME Methodology (Carbon Trust, Aug 2024); "
    "NL destination mix: CBS Afvalmonitor 2023; "
    "DM fractions: USDA FoodData Central"
)
_METHODOLOGY_VERSION = "FRAME-NL-v2.0"


def _be(kg_wet: float, category: str) -> float:
    """Baseline emission for one food category in kgCO2e."""
    return kg_wet * _DM[category] * _NL_EF_KG_PER_KG_DM


def compute_frame(session: Session, report: AnnualReport) -> FrameResult:
    """Compute FrameResult using full FRAME methodology (GFN/Carbon Trust 2024).

    Raises ValueError if neither FoodCategories nor FoodVolume weight data available.
    """
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report.id)).first()
    fc = session.exec(select(FoodCategories).where(FoodCategories.report_id == report.id)).first()

    _CAT_FIELDS = (
        "kg_produce", "kg_meat_fish", "kg_dairy_eggs",
        "kg_dry_goods", "kg_bread_bakery", "kg_prepared",
    )
    _cat_populated = sum(1 for f in _CAT_FIELDS if getattr(fc, f, None) not in (None, 0.0)) if fc else 0

    if fc and _cat_populated >= 1:
        produce   = fc.kg_produce      or 0.0
        meat_fish = fc.kg_meat_fish    or 0.0
        dairy     = fc.kg_dairy_eggs   or 0.0
        dry_goods = fc.kg_dry_goods    or 0.0
        bakery    = fc.kg_bread_bakery or 0.0
        prepared  = fc.kg_prepared     or 0.0
    elif fv and (fv.kg_received_total or (fv.kg_direct or 0) + (fv.kg_via_national_dc or 0)):
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

    # Step 1: Baseline emissions per category (BE)
    be_produce   = _be(produce,   "produce")
    be_meat_fish = _be(meat_fish, "meat_fish")
    be_dairy     = _be(dairy,     "dairy")
    be_dry_goods = _be(dry_goods, "dry_goods")
    be_bakery    = _be(bakery,    "bakery")
    be_prepared  = _be(prepared,  "prepared")
    baseline_co2e = be_produce + be_meat_fish + be_dairy + be_dry_goods + be_bakery + be_prepared

    # Step 2: Leakage — food wasted at the foodbank itself (LE)
    leakage_co2e = 0.0
    if fv and fv.waste_pct and (fv.kg_received_total or 0) > 0:
        kg_total = float(fv.kg_received_total)
        total_mix = produce + meat_fish + dairy + dry_goods + bakery + prepared
        if total_mix > 0:
            dm_avg = (
                produce   * _DM["produce"]
                + meat_fish * _DM["meat_fish"]
                + dairy     * _DM["dairy"]
                + dry_goods * _DM["dry_goods"]
                + bakery    * _DM["bakery"]
                + prepared  * _DM["prepared"]
            ) / total_mix
        else:
            dm_avg = 0.15  # conservative fallback
        leakage_co2e = kg_total * float(fv.waste_pct) * dm_avg * _NL_EF_KG_PER_KG_DM

    # Step 3: Avoided emissions (AE = BE − LE)
    avoided_co2e = baseline_co2e - leakage_co2e

    return FrameResult(
        report_id=report.id,
        co2e_total_kg=avoided_co2e,        # backward-compat: total = avoided
        co2e_produce_kg=be_produce,
        co2e_meat_fish_kg=be_meat_fish,
        co2e_dairy_eggs_kg=be_dairy,
        co2e_dry_goods_kg=be_dry_goods,
        co2e_bread_kg=be_bakery,
        co2e_prepared_kg=be_prepared,
        baseline_co2e_kg=baseline_co2e,
        leakage_co2e_kg=leakage_co2e,
        avoided_co2e_kg=avoided_co2e,
        counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
        emission_factor_source=_EMISSION_FACTOR_SOURCE,
        methodology_version=_METHODOLOGY_VERSION,
        computed_at=datetime.now(timezone.utc),
    )
