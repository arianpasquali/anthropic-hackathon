# Ingestion Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Typer CLI that reads foodbank annual report PDFs (or pre-extracted .txt files), uses parallel Claude API calls to extract structured metrics into Pydantic schemas, detects model drift with Sonnet fallback, and writes all results into the SQLModel database.

**Architecture:** Five pure-Pydantic extraction schemas (one per measurement section) with section-specific system prompts. Claude Haiku runs 5 parallel calls via `run_in_executor`; a drift detector checks returned key overlap against the schema and retries with Sonnet on failure. A sync DB writer maps extraction results to SQLModel tables with provenance (`source=extracted`, `method=<citation>`).

**Tech Stack:** Python 3.13, Typer, Anthropic SDK, pdfplumber, asyncio, SQLModel, loguru, python-dotenv

---

## File Map

| File | Responsibility |
|---|---|
| `src/backend/preprocessing/__init__.py` | Package marker |
| `src/backend/preprocessing/schemas.py` | 5 Pydantic extraction schemas + `ExtractionResult` Pydantic model + per-section system prompts |
| `src/backend/preprocessing/extractor.py` | `extract_text(pdf_path) -> str`: .txt sidecar first, pdfplumber fallback |
| `src/backend/preprocessing/claude.py` | `extract_all(text, model) -> ExtractionResult`: parallel calls + drift detection + Sonnet fallback |
| `src/backend/preprocessing/writer.py` | `write_report(session, ...) -> AnnualReport`: get_or_create Foodbank, skip/overwrite AnnualReport, write 5 measurement tables |
| `src/backend/preprocessing/cli.py` | Typer app: `ingest` (single file) + `ingest-dir` (batch with hardcoded bank map) |
| `tests/backend/preprocessing/__init__.py` | Package marker |
| `tests/backend/preprocessing/test_schemas.py` | Schema field coverage, JSON schema generation |
| `tests/backend/preprocessing/test_extractor.py` | .txt sidecar path, pdfplumber fallback, missing file error |
| `tests/backend/preprocessing/test_claude.py` | Drift detection logic (no API calls) |
| `tests/backend/preprocessing/test_writer.py` | DB write, get_or_create, force overwrite |
| ~~`tests/backend/preprocessing/test_cli.py`~~ | Covered by unit tests + manual smoke test |

---

## Task 1: Dependencies + package structure

**Files:**
- Modify: `pyproject.toml`
- Create: `src/backend/preprocessing/__init__.py`
- Create: `tests/backend/preprocessing/__init__.py`

- [ ] **Step 1: Add missing deps to pyproject.toml**

```toml
dependencies = [
    "sqlmodel>=0.0.21",
    "sqlalchemy>=2.0",
    "passlib[bcrypt]>=1.7.4",
    "fastapi[standard]>=0.115",
    "jinja2>=3.1",
    "itsdangerous>=2.2",
    "anthropic>=0.40",
    "python-multipart>=0.0.9",
    "typer>=0.12.0",
    "python-dotenv>=1.0.0",
    "pdfplumber>=0.11.0",
    "loguru>=0.7.0",
]
```

- [ ] **Step 2: Install**

```bash
uv sync --extra dev
```

Expected: resolves without error.

- [ ] **Step 3: Create package markers**

```bash
touch src/backend/preprocessing/__init__.py
mkdir -p tests/backend/preprocessing
touch tests/backend/preprocessing/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml uv.lock src/backend/preprocessing/__init__.py tests/backend/preprocessing/__init__.py
git commit -m "chore: add typer, pdfplumber, loguru deps; scaffold preprocessing package"
```

---

## Task 2: Extraction schemas + prompts

**Files:**
- Create: `src/backend/preprocessing/schemas.py`
- Create: `tests/backend/preprocessing/test_schemas.py`

- [ ] **Step 1: Write failing test**

`tests/backend/preprocessing/test_schemas.py`:

```python
from src.backend.preprocessing.schemas import (
    FoodVolumeExtraction,
    FoodCategoriesExtraction,
    PeopleServedExtraction,
    OperationsExtraction,
    DonationsExtraction,
    ExtractionResult,
    SECTION_PROMPTS,
)


def test_food_volume_schema_fields():
    schema = FoodVolumeExtraction.model_json_schema()
    props = schema["properties"]
    assert "kg_received_total" in props
    assert "kg_received_total_method" in props
    assert "waste_pct" in props
    assert "waste_pct_method" in props
    assert "parcels_distributed" in props


def test_food_categories_schema_fields():
    schema = FoodCategoriesExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["kg_produce", "kg_meat_fish", "kg_dairy_eggs", "kg_dry_goods", "kg_bread_bakery", "kg_prepared"]:
        assert field in props
        assert f"{field}_method" in props


def test_people_served_schema_fields():
    schema = PeopleServedExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["households_weekly", "individuals_total", "children_count", "pct_under_18"]:
        assert field in props


def test_operations_schema_fields():
    schema = OperationsExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["volunteers_count", "distribution_locations", "annual_budget_eur", "total_expenditure_eur"]:
        assert field in props


def test_donations_schema_fields():
    schema = DonationsExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["food_supermarket_kg", "food_company_kg", "money_individuals_eur", "money_companies_eur"]:
        assert field in props


def test_all_fields_optional():
    # All extraction schemas must instantiate with zero arguments
    FoodVolumeExtraction()
    FoodCategoriesExtraction()
    PeopleServedExtraction()
    OperationsExtraction()
    DonationsExtraction()


def test_extraction_result_holds_all_sections():
    result = ExtractionResult(
        food_volume=FoodVolumeExtraction(),
        food_categories=FoodCategoriesExtraction(),
        people_served=PeopleServedExtraction(),
        operations=OperationsExtraction(),
        donations=DonationsExtraction(),
    )
    assert result.food_volume is not None
    assert result.people_served is not None


def test_section_prompts_exist_for_all_tools():
    tool_names = [
        "extract_food_volume",
        "extract_food_categories",
        "extract_people_served",
        "extract_operations",
        "extract_donations",
    ]
    for name in tool_names:
        assert name in SECTION_PROMPTS
        assert len(SECTION_PROMPTS[name]) > 50
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/preprocessing/test_schemas.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement schemas**

`src/backend/preprocessing/schemas.py`:

```python
from decimal import Decimal

