# Foodbank Data Model Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the full SQLModel data model for the foodbank platform — auth, marketplace, and annual report measurement layers — with a shared DB engine and full test coverage.

**Architecture:** All entities live in `src/backend/models/` as SQLModel classes, shareable by both the webapp and the ingestion pipeline. A provenance mixin pattern attaches `_source` and `_method` siblings to every nullable measurement field. The DB engine and session factory live in `src/backend/database.py`.

**Tech Stack:** Python 3.13, SQLModel, SQLite (dev) / Postgres (prod), pytest, uv

---

## File Map

| File | Responsibility |
|---|---|
| `src/backend/models/__init__.py` | Re-export all models |
| `src/backend/models/enums.py` | All enum definitions |
| `src/backend/models/user.py` | `User` model |
| `src/backend/models/foodbank.py` | `Foodbank`, `AnnualReport` |
| `src/backend/models/measurements.py` | `FoodVolume`, `FoodCategories`, `PeopleServed`, `Operations`, `Donations` |
| `src/backend/models/frame.py` | `FrameResult` |
| `src/backend/models/marketplace.py` | `Package`, `PackageFoodbank`, `FundSubscription`, `CsrReport` |
| `src/backend/database.py` | Engine, session factory, `create_db_and_tables()` |
| `tests/backend/models/test_enums.py` | Enum value tests |
| `tests/backend/models/test_user.py` | User CRUD |
| `tests/backend/models/test_foodbank.py` | Foodbank + AnnualReport CRUD |
| `tests/backend/models/test_measurements.py` | Measurement tables + provenance |
| `tests/backend/models/test_marketplace.py` | Package → FundSubscription → CsrReport chain |
| `tests/backend/models/test_integration.py` | Full chain: User buys Package → FrameResult → CsrReport |
| `tests/backend/conftest.py` | Shared in-memory SQLite session fixture |

---

## Task 1: Project dependencies

**Files:**
- Modify: `pyproject.toml`

- [ ] **Step 1: Add dependencies**

Replace `pyproject.toml` with:

```toml
[project]
name = "anthropic-hackathon"
version = "0.1.0"
description = "Climate-Action Packages for Dutch Foodbanks"
readme = "README.md"
requires-python = ">=3.13"
dependencies = [
    "sqlmodel>=0.0.21",
    "sqlalchemy>=2.0",
    "passlib[bcrypt]>=1.7.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]
```

- [ ] **Step 2: Install**

```bash
uv sync --extra dev
```

Expected: resolves without error, `.venv` created.

- [ ] **Step 3: Create package structure**

```bash
mkdir -p src/backend/models tests/backend/models
touch src/backend/__init__.py
touch src/backend/models/__init__.py
touch tests/__init__.py
touch tests/backend/__init__.py
touch tests/backend/models/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git add pyproject.toml src/ tests/
git commit -m "chore: scaffold backend models package and add deps"
```

---

## Task 2: Enums

**Files:**
- Create: `src/backend/models/enums.py`
- Create: `tests/backend/models/test_enums.py`

- [ ] **Step 1: Write failing test**

`tests/backend/models/test_enums.py`:

```python
from src.backend.models.enums import (
    SourceEnum, RoleEnum, RegionEnum, StatusEnum,
    TemplateEnum, CounterfactualEnum,
)


def test_source_enum_values():
    assert SourceEnum.extracted == "extracted"
    assert SourceEnum.inferred_national_avg == "inferred_national_avg"
    assert SourceEnum.inferred_category_split == "inferred_category_split"
    assert SourceEnum.inferred_calculation == "inferred_calculation"
    assert SourceEnum.manual == "manual"


def test_role_enum_values():
    assert RoleEnum.corporate == "corporate"
    assert RoleEnum.foodbank_op == "foodbank_op"
    assert RoleEnum.admin == "admin"


def test_region_enum_values():
    expected = {"noord", "oost", "zuid", "west", "randstad"}
    assert {r.value for r in RegionEnum} == expected


def test_status_enum_values():
    assert StatusEnum.pending == "pending"
    assert StatusEnum.paid == "paid"
    assert StatusEnum.failed == "failed"
    assert StatusEnum.refunded == "refunded"


def test_counterfactual_enum_values():
    assert CounterfactualEnum.incineration_energy_recovery == "incineration_energy_recovery"
    assert CounterfactualEnum.landfill == "landfill"
    assert CounterfactualEnum.composting == "composting"


def test_template_enum_values():
    expected = {"gri", "csrd", "esrs_e1", "generic"}
    assert {t.value for t in TemplateEnum} == expected
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_enums.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement enums**

`src/backend/models/enums.py`:

```python
from enum import Enum


