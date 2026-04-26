# Kavel API Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the full Kavel web app — corporate marketplace where companies buy Climate-Action Packages, a dynamic allocation engine distributes funds across Dutch food banks, and Claude generates CSRD-aligned impact reports delivered via SSE streaming.

**Architecture:** FastAPI serves Jinja2-rendered HTML pages and HTMX partials. SQLite via SQLModel. Auth uses signed session cookies (itsdangerous). Claude streams report text via Server-Sent Events. Allocation engine ranks food banks by impact profile at checkout time and writes weight_pct rows.

**Tech Stack:** Python 3.13, FastAPI, Jinja2, HTMX (CDN), SQLModel/SQLite, Anthropic SDK, itsdangerous, passlib[bcrypt], pytest/httpx

---

## File Map

**New files:**
```
src/backend/models/allocation.py          # Allocation table
src/backend/routers/__init__.py
src/backend/routers/auth.py               # /login /register /logout
src/backend/routers/marketplace.py        # /packages
src/backend/routers/checkout.py           # /checkout
src/backend/routers/dashboard.py          # /dashboard
src/backend/routers/report.py             # /report (SSE)
src/backend/routers/admin.py              # /admin
src/backend/services/__init__.py
src/backend/services/auth.py              # password hashing, session cookie
src/backend/services/allocation.py        # allocation engine
src/backend/services/report.py            # Claude integration
src/backend/app.py                        # FastAPI app + router registration
src/backend/seed.py                       # seed data script
src/frontend/templates/base.html
src/frontend/templates/auth/login.html
src/frontend/templates/auth/register.html
src/frontend/templates/packages/index.html
src/frontend/templates/packages/detail.html
src/frontend/templates/packages/_card.html   # HTMX partial
src/frontend/templates/checkout/confirm.html
src/frontend/templates/checkout/success.html
src/frontend/templates/dashboard/index.html
src/frontend/templates/dashboard/detail.html
src/frontend/templates/report/_stream.html   # SSE partial
src/frontend/templates/admin/foodbanks.html
src/frontend/static/css/main.css
tests/backend/services/__init__.py
tests/backend/services/test_allocation.py
tests/backend/routers/__init__.py
tests/backend/routers/conftest.py            # app + client fixture
tests/backend/routers/test_auth.py
tests/backend/routers/test_marketplace.py
tests/backend/routers/test_checkout.py
```

**Modified files:**
```
pyproject.toml                            # add fastapi, jinja2, httpx, anthropic, itsdangerous
src/backend/models/enums.py               # add ImpactProfileEnum
src/backend/models/marketplace.py         # add impact_profile, top_n to Package
src/backend/models/__init__.py            # export Allocation, ImpactProfileEnum
```

---

## Task 1: Add dependencies

**Files:** `pyproject.toml`

- [ ] **Step 1: Update pyproject.toml**

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
    "fastapi[standard]>=0.115",
    "jinja2>=3.1",
    "itsdangerous>=2.2",
    "anthropic>=0.40",
    "python-multipart>=0.0.9",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
    "httpx>=0.27",
]
```

- [ ] **Step 2: Install**

```bash
uv sync --extra dev
```

Expected: resolves without error.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add fastapi, jinja2, anthropic, itsdangerous dependencies"
```

---

## Task 2: Add ImpactProfileEnum and extend Package model

**Files:**
- Modify: `src/backend/models/enums.py`
- Modify: `src/backend/models/marketplace.py`
- Modify: `src/backend/models/__init__.py`
- Test: `tests/backend/models/test_marketplace.py`

- [ ] **Step 1: Add ImpactProfileEnum to enums.py**

Add after `TemplateEnum`:

```python
class ImpactProfileEnum(str, Enum):
    co2_focus = "co2_focus"
    social_focus = "social_focus"
    balanced = "balanced"
```

- [ ] **Step 2: Extend Package in marketplace.py**

Replace the Package class:

```python
class Package(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None
    region: RegionEnum
    price_eur: float = 25000.0
    co2e_claim_kg: float = 600000.0
    impact_profile: ImpactProfileEnum = ImpactProfileEnum.balanced
    top_n: int = 50
    is_active: bool = True
```

Add import at top of marketplace.py:
```python
from src.backend.models.enums import RegionEnum, StatusEnum, TemplateEnum, ImpactProfileEnum
```

- [ ] **Step 3: Update models/__init__.py exports**

Add `ImpactProfileEnum` to imports and `__all__`.

- [ ] **Step 4: Write failing test**

In `tests/backend/models/test_marketplace.py`, add:

```python
from src.backend.models.enums import ImpactProfileEnum

def test_package_has_impact_profile(session: Session):
    from src.backend.models.foodbank import Foodbank
    fb = Foodbank(name="Test", city="Test", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    pkg = Package(
        name="CO2 Package",
        region=RegionEnum.west,
        price_eur=15000.0,
        co2e_claim_kg=300000.0,
        impact_profile=ImpactProfileEnum.co2_focus,
        top_n=10,
    )
    session.add(pkg)
    session.commit()
    session.refresh(pkg)
    assert pkg.impact_profile == ImpactProfileEnum.co2_focus
    assert pkg.top_n == 10

def test_package_impact_profile_defaults_to_balanced(session: Session):
    pkg = Package(name="Default", region=RegionEnum.west, price_eur=5000.0, co2e_claim_kg=100000.0)
    session.add(pkg)
    session.commit()
    session.refresh(pkg)
    assert pkg.impact_profile == ImpactProfileEnum.balanced
    assert pkg.top_n == 50
```

- [ ] **Step 5: Run test to verify it fails**

```bash
pytest tests/backend/models/test_marketplace.py::test_package_has_impact_profile -v
```

Expected: FAIL (AttributeError or column missing)

- [ ] **Step 6: Run test after implementation**

```bash
pytest tests/backend/models/test_marketplace.py -v
```

Expected: all pass

- [ ] **Step 7: Commit**

```bash
git add src/backend/models/enums.py src/backend/models/marketplace.py src/backend/models/__init__.py tests/backend/models/test_marketplace.py
git commit -m "feat: add ImpactProfileEnum and extend Package with impact_profile, top_n"
```

---

## Task 3: Add Allocation model

**Files:**
- Create: `src/backend/models/allocation.py`
- Modify: `src/backend/models/__init__.py`
- Test: `tests/backend/models/test_marketplace.py`

- [ ] **Step 1: Write failing test**

In `tests/backend/models/test_marketplace.py`, add:

```python
from src.backend.models.allocation import Allocation

def test_allocation_stores_weight_pct(session: Session, report: AnnualReport):
    from src.backend.models.enums import RoleEnum
    from src.backend.models.user import User

    user = User(email="corp@test.com", hashed_password="x", role=RoleEnum.corporate)
    session.add(user)
    session.commit()

    pkg = Package(name="Test Pkg", region=RegionEnum.west, price_eur=10000.0, co2e_claim_kg=200000.0)
    session.add(pkg)
    session.commit()

    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=10000.0)
    session.add(sub)
    session.commit()

    alloc = Allocation(
        subscription_id=sub.id,
        foodbank_id=report.foodbank_id,
        weight_pct=0.6,
    )
    session.add(alloc)
    session.commit()
    session.refresh(alloc)
    assert alloc.weight_pct == 0.6
    assert alloc.subscription_id == sub.id
```

- [ ] **Step 2: Run test to verify it fails**

```bash
pytest tests/backend/models/test_marketplace.py::test_allocation_stores_weight_pct -v
```

Expected: FAIL (ImportError)

- [ ] **Step 3: Create allocation.py**

```python
import uuid
from sqlmodel import Field, SQLModel


class Allocation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="fundsubscription.id", index=True)
    foodbank_id: uuid.UUID = Field(foreign_key="foodbank.id", index=True)
    weight_pct: float
```

- [ ] **Step 4: Add to models/__init__.py**

Add import and export:
```python
from src.backend.models.allocation import Allocation
# add "Allocation" to __all__
```

- [ ] **Step 5: Run test**

```bash
pytest tests/backend/models/test_marketplace.py::test_allocation_stores_weight_pct -v
```

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add src/backend/models/allocation.py src/backend/models/__init__.py tests/backend/models/test_marketplace.py
git commit -m "feat: add Allocation model"
```

---

## Task 4: Allocation engine

**Files:**
- Create: `src/backend/services/__init__.py`
- Create: `src/backend/services/allocation.py`
- Create: `tests/backend/services/__init__.py`
- Create: `tests/backend/services/test_allocation.py`

- [ ] **Step 1: Write failing tests**

Create `tests/backend/services/test_allocation.py`:

```python
import uuid
from datetime import date
from decimal import Decimal
from sqlmodel import Session

