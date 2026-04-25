# Full FRAME Methodology Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the simple food-category × fixed-EF calculation with the full GFN/Carbon Trust FRAME methodology: dry matter conversion, NL destination-weighted EF, and leakage subtraction (AE = BE − LE).

**Architecture:** `FrameResult` gains three new audit fields (`baseline_co2e_kg`, `leakage_co2e_kg`, `avoided_co2e_kg`). The service rewrites to: (1) convert wet-kg per category → kg dry matter, (2) multiply by NL-weighted destination EF, (3) subtract leakage from `waste_pct`. `co2e_total_kg` is redefined as the avoided total (backward-compatible with all consumers).

**Tech Stack:** Python 3.13, SQLModel, SQLite/Alembic, pytest

---

## File Map

| File | Change |
|---|---|
| `src/backend/models/frame.py` | Add `baseline_co2e_kg`, `leakage_co2e_kg`, `avoided_co2e_kg` fields |
| `src/backend/services/frame.py` | Full rewrite — FRAME DM-based calculation |
| `migrations/versions/<hash>_frame_full_methodology.py` | New Alembic migration for 3 new columns |
| `src/backend/seed.py` | Populate new FrameResult fields |
| `tests/backend/models/test_frame.py` | Update model tests for new fields |
| `tests/backend/services/test_frame.py` | New — service-level unit tests |

---

## FRAME Constants Reference

**NL destination mix (CBS 2023):**
- Incineration: 56% → EF 0.131 tCO2e/t DM
- Composting: 20% → EF 0.392 tCO2e/t DM
- Anaerobic digestion (wet): 19% → EF 0.359 tCO2e/t DM
- Landfill with flaring: 5% → EF 2.222 tCO2e/t DM
- Weighted NL EF: **0.3311 tCO2e/t DM = 331.1 kgCO2e/t DM**

**DM fractions (USDA FoodData defaults):**
- produce: 0.10 (90% water)
- dairy_eggs: 0.13
- meat_fish: 0.35
- dry_goods: 0.88
- bread_bakery: 0.65
- prepared: 0.30

**NL category split fallback (Voedselbanken NL 2024):**
- produce: 36.5%, meat_fish: 24.0%, dairy: 15.1%,
  dry_goods: 14.4%, bakery: 10.0%, prepared: 0.0%

**Core formula:**
```
BE_category = kg_wet_category × DM_category × NL_EF_kgCO2e_per_kg_DM
BE_total    = Σ BE_category
leakage_kg  = kg_received_total × waste_pct × DM_avg × NL_EF_kgCO2e_per_kg_DM
AE          = BE_total − leakage_kg        (= co2e_total_kg)
```

---

## Task 1: Extend FrameResult model

**Files:**
- Modify: `src/backend/models/frame.py`

- [ ] **Step 1: Write failing model test**

```python
# tests/backend/models/test_frame.py — add after existing tests

def test_frame_result_has_baseline_leakage_avoided(session: Session, report: AnnualReport):
    result = FrameResult(
        report_id=report.id,
        co2e_total_kg=950.0,
        co2e_produce_kg=300.0,
        co2e_meat_fish_kg=200.0,
        co2e_dairy_eggs_kg=150.0,
        co2e_dry_goods_kg=200.0,
        co2e_bread_kg=100.0,
        baseline_co2e_kg=1000.0,
        leakage_co2e_kg=50.0,
        avoided_co2e_kg=950.0,
        emission_factor_source="GFN FRAME 2024",
        methodology_version="FRAME-NL-v2.0",
    )
    session.add(result)
    session.commit()
    session.refresh(result)
    assert result.baseline_co2e_kg == 1000.0
    assert result.leakage_co2e_kg == 50.0
    assert result.avoided_co2e_kg == 950.0
```

- [ ] **Step 2: Run test — expect FAIL**

```bash
cd /Users/baukebrenninkmeijer/Developer/anthropic-hackathon
uv run pytest tests/backend/models/test_frame.py::test_frame_result_has_baseline_leakage_avoided -v
```

Expected: `FAILED` — `FrameResult` has no attribute `baseline_co2e_kg`

- [ ] **Step 3: Add fields to model**