from pydantic import BaseModel, Field


class FoodVolumeExtraction(BaseModel):
    kg_received_total: float | None = None
    kg_received_total_method: str | None = None
    kg_via_national_dc: float | None = None
    kg_via_national_dc_method: str | None = None
    kg_direct: float | None = None
    kg_direct_method: str | None = None
    waste_pct: float | None = Field(default=None, ge=0.0, le=1.0)
    waste_pct_method: str | None = None
    parcels_distributed: int | None = None
    parcels_distributed_method: str | None = None
    avg_products_per_parcel: float | None = None
    avg_products_per_parcel_method: str | None = None
    pct_schijf_van_vijf: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_schijf_van_vijf_method: str | None = None
    food_value_eur: float | None = None
    food_value_eur_method: str | None = None


class FoodCategoriesExtraction(BaseModel):
    kg_produce: float | None = None
    kg_produce_method: str | None = None
    kg_meat_fish: float | None = None
    kg_meat_fish_method: str | None = None
    kg_dairy_eggs: float | None = None
    kg_dairy_eggs_method: str | None = None
    kg_dry_goods: float | None = None
    kg_dry_goods_method: str | None = None
    kg_bread_bakery: float | None = None
    kg_bread_bakery_method: str | None = None
    kg_prepared: float | None = None
    kg_prepared_method: str | None = None


class PeopleServedExtraction(BaseModel):
    households_weekly: int | None = None
    households_weekly_method: str | None = None
    individuals_total: int | None = None
    individuals_total_method: str | None = None
    children_count: int | None = None
    children_count_method: str | None = None
    pct_under_18: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_under_18_method: str | None = None
    pct_single_adults: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_single_adults_method: str | None = None
    pct_single_parent: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_single_parent_method: str | None = None
    pct_families: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_families_method: str | None = None
    pct_couples: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_couples_method: str | None = None


class OperationsExtraction(BaseModel):
    volunteers_count: int | None = None
    volunteers_count_method: str | None = None
    distribution_locations: int | None = None
    distribution_locations_method: str | None = None
    satellite_banks_served: int | None = None
    satellite_banks_served_method: str | None = None
    annual_budget_eur: float | None = None
    annual_budget_eur_method: str | None = None
    total_expenditure_eur: float | None = None
    total_expenditure_eur_method: str | None = None


class DonationsExtraction(BaseModel):
    food_supermarket_kg: float | None = None
    food_supermarket_kg_method: str | None = None
    food_company_kg: float | None = None
    food_company_kg_method: str | None = None
    food_dc_kg: float | None = None
    food_dc_kg_method: str | None = None
    money_individuals_eur: float | None = None
    money_individuals_eur_method: str | None = None
    money_companies_eur: float | None = None
    money_companies_eur_method: str | None = None
    money_orgs_eur: float | None = None
    money_orgs_eur_method: str | None = None
    money_government_eur: float | None = None
    money_government_eur_method: str | None = None


class ExtractionResult(BaseModel):
    food_volume: FoodVolumeExtraction
    food_categories: FoodCategoriesExtraction
    people_served: PeopleServedExtraction
    operations: OperationsExtraction
    donations: DonationsExtraction


_BASE_INSTRUCTIONS = """You extract structured data from Dutch foodbank annual reports.
Extract ONLY values explicitly stated in the text — do not infer or estimate.
For each extracted value, fill the companion _method field with a short citation
(e.g. "p.10 'Ontvangen voedsel 507.496 kilo'").
All percentage/fraction fields must be expressed as fractions 0–1
(e.g. 0.006 for 0.6%, 0.37 for 37%). Return null for any value not found."""