from src.backend.models.allocation import Allocation
from src.backend.models.enums import (
    RegionEnum, RoleEnum, SourceEnum, CounterfactualEnum, ImpactProfileEnum
)
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import PeopleServed
from src.backend.models.user import User
from src.backend.services.allocation import compute_allocations


def _make_foodbank_with_data(
    session: Session,
    name: str,
    co2e_kg: float,
    households: int,
) -> Foodbank:
    fb = Foodbank(name=name, city="Test", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    report = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="test.txt",
        ingestion_model="test",
    )
    session.add(report)
    session.commit()
    frame = FrameResult(
        report_id=report.id,
        co2e_total_kg=co2e_kg,
        co2e_produce_kg=co2e_kg * 0.4,
        co2e_meat_fish_kg=co2e_kg * 0.2,
        co2e_dairy_eggs_kg=co2e_kg * 0.15,
        co2e_dry_goods_kg=co2e_kg * 0.15,
        co2e_bread_kg=co2e_kg * 0.1,
        emission_factor_source="test",
        methodology_version="FRAME-NL-v1.0",
    )
    session.add(frame)
    people = PeopleServed(
        report_id=report.id,
        households_weekly=households,
        households_weekly_source=SourceEnum.extracted,
        households_weekly_method="test",
    )
    session.add(people)
    session.commit()
    return fb


def _make_subscription(session: Session, profile: ImpactProfileEnum, top_n: int = 3) -> FundSubscription:
    user = User(email=f"corp_{uuid.uuid4().hex[:6]}@test.com", hashed_password="x", role=RoleEnum.corporate)
    session.add(user)
    session.commit()
    pkg = Package(
        name="Test Package",
        region=RegionEnum.west,
        price_eur=10000.0,
        co2e_claim_kg=200000.0,
        impact_profile=profile,
        top_n=top_n,
    )
    session.add(pkg)
    session.commit()
    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=10000.0)
    session.add(sub)
    session.commit()
    return sub


def test_co2_focus_ranks_by_co2e(session: Session):
    _make_foodbank_with_data(session, "High CO2", co2e_kg=1000.0, households=100)
    _make_foodbank_with_data(session, "Low CO2", co2e_kg=200.0, households=500)
    _make_foodbank_with_data(session, "Mid CO2", co2e_kg=600.0, households=300)
    sub = _make_subscription(session, ImpactProfileEnum.co2_focus, top_n=2)

    allocations = compute_allocations(session, sub.id)
    assert len(allocations) == 2
    # weights sum to 1.0
    assert abs(sum(a.weight_pct for a in allocations) - 1.0) < 1e-6
    # highest CO2 bank gets highest weight
    assert allocations[0].weight_pct > allocations[1].weight_pct


def test_social_focus_ranks_by_households(session: Session):
    _make_foodbank_with_data(session, "Many Families", co2e_kg=100.0, households=2000)
    _make_foodbank_with_data(session, "Few Families", co2e_kg=900.0, households=200)
    sub = _make_subscription(session, ImpactProfileEnum.social_focus, top_n=2)

    allocations = compute_allocations(session, sub.id)
    assert len(allocations) == 2
    assert abs(sum(a.weight_pct for a in allocations) - 1.0) < 1e-6
    # highest household bank gets highest weight
    assert allocations[0].weight_pct > allocations[1].weight_pct


def test_top_n_limits_allocation_count(session: Session):
    for i in range(5):
        _make_foodbank_with_data(session, f"Bank {i}", co2e_kg=float(i + 1) * 100, households=i + 1)
    sub = _make_subscription(session, ImpactProfileEnum.co2_focus, top_n=3)

    allocations = compute_allocations(session, sub.id)
    assert len(allocations) == 3


def test_allocations_written_to_db(session: Session):
    _make_foodbank_with_data(session, "A", co2e_kg=500.0, households=100)
    _make_foodbank_with_data(session, "B", co2e_kg=300.0, households=200)
    sub = _make_subscription(session, ImpactProfileEnum.co2_focus, top_n=2)

    allocations = compute_allocations(session, sub.id, commit=True)
    assert all(a.id is not None for a in allocations)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/backend/services/test_allocation.py -v
```

Expected: FAIL (ImportError)

- [ ] **Step 3: Create services/__init__.py**

```bash
touch src/backend/services/__init__.py tests/backend/services/__init__.py
```

- [ ] **Step 4: Create allocation.py**

```python
import uuid
from sqlmodel import Session, select

from src.backend.models.allocation import Allocation
from src.backend.models.enums import ImpactProfileEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import PeopleServed


def _score(
    co2e_kg: float,
    households: int,
    profile: ImpactProfileEnum,
    max_co2: float,
    max_households: float,
) -> float:
    if profile == ImpactProfileEnum.co2_focus:
        return co2e_kg
    if profile == ImpactProfileEnum.social_focus:
        return float(households)
    # balanced: normalized blend
    norm_co2 = co2e_kg / max_co2 if max_co2 > 0 else 0.0
    norm_social = households / max_households if max_households > 0 else 0.0
    return 0.5 * norm_co2 + 0.5 * norm_social


def compute_allocations(
    session: Session,
    subscription_id: uuid.UUID,
    commit: bool = False,
) -> list[Allocation]:
    sub = session.get(FundSubscription, subscription_id)
    package = session.get(Package, sub.package_id)

    # Fetch all food banks that have both FrameResult and PeopleServed
    rows = session.exec(
        select(Foodbank, FrameResult, PeopleServed)
        .join(AnnualReport, AnnualReport.foodbank_id == Foodbank.id)
        .join(FrameResult, FrameResult.report_id == AnnualReport.id)
        .join(PeopleServed, PeopleServed.report_id == AnnualReport.id)
    ).all()

    if not rows:
        return []

    co2_values = [frame.co2e_total_kg for _, frame, _ in rows]
    social_values = [float(people.households_weekly or 0) for _, _, people in rows]
    max_co2 = max(co2_values) if co2_values else 1.0
    max_social = max(social_values) if social_values else 1.0

    scored = [
        (fb, _score(frame.co2e_total_kg, people.households_weekly or 0,
                    package.impact_profile, max_co2, max_social))
        for fb, frame, people in rows
    ]
    scored.sort(key=lambda x: x[1], reverse=True)
    top = scored[:package.top_n]

    total = sum(score for _, score in top)
    allocations = [
        Allocation(
            subscription_id=subscription_id,
            foodbank_id=fb.id,
            weight_pct=score / total if total > 0 else 1.0 / len(top),
        )
        for fb, score in top
    ]

    if commit:
        for alloc in allocations:
            session.add(alloc)
        session.commit()
        for alloc in allocations:
            session.refresh(alloc)

    return allocations
```

- [ ] **Step 5: Run tests**

```bash
pytest tests/backend/services/test_allocation.py -v
```

Expected: all pass

- [ ] **Step 6: Commit**

```bash
git add src/backend/services/__init__.py src/backend/services/allocation.py tests/backend/services/__init__.py tests/backend/services/test_allocation.py
git commit -m "feat: allocation engine — ranks food banks by impact profile, writes weight_pct rows"
```

---

## Task 5: Auth service

**Files:**
- Create: `src/backend/services/auth.py`
- Test: `tests/backend/services/test_allocation.py` (no auth service unit test needed — tested via routes)

- [ ] **Step 1: Create auth.py**

```python
import os
from typing import Optional

from fastapi import Cookie, Depends, HTTPException, Request, status
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from passlib.context import CryptContext
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.user import User

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
_SECRET = os.getenv("SESSION_SECRET", "dev-secret-change-in-prod")
_signer = URLSafeTimedSerializer(_SECRET)
COOKIE_NAME = "session"


def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


def make_session_cookie(user_id: str) -> str:
    return _signer.dumps(user_id)


def decode_session_cookie(token: str) -> Optional[str]:
    try:
        return _signer.loads(token, max_age=86400 * 7)  # 7 days
    except (BadSignature, SignatureExpired):
        return None


def get_current_user(
    session: Session = Depends(get_session),
    session_cookie: Optional[str] = Cookie(default=None, alias=COOKIE_NAME),
) -> User:
    if not session_cookie:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    user_id = decode_session_cookie(session_cookie)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user


def require_admin(user: User = Depends(get_current_user)) -> User:
    from src.backend.models.enums import RoleEnum
    if user.role != RoleEnum.admin:
        raise HTTPException(status_code=403)
    return user