class SourceEnum(str, Enum):
    extracted = "extracted"
    inferred_national_avg = "inferred_national_avg"
    inferred_category_split = "inferred_category_split"
    inferred_calculation = "inferred_calculation"
    manual = "manual"


class RoleEnum(str, Enum):
    corporate = "corporate"
    foodbank_op = "foodbank_op"
    admin = "admin"


class RegionEnum(str, Enum):
    noord = "noord"
    oost = "oost"
    zuid = "zuid"
    west = "west"
    randstad = "randstad"


class StatusEnum(str, Enum):
    pending = "pending"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"


class CounterfactualEnum(str, Enum):
    incineration_energy_recovery = "incineration_energy_recovery"
    landfill = "landfill"
    composting = "composting"


class TemplateEnum(str, Enum):
    gri = "gri"
    csrd = "csrd"
    esrs_e1 = "esrs_e1"
    generic = "generic"
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/models/test_enums.py -v
```

Expected: 6 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/models/enums.py tests/backend/models/test_enums.py
git commit -m "feat: add all model enums"
```

---

## Task 3: Database engine + test fixture

**Files:**
- Create: `src/backend/database.py`
- Create: `tests/backend/conftest.py`

- [ ] **Step 1: Write failing test**

`tests/backend/models/test_enums.py` — add at bottom:

```python
def test_db_import():
    from src.backend.database import create_db_and_tables, get_session
    assert callable(create_db_and_tables)
    assert callable(get_session)
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_enums.py::test_db_import -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement database module**

`src/backend/database.py`:

```python
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./foodbank.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

- [ ] **Step 4: Create shared test fixture**

`tests/backend/conftest.py`:

```python
import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)
```

- [ ] **Step 5: Run — expect pass**

```bash
uv run pytest tests/backend/models/test_enums.py::test_db_import -v
```

Expected: PASSED

- [ ] **Step 6: Commit**

```bash
git add src/backend/database.py tests/backend/conftest.py
git commit -m "feat: add database engine and test session fixture"
```

---

## Task 4: User model

**Files:**
- Create: `src/backend/models/user.py`
- Create: `tests/backend/models/test_user.py`

- [ ] **Step 1: Write failing test**

`tests/backend/models/test_user.py`:

```python
import pytest
from sqlmodel import Session, select
from src.backend.models.user import User
from src.backend.models.enums import RoleEnum


def test_create_user(session: Session):
    user = User(
        email="buyer@acme.com",
        hashed_password="hashed_abc",
        role=RoleEnum.corporate,
        org_name="ACME Corp",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    assert user.id is not None
    assert user.email == "buyer@acme.com"
    assert user.role == RoleEnum.corporate


def test_user_email_unique(session: Session):
    u1 = User(email="dup@test.com", hashed_password="x", role=RoleEnum.corporate)
    u2 = User(email="dup@test.com", hashed_password="y", role=RoleEnum.admin)
    session.add(u1)
    session.commit()
    session.add(u2)
    with pytest.raises(Exception):
        session.commit()


def test_user_role_default(session: Session):
    user = User(email="op@bank.nl", hashed_password="x", role=RoleEnum.foodbank_op)
    session.add(user)
    session.commit()
    result = session.exec(select(User).where(User.email == "op@bank.nl")).one()
    assert result.role == RoleEnum.foodbank_op
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_user.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement User model**

`src/backend/models/user.py`:

```python
import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from src.backend.models.enums import RoleEnum


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: RoleEnum
    org_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/models/test_user.py -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/models/user.py tests/backend/models/test_user.py
git commit -m "feat: add User model with role enum"
```

---

## Task 5: Foodbank + AnnualReport

**Files:**
- Create: `src/backend/models/foodbank.py`
- Create: `tests/backend/models/test_foodbank.py`

- [ ] **Step 1: Write failing test**

`tests/backend/models/test_foodbank.py`:

```python
import uuid
from datetime import date
from sqlmodel import Session, select
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.enums import RegionEnum