SECTION_PROMPTS: dict[str, str] = {
    "extract_food_volume": f"""{_BASE_INSTRUCTIONS}

Extract ONLY food weight and volume metrics:
total kg received, kg from national DC (distributiecentrum), kg from direct donations,
waste percentage (naar de stort), total parcels/packages distributed,
average products per parcel, percentage healthy foods (Schijf van Vijf), food value in euros.
Do NOT extract household counts, demographics, volunteer counts, or donation money.""",

    "extract_food_categories": f"""{_BASE_INSTRUCTIONS}

Extract ONLY food broken down by category in kilograms:
produce/vegetables/fruit (groente en fruit, aardappelen),
meat and fish (vlees en vis),
dairy and eggs (zuivel en eieren),
dry goods/pantry items (droge kruidenierswaren),
bread and bakery (brood),
prepared foods (bereide maaltijden).
Do NOT extract totals, household counts, or money figures.""",

    "extract_people_served": f"""{_BASE_INSTRUCTIONS}

Extract ONLY beneficiary and demographic data:
weekly household count (huishoudens per week), total individuals (personen),
number of children (kinderen onder 18),
percentage under 18 (as fraction 0–1),
percentage single adults, single-parent households, families, couples.
Do NOT extract food weights, kg figures, or financial data.""",

    "extract_operations": f"""{_BASE_INSTRUCTIONS}

Extract ONLY operational metrics:
number of volunteers (vrijwilligers),
number of distribution locations (locaties, uitgiftepunten),
number of satellite banks served (aangesloten voedselbanken),
annual budget (begroting in euros),
total expenditure/costs (uitgaven, kosten in euros).
Do NOT extract food weights, household counts, or donation breakdowns.""",

    "extract_donations": f"""{_BASE_INSTRUCTIONS}

Extract ONLY donation data — both food and monetary:
food donated by supermarkets (kg), food donated by companies/suppliers (kg),
food received via national DC (kg),
monetary donations from individuals (particulieren in euros),
from companies/businesses (bedrijven in euros),
from non-profit organisations (organisaties in euros),
from government/municipality (gemeente, overheid in euros).
Do NOT extract household counts, volunteer numbers, or food category breakdowns.""",
}

TOOL_SCHEMA_MAP: dict[str, type] = {
    "extract_food_volume": FoodVolumeExtraction,
    "extract_food_categories": FoodCategoriesExtraction,
    "extract_people_served": PeopleServedExtraction,
    "extract_operations": OperationsExtraction,
    "extract_donations": DonationsExtraction,
}
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/preprocessing/test_schemas.py -v
```

Expected: 9 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/preprocessing/schemas.py tests/backend/preprocessing/test_schemas.py
git commit -m "feat: add extraction schemas and per-section system prompts"
```

---

## Task 3: Text extractor

**Files:**
- Create: `src/backend/preprocessing/extractor.py`
- Create: `tests/backend/preprocessing/test_extractor.py`

- [ ] **Step 1: Write failing test**

`tests/backend/preprocessing/test_extractor.py`:

```python
import pytest
from pathlib import Path

from src.backend.preprocessing.extractor import extract_text, ExtractionError


def test_reads_txt_sidecar(tmp_path: Path):
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    txt = tmp_path / "report.txt"
    txt.write_text("Voedselbank tekst inhoud", encoding="utf-8")

    result = extract_text(pdf)
    assert result == "Voedselbank tekst inhoud"


def test_returns_string_not_empty(tmp_path: Path):
    pdf = tmp_path / "report.pdf"
    pdf.write_bytes(b"%PDF-1.4 fake")
    txt = tmp_path / "report.txt"
    txt.write_text("some content", encoding="utf-8")

    result = extract_text(pdf)
    assert isinstance(result, str)
    assert len(result) > 0


def test_raises_on_missing_file(tmp_path: Path):
    missing = tmp_path / "nonexistent.pdf"
    with pytest.raises(ExtractionError, match="not found"):
        extract_text(missing)


def test_accepts_txt_path_directly(tmp_path: Path):
    txt = tmp_path / "report.txt"
    txt.write_text("direct txt content", encoding="utf-8")

    result = extract_text(txt)
    assert result == "direct txt content"
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/preprocessing/test_extractor.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement extractor**

`src/backend/preprocessing/extractor.py`:

```python
from pathlib import Path

from loguru import logger


class ExtractionError(Exception):
    pass


def extract_text(path: Path) -> str:
    path = Path(path)

    if not path.exists():
        raise ExtractionError(f"File not found: {path}")

    # If a .txt file is given directly, read it
    if path.suffix.lower() == ".txt":
        logger.debug(f"Reading txt directly: {path}")
        return path.read_text(encoding="utf-8")

    # Try .txt sidecar alongside the PDF
    txt_sidecar = path.with_suffix(".txt")
    if txt_sidecar.exists():
        logger.debug(f"Using txt sidecar: {txt_sidecar}")
        return txt_sidecar.read_text(encoding="utf-8")

    # Fall back to pdfplumber
    logger.debug(f"Extracting text from PDF: {path}")
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages).strip()
        logger.debug(f"Extracted {len(text)} chars from {len(pages)} pages")
        return text
    except Exception as e:
        raise ExtractionError(f"pdfplumber failed on {path}: {e}") from e
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/preprocessing/test_extractor.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/preprocessing/extractor.py tests/backend/preprocessing/test_extractor.py
git commit -m "feat: add text extractor with txt sidecar and pdfplumber fallback"
```

---

## Task 4: Claude client + drift detection

**Files:**
- Create: `src/backend/preprocessing/claude.py`
- Create: `tests/backend/preprocessing/test_claude.py`

- [ ] **Step 1: Write failing test**

`tests/backend/preprocessing/test_claude.py`:

```python
from pydantic import BaseModel