```

- [ ] **Step 2: Commit**

```bash
git add src/backend/services/auth.py
git commit -m "feat: auth service — password hashing, signed session cookies"
```

---

## Task 6: Seed data

**Files:**
- Create: `src/backend/seed.py`

This creates demo food banks, FrameResults, PeopleServed records, packages, and a demo corporate user.

- [ ] **Step 1: Create seed.py**

```python
"""Run once: python -m src.backend.seed"""
from datetime import date
from decimal import Decimal

from sqlmodel import Session, select

from src.backend.database import create_db_and_tables, engine
from src.backend.models.enums import (
    CounterfactualEnum, ImpactProfileEnum, RegionEnum, RoleEnum, SourceEnum,
)
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import Package
from src.backend.models.measurements import Operations, PeopleServed, FoodVolume
from src.backend.models.user import User
from src.backend.services.auth import hash_password

FOODBANKS = [
    {"name": "Voedselbank Rotterdam", "city": "Rotterdam", "region": RegionEnum.west, "is_regional_dc": True,
     "co2e_kg": 1268740.0, "households": 3200},
    {"name": "Voedselbank Amsterdam", "city": "Amsterdam", "region": RegionEnum.randstad, "is_regional_dc": True,
     "co2e_kg": 1450000.0, "households": 4100},
    {"name": "Voedselbank Den Haag", "city": "Den Haag", "region": RegionEnum.west, "is_regional_dc": False,
     "co2e_kg": 890000.0, "households": 2500},
    {"name": "Voedselbank Utrecht", "city": "Utrecht", "region": RegionEnum.randstad, "is_regional_dc": False,
     "co2e_kg": 720000.0, "households": 1800},
    {"name": "Voedselbank Eindhoven", "city": "Eindhoven", "region": RegionEnum.zuidoost, "is_regional_dc": False,
     "co2e_kg": 650000.0, "households": 1600},
    {"name": "Voedselbank Tilburg", "city": "Tilburg", "region": RegionEnum.zuidoost, "is_regional_dc": True,
     "co2e_kg": 580000.0, "households": 1400},
    {"name": "Voedselbank Groningen", "city": "Groningen", "region": RegionEnum.noord, "is_regional_dc": True,
     "co2e_kg": 420000.0, "households": 1100},
    {"name": "Voedselbank Breda", "city": "Breda", "region": RegionEnum.zuidoost, "is_regional_dc": False,
     "co2e_kg": 390000.0, "households": 980},
    {"name": "Voedselbank Nijmegen", "city": "Nijmegen", "region": RegionEnum.oost, "is_regional_dc": False,
     "co2e_kg": 310000.0, "households": 820},
    {"name": "Voedselbank Zwolle", "city": "Zwolle", "region": RegionEnum.oost, "is_regional_dc": False,
     "co2e_kg": 270000.0, "households": 700},
]

PACKAGES = [
    {
        "name": "CO2 Impact Fund",
        "description": "Funds the 10 food banks with highest CO2e impact in the Netherlands. Ideal for Scope 3 reporting.",
        "region": RegionEnum.randstad,
        "price_eur": 25000.0,
        "co2e_claim_kg": 800000.0,
        "impact_profile": ImpactProfileEnum.co2_focus,
        "top_n": 10,
    },
    {
        "name": "Social Reach Fund",
        "description": "Targets food banks serving the most households. Maximises social impact across your supply chain.",
        "region": RegionEnum.randstad,
        "price_eur": 15000.0,
        "co2e_claim_kg": 400000.0,
        "impact_profile": ImpactProfileEnum.social_focus,
        "top_n": 10,
    },
    {
        "name": "Balanced Impact Fund",
        "description": "Equal weighting of CO2e impact and social reach. Best fit for ESRS E5 and S3 disclosure.",
        "region": RegionEnum.randstad,
        "price_eur": 50000.0,
        "co2e_claim_kg": 1500000.0,
        "impact_profile": ImpactProfileEnum.balanced,
        "top_n": 10,
    },
]


def seed():
    create_db_and_tables()
    with Session(engine) as session:
        # Skip if already seeded
        if session.exec(select(Foodbank)).first():
            print("Already seeded, skipping.")
            return

        # Demo corporate user
        user = User(
            email="demo@acme.nl",
            hashed_password=hash_password("demo1234"),
            role=RoleEnum.corporate,
            org_name="ACME Nederland BV",
        )
        session.add(user)

        # Food banks + annual reports + measurements
        for fb_data in FOODBANKS:
            fb = Foodbank(
                name=fb_data["name"],
                city=fb_data["city"],
                region=fb_data["region"],
                is_regional_dc=fb_data["is_regional_dc"],
            )
            session.add(fb)
            session.flush()

            report = AnnualReport(
                foodbank_id=fb.id,
                year=2024,
                period_start=date(2024, 1, 1),
                period_end=date(2024, 12, 31),
                raw_file_path=f"data/{fb_data['city'].lower()}-2024.pdf",
                ingestion_model="claude-sonnet-4-6",
            )
            session.add(report)
            session.flush()

            co2 = fb_data["co2e_kg"]
            frame = FrameResult(
                report_id=report.id,
                co2e_total_kg=co2,
                co2e_produce_kg=co2 * 0.365,
                co2e_meat_fish_kg=co2 * 0.240,
                co2e_dairy_eggs_kg=co2 * 0.151,
                co2e_dry_goods_kg=co2 * 0.144,
                co2e_bread_kg=co2 * 0.100,
                co2e_prepared_kg=0.0,
                counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
                emission_factor_source="FAO Food Wastage Footprint 2013 + WRAP UK 2022",
                methodology_version="FRAME-NL-v1.0",
            )
            session.add(frame)

            people = PeopleServed(
                report_id=report.id,
                households_weekly=fb_data["households"],
                households_weekly_source=SourceEnum.extracted,
                households_weekly_method="extracted from annual report",
                pct_under_18=0.37,
                pct_under_18_source=SourceEnum.inferred_national_avg,
                pct_under_18_method="NL national average Feiten & Cijfers 2024",
            )
            session.add(people)

        # Packages
        for pkg_data in PACKAGES:
            pkg = Package(**pkg_data)
            session.add(pkg)

        session.commit()
        print("Seeded successfully.")
        print("Demo login: demo@acme.nl / demo1234")


if __name__ == "__main__":
    seed()
```

**Note:** `RegionEnum.zuidoost` and `RegionEnum.randstad` need to exist. Check `enums.py` — if missing, add them before running seed.

- [ ] **Step 2: Verify RegionEnum has needed values, add if missing**

Open `src/backend/models/enums.py`. Ensure:
```python
class RegionEnum(str, Enum):
    noord = "noord"
    oost = "oost"
    zuidoost = "zuidoost"
    zuid = "zuid"
    west = "west"
    randstad = "randstad"
```

- [ ] **Step 3: Run seed**

```bash
python -m src.backend.seed
```

Expected: "Seeded successfully. Demo login: demo@acme.nl / demo1234"

- [ ] **Step 4: Commit**

```bash
git add src/backend/seed.py src/backend/models/enums.py
git commit -m "feat: seed data — 10 Dutch food banks, 3 packages, demo corporate user"
```

---

## Task 7: FastAPI app skeleton

**Files:**
- Create: `src/backend/app.py`
- Create: `src/backend/routers/__init__.py`
- Create: `src/frontend/templates/base.html`
- Create: `src/frontend/static/css/main.css`

- [ ] **Step 1: Create src/backend/routers/__init__.py**

```python
```
(empty)

- [ ] **Step 2: Create src/backend/app.py**

```python
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from src.backend.database import create_db_and_tables

TEMPLATES_DIR = Path(__file__).parent.parent / "frontend" / "templates"
STATIC_DIR = Path(__file__).parent.parent / "frontend" / "static"

app = FastAPI(title="Kavel")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse("packages/index.html", {"request": request})