def test_create_foodbank(session: Session):
    fb = Foodbank(
        name="Voedselbank Rotterdam",
        city="Rotterdam",
        region=RegionEnum.west,
        is_regional_dc=True,
    )
    session.add(fb)
    session.commit()
    session.refresh(fb)
    assert fb.id is not None
    assert fb.is_regional_dc is True


def test_create_annual_report(session: Session):
    fb = Foodbank(name="Voedselbank Breda", city="Breda", region=RegionEnum.zuid, is_regional_dc=False)
    session.add(fb)
    session.commit()

    report = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="df/data/breda-2024-fin.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    assert report.id is not None
    assert report.foodbank_id == fb.id


def test_foodbank_annual_report_relationship(session: Session):
    fb = Foodbank(name="Voedselbank Amsterdam", city="Amsterdam", region=RegionEnum.randstad, is_regional_dc=True)
    session.add(fb)
    session.commit()

    for year in [2023, 2024]:
        session.add(AnnualReport(
            foodbank_id=fb.id,
            year=year,
            period_start=date(year, 1, 1),
            period_end=date(year, 12, 31),
            raw_file_path=f"df/data/amsterdam-{year}.txt",
            ingestion_model="claude-sonnet-4-6",
        ))
    session.commit()

    reports = session.exec(select(AnnualReport).where(AnnualReport.foodbank_id == fb.id)).all()
    assert len(reports) == 2
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_foodbank.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement models**

`src/backend/models/foodbank.py`:

```python
import uuid
from datetime import date, datetime, timezone
from sqlmodel import Field, SQLModel
from src.backend.models.enums import RegionEnum


class Foodbank(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    city: str
    region: RegionEnum
    is_regional_dc: bool = False
    vbn_member_id: str | None = None


class AnnualReport(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    foodbank_id: uuid.UUID = Field(foreign_key="foodbank.id", index=True)
    year: int = Field(index=True)
    period_start: date
    period_end: date
    raw_file_path: str
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ingestion_model: str
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/models/test_foodbank.py -v
```

Expected: 3 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/models/foodbank.py tests/backend/models/test_foodbank.py
git commit -m "feat: add Foodbank and AnnualReport models"
```

---

## Task 6: Measurement tables with provenance

**Files:**
- Create: `src/backend/models/measurements.py`
- Create: `tests/backend/models/test_measurements.py`

- [ ] **Step 1: Write failing test**

`tests/backend/models/test_measurements.py`:

```python
import uuid
from datetime import date
from sqlmodel import Session, select
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.measurements import (
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
)
from src.backend.models.enums import RegionEnum, SourceEnum, CounterfactualEnum


def _make_report(session: Session) -> AnnualReport:
    fb = Foodbank(name="Test Bank", city="Test", region=RegionEnum.noord, is_regional_dc=False)
    session.add(fb)
    session.commit()
    report = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="test.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()
    return report


def test_food_volume_with_provenance(session: Session):
    report = _make_report(session)
    fv = FoodVolume(
        report_id=report.id,
        kg_received_total=507496.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="extracted from PDF p.10 'Ontvangen voedsel'",
        waste_pct=0.6,
        waste_pct_source=SourceEnum.extracted,
        waste_pct_method="extracted from PDF p.10 '0,6 procent naar de stort'",
    )
    session.add(fv)
    session.commit()
    session.refresh(fv)
    assert fv.kg_received_total == 507496.0
    assert fv.kg_received_total_source == SourceEnum.extracted
    assert fv.waste_pct == 0.6


def test_food_volume_nullable_fields(session: Session):
    report = _make_report(session)
    fv = FoodVolume(report_id=report.id)
    session.add(fv)
    session.commit()
    session.refresh(fv)
    assert fv.kg_received_total is None
    assert fv.kg_received_total_source is None


def test_food_categories_inferred(session: Session):
    report = _make_report(session)
    fc = FoodCategories(
        report_id=report.id,
        kg_produce=185036.0,
        kg_produce_source=SourceEnum.extracted,
        kg_produce_method="extracted from PDF p.11 category table",
        kg_dairy_eggs=47819.0,
        kg_dairy_eggs_source=SourceEnum.extracted,
        kg_dairy_eggs_method="extracted from PDF p.11 category table",
        kg_meat_fish=30437.0,
        kg_meat_fish_source=SourceEnum.extracted,
        kg_meat_fish_method="extracted from PDF p.11 category table",
        kg_dry_goods=None,
        kg_dry_goods_source=SourceEnum.inferred_national_avg,
        kg_dry_goods_method="NL avg 18% applied to total 507496kg",
    )
    session.add(fc)
    session.commit()
    session.refresh(fc)
    assert fc.kg_produce == 185036.0
    assert fc.kg_dry_goods is None
    assert fc.kg_dry_goods_source == SourceEnum.inferred_national_avg