```python
# src/backend/models/frame.py — full file replacement
import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

from src.backend.models.enums import CounterfactualEnum


class FrameResult(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    # Avoided emissions = baseline − leakage (the auditable claim)
    co2e_total_kg: float  # = avoided_co2e_kg; kept for backward compat
    co2e_produce_kg: float
    co2e_meat_fish_kg: float
    co2e_dairy_eggs_kg: float
    co2e_dry_goods_kg: float
    co2e_bread_kg: float
    co2e_prepared_kg: float | None = None

    # Full FRAME breakdown
    baseline_co2e_kg: float | None = None   # BE before leakage
    leakage_co2e_kg: float | None = None    # LE = foodbank waste
    avoided_co2e_kg: float | None = None    # AE = BE − LE

    counterfactual_route: CounterfactualEnum = CounterfactualEnum.incineration_energy_recovery
    emission_factor_source: str
    methodology_version: str
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 4: Run test — expect PASS**

```bash
uv run pytest tests/backend/models/test_frame.py -v
```

Expected: all PASS (new test + old tests)

- [ ] **Step 5: Create Alembic migration**

```bash
uv run alembic revision --autogenerate -m "frame_full_methodology_fields"
```

Review the generated file in `migrations/versions/` — confirm it adds:
- `baseline_co2e_kg FLOAT`
- `leakage_co2e_kg FLOAT`
- `avoided_co2e_kg FLOAT`

Then apply:

```bash
uv run alembic upgrade head
```

- [ ] **Step 6: Commit**

```bash
git add src/backend/models/frame.py migrations/versions/
git commit -m "feat: extend FrameResult with baseline/leakage/avoided fields"
```

---

## Task 2: Rewrite frame service with full FRAME calculation

**Files:**
- Modify: `src/backend/services/frame.py`
- Create: `tests/backend/services/test_frame.py`

- [ ] **Step 1: Write failing service tests**

Create `tests/backend/services/test_frame.py`:

```python
from datetime import date
import pytest
from sqlmodel import Session

from src.backend.models.enums import RegionEnum, SourceEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.measurements import FoodCategories, FoodVolume
from src.backend.services.frame import compute_frame, _NL_EF_KG_PER_KG_DM, _DM