# Routers registered in later tasks
```

- [ ] **Step 3: Create directory structure**

```bash
mkdir -p src/frontend/templates/auth
mkdir -p src/frontend/templates/packages
mkdir -p src/frontend/templates/checkout
mkdir -p src/frontend/templates/dashboard
mkdir -p src/frontend/templates/report
mkdir -p src/frontend/templates/admin
mkdir -p src/frontend/static/css
```

- [ ] **Step 4: Create base.html**

```html
<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}Kavel{% endblock %}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/htmx.org@1.9.12"></script>
  <script src="https://unpkg.com/htmx.org@1.9.12/dist/ext/sse.js"></script>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body class="bg-gray-50 text-gray-900 min-h-screen">
  <nav class="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
    <a href="/" class="text-xl font-bold text-green-700">🌱 Kavel</a>
    <div class="flex gap-4 text-sm">
      <a href="/packages" class="hover:text-green-700">Packages</a>
      {% if user %}
        <a href="/dashboard" class="hover:text-green-700">Dashboard</a>
        <form method="post" action="/logout" class="inline">
          <button type="submit" class="hover:text-red-600">Logout</button>
        </form>
      {% else %}
        <a href="/login" class="hover:text-green-700">Login</a>
        <a href="/register" class="bg-green-700 text-white px-3 py-1 rounded hover:bg-green-800">Register</a>
      {% endif %}
    </div>
  </nav>

  {% if toast %}
  <div id="toast" class="fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded shadow z-50">
    {{ toast }}
  </div>
  <script>setTimeout(() => document.getElementById('toast')?.remove(), 3000)</script>
  {% endif %}

  <main class="max-w-6xl mx-auto px-6 py-8">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```

- [ ] **Step 5: Create main.css**

```css
/* Kavel — minimal overrides on top of Tailwind */
.htmx-indicator { opacity: 0; transition: opacity 200ms ease-in; }
.htmx-request .htmx-indicator { opacity: 1; }
.htmx-request.htmx-indicator { opacity: 1; }
```

- [ ] **Step 6: Verify app starts**

```bash
uvicorn src.backend.app:app --reload
```

Expected: server starts at http://127.0.0.1:8000, no errors.

- [ ] **Step 7: Commit**

```bash
git add src/backend/app.py src/backend/routers/__init__.py src/frontend/templates/base.html src/frontend/static/css/main.css
git commit -m "feat: FastAPI app skeleton with Jinja2, HTMX, base template"
```

---

## Task 8: Auth routes

**Files:**
- Create: `src/backend/routers/auth.py`
- Create: `src/frontend/templates/auth/login.html`
- Create: `src/frontend/templates/auth/register.html`
- Create: `tests/backend/routers/conftest.py`
- Create: `tests/backend/routers/__init__.py`
- Create: `tests/backend/routers/test_auth.py`

- [ ] **Step 1: Create routers/conftest.py**

```python
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

import src.backend.models  # noqa: F401
from src.backend.app import app
from src.backend.database import get_session


@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app, follow_redirects=False) as c:
        yield c
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
```

- [ ] **Step 2: Write failing auth tests**

Create `tests/backend/routers/test_auth.py`:

```python
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.enums import RoleEnum
from src.backend.models.user import User
from src.backend.services.auth import hash_password


def _create_user(client: TestClient, email: str = "test@corp.nl", password: str = "pass1234"):
    resp = client.post("/register", data={"email": email, "password": password, "org_name": "Test BV"})
    return resp


def test_register_creates_user(client: TestClient):
    resp = _create_user(client)
    assert resp.status_code == 303
    assert resp.headers["location"] == "/login"


def test_register_duplicate_email_fails(client: TestClient):
    _create_user(client)
    resp = _create_user(client)
    assert resp.status_code == 400


def test_login_sets_cookie(client: TestClient):
    _create_user(client)
    resp = client.post("/login", data={"email": "test@corp.nl", "password": "pass1234"})
    assert resp.status_code == 303
    assert "session" in resp.cookies


def test_login_wrong_password(client: TestClient):
    _create_user(client)
    resp = client.post("/login", data={"email": "test@corp.nl", "password": "wrong"})
    assert resp.status_code == 200  # re-renders login with error
    assert b"Invalid" in resp.content


def test_logout_clears_cookie(client: TestClient):
    _create_user(client)
    client.post("/login", data={"email": "test@corp.nl", "password": "pass1234"})
    resp = client.post("/logout")
    assert resp.status_code == 303
    assert resp.cookies.get("session") == "" or "session" not in client.cookies
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/backend/routers/test_auth.py -v
```

Expected: FAIL (404 — routes not registered)

- [ ] **Step 4: Create routers/auth.py**

```python
from fastapi import APIRouter, Depends, Form, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.enums import RoleEnum
from src.backend.models.user import User
from src.backend.services.auth import (
    COOKIE_NAME, hash_password, make_session_cookie, verify_password,
)

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "frontend" / "templates"))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.post("/login")
def login(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    session: Session = Depends(get_session),
):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "Invalid email or password"},
            status_code=400,
        )
    response = RedirectResponse(url="/packages", status_code=status.HTTP_303_SEE_OTHER)
    response.set_cookie(COOKIE_NAME, make_session_cookie(str(user.id)), httponly=True, samesite="lax")
    return response


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.post("/register")
def register(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    org_name: str = Form(),
    session: Session = Depends(get_session),
):
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        return templates.TemplateResponse(
            "auth/register.html",
            {"request": request, "error": "Email already registered"},
            status_code=400,
        )
    user = User(email=email, hashed_password=hash_password(password), role=RoleEnum.corporate, org_name=org_name)
    session.add(user)
    session.commit()
    return RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout")
def logout():
    response = RedirectResponse(url="/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(COOKIE_NAME)
    return response
```

- [ ] **Step 5: Register router in app.py**

Add to `src/backend/app.py` after existing imports:

```python
from src.backend.routers import auth as auth_router
app.include_router(auth_router.router)
```

- [ ] **Step 6: Create login.html**

```html
{% extends "base.html" %}
{% block title %}Login — Kavel{% endblock %}
{% block content %}
<div class="max-w-md mx-auto mt-16">
  <h1 class="text-2xl font-bold mb-6">Login</h1>
  {% if error %}
  <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded mb-4">{{ error }}</div>
  {% endif %}
  <form method="post" action="/login" class="space-y-4">
    <div>
      <label class="block text-sm font-medium mb-1">Email</label>
      <input name="email" type="email" required class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500">
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Password</label>
      <input name="password" type="password" required class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500">
    </div>
    <button type="submit" class="w-full bg-green-700 text-white py-2 rounded hover:bg-green-800 font-medium">Login</button>
  </form>
  <p class="mt-4 text-sm text-center">No account? <a href="/register" class="text-green-700 hover:underline">Register</a></p>
</div>
{% endblock %}
```

- [ ] **Step 7: Create register.html**

```html
{% extends "base.html" %}
{% block title %}Register — Kavel{% endblock %}
{% block content %}
<div class="max-w-md mx-auto mt-16">
  <h1 class="text-2xl font-bold mb-6">Create account</h1>
  {% if error %}
  <div class="bg-red-50 border border-red-200 text-red-700 px-4 py-2 rounded mb-4">{{ error }}</div>
  {% endif %}
  <form method="post" action="/register" class="space-y-4">
    <div>
      <label class="block text-sm font-medium mb-1">Organisation name</label>
      <input name="org_name" type="text" required class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500">
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Email</label>
      <input name="email" type="email" required class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500">
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Password</label>
      <input name="password" type="password" required minlength="8" class="w-full border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-green-500">
    </div>
    <button type="submit" class="w-full bg-green-700 text-white py-2 rounded hover:bg-green-800 font-medium">Create account</button>
  </form>
  <p class="mt-4 text-sm text-center">Already registered? <a href="/login" class="text-green-700 hover:underline">Login</a></p>
</div>
{% endblock %}
```

- [ ] **Step 8: Run tests**

```bash
pytest tests/backend/routers/test_auth.py -v
```

Expected: all pass

- [ ] **Step 9: Commit**

```bash
git add src/backend/routers/auth.py src/frontend/templates/auth/ tests/backend/routers/ src/backend/app.py
git commit -m "feat: auth routes — login, register, logout with signed session cookies"
```

---

## Task 9: Marketplace routes

**Files:**
- Create: `src/backend/routers/marketplace.py`
- Create: `src/frontend/templates/packages/index.html`
- Create: `src/frontend/templates/packages/_card.html`
- Create: `src/frontend/templates/packages/detail.html`
- Create: `tests/backend/routers/test_marketplace.py`

- [ ] **Step 1: Write failing tests**

Create `tests/backend/routers/test_marketplace.py`:

```python
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.enums import ImpactProfileEnum, RegionEnum, RoleEnum
from src.backend.models.marketplace import Package
from src.backend.models.user import User
from src.backend.services.auth import COOKIE_NAME, hash_password, make_session_cookie


def _seed_package(client: TestClient) -> str:
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    pkg = Package(
        name="Test CO2 Fund",
        region=RegionEnum.west,
        price_eur=25000.0,
        co2e_claim_kg=600000.0,
        impact_profile=ImpactProfileEnum.co2_focus,
    )
    session.add(pkg)
    session.commit()
    return str(pkg.id)


def _login(client: TestClient):
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    user = User(email="corp@test.nl", hashed_password=hash_password("pass"), role=RoleEnum.corporate, org_name="Test")
    session.add(user)
    session.commit()
    client.cookies.set(COOKIE_NAME, make_session_cookie(str(user.id)))


def test_packages_page_returns_200(client: TestClient):
    resp = client.get("/packages")
    assert resp.status_code == 200
    assert b"Kavel" in resp.content


def test_packages_page_shows_packages(client: TestClient):
    _seed_package(client)
    resp = client.get("/packages")
    assert b"Test CO2 Fund" in resp.content


def test_package_detail_returns_200(client: TestClient):
    pkg_id = _seed_package(client)
    resp = client.get(f"/packages/{pkg_id}")
    assert resp.status_code == 200


def test_package_detail_404_on_missing(client: TestClient):
    import uuid
    resp = client.get(f"/packages/{uuid.uuid4()}")
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/backend/routers/test_marketplace.py -v
```

Expected: FAIL (404)

- [ ] **Step 3: Create routers/marketplace.py**

```python
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.enums import ImpactProfileEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import Package
from src.backend.models.measurements import PeopleServed
from src.backend.services.auth import get_current_user
from src.backend.models.user import User

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "frontend" / "templates"))