def test_people_served(session: Session):
    report = _make_report(session)
    ps = PeopleServed(
        report_id=report.id,
        households_weekly=1600,
        households_weekly_source=SourceEnum.extracted,
        households_weekly_method="extracted from PDF p.2",
        pct_under_18=0.37,
        pct_under_18_source=SourceEnum.inferred_national_avg,
        pct_under_18_method="NL national average from Feiten & Cijfers 2024",
    )
    session.add(ps)
    session.commit()
    session.refresh(ps)
    assert ps.households_weekly == 1600
    assert ps.pct_under_18 == 0.37


def test_operations_counterfactual(session: Session):
    report = _make_report(session)
    ops = Operations(
        report_id=report.id,
        volunteers_count=108,
        volunteers_count_source=SourceEnum.extracted,
        volunteers_count_method="extracted from PDF p.4",
        counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
    )
    session.add(ops)
    session.commit()
    session.refresh(ops)
    assert ops.counterfactual_route == CounterfactualEnum.incineration_energy_recovery


def test_donations(session: Session):
    report = _make_report(session)
    d = Donations(
        report_id=report.id,
        money_individuals_eur=45000.0,
        money_individuals_eur_source=SourceEnum.extracted,
        money_individuals_eur_method="extracted from financial section",
        money_companies_eur=62186.0,
        money_companies_eur_source=SourceEnum.extracted,
        money_companies_eur_method="extracted from financial section",
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    assert d.money_individuals_eur == 45000.0
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_measurements.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement measurement models**

`src/backend/models/measurements.py`:

```python
import uuid
from sqlmodel import Field, SQLModel
from src.backend.models.enums import SourceEnum, CounterfactualEnum


class FoodVolume(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    kg_received_total: float | None = None
    kg_received_total_source: SourceEnum | None = None
    kg_received_total_method: str | None = None

    kg_via_national_dc: float | None = None
    kg_via_national_dc_source: SourceEnum | None = None
    kg_via_national_dc_method: str | None = None

    kg_direct: float | None = None
    kg_direct_source: SourceEnum | None = None
    kg_direct_method: str | None = None

    waste_pct: float | None = None
    waste_pct_source: SourceEnum | None = None
    waste_pct_method: str | None = None

    parcels_distributed: int | None = None
    parcels_distributed_source: SourceEnum | None = None
    parcels_distributed_method: str | None = None

    avg_products_per_parcel: float | None = None
    avg_products_per_parcel_source: SourceEnum | None = None
    avg_products_per_parcel_method: str | None = None

    pct_schijf_van_vijf: float | None = None
    pct_schijf_van_vijf_source: SourceEnum | None = None
    pct_schijf_van_vijf_method: str | None = None

    food_value_eur: float | None = None
    food_value_eur_source: SourceEnum | None = None
    food_value_eur_method: str | None = None


class FoodCategories(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    kg_produce: float | None = None
    kg_produce_source: SourceEnum | None = None
    kg_produce_method: str | None = None

    kg_meat_fish: float | None = None
    kg_meat_fish_source: SourceEnum | None = None
    kg_meat_fish_method: str | None = None

    kg_dairy_eggs: float | None = None
    kg_dairy_eggs_source: SourceEnum | None = None
    kg_dairy_eggs_method: str | None = None

    kg_dry_goods: float | None = None
    kg_dry_goods_source: SourceEnum | None = None
    kg_dry_goods_method: str | None = None

    kg_bread_bakery: float | None = None
    kg_bread_bakery_source: SourceEnum | None = None
    kg_bread_bakery_method: str | None = None

    kg_prepared: float | None = None
    kg_prepared_source: SourceEnum | None = None
    kg_prepared_method: str | None = None

    kg_non_food: float | None = None
    kg_non_food_source: SourceEnum | None = None
    kg_non_food_method: str | None = None


class PeopleServed(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    households_weekly: int | None = None
    households_weekly_source: SourceEnum | None = None
    households_weekly_method: str | None = None

    individuals_total: int | None = None
    individuals_total_source: SourceEnum | None = None
    individuals_total_method: str | None = None

    children_count: int | None = None
    children_count_source: SourceEnum | None = None
    children_count_method: str | None = None

    pct_under_18: float | None = None
    pct_under_18_source: SourceEnum | None = None
    pct_under_18_method: str | None = None

    pct_single_adults: float | None = None
    pct_single_adults_source: SourceEnum | None = None
    pct_single_adults_method: str | None = None

    pct_single_parent: float | None = None
    pct_single_parent_source: SourceEnum | None = None
    pct_single_parent_method: str | None = None

    pct_families: float | None = None
    pct_families_source: SourceEnum | None = None
    pct_families_method: str | None = None

    pct_couples: float | None = None
    pct_couples_source: SourceEnum | None = None
    pct_couples_method: str | None = None


class Operations(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    volunteers_count: int | None = None
    volunteers_count_source: SourceEnum | None = None
    volunteers_count_method: str | None = None

    distribution_locations: int | None = None
    distribution_locations_source: SourceEnum | None = None
    distribution_locations_method: str | None = None

    satellite_banks_served: int | None = None
    satellite_banks_served_source: SourceEnum | None = None
    satellite_banks_served_method: str | None = None

    annual_budget_eur: float | None = None
    annual_budget_eur_source: SourceEnum | None = None
    annual_budget_eur_method: str | None = None

    total_expenditure_eur: float | None = None
    total_expenditure_eur_source: SourceEnum | None = None
    total_expenditure_eur_method: str | None = None

    # Always set explicitly for FRAME audit trail
    counterfactual_route: CounterfactualEnum = CounterfactualEnum.incineration_energy_recovery


class Donations(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    food_supermarket_kg: float | None = None
    food_supermarket_kg_source: SourceEnum | None = None
    food_supermarket_kg_method: str | None = None

    food_company_kg: float | None = None
    food_company_kg_source: SourceEnum | None = None
    food_company_kg_method: str | None = None

    food_dc_kg: float | None = None
    food_dc_kg_source: SourceEnum | None = None
    food_dc_kg_method: str | None = None

    money_individuals_eur: float | None = None
    money_individuals_eur_source: SourceEnum | None = None
    money_individuals_eur_method: str | None = None

    money_companies_eur: float | None = None
    money_companies_eur_source: SourceEnum | None = None
    money_companies_eur_method: str | None = None

    money_orgs_eur: float | None = None
    money_orgs_eur_source: SourceEnum | None = None
    money_orgs_eur_method: str | None = None

    money_government_eur: float | None = None
    money_government_eur_source: SourceEnum | None = None
    money_government_eur_method: str | None = None
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/models/test_measurements.py -v
```

Expected: 6 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/models/measurements.py tests/backend/models/test_measurements.py
git commit -m "feat: add measurement tables with per-field provenance"
```

---

## Task 7: FrameResult

**Files:**
- Create: `src/backend/models/frame.py`
- Create: `tests/backend/models/test_frame.py`

- [ ] **Step 1: Write failing test**

`tests/backend/models/test_frame.py`:

```python
import uuid
from datetime import date, datetime, timezone
from sqlmodel import Session
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.enums import RegionEnum


def test_create_frame_result(session: Session):
    fb = Foodbank(name="Voedselbank Breda", city="Breda", region=RegionEnum.zuid, is_regional_dc=False)
    session.add(fb)
    session.commit()
    report = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="df/data/breda-2024-fin.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()

    result = FrameResult(
        report_id=report.id,
        co2e_total_kg=1268740.0,
        co2e_produce_kg=462590.0,
        co2e_meat_fish_kg=304370.0,
        co2e_dairy_eggs_kg=191276.0,
        co2e_dry_goods_kg=182698.0,
        co2e_bread_kg=127806.0,
        emission_factor_source="FAO Food Wastage Footprint 2013 + WRAP UK 2022",
        methodology_version="FRAME-NL-v1.0",
    )
    session.add(result)
    session.commit()
    session.refresh(result)

    assert result.id is not None
    assert result.co2e_total_kg == 1268740.0
    assert result.methodology_version == "FRAME-NL-v1.0"
    assert isinstance(result.computed_at, datetime)
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_frame.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement FrameResult**

`src/backend/models/frame.py`:

```python
import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class FrameResult(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    co2e_total_kg: float
    co2e_produce_kg: float
    co2e_meat_fish_kg: float
    co2e_dairy_eggs_kg: float
    co2e_dry_goods_kg: float
    co2e_bread_kg: float

    emission_factor_source: str
    methodology_version: str
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/models/test_frame.py -v
```

Expected: 1 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/models/frame.py tests/backend/models/test_frame.py
git commit -m "feat: add FrameResult model"
```

---

## Task 8: Marketplace models

**Files:**
- Create: `src/backend/models/marketplace.py`
- Create: `tests/backend/models/test_marketplace.py`

- [ ] **Step 1: Write failing test**

`tests/backend/models/test_marketplace.py`:

```python
import uuid
from datetime import date
from sqlmodel import Session, select
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import Package, PackageFoodbank, FundSubscription, CsrReport
from src.backend.models.user import User
from src.backend.models.enums import RegionEnum, RoleEnum, StatusEnum, TemplateEnum


def _make_user(session: Session) -> User:
    u = User(email="csr@acme.com", hashed_password="x", role=RoleEnum.corporate, org_name="ACME")
    session.add(u)
    session.commit()
    return u


def _make_foodbank(session: Session, name="Test Bank") -> Foodbank:
    fb = Foodbank(name=name, city="Test", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    return fb


def test_create_package(session: Session):
    fb = _make_foodbank(session)
    pkg = Package(
        name="Rotterdam Climate Package",
        region=RegionEnum.west,
        price_eur=25000.0,
        co2e_claim_kg=600000.0,
        is_active=True,
    )
    session.add(pkg)
    session.commit()

    link = PackageFoodbank(package_id=pkg.id, foodbank_id=fb.id, weight_pct=1.0)
    session.add(link)
    session.commit()

    links = session.exec(select(PackageFoodbank).where(PackageFoodbank.package_id == pkg.id)).all()
    assert len(links) == 1
    assert links[0].foodbank_id == fb.id


def test_create_fund_subscription(session: Session):
    user = _make_user(session)
    fb = _make_foodbank(session, "Rotterdam")
    pkg = Package(name="Rotterdam Package", region=RegionEnum.west, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(pkg)
    session.commit()

    sub = FundSubscription(
        user_id=user.id,
        package_id=pkg.id,
        amount_eur=25000.0,
        status=StatusEnum.paid,
        solvimon_id="solv_abc123",
    )
    session.add(sub)
    session.commit()
    session.refresh(sub)
    assert sub.id is not None
    assert sub.status == StatusEnum.paid
    assert sub.csr_report_id is None  # not yet generated


def test_attach_csr_report_to_subscription(session: Session):
    user = _make_user(session)
    fb = _make_foodbank(session, "Breda")
    pkg = Package(name="Breda Package", region=RegionEnum.zuid, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(pkg)
    session.commit()

    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=25000.0, status=StatusEnum.paid)
    session.add(sub)
    session.commit()

    report = AnnualReport(
        foodbank_id=fb.id, year=2024,
        period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
        raw_file_path="test.txt", ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()

    frame = FrameResult(
        report_id=report.id,
        co2e_total_kg=1000000.0, co2e_produce_kg=300000.0,
        co2e_meat_fish_kg=200000.0, co2e_dairy_eggs_kg=200000.0,
        co2e_dry_goods_kg=200000.0, co2e_bread_kg=100000.0,
        emission_factor_source="FAO 2013", methodology_version="FRAME-NL-v1.0",
    )
    session.add(frame)
    session.commit()

    csr = CsrReport(
        subscription_id=sub.id,
        frame_result_id=frame.id,
        file_path="reports/acme-breda-2024.pdf",
        template=TemplateEnum.csrd,
    )
    session.add(csr)
    session.commit()

    # Populate the back-reference on subscription
    sub.csr_report_id = csr.id
    session.add(sub)
    session.commit()
    session.refresh(sub)

    assert sub.csr_report_id == csr.id


def test_cluster_package_multiple_banks(session: Session):
    fb1 = _make_foodbank(session, "Groningen")
    fb2 = _make_foodbank(session, "Leeuwarden")
    pkg = Package(name="North Cluster", region=RegionEnum.noord, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(pkg)
    session.commit()

    session.add(PackageFoodbank(package_id=pkg.id, foodbank_id=fb1.id, weight_pct=0.6))
    session.add(PackageFoodbank(package_id=pkg.id, foodbank_id=fb2.id, weight_pct=0.4))
    session.commit()

    links = session.exec(select(PackageFoodbank).where(PackageFoodbank.package_id == pkg.id)).all()
    assert len(links) == 2
    assert sum(l.weight_pct for l in links) == 1.0
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_marketplace.py -v
```

Expected: `ModuleNotFoundError`

- [ ] **Step 3: Implement marketplace models**

`src/backend/models/marketplace.py`:

```python
import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from src.backend.models.enums import RegionEnum, StatusEnum, TemplateEnum


class Package(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None
    region: RegionEnum
    price_eur: float = 25000.0
    co2e_claim_kg: float = 600000.0
    is_active: bool = True


class PackageFoodbank(SQLModel, table=True):
    package_id: uuid.UUID = Field(foreign_key="package.id", primary_key=True)
    foodbank_id: uuid.UUID = Field(foreign_key="foodbank.id", primary_key=True)
    weight_pct: float | None = None


class FundSubscription(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    package_id: uuid.UUID = Field(foreign_key="package.id", index=True)
    amount_eur: float
    status: StatusEnum = StatusEnum.pending
    solvimon_id: str | None = None
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    csr_report_id: uuid.UUID | None = Field(default=None, foreign_key="csrreport.id")


class CsrReport(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="fundsubscription.id")
    frame_result_id: uuid.UUID = Field(foreign_key="frameresult.id")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_path: str
    template: TemplateEnum = TemplateEnum.generic
```

- [ ] **Step 4: Run — expect pass**

```bash
uv run pytest tests/backend/models/test_marketplace.py -v
```

Expected: 4 PASSED

- [ ] **Step 5: Commit**

```bash
git add src/backend/models/marketplace.py tests/backend/models/test_marketplace.py
git commit -m "feat: add marketplace models (Package, FundSubscription, CsrReport)"
```

---

## Task 9: Wire __init__.py + full test suite

**Files:**
- Modify: `src/backend/models/__init__.py`
- Create: `tests/backend/models/test_integration.py`

- [ ] **Step 1: Write failing integration test**

`tests/backend/models/test_integration.py`:

```python
"""Full chain: ingest report → FRAME → User buys Package → CsrReport generated."""
import uuid
from datetime import date
from sqlmodel import Session, select

from src.backend.models import (
    User, Foodbank, AnnualReport,
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
    FrameResult, Package, PackageFoodbank, FundSubscription, CsrReport,
)
from src.backend.models.enums import (
    RegionEnum, RoleEnum, StatusEnum, SourceEnum,
    CounterfactualEnum, TemplateEnum,
)


def test_full_breda_chain(session: Session):
    # 1. Create foodbank
    fb = Foodbank(name="Voedselbank Breda", city="Breda", region=RegionEnum.zuid, is_regional_dc=False)
    session.add(fb)
    session.commit()

    # 2. Ingest annual report
    report = AnnualReport(
        foodbank_id=fb.id, year=2024,
        period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
        raw_file_path="df/data/breda-2024-fin.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()

    # 3. Store extracted measurements
    session.add(FoodVolume(
        report_id=report.id,
        kg_received_total=507496.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="PDF p.10",
        waste_pct=0.6,
        waste_pct_source=SourceEnum.extracted,
        waste_pct_method="PDF p.10 '0,6 procent naar de stort'",
    ))
    session.add(FoodCategories(
        report_id=report.id,
        kg_produce=185036.0,
        kg_produce_source=SourceEnum.extracted,
        kg_produce_method="PDF p.11 category table",
        kg_meat_fish=30437.0,
        kg_meat_fish_source=SourceEnum.extracted,
        kg_meat_fish_method="PDF p.11 category table",
        kg_dairy_eggs=47819.0,
        kg_dairy_eggs_source=SourceEnum.extracted,
        kg_dairy_eggs_method="PDF p.11 category table",
        kg_dry_goods=91349.0,
        kg_dry_goods_source=SourceEnum.inferred_national_avg,
        kg_dry_goods_method="NL avg 18% applied to total 507496kg",
    ))
    session.add(PeopleServed(
        report_id=report.id,
        households_weekly=327,
        households_weekly_source=SourceEnum.extracted,
        households_weekly_method="PDF p.8 '17748 / 52'",
        pct_under_18=0.37,
        pct_under_18_source=SourceEnum.inferred_national_avg,
        pct_under_18_method="NL national average Feiten & Cijfers 2024",
    ))
    session.add(Operations(
        report_id=report.id,
        volunteers_count=108,
        volunteers_count_source=SourceEnum.extracted,
        volunteers_count_method="PDF p.4",
        distribution_locations=3,
        distribution_locations_source=SourceEnum.extracted,
        distribution_locations_method="PDF p.4",
        counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
    ))
    session.add(Donations(
        report_id=report.id,
        food_supermarket_kg=200000.0,
        food_supermarket_kg_source=SourceEnum.inferred_calculation,
        food_supermarket_kg_method="estimated from partner list + national DC proportion",
    ))
    session.commit()

    # 4. FRAME engine output
    frame = FrameResult(
        report_id=report.id,
        co2e_total_kg=1268740.0,
        co2e_produce_kg=462590.0,
        co2e_meat_fish_kg=304370.0,
        co2e_dairy_eggs_kg=191276.0,
        co2e_dry_goods_kg=182698.0,
        co2e_bread_kg=127806.0,
        emission_factor_source="FAO Food Wastage Footprint 2013 + WRAP UK 2022",
        methodology_version="FRAME-NL-v1.0",
    )
    session.add(frame)
    session.commit()

    # 5. Corporate buys package
    user = User(email="esg@acme.com", hashed_password="hashed_x", role=RoleEnum.corporate, org_name="ACME")
    pkg = Package(name="Breda Climate Package", region=RegionEnum.zuid, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(user)
    session.add(pkg)
    session.commit()

    session.add(PackageFoodbank(package_id=pkg.id, foodbank_id=fb.id, weight_pct=1.0))
    session.commit()

    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=25000.0, status=StatusEnum.paid, solvimon_id="solv_xyz")
    session.add(sub)
    session.commit()

    # 6. Generate CSR report
    csr = CsrReport(
        subscription_id=sub.id,
        frame_result_id=frame.id,
        file_path="reports/acme-breda-2024.pdf",
        template=TemplateEnum.csrd,
    )
    session.add(csr)
    session.commit()

    sub.csr_report_id = csr.id
    session.add(sub)
    session.commit()
    session.refresh(sub)

    # Assert full chain integrity
    assert sub.csr_report_id == csr.id
    result_sub = session.exec(select(FundSubscription).where(FundSubscription.id == sub.id)).one()
    assert result_sub.status == StatusEnum.paid
    result_frame = session.exec(select(FrameResult).where(FrameResult.report_id == report.id)).one()
    assert result_frame.co2e_total_kg == 1268740.0
```

- [ ] **Step 2: Run — expect import error**

```bash
uv run pytest tests/backend/models/test_integration.py -v
```

Expected: `ImportError` (models not exported from `__init__`)

- [ ] **Step 3: Wire __init__.py**

`src/backend/models/__init__.py`:

```python
from src.backend.models.enums import (
    SourceEnum, RoleEnum, RegionEnum, StatusEnum,
    CounterfactualEnum, TemplateEnum,
)
from src.backend.models.user import User
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.measurements import (
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
)
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import Package, PackageFoodbank, FundSubscription, CsrReport

__all__ = [
    "SourceEnum", "RoleEnum", "RegionEnum", "StatusEnum", "CounterfactualEnum", "TemplateEnum",
    "User",
    "Foodbank", "AnnualReport",
    "FoodVolume", "FoodCategories", "PeopleServed", "Operations", "Donations",
    "FrameResult",
    "Package", "PackageFoodbank", "FundSubscription", "CsrReport",
]
```

- [ ] **Step 4: Run full suite**

```bash
uv run pytest tests/backend/models/ -v
```

Expected: all PASSED (≈20 tests)

- [ ] **Step 5: Update database.py to import all models before create_all**

`src/backend/database.py`:

```python
from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./foodbank.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    # Import all models so SQLModel.metadata is populated before create_all
    import src.backend.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

- [ ] **Step 6: Run full suite again**

```bash
uv run pytest tests/ -v --tb=short
```

Expected: all PASSED

- [ ] **Step 7: Final commit**

```bash
git add src/backend/models/__init__.py src/backend/database.py tests/backend/models/test_integration.py
git commit -m "feat: wire models __init__ and integration test for full data chain"
```