def _make_report(session: Session) -> AnnualReport:
    fb = Foodbank(name="Test", city="Test", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    r = AnnualReport(
        foodbank_id=fb.id, year=2024,
        period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
        raw_file_path="t.txt", ingestion_model="test",
    )
    session.add(r)
    session.commit()
    return r


def test_compute_frame_with_categories_no_waste(session: Session):
    """100 kg produce only, no waste → BE = AE, leakage = 0."""
    report = _make_report(session)
    fc = FoodCategories(
        report_id=report.id,
        kg_produce=100.0, kg_produce_source=SourceEnum.extracted, kg_produce_method="test",
        kg_meat_fish=0.0, kg_meat_fish_source=SourceEnum.extracted, kg_meat_fish_method="test",
        kg_dairy_eggs=0.0, kg_dairy_eggs_source=SourceEnum.extracted, kg_dairy_eggs_method="test",
        kg_dry_goods=0.0, kg_dry_goods_source=SourceEnum.extracted, kg_dry_goods_method="test",
        kg_bread_bakery=0.0, kg_bread_bakery_source=SourceEnum.extracted, kg_bread_bakery_method="test",
    )
    session.add(fc)
    session.commit()

    result = compute_frame(session, report)

    # BE_produce = 100 kg × DM_produce × NL_EF
    expected_be_produce = 100.0 * _DM["produce"] * _NL_EF_KG_PER_KG_DM
    assert abs(result.co2e_produce_kg - expected_be_produce) < 0.01
    assert result.leakage_co2e_kg == pytest.approx(0.0)
    assert result.avoided_co2e_kg == pytest.approx(result.baseline_co2e_kg)
    assert result.co2e_total_kg == pytest.approx(result.avoided_co2e_kg)


def test_compute_frame_leakage_reduces_avoided(session: Session):
    """10% waste reduces avoided vs baseline."""
    report = _make_report(session)
    fv = FoodVolume(
        report_id=report.id,
        kg_received_total=1000.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="test",
        waste_pct=0.10,
        waste_pct_source=SourceEnum.extracted,
        waste_pct_method="test",
    )
    session.add(fv)
    session.commit()

    result = compute_frame(session, report)

    assert result.leakage_co2e_kg > 0
    assert result.avoided_co2e_kg < result.baseline_co2e_kg
    assert result.co2e_total_kg == pytest.approx(result.avoided_co2e_kg)


def test_compute_frame_no_waste_data_uses_zero_leakage(session: Session):
    """No FoodVolume → leakage defaults to 0."""
    report = _make_report(session)
    fc = FoodCategories(
        report_id=report.id,
        kg_produce=500.0, kg_produce_source=SourceEnum.extracted, kg_produce_method="test",
        kg_meat_fish=0.0, kg_meat_fish_source=SourceEnum.extracted, kg_meat_fish_method="test",
        kg_dairy_eggs=0.0, kg_dairy_eggs_source=SourceEnum.extracted, kg_dairy_eggs_method="test",
        kg_dry_goods=0.0, kg_dry_goods_source=SourceEnum.extracted, kg_dry_goods_method="test",
        kg_bread_bakery=0.0, kg_bread_bakery_source=SourceEnum.extracted, kg_bread_bakery_method="test",
    )
    session.add(fc)
    session.commit()

    result = compute_frame(session, report)
    assert result.leakage_co2e_kg == pytest.approx(0.0)
    assert result.avoided_co2e_kg == pytest.approx(result.baseline_co2e_kg)


def test_compute_frame_fallback_to_total_kg(session: Session):
    """No FoodCategories → apply NL split to FoodVolume.kg_received_total."""
    report = _make_report(session)
    fv = FoodVolume(
        report_id=report.id,
        kg_received_total=1000.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="test",
    )
    session.add(fv)
    session.commit()

    result = compute_frame(session, report)
    assert result.co2e_total_kg > 0
    assert result.baseline_co2e_kg > 0
    assert result.methodology_version == "FRAME-NL-v2.0"


def test_compute_frame_raises_with_no_data(session: Session):
    """No FoodCategories and no FoodVolume → ValueError."""
    report = _make_report(session)
    with pytest.raises(ValueError, match="No weight data"):
        compute_frame(session, report)
```

- [ ] **Step 2: Run tests — expect FAIL**

```bash
uv run pytest tests/backend/services/test_frame.py -v
```

Expected: `FAILED` — `cannot import name '_NL_EF_KG_PER_KG_DM'` or similar

- [ ] **Step 3: Rewrite service**

```python
# src/backend/services/frame.py — full replacement
"""Full FRAME (Food Recovery to Avoid Methane Emissions) CO2e calculation.

Methodology: GFN + Carbon Trust, August 2024.
Reference: https://www.foodbanking.org/resources/frame-methodology/

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
# EFs in tCO2e/t DM → converted to kgCO2e/kg DM (same numeric value × 1)
# ---------------------------------------------------------------------------
_NL_DESTINATION_MIX: dict[str, tuple[float, float]] = {
    # destination: (share, EF tCO2e/t DM)
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
    "produce":    0.10,   # fruit, veg, potatoes — ~90% water
    "dairy":      0.13,   # dairy & eggs
    "meat_fish":  0.35,   # meat and fish
    "dry_goods":  0.88,   # pasta, rice, canned, dry pantry
    "bakery":     0.65,   # bread and bakery
    "prepared":   0.30,   # ready meals
}

# NL national average category split (Voedselbanken NL Feiten & Cijfers 2024)
# Used when FoodCategories is absent or has <3 populated fields.
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
    """Baseline emission for one food category (kgCO2e)."""
    return kg_wet * _DM[category] * _NL_EF_KG_PER_KG_DM


def compute_frame(session: Session, report: AnnualReport) -> FrameResult:
    """Compute FrameResult using full FRAME methodology.

    Raises ValueError if neither FoodCategories nor FoodVolume weight is available.
    """
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report.id)).first()
    fc = session.exec(select(FoodCategories).where(FoodCategories.report_id == report.id)).first()

    _CAT_FIELDS = (
        "kg_produce", "kg_meat_fish", "kg_dairy_eggs",
        "kg_dry_goods", "kg_bread_bakery", "kg_prepared",
    )
    _cat_populated = sum(1 for f in _CAT_FIELDS if getattr(fc, f, None) not in (None, 0.0)) if fc else 0

    if fc and _cat_populated >= 3:
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

    # Step 2: Leakage — food wasted at the foodbank
    leakage_co2e = 0.0
    if fv and fv.waste_pct and (fv.kg_received_total or 0) > 0:
        kg_total = float(fv.kg_received_total)
        # Weighted-average DM for the food mix
        total_kg = produce + meat_fish + dairy + dry_goods + bakery + prepared
        if total_kg > 0:
            dm_avg = (
                produce   * _DM["produce"]
                + meat_fish * _DM["meat_fish"]
                + dairy     * _DM["dairy"]
                + dry_goods * _DM["dry_goods"]
                + bakery    * _DM["bakery"]
                + prepared  * _DM["prepared"]
            ) / total_kg
        else:
            dm_avg = 0.15  # conservative default
        leakage_co2e = kg_total * float(fv.waste_pct) * dm_avg * _NL_EF_KG_PER_KG_DM

    # Step 3: Avoided emissions
    avoided_co2e = baseline_co2e - leakage_co2e

    return FrameResult(
        report_id=report.id,
        co2e_total_kg=avoided_co2e,         # backward-compat: total = avoided
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
```

- [ ] **Step 4: Run tests — expect PASS**

```bash
uv run pytest tests/backend/services/test_frame.py -v
```

Expected: all 5 PASS

- [ ] **Step 5: Run full test suite to check no regressions**

```bash
uv run pytest --tb=short -q
```

Expected: all PASS (existing tests use `co2e_total_kg` which still exists)

- [ ] **Step 6: Commit**

```bash
git add src/backend/services/frame.py tests/backend/services/test_frame.py
git commit -m "feat: implement full GFN FRAME methodology — DM-based, NL destination mix, leakage subtraction"
```

---

## Task 3: Update seed.py for new fields

**Files:**
- Modify: `src/backend/seed.py`

- [ ] **Step 1: Find the FrameResult creation in seed.py**

```bash
grep -n "FrameResult" src/backend/seed.py
```

- [ ] **Step 2: Update seed to populate new fields**

Find the `FrameResult(` block in `src/backend/seed.py` (around line 134). Replace it:

```python
# In seed.py — the FrameResult construction block
# (co2 is the variable holding the total co2e kg value in the existing seed loop)
frame = FrameResult(
    report_id=report.id,
    co2e_total_kg=co2,
    co2e_produce_kg=co2 * 0.365,
    co2e_meat_fish_kg=co2 * 0.240,
    co2e_dairy_eggs_kg=co2 * 0.151,
    co2e_dry_goods_kg=co2 * 0.144,
    co2e_bread_kg=co2 * 0.100,
    baseline_co2e_kg=co2 * 1.05,     # approximate: avoided ≈ 95% of baseline
    leakage_co2e_kg=co2 * 0.05,
    avoided_co2e_kg=co2,
    emission_factor_source=(
        "GFN FRAME Methodology (Carbon Trust, Aug 2024); "
        "NL destination mix: CBS Afvalmonitor 2023; "
        "DM fractions: USDA FoodData Central"
    ),
    methodology_version="FRAME-NL-v2.0",
)
```

- [ ] **Step 3: Verify seed runs**

```bash
python -m src.backend.seed
```

Expected: no errors, exits 0

- [ ] **Step 4: Commit**

```bash
git add src/backend/seed.py
git commit -m "chore: update seed FrameResult with FRAME-NL-v2.0 fields"
```

---

## Task 4: Update existing model tests

**Files:**
- Modify: `tests/backend/models/test_frame.py`

The existing tests create `FrameResult` without the new nullable fields — they will still pass because the fields default to `None`. Run to confirm:

- [ ] **Step 1: Verify existing model tests still pass**

```bash
uv run pytest tests/backend/models/test_frame.py -v
```

Expected: all PASS (nullable fields default to None)

- [ ] **Step 2: No changes needed — confirm and note**

All 3 existing tests + 1 new test from Task 1 should PASS. No edits required.

---

## Task 5: Final validation

- [ ] **Step 1: Full test suite**

```bash
uv run pytest --tb=short
```

Expected: all PASS

- [ ] **Step 2: Verify alembic current**

```bash
uv run alembic current
```

Expected: shows `head`

- [ ] **Step 3: Smoke test via CLI recalc**

```bash
python -m src.backend.preprocessing.cli recalc --help
```

Verify the recalc command exists and shows help without errors.

- [ ] **Step 4: Final commit if any loose files**

```bash
git status
```

If clean: done. If any files remain staged, commit them.