def _get_packages(session: Session, profile: str | None = None) -> list[Package]:
    q = select(Package).where(Package.is_active == True)
    if profile:
        try:
            q = q.where(Package.impact_profile == ImpactProfileEnum(profile))
        except ValueError:
            pass
    return session.exec(q).all()


@router.get("/packages", response_class=HTMLResponse)
def packages_page(
    request: Request,
    profile: str | None = None,
    session: Session = Depends(get_session),
):
    packages = _get_packages(session, profile)
    is_htmx = request.headers.get("HX-Request") == "true"
    template = "packages/_cards.html" if is_htmx else "packages/index.html"
    return templates.TemplateResponse(template, {"request": request, "packages": packages, "profile": profile})


@router.get("/packages/{package_id}", response_class=HTMLResponse)
def package_detail(
    request: Request,
    package_id: uuid.UUID,
    session: Session = Depends(get_session),
):
    package = session.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("packages/detail.html", {"request": request, "package": package})
```

- [ ] **Step 4: Register router in app.py**

```python
from src.backend.routers import marketplace as marketplace_router
app.include_router(marketplace_router.router)
```

- [ ] **Step 5: Create packages/index.html**

```html
{% extends "base.html" %}
{% block title %}Climate-Action Packages — Kavel{% endblock %}
{% block content %}
<div class="mb-8">
  <h1 class="text-3xl font-bold mb-2">Climate-Action Packages</h1>
  <p class="text-gray-600">Fund Dutch food banks and generate CSRD-ready impact reports.</p>
</div>

<div class="flex gap-3 mb-6">
  <button hx-get="/packages" hx-target="#package-grid" hx-push-url="true"
          class="px-4 py-1.5 rounded-full text-sm border {% if not profile %}bg-green-700 text-white border-green-700{% else %}border-gray-300 hover:border-green-700{% endif %}">
    All
  </button>
  <button hx-get="/packages?profile=co2_focus" hx-target="#package-grid" hx-push-url="true"
          class="px-4 py-1.5 rounded-full text-sm border {% if profile == 'co2_focus' %}bg-green-700 text-white border-green-700{% else %}border-gray-300 hover:border-green-700{% endif %}">
    CO₂ Impact
  </button>
  <button hx-get="/packages?profile=social_focus" hx-target="#package-grid" hx-push-url="true"
          class="px-4 py-1.5 rounded-full text-sm border {% if profile == 'social_focus' %}bg-green-700 text-white border-green-700{% else %}border-gray-300 hover:border-green-700{% endif %}">
    Social Reach
  </button>
  <button hx-get="/packages?profile=balanced" hx-target="#package-grid" hx-push-url="true"
          class="px-4 py-1.5 rounded-full text-sm border {% if profile == 'balanced' %}bg-green-700 text-white border-green-700{% else %}border-gray-300 hover:border-green-700{% endif %}">
    Balanced
  </button>
</div>

<div id="package-grid" class="grid grid-cols-1 md:grid-cols-3 gap-6">
  {% for pkg in packages %}
    {% include "packages/_card.html" %}
  {% endfor %}
</div>
{% endblock %}
```

- [ ] **Step 6: Create packages/_card.html**

```html
<div class="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
  <div class="flex items-start justify-between mb-3">
    <span class="text-xs font-medium px-2 py-1 rounded-full
      {% if pkg.impact_profile.value == 'co2_focus' %}bg-blue-50 text-blue-700
      {% elif pkg.impact_profile.value == 'social_focus' %}bg-orange-50 text-orange-700
      {% else %}bg-green-50 text-green-700{% endif %}">
      {{ pkg.impact_profile.value | replace('_', ' ') | title }}
    </span>
    <span class="text-lg font-bold text-green-700">€{{ "{:,.0f}".format(pkg.price_eur) }}</span>
  </div>
  <h3 class="text-lg font-semibold mb-2">{{ pkg.name }}</h3>
  <p class="text-gray-500 text-sm mb-4">{{ pkg.description or '' }}</p>
  <div class="text-sm text-gray-600 mb-4">
    <span class="font-medium">{{ "{:,.0f}".format(pkg.co2e_claim_kg / 1000) }} tCO₂e</span> avoided impact
  </div>
  <a href="/packages/{{ pkg.id }}"
     class="block text-center bg-green-700 text-white py-2 rounded-lg hover:bg-green-800 text-sm font-medium">
    View package
  </a>
</div>
```

- [ ] **Step 7: Create packages/detail.html**

```html
{% extends "base.html" %}
{% block title %}{{ package.name }} — Kavel{% endblock %}
{% block content %}
<div class="max-w-2xl">
  <a href="/packages" class="text-sm text-gray-500 hover:text-green-700 mb-4 inline-block">← All packages</a>
  <h1 class="text-3xl font-bold mb-2">{{ package.name }}</h1>
  <p class="text-gray-600 mb-6">{{ package.description or '' }}</p>

  <div class="grid grid-cols-3 gap-4 mb-8">
    <div class="bg-green-50 rounded-xl p-4 text-center">
      <div class="text-2xl font-bold text-green-700">€{{ "{:,.0f}".format(package.price_eur) }}</div>
      <div class="text-xs text-gray-600 mt-1">Annual contribution</div>
    </div>
    <div class="bg-blue-50 rounded-xl p-4 text-center">
      <div class="text-2xl font-bold text-blue-700">{{ "{:,.0f}".format(package.co2e_claim_kg / 1000) }} t</div>
      <div class="text-xs text-gray-600 mt-1">CO₂e avoided</div>
    </div>
    <div class="bg-orange-50 rounded-xl p-4 text-center">
      <div class="text-2xl font-bold text-orange-700">{{ package.top_n }}</div>
      <div class="text-xs text-gray-600 mt-1">Food banks funded</div>
    </div>
  </div>

  <div class="bg-gray-50 rounded-xl p-4 mb-8 text-sm text-gray-600">
    <strong>Allocation method:</strong>
    {% if package.impact_profile.value == 'co2_focus' %}
      Funds top {{ package.top_n }} food banks by CO₂e avoided, weighted proportionally.
    {% elif package.impact_profile.value == 'social_focus' %}
      Funds top {{ package.top_n }} food banks by households served weekly, weighted proportionally.
    {% else %}
      Funds top {{ package.top_n }} food banks using a balanced score of CO₂e impact and social reach.
    {% endif %}
    <br><span class="text-xs">Methodology: FRAME-NL-v1.0 · ESRS E5/S3 compliant</span>
  </div>

  <form method="post" action="/packages/{{ package.id }}/checkout">
    <button type="submit"
            class="bg-green-700 text-white px-8 py-3 rounded-xl hover:bg-green-800 font-semibold text-lg">
      Fund this package — €{{ "{:,.0f}".format(package.price_eur) }}
    </button>
  </form>