from src.backend.preprocessing.claude import detect_drift
from src.backend.preprocessing.schemas import (
    FoodVolumeExtraction,
    PeopleServedExtraction,
)


def test_detect_drift_no_drift():
    raw = {
        "households_weekly": 335,
        "individuals_total": 2046,
        "pct_under_18": 0.157,
    }
    assert detect_drift(raw, PeopleServedExtraction) is False


def test_detect_drift_wrong_schema():
    # Haiku returned food_volume fields for a people_served call
    raw = {
        "kg_received_total": 507496,
        "waste_pct": 0.006,
        "parcels_distributed": 17748,
    }
    assert detect_drift(raw, PeopleServedExtraction) is True


def test_detect_drift_empty_result():
    # All nulls — Claude found nothing; this is not drift, just no data
    assert detect_drift({}, PeopleServedExtraction) is False


def test_detect_drift_partial_overlap():
    # 1 out of 3 keys matches — below 50% threshold → drift
    raw = {
        "households_weekly": 335,   # correct field
        "kg_received_total": 507496,  # wrong field
        "waste_pct": 0.006,           # wrong field
    }
    assert detect_drift(raw, PeopleServedExtraction) is True


def test_detect_drift_majority_correct():
    # 3 out of 4 keys match → not drift
    raw = {
        "households_weekly": 335,
        "individuals_total": 2046,
        "children_count": 321,
        "kg_received_total": None,  # stray field but only 1 of 4
    }
    assert detect_drift(raw, PeopleServedExtraction) is False
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/preprocessing/test_claude.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement claude.py**

`src/backend/preprocessing/claude.py`:

```python
import asyncio
from typing import Any

import anthropic
from loguru import logger
from pydantic import BaseModel

from src.backend.preprocessing.schemas import (
    DonationsExtraction,
    ExtractionResult,
    FoodCategoriesExtraction,
    FoodVolumeExtraction,
    OperationsExtraction,
    PeopleServedExtraction,
    SECTION_PROMPTS,
    TOOL_SCHEMA_MAP,
)

DEFAULT_MODEL = "claude-haiku-4-5-20251001"
FALLBACK_MODEL = "claude-sonnet-4-6"


def detect_drift(raw: dict[str, Any], schema: type[BaseModel]) -> bool:
    """Return True if returned keys don't match the target schema (model used wrong field names)."""
    non_null_keys = {k for k, v in raw.items() if v is not None}
    if not non_null_keys:
        return False  # empty result — no data found, not drift
    schema_fields = set(schema.model_fields)
    overlap = non_null_keys & schema_fields
    return len(overlap) / len(non_null_keys) < 0.5


def _call_claude(
    client: anthropic.Anthropic,
    text: str,
    tool_name: str,
    model: str,
) -> dict[str, Any]:
    schema_cls = TOOL_SCHEMA_MAP[tool_name]
    system_prompt = SECTION_PROMPTS[tool_name]
    logger.debug(f"[{tool_name}] calling {model} ({len(text)} chars)")
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        tools=[{"name": tool_name, "input_schema": schema_cls.model_json_schema()}],
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content": text[:20000]}],
    )
    raw = response.content[0].input
    logger.debug(
        f"[{tool_name}] {model} → stop={response.stop_reason} "
        f"in={response.usage.input_tokens} out={response.usage.output_tokens}"
    )
    logger.debug(f"[{tool_name}] raw output: {raw}")

    if detect_drift(raw, schema_cls):
        logger.warning(f"[{tool_name}] drift detected with {model}, retrying with {FALLBACK_MODEL}")
        return _call_claude(client, text, tool_name, FALLBACK_MODEL)

    return raw


def _parse_section(raw: dict, schema_cls: type[BaseModel]) -> BaseModel:
    try:
        return schema_cls.model_validate(raw)
    except Exception as e:
        logger.warning(f"Validation failed for {schema_cls.__name__}: {e} — returning empty")
        return schema_cls()


async def extract_all(text: str, model: str = DEFAULT_MODEL) -> ExtractionResult:
    client = anthropic.Anthropic()
    loop = asyncio.get_event_loop()

    tool_names = list(TOOL_SCHEMA_MAP.keys())
    logger.info(f"Dispatching {len(tool_names)} parallel extractions with {model}")

    results = await asyncio.gather(*[
        loop.run_in_executor(None, _call_claude, client, text, tool_name, model)
        for tool_name in tool_names
    ])

    raw_map = dict(zip(tool_names, results))
    logger.info("All extractions complete")

    return ExtractionResult(
        food_volume=_parse_section(raw_map["extract_food_volume"], FoodVolumeExtraction),
        food_categories=_parse_section(raw_map["extract_food_categories"], FoodCategoriesExtraction),
        people_served=_parse_section(raw_map["extract_people_served"], PeopleServedExtraction),
        operations=_parse_section(raw_map["extract_operations"], OperationsExtraction),
        donations=_parse_section(raw_map["extract_donations"], DonationsExtraction),
    )
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/preprocessing/test_claude.py -v
```