</div>
{% endblock %}
```

- [ ] **Step 8: Create packages/_cards.html (HTMX partial)**

```html
{% for pkg in packages %}
  {% include "packages/_card.html" %}
{% endfor %}
```

- [ ] **Step 9: Run tests**

```bash
pytest tests/backend/routers/test_marketplace.py -v
```

Expected: all pass

- [ ] **Step 10: Commit**

```bash
git add src/backend/routers/marketplace.py src/frontend/templates/packages/ tests/backend/routers/test_marketplace.py src/backend/app.py
git commit -m "feat: marketplace routes — package listing with HTMX filter, package detail"
```

---

## Task 10: Checkout routes + allocation at purchase

**Files:**
- Create: `src/backend/routers/checkout.py`
- Create: `src/frontend/templates/checkout/confirm.html`
- Create: `src/frontend/templates/checkout/success.html`
- Create: `tests/backend/routers/test_checkout.py`

- [ ] **Step 1: Write failing tests**

Create `tests/backend/routers/test_checkout.py`:

```python
import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.enums import ImpactProfileEnum, RegionEnum, RoleEnum
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.user import User
from src.backend.services.auth import COOKIE_NAME, hash_password, make_session_cookie


def _setup(client: TestClient):
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    user = User(email="corp@test.nl", hashed_password=hash_password("pass"), role=RoleEnum.corporate, org_name="ACME")
    session.add(user)
    pkg = Package(name="Test Fund", region=RegionEnum.west, price_eur=10000.0,
                  co2e_claim_kg=200000.0, impact_profile=ImpactProfileEnum.co2_focus, top_n=5)
    session.add(pkg)
    session.commit()
    client.cookies.set(COOKIE_NAME, make_session_cookie(str(user.id)))
    return user, pkg


def test_checkout_post_creates_subscription(client: TestClient):
    user, pkg = _setup(client)
    resp = client.post(f"/packages/{pkg.id}/checkout")
    assert resp.status_code == 303
    assert "/checkout/" in resp.headers["location"]


def test_confirm_page_returns_200(client: TestClient):
    user, pkg = _setup(client)
    resp = client.post(f"/packages/{pkg.id}/checkout")
    sub_url = resp.headers["location"]
    resp2 = client.get(sub_url)
    assert resp2.status_code == 200


def test_pay_creates_allocations(client: TestClient):
    from datetime import date
    from src.backend.models.foodbank import AnnualReport, Foodbank
    from src.backend.models.frame import FrameResult
    from src.backend.models.measurements import PeopleServed
    from src.backend.models.enums import CounterfactualEnum, SourceEnum

    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    user, pkg = _setup(client)

    # Seed food bank data so allocation engine has something to work with
    for i in range(3):
        fb = Foodbank(name=f"Bank {i}", city="Test", region=RegionEnum.west, is_regional_dc=False)
        session.add(fb)
        session.flush()
        rep = AnnualReport(foodbank_id=fb.id, year=2024, period_start=date(2024,1,1),
                           period_end=date(2024,12,31), raw_file_path="test.txt", ingestion_model="test")
        session.add(rep)
        session.flush()
        session.add(FrameResult(report_id=rep.id, co2e_total_kg=float(i+1)*100,
                                co2e_produce_kg=float(i+1)*40, co2e_meat_fish_kg=float(i+1)*20,
                                co2e_dairy_eggs_kg=float(i+1)*15, co2e_dry_goods_kg=float(i+1)*15,
                                co2e_bread_kg=float(i+1)*10,
                                emission_factor_source="test", methodology_version="FRAME-NL-v1.0"))
        session.add(PeopleServed(report_id=rep.id, households_weekly=i*100+50,
                                  households_weekly_source=SourceEnum.extracted,
                                  households_weekly_method="test"))
    session.commit()

    resp = client.post(f"/packages/{pkg.id}/checkout")
    sub_url = resp.headers["location"]
    confirm_url = sub_url.replace("/confirm", "")
    sub_id = sub_url.split("/checkout/")[1].replace("/confirm", "")

    resp2 = client.post(f"/checkout/{sub_id}/pay")
    assert resp2.status_code == 303

    allocations = session.exec(select(Allocation).where(Allocation.subscription_id == uuid.UUID(sub_id))).all()
    assert len(allocations) > 0
    assert abs(sum(a.weight_pct for a in allocations) - 1.0) < 1e-6
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/backend/routers/test_checkout.py -v
```

Expected: FAIL

- [ ] **Step 3: Create routers/checkout.py**

```python
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.enums import StatusEnum
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.user import User
from src.backend.services.allocation import compute_allocations
from src.backend.services.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "frontend" / "templates"))


@router.post("/packages/{package_id}/checkout")
def create_checkout(
    package_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    package = session.get(Package, package_id)
    if not package:
        raise HTTPException(status_code=404)
    sub = FundSubscription(
        user_id=user.id,
        package_id=package_id,
        amount_eur=package.price_eur,
        status=StatusEnum.pending,
    )
    session.add(sub)
    session.commit()
    return RedirectResponse(url=f"/checkout/{sub.id}/confirm", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/checkout/{sub_id}/confirm", response_class=HTMLResponse)
def confirm_page(
    request: Request,
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    package = session.get(Package, sub.package_id)
    return templates.TemplateResponse("checkout/confirm.html", {
        "request": request, "sub": sub, "package": package, "user": user,
    })


@router.post("/checkout/{sub_id}/pay")
def pay(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    sub.status = StatusEnum.paid
    session.add(sub)
    compute_allocations(session, sub_id, commit=True)
    return RedirectResponse(url=f"/checkout/{sub_id}/success", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/checkout/{sub_id}/success", response_class=HTMLResponse)
def success_page(
    request: Request,
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    package = session.get(Package, sub.package_id)
    return templates.TemplateResponse("checkout/success.html", {
        "request": request, "sub": sub, "package": package, "user": user,
    })
```

- [ ] **Step 4: Register router in app.py**

```python
from src.backend.routers import checkout as checkout_router
app.include_router(checkout_router.router)
```

- [ ] **Step 5: Create checkout/confirm.html**

```html
{% extends "base.html" %}
{% block title %}Confirm purchase — Kavel{% endblock %}
{% block content %}
<div class="max-w-xl">
  <h1 class="text-2xl font-bold mb-6">Confirm your contribution</h1>

  <div class="bg-white rounded-xl border border-gray-200 p-6 mb-6 space-y-3">
    <div class="flex justify-between text-sm">
      <span class="text-gray-600">Package</span>
      <span class="font-medium">{{ package.name }}</span>
    </div>
    <div class="flex justify-between text-sm">
      <span class="text-gray-600">Organisation</span>
      <span class="font-medium">{{ user.org_name }}</span>
    </div>
    <div class="flex justify-between text-sm">
      <span class="text-gray-600">CO₂e impact</span>
      <span class="font-medium">{{ "{:,.0f}".format(package.co2e_claim_kg / 1000) }} tCO₂e</span>
    </div>
    <div class="border-t pt-3 flex justify-between">
      <span class="font-semibold">Annual contribution</span>
      <span class="font-bold text-green-700 text-lg">€{{ "{:,.0f}".format(sub.amount_eur) }}</span>
    </div>
  </div>

  <form method="post" action="/checkout/{{ sub.id }}/pay">
    <button type="submit"
            hx-post="/checkout/{{ sub.id }}/pay"
            hx-indicator="#pay-spinner"
            class="w-full bg-green-700 text-white py-3 rounded-xl hover:bg-green-800 font-semibold text-lg relative">
      <span>Confirm & fund</span>
      <span id="pay-spinner" class="htmx-indicator absolute right-4 top-3">⏳</span>
    </button>
  </form>
  <p class="text-xs text-gray-400 mt-3 text-center">No actual payment — demo mode</p>
</div>
{% endblock %}
```

- [ ] **Step 6: Create checkout/success.html**

```html
{% extends "base.html" %}
{% block title %}Thank you — Kavel{% endblock %}
{% block content %}
<div class="max-w-xl text-center">
  <div class="text-6xl mb-4">🌱</div>
  <h1 class="text-3xl font-bold mb-2">Thank you, {{ user.org_name }}!</h1>
  <p class="text-gray-600 mb-8">
    Your contribution to <strong>{{ package.name }}</strong> has been confirmed.
    Funds are now allocated across {{ package.top_n }} Dutch food banks.
  </p>
  <div class="flex gap-4 justify-center">
    <a href="/dashboard/{{ sub.id }}"
       class="bg-green-700 text-white px-6 py-2.5 rounded-xl hover:bg-green-800 font-medium">
      View impact dashboard
    </a>
    <a href="/packages" class="border border-gray-300 px-6 py-2.5 rounded-xl hover:border-green-700 font-medium">
      Browse packages
    </a>
  </div>
</div>
{% endblock %}
```

- [ ] **Step 7: Run tests**

```bash
pytest tests/backend/routers/test_checkout.py -v
```

Expected: all pass

- [ ] **Step 8: Commit**

```bash
git add src/backend/routers/checkout.py src/frontend/templates/checkout/ tests/backend/routers/test_checkout.py src/backend/app.py
git commit -m "feat: checkout flow — subscription creation, mock payment, allocation engine wired at pay"
```

---

## Task 11: Dashboard routes

**Files:**
- Create: `src/backend/routers/dashboard.py`
- Create: `src/frontend/templates/dashboard/index.html`
- Create: `src/frontend/templates/dashboard/detail.html`

- [ ] **Step 1: Create routers/dashboard.py**

```python
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import CsrReport, FundSubscription, Package
from src.backend.models.user import User
from src.backend.services.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "frontend" / "templates"))


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    subs = session.exec(
        select(FundSubscription).where(FundSubscription.user_id == user.id)
    ).all()
    return templates.TemplateResponse("dashboard/index.html", {
        "request": request, "subs": subs, "user": user,
    })


def _get_allocation_details(session: Session, sub_id: uuid.UUID) -> list[dict]:
    allocations = session.exec(
        select(Allocation).where(Allocation.subscription_id == sub_id)
    ).all()
    result = []
    for alloc in allocations:
        fb = session.get(Foodbank, alloc.foodbank_id)
        annual = session.exec(
            select(AnnualReport).where(AnnualReport.foodbank_id == alloc.foodbank_id)
        ).first()
        frame = session.exec(
            select(FrameResult).where(FrameResult.report_id == annual.id)
        ).first() if annual else None
        result.append({
            "foodbank": fb,
            "weight_pct": alloc.weight_pct,
            "co2e_attributed_kg": (frame.co2e_total_kg * alloc.weight_pct) if frame else 0.0,
        })
    return sorted(result, key=lambda x: x["weight_pct"], reverse=True)


@router.get("/dashboard/{sub_id}", response_class=HTMLResponse)
def dashboard_detail(
    request: Request,
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    package = session.get(Package, sub.package_id)
    allocations = _get_allocation_details(session, sub_id)
    total_co2e = sum(a["co2e_attributed_kg"] for a in allocations)
    report = session.exec(
        select(CsrReport).where(CsrReport.subscription_id == sub_id)
    ).first()
    return templates.TemplateResponse("dashboard/detail.html", {
        "request": request, "sub": sub, "package": package,
        "allocations": allocations, "total_co2e": total_co2e,
        "report": report, "user": user,
    })
```

- [ ] **Step 2: Register router in app.py**

```python
from src.backend.routers import dashboard as dashboard_router
app.include_router(dashboard_router.router)
```

- [ ] **Step 3: Create dashboard/index.html**

```html
{% extends "base.html" %}
{% block title %}Dashboard — Kavel{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-6">{{ user.org_name }} — Impact Dashboard</h1>

{% if not subs %}
<div class="text-center py-16 text-gray-500">
  <p class="mb-4">No active contributions yet.</p>
  <a href="/packages" class="bg-green-700 text-white px-6 py-2.5 rounded-xl hover:bg-green-800">Browse packages</a>
</div>
{% else %}
<div class="space-y-4">
  {% for sub in subs %}
  <a href="/dashboard/{{ sub.id }}"
     class="block bg-white rounded-xl border border-gray-200 p-5 hover:shadow-md transition-shadow">
    <div class="flex items-center justify-between">
      <div>
        <div class="font-semibold">Subscription #{{ loop.index }}</div>
        <div class="text-sm text-gray-500">{{ sub.purchased_at.strftime('%d %b %Y') }} · €{{ "{:,.0f}".format(sub.amount_eur) }}/yr</div>
      </div>
      <span class="text-xs px-2 py-1 rounded-full
        {% if sub.status.value == 'paid' %}bg-green-50 text-green-700{% else %}bg-yellow-50 text-yellow-700{% endif %}">
        {{ sub.status.value }}
      </span>
    </div>
  </a>
  {% endfor %}
</div>
{% endif %}
{% endblock %}
```

- [ ] **Step 4: Create dashboard/detail.html**

```html
{% extends "base.html" %}
{% block title %}Impact Detail — Kavel{% endblock %}
{% block content %}
<a href="/dashboard" class="text-sm text-gray-500 hover:text-green-700 mb-4 inline-block">← Dashboard</a>
<h1 class="text-2xl font-bold mb-2">{{ package.name }}</h1>
<p class="text-gray-500 text-sm mb-6">Contribution of €{{ "{:,.0f}".format(sub.amount_eur) }} · {{ sub.purchased_at.strftime('%d %b %Y') }}</p>

<div class="grid grid-cols-2 gap-4 mb-8">
  <div class="bg-green-50 rounded-xl p-4 text-center">
    <div class="text-3xl font-bold text-green-700">{{ "{:,.0f}".format(total_co2e / 1000) }}</div>
    <div class="text-sm text-gray-600 mt-1">tonnes CO₂e attributed</div>
  </div>
  <div class="bg-blue-50 rounded-xl p-4 text-center">
    <div class="text-3xl font-bold text-blue-700">{{ allocations | length }}</div>
    <div class="text-sm text-gray-600 mt-1">food banks funded</div>
  </div>
</div>

<h2 class="text-lg font-semibold mb-3">Allocation breakdown</h2>
<div class="space-y-2 mb-8">
  {% for alloc in allocations %}
  <div class="bg-white rounded-lg border border-gray-100 p-3 flex items-center gap-4">
    <div class="flex-1">
      <div class="font-medium text-sm">{{ alloc.foodbank.name }}</div>
      <div class="text-xs text-gray-500">{{ alloc.foodbank.city }}</div>
    </div>
    <div class="text-right text-sm">
      <div class="font-semibold">{{ "{:.1f}".format(alloc.weight_pct * 100) }}%</div>
      <div class="text-xs text-gray-500">{{ "{:,.0f}".format(alloc.co2e_attributed_kg / 1000) }} tCO₂e</div>
    </div>
    <div class="w-24 bg-gray-100 rounded-full h-2">
      <div class="bg-green-500 h-2 rounded-full" style="width: {{ alloc.weight_pct * 100 }}%"></div>
    </div>
  </div>
  {% endfor %}
</div>

<div class="border-t pt-6">
  {% if report %}
    <a href="/report/{{ sub.id }}/download"
       class="bg-green-700 text-white px-6 py-2.5 rounded-xl hover:bg-green-800 font-medium">
      Download CSRD Report
    </a>
  {% else %}
    <button hx-post="/report/{{ sub.id }}/generate"
            hx-target="#report-section"
            hx-swap="outerHTML"
            class="bg-blue-600 text-white px-6 py-2.5 rounded-xl hover:bg-blue-700 font-medium">
      Generate CSRD Report
    </button>
    <div id="report-section"></div>
  {% endif %}
</div>
{% endblock %}
```

- [ ] **Step 5: Commit**

```bash
git add src/backend/routers/dashboard.py src/frontend/templates/dashboard/ src/backend/app.py
git commit -m "feat: dashboard routes — subscription list and allocation breakdown detail"
```

---

## Task 12: Claude CSRD report generation (SSE)

**Files:**
- Create: `src/backend/services/report.py`
- Create: `src/backend/routers/report.py`
- Create: `src/frontend/templates/report/_stream.html`

- [ ] **Step 1: Create services/report.py**

```python
import os
from typing import AsyncIterator

import anthropic

from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.user import User

_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

_SYSTEM = """You are a sustainability reporting specialist. Write CSRD-aligned impact reports for corporate sponsors of Dutch food banks. Use ESRS E5 (circular economy) and ESRS S3 (affected communities) language. Be specific, factual, and concise. Format in Markdown."""


def _build_prompt(
    user: User,
    package: Package,
    total_co2e_kg: float,
    allocations: list[dict],
    year: int = 2024,
) -> str:
    alloc_lines = "\n".join(
        f"- {a['foodbank'].name} ({a['foodbank'].city}): {a['weight_pct']*100:.1f}% share, {a['co2e_attributed_kg']/1000:.1f} tCO₂e attributed"
        for a in allocations[:10]
    )
    return f"""Generate a CSRD impact report section for:

**Company:** {user.org_name}
**Package:** {package.name}
**Reporting year:** {year}
**Annual contribution:** €{package.price_eur:,.0f}
**Total CO₂e avoided:** {total_co2e_kg/1000:,.1f} tonnes CO₂e
**Methodology:** FRAME-NL-v1.0 (landfill counterfactual comparison, FAO emission factors)
**Allocation:**
{alloc_lines}

Write a 400-600 word CSRD-ready report section covering:
1. Executive summary of the contribution
2. Environmental impact (ESRS E5) — CO₂e methodology, counterfactual, confidence level
3. Social impact (ESRS S3) — households supported, food poverty context in NL
4. Attribution methodology — how the {package.top_n} food banks were selected
5. Forward commitment and monitoring

Use precise language suitable for inclusion in an annual sustainability report. Include a note that estimates use FRAME-NL-v1.0 methodology and are suitable for CSRD disclosure under ESRS E5/S3."""


async def stream_report(
    user: User,
    package: Package,
    total_co2e_kg: float,
    allocations: list[dict],
) -> AsyncIterator[str]:
    prompt = _build_prompt(user, package, total_co2e_kg, allocations)
    with _client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield text
```

- [ ] **Step 2: Create routers/report.py**

```python
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.enums import StatusEnum, TemplateEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import CsrReport, FundSubscription, Package
from src.backend.models.user import User
from src.backend.services.auth import get_current_user
from src.backend.services.report import stream_report

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "frontend" / "templates"))


def _get_allocation_details(session: Session, sub_id: uuid.UUID) -> list[dict]:
    allocations = session.exec(select(Allocation).where(Allocation.subscription_id == sub_id)).all()
    result = []
    for alloc in allocations:
        fb = session.get(Foodbank, alloc.foodbank_id)
        annual = session.exec(select(AnnualReport).where(AnnualReport.foodbank_id == alloc.foodbank_id)).first()
        frame = session.exec(select(FrameResult).where(FrameResult.report_id == annual.id)).first() if annual else None
        result.append({
            "foodbank": fb,
            "weight_pct": alloc.weight_pct,
            "co2e_attributed_kg": (frame.co2e_total_kg * alloc.weight_pct) if frame else 0.0,
        })
    return sorted(result, key=lambda x: x["weight_pct"], reverse=True)


@router.post("/report/{sub_id}/generate", response_class=HTMLResponse)
def start_report(
    request: Request,
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("report/_stream.html", {
        "request": request, "sub_id": sub_id,
    })


@router.get("/report/{sub_id}/stream")
async def stream(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    package = session.get(Package, sub.package_id)
    allocations = _get_allocation_details(session, sub_id)
    total_co2e = sum(a["co2e_attributed_kg"] for a in allocations)

    async def event_generator():
        full_text = []
        async for chunk in stream_report(user, package, total_co2e, allocations):
            full_text.append(chunk)
            yield f"data: {chunk}\n\n"

        # Save completed report
        report = CsrReport(
            subscription_id=sub_id,
            frame_result_id=None,
            file_path=f"reports/{sub_id}.md",
            template=TemplateEnum.csrd,
        )
        session.add(report)
        sub.csr_report_id = report.id
        session.add(sub)
        session.commit()
        yield "event: done\ndata: complete\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/report/{sub_id}/download")
def download_report(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    report = session.exec(select(CsrReport).where(CsrReport.subscription_id == sub_id)).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not generated yet")
    report_path = Path(report.file_path)
    if not report_path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")
    return StreamingResponse(
        open(report_path, "rb"),
        media_type="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=csrd-report-{sub_id}.md"},
    )
```

- [ ] **Step 3: Register router in app.py**

```python
from src.backend.routers import report as report_router
app.include_router(report_router.router)
```

- [ ] **Step 4: Create report/_stream.html**

```html
<div id="report-section" class="mt-6">
  <div class="bg-gray-50 rounded-xl p-6 border border-gray-200">
    <h3 class="font-semibold mb-3 flex items-center gap-2">
      <span class="animate-spin text-green-600">⟳</span>
      Generating CSRD report...
    </h3>
    <div
      id="report-output"
      hx-ext="sse"
      sse-connect="/report/{{ sub_id }}/stream"
      sse-swap="message"
      hx-swap="beforeend"
      class="prose prose-sm max-w-none whitespace-pre-wrap text-gray-700 min-h-32"
    ></div>
  </div>
</div>

<script>
document.addEventListener('htmx:sseClose', function(e) {
  document.querySelector('.animate-spin')?.remove();
  document.getElementById('report-section').innerHTML += `
    <div class="mt-4">
      <a href="/report/{{ sub_id }}/download"
         class="bg-green-700 text-white px-6 py-2.5 rounded-xl hover:bg-green-800 font-medium">
        Download CSRD Report
      </a>
    </div>`;
});
</script>
```

- [ ] **Step 5: Fix CsrReport.frame_result_id to be nullable**

The CsrReport model has `frame_result_id: uuid.UUID` (non-nullable). Change to optional since streaming doesn't tie to a specific FrameResult row:

In `src/backend/models/marketplace.py`, update CsrReport:
```python
class CsrReport(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="fundsubscription.id")
    frame_result_id: uuid.UUID | None = Field(default=None, foreign_key="frameresult.id")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_path: str
    template: TemplateEnum = TemplateEnum.generic
```

- [ ] **Step 6: Set ANTHROPIC_API_KEY and verify manually**

```bash
export ANTHROPIC_API_KEY=your_key_here
uvicorn src.backend.app:app --reload
```

Navigate to `/dashboard/{sub_id}`, click "Generate CSRD Report", verify text streams in.

- [ ] **Step 7: Commit**

```bash
git add src/backend/services/report.py src/backend/routers/report.py src/frontend/templates/report/ src/backend/models/marketplace.py src/backend/app.py
git commit -m "feat: Claude SSE report generation — streaming CSRD report with FRAME methodology"
```

---

## Task 13: Admin routes

**Files:**
- Create: `src/backend/routers/admin.py`
- Create: `src/frontend/templates/admin/foodbanks.html`

- [ ] **Step 1: Create routers/admin.py**

```python
from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.foodbank import Foodbank
from src.backend.models.user import User
from src.backend.services.auth import require_admin

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent.parent / "frontend" / "templates"))


@router.get("/foodbanks", response_class=HTMLResponse)
def admin_foodbanks(
    request: Request,
    session: Session = Depends(get_session),
    user: User = Depends(require_admin),
):
    foodbanks = session.exec(select(Foodbank)).all()
    return templates.TemplateResponse("admin/foodbanks.html", {
        "request": request, "foodbanks": foodbanks, "user": user,
    })
```

- [ ] **Step 2: Register in app.py**

```python
from src.backend.routers import admin as admin_router
app.include_router(admin_router.router)
```

- [ ] **Step 3: Create admin/foodbanks.html**

```html
{% extends "base.html" %}
{% block title %}Admin — Food Banks{% endblock %}
{% block content %}
<h1 class="text-2xl font-bold mb-6">Food Banks</h1>
<table class="w-full text-sm bg-white rounded-xl border border-gray-200 overflow-hidden">
  <thead class="bg-gray-50 border-b">
    <tr>
      <th class="px-4 py-2 text-left font-medium">Name</th>
      <th class="px-4 py-2 text-left font-medium">City</th>
      <th class="px-4 py-2 text-left font-medium">Region</th>
      <th class="px-4 py-2 text-left font-medium">RDC</th>
    </tr>
  </thead>
  <tbody class="divide-y divide-gray-100">
    {% for fb in foodbanks %}
    <tr class="hover:bg-gray-50">
      <td class="px-4 py-2">{{ fb.name }}</td>
      <td class="px-4 py-2">{{ fb.city }}</td>
      <td class="px-4 py-2">{{ fb.region.value }}</td>
      <td class="px-4 py-2">{{ '✓' if fb.is_regional_dc else '' }}</td>
    </tr>
    {% endfor %}
  </tbody>
</table>
{% endblock %}
```

- [ ] **Step 4: Commit**

```bash
git add src/backend/routers/admin.py src/frontend/templates/admin/ src/backend/app.py
git commit -m "feat: admin foodbank list (admin role only)"
```

---

## Task 14: Run full test suite and smoke test

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: all pass

- [ ] **Step 2: Run seed script**

```bash
python -m src.backend.seed
```

- [ ] **Step 3: Start server and smoke test**

```bash
uvicorn src.backend.app:app --reload
```

Manual checks:
1. `GET /` → redirects or shows packages
2. `GET /packages` → shows 3 packages
3. Register new account → redirects to login
4. Login with `demo@acme.nl` / `demo1234` → redirects to packages
5. Click a package → detail page with fund button
6. Click fund → confirm page → click "Confirm & fund" → success page
7. Click "View impact dashboard" → shows allocation breakdown
8. Click "Generate CSRD Report" → text streams in live

- [ ] **Step 4: Final commit**

```bash
git add -A
git commit -m "feat: full Kavel MVP — marketplace, checkout, dashboard, Claude CSRD reports"
```