Expected: 5 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/preprocessing/claude.py tests/backend/preprocessing/test_claude.py
git commit -m "feat: add Claude client with parallel extraction and drift detection"
```

---

## Task 5: DB writer

**Files:**
- Create: `src/backend/preprocessing/writer.py`
- Create: `tests/backend/preprocessing/test_writer.py`

- [ ] **Step 1: Write failing test**

`tests/backend/preprocessing/test_writer.py`:

```python
from datetime import date
from decimal import Decimal

import pytest
from sqlmodel import Session, select

from src.backend.models import (
    AnnualReport, Foodbank,
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
)
from src.backend.models.enums import RegionEnum, SourceEnum
from src.backend.preprocessing.schemas import (
    DonationsExtraction,
    ExtractionResult,
    FoodCategoriesExtraction,
    FoodVolumeExtraction,
    OperationsExtraction,
    PeopleServedExtraction,
)
from src.backend.preprocessing.writer import write_report


def _make_result(
    kg_total: float = 500000.0,
    households: int = 300,
) -> ExtractionResult:
    return ExtractionResult(
        food_volume=FoodVolumeExtraction(
            kg_received_total=kg_total,
            kg_received_total_method="p.10 'test'",
            waste_pct=0.006,
            waste_pct_method="p.10 '0.6%'",
        ),
        food_categories=FoodCategoriesExtraction(
            kg_produce=185000.0,
            kg_produce_method="p.11 'groente'",
        ),
        people_served=PeopleServedExtraction(
            households_weekly=households,
            households_weekly_method="p.8 'huishoudens'",
            pct_under_18=0.37,
            pct_under_18_method="national average",
        ),
        operations=OperationsExtraction(
            volunteers_count=108,
            volunteers_count_method="p.4 'vrijwilligers'",
        ),
        donations=DonationsExtraction(
            money_individuals_eur=45000.0,
            money_individuals_eur_method="p.19 financieel",
        ),
    )


def test_write_creates_foodbank_and_report(session: Session):
    result = _make_result()
    report = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="archive/df/data/breda-2024.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    assert report.id is not None
    assert report.year == 2024

    fb = session.exec(select(Foodbank).where(Foodbank.name == "Voedselbank Breda")).one()
    assert fb.city == "Breda"


def test_write_populates_food_volume(session: Session):
    result = _make_result(kg_total=507496.0)
    report = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="archive/df/data/breda-2024.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report.id)).one()
    assert fv.kg_received_total == 507496.0
    assert fv.kg_received_total_source == SourceEnum.extracted
    assert fv.kg_received_total_method == "p.10 'test'"
    assert fv.waste_pct == 0.006


def test_write_populates_people_served(session: Session):
    result = _make_result(households=335)
    report = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="archive/df/data/breda-2024.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    ps = session.exec(select(PeopleServed).where(PeopleServed.report_id == report.id)).one()
    assert ps.households_weekly == 335
    assert ps.households_weekly_source == SourceEnum.extracted


def test_write_skips_existing_by_default(session: Session):
    result = _make_result(kg_total=100.0)
    report1 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="first.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )

    # Second ingest — same bank + year, no --force
    report2 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="second.pdf",
        result=_make_result(kg_total=999.0),
        model="claude-haiku-4-5-20251001",
    )

    # Returns original report unchanged
    assert report2.id == report1.id
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report1.id)).one()
    assert fv.kg_received_total == 100.0  # not overwritten


def test_write_force_overwrites(session: Session):
    result = _make_result(kg_total=100.0)
    report1 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="first.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )

    report2 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="second.pdf",
        result=_make_result(kg_total=999.0),
        model="claude-haiku-4-5-20251001",
        force=True,
    )

    # New report row, fresh data
    assert report2.id != report1.id
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report2.id)).one()
    assert fv.kg_received_total == 999.0


def test_get_or_create_foodbank_reuses_existing(session: Session):
    result = _make_result()
    write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2023,
        pdf_path="a.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="b.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    banks = session.exec(select(Foodbank).where(Foodbank.name == "Voedselbank Breda")).all()
    assert len(banks) == 1  # same bank reused
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/preprocessing/test_writer.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement writer**

`src/backend/preprocessing/writer.py`:

```python
from datetime import date, datetime, timezone
from decimal import Decimal

from loguru import logger
from sqlmodel import Session, select

from src.backend.models import (
    AnnualReport, Donations, Foodbank, FoodCategories,
    FoodVolume, Operations, PeopleServed,
)
from src.backend.models.enums import RegionEnum, SourceEnum
from src.backend.preprocessing.schemas import ExtractionResult


def _get_or_create_foodbank(
    session: Session, name: str, city: str, region: RegionEnum
) -> Foodbank:
    existing = session.exec(select(Foodbank).where(Foodbank.name == name)).first()
    if existing:
        return existing
    fb = Foodbank(name=name, city=city, region=region)
    session.add(fb)
    session.commit()
    logger.debug(f"Created foodbank: {name}")
    return fb


def _delete_report_cascade(session: Session, report: AnnualReport) -> None:
    """Delete a report and all its child measurement rows."""
    for model in (FoodVolume, FoodCategories, PeopleServed, Operations, Donations):
        rows = session.exec(
            select(model).where(model.report_id == report.id)  # type: ignore[attr-defined]
        ).all()
        for row in rows:
            session.delete(row)
    session.delete(report)
    session.commit()
    logger.debug(f"Deleted report {report.id} and all children")


def _src(method: str | None) -> SourceEnum | None:
    return SourceEnum.extracted if method is not None else None


def write_report(
    session: Session,
    foodbank_name: str,
    city: str,
    region: RegionEnum,
    year: int,
    pdf_path: str,
    result: ExtractionResult,
    model: str,
    force: bool = False,
) -> AnnualReport:
    fb = _get_or_create_foodbank(session, foodbank_name, city, region)

    existing = session.exec(
        select(AnnualReport).where(
            AnnualReport.foodbank_id == fb.id,
            AnnualReport.year == year,
        )
    ).first()

    if existing and not force:
        logger.info(f"Report {foodbank_name} {year} already exists — skipping (use --force to overwrite)")
        return existing

    if existing and force:
        _delete_report_cascade(session, existing)

    today = date.today()
    report = AnnualReport(
        foodbank_id=fb.id,
        year=year,
        period_start=date(year, 1, 1),
        period_end=date(year, 12, 31),
        raw_file_path=pdf_path,
        ingestion_model=model,
    )
    session.add(report)
    session.commit()
    logger.info(f"Created AnnualReport {foodbank_name} {year} (id={report.id})")

    fv = result.food_volume
    session.add(FoodVolume(
        report_id=report.id,
        kg_received_total=fv.kg_received_total,
        kg_received_total_source=_src(fv.kg_received_total_method),
        kg_received_total_method=fv.kg_received_total_method,
        kg_via_national_dc=fv.kg_via_national_dc,
        kg_via_national_dc_source=_src(fv.kg_via_national_dc_method),
        kg_via_national_dc_method=fv.kg_via_national_dc_method,
        kg_direct=fv.kg_direct,
        kg_direct_source=_src(fv.kg_direct_method),
        kg_direct_method=fv.kg_direct_method,
        waste_pct=fv.waste_pct,
        waste_pct_source=_src(fv.waste_pct_method),
        waste_pct_method=fv.waste_pct_method,
        parcels_distributed=fv.parcels_distributed,
        parcels_distributed_source=_src(fv.parcels_distributed_method),
        parcels_distributed_method=fv.parcels_distributed_method,
        avg_products_per_parcel=fv.avg_products_per_parcel,
        avg_products_per_parcel_source=_src(fv.avg_products_per_parcel_method),
        avg_products_per_parcel_method=fv.avg_products_per_parcel_method,
        pct_schijf_van_vijf=fv.pct_schijf_van_vijf,
        pct_schijf_van_vijf_source=_src(fv.pct_schijf_van_vijf_method),
        pct_schijf_van_vijf_method=fv.pct_schijf_van_vijf_method,
        food_value_eur=Decimal(str(fv.food_value_eur)) if fv.food_value_eur is not None else None,
        food_value_eur_source=_src(fv.food_value_eur_method),
        food_value_eur_method=fv.food_value_eur_method,
    ))

    fc = result.food_categories
    session.add(FoodCategories(
        report_id=report.id,
        kg_produce=fc.kg_produce,
        kg_produce_source=_src(fc.kg_produce_method),
        kg_produce_method=fc.kg_produce_method,
        kg_meat_fish=fc.kg_meat_fish,
        kg_meat_fish_source=_src(fc.kg_meat_fish_method),
        kg_meat_fish_method=fc.kg_meat_fish_method,
        kg_dairy_eggs=fc.kg_dairy_eggs,
        kg_dairy_eggs_source=_src(fc.kg_dairy_eggs_method),
        kg_dairy_eggs_method=fc.kg_dairy_eggs_method,
        kg_dry_goods=fc.kg_dry_goods,
        kg_dry_goods_source=_src(fc.kg_dry_goods_method),
        kg_dry_goods_method=fc.kg_dry_goods_method,
        kg_bread_bakery=fc.kg_bread_bakery,
        kg_bread_bakery_source=_src(fc.kg_bread_bakery_method),
        kg_bread_bakery_method=fc.kg_bread_bakery_method,
        kg_prepared=fc.kg_prepared,
        kg_prepared_source=_src(fc.kg_prepared_method),
        kg_prepared_method=fc.kg_prepared_method,
    ))

    ps = result.people_served
    session.add(PeopleServed(
        report_id=report.id,
        households_weekly=ps.households_weekly,
        households_weekly_source=_src(ps.households_weekly_method),
        households_weekly_method=ps.households_weekly_method,
        individuals_total=ps.individuals_total,
        individuals_total_source=_src(ps.individuals_total_method),
        individuals_total_method=ps.individuals_total_method,
        children_count=ps.children_count,
        children_count_source=_src(ps.children_count_method),
        children_count_method=ps.children_count_method,
        pct_under_18=ps.pct_under_18,
        pct_under_18_source=_src(ps.pct_under_18_method),
        pct_under_18_method=ps.pct_under_18_method,
        pct_single_adults=ps.pct_single_adults,
        pct_single_adults_source=_src(ps.pct_single_adults_method),
        pct_single_adults_method=ps.pct_single_adults_method,
        pct_single_parent=ps.pct_single_parent,
        pct_single_parent_source=_src(ps.pct_single_parent_method),
        pct_single_parent_method=ps.pct_single_parent_method,
        pct_families=ps.pct_families,
        pct_families_source=_src(ps.pct_families_method),
        pct_families_method=ps.pct_families_method,
        pct_couples=ps.pct_couples,
        pct_couples_source=_src(ps.pct_couples_method),
        pct_couples_method=ps.pct_couples_method,
    ))

    ops = result.operations
    session.add(Operations(
        report_id=report.id,
        volunteers_count=ops.volunteers_count,
        volunteers_count_source=_src(ops.volunteers_count_method),
        volunteers_count_method=ops.volunteers_count_method,
        distribution_locations=ops.distribution_locations,
        distribution_locations_source=_src(ops.distribution_locations_method),
        distribution_locations_method=ops.distribution_locations_method,
        satellite_banks_served=ops.satellite_banks_served,
        satellite_banks_served_source=_src(ops.satellite_banks_served_method),
        satellite_banks_served_method=ops.satellite_banks_served_method,
        annual_budget_eur=Decimal(str(ops.annual_budget_eur)) if ops.annual_budget_eur is not None else None,
        annual_budget_eur_source=_src(ops.annual_budget_eur_method),
        annual_budget_eur_method=ops.annual_budget_eur_method,
        total_expenditure_eur=Decimal(str(ops.total_expenditure_eur)) if ops.total_expenditure_eur is not None else None,
        total_expenditure_eur_source=_src(ops.total_expenditure_eur_method),
        total_expenditure_eur_method=ops.total_expenditure_eur_method,
    ))

    don = result.donations
    session.add(Donations(
        report_id=report.id,
        food_supermarket_kg=don.food_supermarket_kg,
        food_supermarket_kg_source=_src(don.food_supermarket_kg_method),
        food_supermarket_kg_method=don.food_supermarket_kg_method,
        food_company_kg=don.food_company_kg,
        food_company_kg_source=_src(don.food_company_kg_method),
        food_company_kg_method=don.food_company_kg_method,
        food_dc_kg=don.food_dc_kg,
        food_dc_kg_source=_src(don.food_dc_kg_method),
        food_dc_kg_method=don.food_dc_kg_method,
        money_individuals_eur=Decimal(str(don.money_individuals_eur)) if don.money_individuals_eur is not None else None,
        money_individuals_eur_source=_src(don.money_individuals_eur_method),
        money_individuals_eur_method=don.money_individuals_eur_method,
        money_companies_eur=Decimal(str(don.money_companies_eur)) if don.money_companies_eur is not None else None,
        money_companies_eur_source=_src(don.money_companies_eur_method),
        money_companies_eur_method=don.money_companies_eur_method,
        money_orgs_eur=Decimal(str(don.money_orgs_eur)) if don.money_orgs_eur is not None else None,
        money_orgs_eur_source=_src(don.money_orgs_eur_method),
        money_orgs_eur_method=don.money_orgs_eur_method,
        money_government_eur=Decimal(str(don.money_government_eur)) if don.money_government_eur is not None else None,
        money_government_eur_source=_src(don.money_government_eur_method),
        money_government_eur_method=don.money_government_eur_method,
    ))

    session.commit()
    logger.info(f"Wrote all measurement tables for {foodbank_name} {year}")
    return report
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/preprocessing/test_writer.py -v
```

Expected: 6 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/preprocessing/writer.py tests/backend/preprocessing/test_writer.py
git commit -m "feat: add DB writer with get_or_create, force overwrite, provenance mapping"
```

---

## Task 6: Typer CLI

**Files:**
- Create: `src/backend/preprocessing/cli.py`
- Create: `tests/backend/preprocessing/test_cli.py`

- [ ] **Step 1: Implement CLI**

`src/backend/preprocessing/cli.py`:

```python
import asyncio
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from loguru import logger
from sqlmodel import Session

from src.backend.database import create_db_and_tables, engine
from src.backend.models.enums import RegionEnum
from src.backend.preprocessing.claude import DEFAULT_MODEL, extract_all
from src.backend.preprocessing.extractor import ExtractionError, extract_text
from src.backend.preprocessing.writer import write_report

load_dotenv()

app = typer.Typer(name="ingest", help="Foodbank report ingestion pipeline")

logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | {message}")
logger.add("logs/ingest.log", level="DEBUG", rotation="10 MB", retention=5)

# Hardcoded map for the 5 demo banks + other known banks
# key = filename stem prefix (lowercase), value = (bank_name, city, region)
BANK_MAP: dict[str, tuple[str, str, RegionEnum]] = {
    "breda":      ("Voedselbank Breda",      "Breda",      RegionEnum.zuid),
    "rotterdam":  ("Voedselbank Rotterdam",  "Rotterdam",  RegionEnum.west),
    "amsterdam":  ("Voedselbank Amsterdam",  "Amsterdam",  RegionEnum.randstad),
    "eindhoven":  ("Voedselbank Eindhoven",  "Eindhoven",  RegionEnum.oost),
    "groningen":  ("Voedselbank Groningen",  "Groningen",  RegionEnum.noord),
    "haaglanden": ("Voedselbank Haaglanden", "Den Haag",   RegionEnum.west),
    "utrecht":    ("Voedselbank Utrecht",    "Utrecht",    RegionEnum.west),
    "tilburg":    ("Voedselbank Tilburg",    "Tilburg",    RegionEnum.zuid),
    "denbosch":   ("Voedselbank Den Bosch",  "Den Bosch",  RegionEnum.zuid),
    "nijmegen":   ("Voedselbank Nijmegen",   "Nijmegen",   RegionEnum.oost),
    "amstelveen": ("Voedselbank Amstelveen", "Amstelveen", RegionEnum.randstad),
    "lelystad":   ("Voedselbank Lelystad",   "Lelystad",   RegionEnum.noord),
    "woerden":    ("Voedselbank Woerden",    "Woerden",    RegionEnum.west),
}


def _year_from_stem(stem: str) -> int | None:
    """Extract 4-digit year from filename stem like 'breda-2025' or 'amsterdam-2024-fin'."""
    for part in stem.split("-"):
        if part.isdigit() and len(part) == 4:
            return int(part)
    return None


def _bank_from_stem(stem: str) -> tuple[str, str, RegionEnum] | None:
    lower = stem.lower()
    for key, info in BANK_MAP.items():
        if lower.startswith(key):
            return info
    return None


@app.command()
def ingest(
    file: Path = typer.Argument(..., help="Path to PDF or .txt report"),
    bank_name: str = typer.Option(..., "--bank-name", help="Full bank name, e.g. 'Voedselbank Breda'"),
    city: str = typer.Option(..., "--city", help="City name"),
    region: str = typer.Option(..., "--region", help="Region: noord|oost|zuid|west|randstad"),
    year: int = typer.Option(..., "--year", help="Report year, e.g. 2024"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Claude model ID"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing report"),
) -> None:
    """Ingest a single foodbank annual report."""
    if not file.exists():
        logger.error(f"File not found: {file}")
        raise typer.Exit(code=1)

    try:
        region_enum = RegionEnum(region)
    except ValueError:
        logger.error(f"Invalid region '{region}'. Must be one of: {[r.value for r in RegionEnum]}")
        raise typer.Exit(code=1)

    try:
        text = extract_text(file)
    except ExtractionError as e:
        logger.error(f"Text extraction failed: {e}")
        raise typer.Exit(code=1)

    logger.info(f"Extracted {len(text)} chars from {file.name}")

    result = asyncio.run(extract_all(text, model=model))

    create_db_and_tables()
    with Session(engine) as session:
        report = write_report(
            session=session,
            foodbank_name=bank_name,
            city=city,
            region=region_enum,
            year=year,
            pdf_path=str(file),
            result=result,
            model=model,
            force=force,
        )

    logger.info(f"Done — report id={report.id}")


@app.command(name="ingest-dir")
def ingest_dir(
    directory: Path = typer.Argument(..., help="Directory containing PDF/txt files"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Claude model ID"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing reports"),
) -> None:
    """Batch ingest all known reports in a directory."""
    if not directory.is_dir():
        logger.error(f"Not a directory: {directory}")
        raise typer.Exit(code=1)

    # Glob PDFs only — extract_text() automatically uses .txt sidecar if present
    to_process = sorted(directory.glob("*.pdf"))

    create_db_and_tables()

    with Session(engine) as session:
        for file in to_process:
            bank_info = _bank_from_stem(file.stem)
            year = _year_from_stem(file.stem)

            if bank_info is None or year is None:
                logger.warning(f"Skipping {file.name} — no bank/year mapping found")
                continue

            bank_name, city, region_enum = bank_info
            logger.info(f"Processing {file.name} → {bank_name} {year}")

            try:
                text = extract_text(file)
            except ExtractionError as e:
                logger.error(f"Skipping {file.name}: {e}")
                continue

            result = asyncio.run(extract_all(text, model=model))
            write_report(
                session=session,
                foodbank_name=bank_name,
                city=city,
                region=region_enum,
                year=year,
                pdf_path=str(file),
                result=result,
                model=model,
                force=force,
            )

    logger.info("Batch ingest complete")


if __name__ == "__main__":
    app()
```

- [ ] **Step 2: Run full preprocessing test suite**

```bash
uv run pytest tests/backend/preprocessing/ -v
```

Expected: all PASSED (≈24 tests)

- [ ] **Step 3: Run full project test suite**

```bash
uv run pytest tests/ -v --tb=short
```

Expected: all PASSED

- [ ] **Step 4: Smoke test against real data**

```bash
uv run python -m src.backend.preprocessing.cli ingest \
  archive/df/data/breda-2025.txt \
  --bank-name "Voedselbank Breda" \
  --city "Breda" \
  --region "zuid" \
  --year 2025
```

Expected: INFO log lines showing extraction + DB write, no errors.

- [ ] **Step 5: Commit**

```bash
git add src/backend/preprocessing/cli.py tests/backend/preprocessing/test_cli.py
git commit -m "feat: add Typer ingestion CLI with ingest and ingest-dir commands"
```
