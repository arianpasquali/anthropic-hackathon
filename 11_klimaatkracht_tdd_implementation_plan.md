# Klimaatkracht — Test-Driven Implementation Plan

This document is a complete implementation brief written for test-driven development. Another instance of Claude reading this should be able to start coding without further architectural input. The architecture relies on food bank operations data (annual reports, weekly distribution logs, operational expense records) ingested in batch — not real-time barcode scanning. Every component is specified by its test contract first, implementation second.

## Architecture summary

**The core engine.** On one side, food bank operations data flows in (intake totals by category, household counts served, operational costs, transport distances, refrigeration energy use). On the other side, corporate buyer commitments flow in with allocation preferences. The engine computes per-chapter impact, distributes commitments across chapters via the allocation engine, and produces attribution records linking buyer EUR to verifiable impact. Quarterly reports are generated from the attribution records, augmented by an LLM for narrative sections.

**External reference data.** CO2e coefficients (Poore & Nemecek 2018, WUR Dutch food-LCA), DEFRA transport emission factors, Klimaatmonitor grid intensity, ESRS disclosure mappings. Treated as version-controlled assets, not live integrations. Pulled at build time, cached, and committed to the repository.

**No real-time intake capture.** Food banks submit operational data periodically (initially monthly, later quarterly aligned with reporting cadence) via spreadsheet upload, CSV import, or direct API integration with their existing inventory systems. The platform never asks volunteers to do anything new at the loading dock.

## Repository structure

```
klimaatkracht/
├── README.md
├── docker-compose.yml             # Postgres only for local dev
├── .env.example
│
├── frontend/                      # Next.js 15 App Router
│   ├── app/
│   │   ├── (marketing)/
│   │   │   ├── page.tsx           # Landing
│   │   │   ├── how-it-works/
│   │   │   ├── methodology/       # Critical credibility page
│   │   │   ├── for-corporates/
│   │   │   └── for-foodbanks/
│   │   ├── (app)/
│   │   │   ├── fund/page.tsx      # Allocation preferences + commit
│   │   │   ├── portfolio/page.tsx # Buyer dashboard
│   │   │   ├── reports/page.tsx   # Report history
│   │   │   └── chapters/page.tsx  # Food bank operational-data upload
│   │   ├── api/
│   │   └── layout.tsx
│   ├── components/
│   │   ├── ui/                    # shadcn/ui primitives
│   │   ├── allocation/            # Sliders, weight visualizer
│   │   ├── charts/                # Recharts wrappers
│   │   ├── operations/            # Data upload, validation feedback
│   │   └── report/                # Report viewer
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── allocation-preview.ts  # JS mirror of backend engine
│   │   └── types.ts
│   └── public/
│
├── backend/                       # FastAPI
│   ├── app/
│   │   ├── main.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── auth.py            # Mocked for hackathon
│   │   ├── models/                # SQLAlchemy
│   │   ├── schemas/               # Pydantic
│   │   ├── routers/
│   │   │   ├── operations.py      # Food bank data ingestion
│   │   │   ├── chapters.py
│   │   │   ├── fund.py
│   │   │   ├── reports.py
│   │   │   └── methodology.py
│   │   ├── services/
│   │   │   ├── impact_calculator.py    # CORE
│   │   │   ├── allocation_engine.py    # CORE
│   │   │   ├── attribution.py          # CORE
│   │   │   ├── operations_ingestor.py  # CSV/spreadsheet parser
│   │   │   ├── report_generator.py     # LLM pipeline
│   │   │   └── external_data.py        # Coefficient lookups
│   │   ├── data/
│   │   │   ├── co2e_coefficients.json
│   │   │   ├── chapter_seed.json
│   │   │   └── esrs_mappings.json
│   │   └── prompts/
│   │       ├── generate_executive_summary.txt
│   │       ├── generate_narrative_section.txt
│   │       └── generate_esrs_section.txt
│   ├── alembic/
│   ├── tests/                     # See test specifications below
│   ├── pyproject.toml
│   └── Dockerfile
│
├── shared/
│   ├── coefficients/
│   ├── methodology/
│   └── demo-script.md
│
└── scripts/
    ├── seed_database.py
    ├── load_coefficients.py
    ├── load_chapter_seed.py
    └── pre_generate_reports.py
```

## Tech stack

**Frontend.** Next.js 15 App Router, Tailwind, shadcn/ui, Recharts. Vercel deployment with continuous deployment from main. Visual reference: carbonequity.com — clean white backgrounds, generous spacing, data-first layouts, sliders and toggles for preference setting.

**Backend.** FastAPI, SQLAlchemy 2.0, Alembic, Python 3.12. Railway deployment. Reasons over Node: pandas for aggregations, idiomatic Anthropic SDK, more readable numerical code.

**Database.** Supabase (Postgres + auth + storage). One service for three concerns cuts setup time materially.

**LLM.** Anthropic API. Claude Sonnet 4.7 for report generation. Claude Haiku 4.5 for high-frequency lookups (allocation preference parsing, anomaly checks).

**External data.** Static JSON assets in `backend/app/data/`, version-controlled, hand-curated:
- Poore & Nemecek 2018 coefficients
- WUR Dutch food-LCA adjustments
- DEFRA 2024 transport emission factors
- Klimaatmonitor 2025 Dutch grid intensity
- ESRS disclosure mappings

## Database schema

```sql
-- Chapters: the supply side
CREATE TABLE chapters (
    id VARCHAR(20) PRIMARY KEY,
    name TEXT NOT NULL,
    type VARCHAR(30) NOT NULL,
    households_served_per_week INTEGER NOT NULL,
    needs_score NUMERIC(3,2) NOT NULL,
    regional_bonus NUMERIC(3,2) NOT NULL DEFAULT 1.0,
    operational_footprint_kgco2e_per_tonne NUMERIC NOT NULL,
    cost_per_household_per_week_eur NUMERIC NOT NULL,
    location GEOGRAPHY(POINT),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Operations records: periodic data submissions from chapters
CREATE TABLE operations_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id VARCHAR(20) REFERENCES chapters(id),
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    submission_method VARCHAR(20) NOT NULL,  -- csv_upload | spreadsheet | api | manual
    total_kg NUMERIC NOT NULL,
    category_breakdown JSONB NOT NULL,       -- {category: kg}
    households_served INTEGER NOT NULL,
    distribution_count INTEGER,              -- number of distribution events
    transport_km NUMERIC,                    -- total volunteer driving km
    refrigeration_kwh NUMERIC,               -- electricity for cold storage
    operational_cost_eur NUMERIC,            -- direct ops cost
    raw_input_url TEXT,                      -- link to uploaded file in object storage
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (chapter_id, period_start, period_end)
);
CREATE INDEX idx_operations_chapter_period ON operations_records(chapter_id, period_start, period_end);

-- Coefficients: versioned reference table
CREATE TABLE co2e_coefficients (
    category VARCHAR(50) NOT NULL,
    coefficient_kgco2e_per_kg NUMERIC NOT NULL,
    source TEXT NOT NULL,
    version VARCHAR(20) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    PRIMARY KEY (category, version)
);

-- Buyers (corporates)
CREATE TABLE buyers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    industry VARCHAR(50),
    csr_framework VARCHAR(20) NOT NULL DEFAULT 'CSRD',
    contact_email TEXT NOT NULL,
    employees_count INTEGER,
    turnover_eur_m INTEGER,
    csrd_in_scope BOOLEAN GENERATED ALWAYS AS (
        employees_count >= 1000 AND turnover_eur_m >= 450
    ) STORED,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Funds: time-bounded pools
CREATE TABLE funds (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    methodology_version VARCHAR(20) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Commitments: a buyer's contribution with stated preferences
CREATE TABLE commitments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    buyer_id UUID REFERENCES buyers(id) NOT NULL,
    fund_id UUID REFERENCES funds(id) NOT NULL,
    amount_eur NUMERIC NOT NULL,
    allocation_preferences JSONB NOT NULL,
    rationale TEXT,
    committed_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active'
);

-- Allocations: how a commitment routes across chapters
CREATE TABLE allocations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commitment_id UUID REFERENCES commitments(id) NOT NULL,
    chapter_id VARCHAR(20) REFERENCES chapters(id) NOT NULL,
    weight NUMERIC NOT NULL,
    amount_eur NUMERIC NOT NULL,
    axis_weights JSONB NOT NULL,
    allocated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Attributions: connects buyer commitments to verified impact
CREATE TABLE attributions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commitment_id UUID REFERENCES commitments(id) NOT NULL,
    chapter_id VARCHAR(20) REFERENCES chapters(id) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    attribution_factor NUMERIC NOT NULL,
    attributed_food_kg NUMERIC NOT NULL,
    attributed_net_avoided_kgco2e NUMERIC NOT NULL,
    attributed_households_supported NUMERIC NOT NULL,
    chapter_total_food_kg NUMERIC NOT NULL,
    chapter_total_avoided_kgco2e NUMERIC NOT NULL,
    chapter_quarterly_op_cost_eur NUMERIC NOT NULL,
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Reports
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    commitment_id UUID REFERENCES commitments(id) NOT NULL,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    pdf_url TEXT,
    markdown_content TEXT,
    json_data JSONB NOT NULL,
    llm_model VARCHAR(50),
    llm_prompt_version VARCHAR(20),
    methodology_version VARCHAR(20),
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit log: append-only
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    actor_type VARCHAR(20) NOT NULL,
    actor_id TEXT,
    action_type VARCHAR(50) NOT NULL,
    target_table VARCHAR(50),
    target_id TEXT,
    details JSONB
);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
```

The schema is deliberately denormalized in the `attributions` table — values like `chapter_total_food_kg` are redundant with aggregations on `operations_records` but freezing them at calculation time means an auditor can verify a historical report without recomputing aggregations across an evolving operations table. This matters more than database elegance.

## Test-driven development workflow

Each component is specified by its test contract first. The implementation order follows the test pyramid: pure unit tests first (impact calculator), then service-level tests (allocation, attribution), then integration tests (operations ingestion, report generation), then end-to-end tests (full pipeline from operations data to report PDF).

For each section below: write the test, run it (should fail), implement until it passes, refactor. Do not move to the next test until the current one is green.

### Test layer 1: Impact calculator (`tests/test_impact_calculator.py`)

The simplest component, no database, fully testable. Pure functions over dictionaries.

```python
# tests/test_impact_calculator.py

import pytest
from app.services.impact_calculator import (
    calculate_avoided_emissions,
    calculate_operational_footprint,
    ImpactResult,
)


class TestImpactCalculator:
    """
    Test contract for impact_calculator.

    Inputs: category breakdown (kg by food category), CO2e coefficients,
    operational footprint per tonne.
    Output: ImpactResult with gross, operational, net, and per-category breakdown.
    """

    def test_empty_intake_yields_zero_impact(self):
        result = calculate_avoided_emissions(
            category_kg={},
            coefficients={"fresh_produce": 1.4},
            operational_footprint_per_tonne=38.0,
        )
        assert result.gross_avoided_kgco2e == 0
        assert result.operational_kgco2e == 0
        assert result.net_avoided_kgco2e == 0

    def test_single_category_calculation(self):
        """1000 kg fresh produce at 1.4 coefficient = 1400 kg gross avoided."""
        result = calculate_avoided_emissions(
            category_kg={"fresh_produce": 1000.0},
            coefficients={"fresh_produce": 1.4},
            operational_footprint_per_tonne=38.0,
        )
        assert result.gross_avoided_kgco2e == 1400.0
        # Operational: 1 tonne * 38 kg/tonne = 38 kg
        assert result.operational_kgco2e == 38.0
        assert result.net_avoided_kgco2e == 1362.0

    def test_multi_category_aggregation(self):
        """Verify per-category contribution is correctly summed."""
        result = calculate_avoided_emissions(
            category_kg={
                "fresh_produce": 500.0,    # 500 * 1.4 = 700
                "dairy": 200.0,             # 200 * 3.2 = 640
                "bread_bakery": 300.0,      # 300 * 1.1 = 330
            },
            coefficients={
                "fresh_produce": 1.4,
                "dairy": 3.2,
                "bread_bakery": 1.1,
            },
            operational_footprint_per_tonne=38.0,
        )
        assert result.gross_avoided_kgco2e == 1670.0  # 700+640+330
        # Operational: (500+200+300)/1000 * 38 = 38
        assert result.operational_kgco2e == 38.0
        assert result.net_avoided_kgco2e == 1632.0
        assert result.category_contributions == {
            "fresh_produce": 700.0,
            "dairy": 640.0,
            "bread_bakery": 330.0,
        }

    def test_unknown_category_raises_error(self):
        """Unknown category should raise rather than silently zero out."""
        with pytest.raises(KeyError, match="unknown_category"):
            calculate_avoided_emissions(
                category_kg={"unknown_category": 100.0},
                coefficients={"fresh_produce": 1.4},
                operational_footprint_per_tonne=38.0,
            )

    def test_negative_net_when_operational_exceeds_gross(self):
        """A chapter with poor efficiency should yield negative net (warning state)."""
        result = calculate_avoided_emissions(
            category_kg={"fresh_produce": 100.0},  # 100 * 1.4 = 140
            coefficients={"fresh_produce": 1.4},
            operational_footprint_per_tonne=2000.0,  # absurdly high
        )
        # Operational: 0.1 tonne * 2000 = 200
        assert result.gross_avoided_kgco2e == 140.0
        assert result.operational_kgco2e == 200.0
        assert result.net_avoided_kgco2e == -60.0

    def test_simulation_corp_x_attribution_total(self):
        """
        Regression test: against the simulation script's known output,
        Corporation X's EUR 100,000 should yield 561.7 tCO2e net avoided
        (within a 1% tolerance for floating-point).
        """
        # This test loads the full simulation seed and runs the
        # impact calculator across all five chapters' Q1 data,
        # then sums attribution-weighted impact.
        # Expected: 561.7 tCO2e (±1%)
        # Implementation reads from tests/fixtures/simulation_q1_2026.json
        from tests.fixtures import load_simulation_seed
        seed = load_simulation_seed("q1_2026")

        total_net_avoided = 0
        for chapter in seed["chapters"]:
            result = calculate_avoided_emissions(
                category_kg=chapter["category_breakdown"],
                coefficients=seed["coefficients"],
                operational_footprint_per_tonne=chapter["operational_footprint_per_tonne"],
            )
            total_net_avoided += result.net_avoided_kgco2e

        # Network total before attribution: ~1213.5 tCO2e
        assert abs(total_net_avoided / 1000 - 1213.5) / 1213.5 < 0.01
```

**Implementation file: `backend/app/services/impact_calculator.py`**

```python
from dataclasses import dataclass
from typing import Dict


@dataclass
class ImpactResult:
    gross_avoided_kgco2e: float
    operational_kgco2e: float
    net_avoided_kgco2e: float
    category_contributions: Dict[str, float]


def calculate_avoided_emissions(
    category_kg: Dict[str, float],
    coefficients: Dict[str, float],
    operational_footprint_per_tonne: float,
) -> ImpactResult:
    """Pure function. No I/O, no globals."""
    contributions = {
        cat: kg * coefficients[cat]  # KeyError if missing — desired behavior
        for cat, kg in category_kg.items()
    }
    gross = sum(contributions.values())
    total_kg = sum(category_kg.values())
    operational = (total_kg / 1000) * operational_footprint_per_tonne
    return ImpactResult(
        gross_avoided_kgco2e=gross,
        operational_kgco2e=operational,
        net_avoided_kgco2e=gross - operational,
        category_contributions=contributions,
    )


def calculate_operational_footprint(
    total_kg: float,
    transport_km: float,
    refrigeration_kwh: float,
    transport_factor: float = 0.27,    # kg CO2e/km, DEFRA 2024 light van
    grid_intensity: float = 0.27,      # kg CO2e/kWh, Klimaatmonitor 2025
) -> float:
    """Compute operational footprint from raw operational data when available."""
    return (transport_km * transport_factor) + (refrigeration_kwh * grid_intensity)
```

The regression test against the simulation output is the single most important test in the codebase. It catches drift between the documented numbers (which appear in the pitch, the sample report, and the methodology page) and the actual implementation. If this test fails, the demo numbers are wrong, and credibility collapses.

### Test layer 2: Allocation engine (`tests/test_allocation_engine.py`)

```python
# tests/test_allocation_engine.py

import pytest
from app.services.allocation_engine import (
    compute_allocation,
    AllocationPreferences,
    ChapterSnapshot,
)


class TestAllocationEngine:
    """
    Test contract: given chapters with computed impact metrics and a buyer's
    preferences, return EUR allocation per chapter such that:
    - Sum of allocations equals the input EUR amount
    - Each chapter's weight reflects the blended preference axes
    - Per-axis weights are returned for transparency
    """

    @pytest.fixture
    def five_chapters(self):
        """The simulation's five chapters."""
        return [
            ChapterSnapshot(
                id="VB-AMS-OOST",
                net_avoided_tco2e=274.0,
                households_served_quarter=4940,
                needs_score=0.78,
                regional_bonus=1.0,
                total_tonnes=162.5,
            ),
            ChapterSnapshot(
                id="VB-RDM-ZUID",
                net_avoided_tco2e=247.0,
                households_served_quarter=5460,
                needs_score=0.92,
                regional_bonus=1.0,
                total_tonnes=145.6,
            ),
            ChapterSnapshot(
                id="VB-LEI-CTR",
                net_avoided_tco2e=174.5,
                households_served_quarter=3120,
                needs_score=0.61,
                regional_bonus=1.0,
                total_tonnes=101.4,
            ),
            ChapterSnapshot(
                id="VB-FRL-NRD",
                net_avoided_tco2e=64.8,
                households_served_quarter=1235,
                needs_score=0.71,
                regional_bonus=1.15,
                total_tonnes=44.2,
            ),
            ChapterSnapshot(
                id="VB-EHV-CTR",
                net_avoided_tco2e=199.2,
                households_served_quarter=3705,
                needs_score=0.68,
                regional_bonus=1.0,
                total_tonnes=118.3,
            ),
        ]

    def test_allocation_sums_to_amount(self, five_chapters):
        """Total allocated EUR must equal commitment amount within EUR 1."""
        prefs = AllocationPreferences(
            max_climate_impact=0.4,
            max_social_need=0.4,
            balanced_distribution=0.2,
        )
        result = compute_allocation(five_chapters, prefs, 100_000)
        total = sum(r.amount_eur for r in result.values())
        assert abs(total - 100_000) < 1.0

    def test_blended_allocation_matches_simulation(self, five_chapters):
        """
        Regression test: with blended 40/40/20 preferences and EUR 100k,
        Rotterdam-Zuid should receive ~EUR 29,106 (within EUR 100 tolerance).
        """
        prefs = AllocationPreferences(
            max_climate_impact=0.4,
            max_social_need=0.4,
            balanced_distribution=0.2,
        )
        result = compute_allocation(five_chapters, prefs, 100_000)
        assert abs(result["VB-RDM-ZUID"].amount_eur - 29_106) < 100
        assert abs(result["VB-FRL-NRD"].amount_eur - 7_496) < 100

    def test_climate_only_reduces_rural_allocation(self, five_chapters):
        """100% climate preference should drop Friesland to under 4% (lower than blended)."""
        prefs = AllocationPreferences(
            max_climate_impact=1.0,
            max_social_need=0.0,
            balanced_distribution=0.0,
        )
        result = compute_allocation(five_chapters, prefs, 100_000)
        assert result["VB-FRL-NRD"].weight < 0.04

    def test_social_only_includes_regional_bonus(self, five_chapters):
        """100% social preference should boost Friesland via 1.15x regional multiplier."""
        prefs = AllocationPreferences(
            max_climate_impact=0.0,
            max_social_need=1.0,
            balanced_distribution=0.0,
        )
        result = compute_allocation(five_chapters, prefs, 100_000)
        # Compute Friesland's share without bonus would be lower
        # With bonus, it should rise — at least higher than pure climate
        prefs_climate = AllocationPreferences(1.0, 0.0, 0.0)
        result_climate = compute_allocation(five_chapters, prefs_climate, 100_000)
        assert result["VB-FRL-NRD"].weight > result_climate["VB-FRL-NRD"].weight

    def test_axis_weights_are_returned(self, five_chapters):
        """Each chapter result should include per-axis weights for transparency."""
        prefs = AllocationPreferences(0.4, 0.4, 0.2)
        result = compute_allocation(five_chapters, prefs, 100_000)
        for r in result.values():
            assert "climate" in r.axis_weights
            assert "social" in r.axis_weights
            assert "balanced" in r.axis_weights

    def test_preferences_must_sum_to_one(self):
        """Invalid preferences should raise."""
        with pytest.raises(ValueError, match="must sum to 1"):
            AllocationPreferences(
                max_climate_impact=0.5,
                max_social_need=0.4,
                balanced_distribution=0.4,  # Sum = 1.3
            )
```

**Implementation file: `backend/app/services/allocation_engine.py`**

```python
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AllocationPreferences:
    max_climate_impact: float
    max_social_need: float
    balanced_distribution: float

    def __post_init__(self):
        total = self.max_climate_impact + self.max_social_need + self.balanced_distribution
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Preferences must sum to 1.0, got {total}")


@dataclass
class ChapterSnapshot:
    id: str
    net_avoided_tco2e: float
    households_served_quarter: float
    needs_score: float
    regional_bonus: float
    total_tonnes: float


@dataclass
class AllocationResult:
    chapter_id: str
    weight: float
    amount_eur: float
    axis_weights: Dict[str, float]


def normalize(d: Dict[str, float]) -> Dict[str, float]:
    total = sum(d.values())
    return {k: v / total for k, v in d.items()} if total > 0 else d


def compute_allocation(
    chapters: List[ChapterSnapshot],
    preferences: AllocationPreferences,
    amount_eur: float,
) -> Dict[str, AllocationResult]:
    climate_w = normalize({c.id: c.net_avoided_tco2e for c in chapters})
    social_w = normalize({
        c.id: c.households_served_quarter * c.needs_score * c.regional_bonus
        for c in chapters
    })
    balanced_w = normalize({c.id: c.total_tonnes for c in chapters})

    blended = {
        c.id: (
            climate_w[c.id]  * preferences.max_climate_impact +
            social_w[c.id]   * preferences.max_social_need +
            balanced_w[c.id] * preferences.balanced_distribution
        )
        for c in chapters
    }
    blended = normalize(blended)

    return {
        c.id: AllocationResult(
            chapter_id=c.id,
            weight=blended[c.id],
            amount_eur=amount_eur * blended[c.id],
            axis_weights={
                "climate": climate_w[c.id],
                "social": social_w[c.id],
                "balanced": balanced_w[c.id],
            },
        )
        for c in chapters
    }
```

### Test layer 3: Attribution service (`tests/test_attribution.py`)

The most subtle component. The critical invariant — across all attributions for a chapter in a period, attribution factors must sum to ≤ 1.0 — is the strongest defense against double-counting.

```python
# tests/test_attribution.py

import pytest
from datetime import date
from app.services.attribution import (
    compute_attribution,
    Attribution,
    DateRange,
)


class TestAttribution:
    """
    Test contract: given a commitment, a chapter, and a reporting period,
    compute the attribution factor and apply it to the chapter's actual impact.

    Critical invariant: sum of attribution factors across all commitments
    for a single chapter in a period must be <= 1.0 (no double-counting).
    """

    @pytest.fixture
    def q1_period(self):
        return DateRange(start=date(2026, 1, 6), end=date(2026, 3, 30))

    def test_partial_funding_attribution_factor(self, q1_period):
        """
        Chapter quarterly cost: 420 households/wk * EUR 10.80 * 13 weeks = EUR 58,968
        Allocation: EUR 29,106
        Expected factor: 29,106 / 58,968 = 0.4936
        """
        attr = compute_attribution(
            commitment_id="commit-uuid-1",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=29_106,
            chapter_quarterly_cost_eur=58_968,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        assert abs(attr.attribution_factor - 0.4936) < 0.001
        assert abs(attr.attributed_food_kg - 71_867) < 100
        assert abs(attr.attributed_net_avoided_kgco2e - 121_899) < 200

    def test_attribution_factor_capped_at_one(self, q1_period):
        """No funder may claim more than 100% of a chapter's impact."""
        attr = compute_attribution(
            commitment_id="commit-uuid-1",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=200_000,           # 2x the chapter's cost
            chapter_quarterly_cost_eur=58_968,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        assert attr.attribution_factor == 1.0

    def test_no_double_counting_invariant(self, q1_period):
        """
        Multiple buyers funding the same chapter: their attribution factors
        must sum to no more than 1.0.
        """
        chapter_cost = 58_968
        buyer_a_alloc = 25_000
        buyer_b_alloc = 30_000
        # Combined: 55,000 / 58,968 = 0.933 — under 1.0, valid
        attr_a = compute_attribution(
            commitment_id="commit-a",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=buyer_a_alloc,
            chapter_quarterly_cost_eur=chapter_cost,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        attr_b = compute_attribution(
            commitment_id="commit-b",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=buyer_b_alloc,
            chapter_quarterly_cost_eur=chapter_cost,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        assert (attr_a.attribution_factor + attr_b.attribution_factor) <= 1.0

    def test_overcommitted_chapter_warning(self, q1_period):
        """
        When sum of allocations > chapter cost, the system must surface
        a warning (allocations remain valid but excess must be reallocated).
        """
        from app.services.attribution import check_chapter_overcommitment

        result = check_chapter_overcommitment(
            chapter_id="VB-RDM-ZUID",
            chapter_quarterly_cost_eur=58_968,
            allocations=[
                ("commit-a", 30_000),
                ("commit-b", 35_000),  # Total 65k > 58.9k
            ],
        )
        assert result.is_overcommitted
        assert result.excess_eur == pytest.approx(6_032, abs=10)

    def test_corp_x_full_quarter_attribution(self, q1_period):
        """
        Regression test: Corporation X's full attribution across 5 chapters
        should yield 561.7 tCO2e net avoided (within 1% tolerance).
        """
        from tests.fixtures import load_simulation_seed
        seed = load_simulation_seed("q1_2026")

        total_attributed = 0
        for chapter_data in seed["chapters"]:
            allocation = seed["corp_x_allocations"][chapter_data["id"]]
            attr = compute_attribution(
                commitment_id="corp-x-commit",
                chapter_id=chapter_data["id"],
                allocation_eur=allocation,
                chapter_quarterly_cost_eur=chapter_data["quarterly_cost_eur"],
                chapter_total_food_kg=chapter_data["total_food_kg"],
                chapter_net_avoided_kgco2e=chapter_data["net_avoided_kgco2e"],
                chapter_households_served_quarter=chapter_data["households_quarter"],
                period=q1_period,
            )
            total_attributed += attr.attributed_net_avoided_kgco2e

        assert abs(total_attributed / 1000 - 561.7) / 561.7 < 0.01
```

**Implementation file: `backend/app/services/attribution.py`**

```python
from dataclasses import dataclass
from datetime import date
from typing import List, Tuple


@dataclass
class DateRange:
    start: date
    end: date

    def weeks_count(self) -> int:
        return (self.end - self.start).days // 7 + 1


@dataclass
class Attribution:
    commitment_id: str
    chapter_id: str
    attribution_factor: float
    attributed_food_kg: float
    attributed_net_avoided_kgco2e: float
    attributed_households_supported: float
    chapter_total_food_kg: float
    chapter_total_avoided_kgco2e: float
    chapter_quarterly_op_cost_eur: float


@dataclass
class OvercommitmentResult:
    is_overcommitted: bool
    total_allocated_eur: float
    chapter_quarterly_cost_eur: float
    excess_eur: float


def compute_attribution(
    commitment_id: str,
    chapter_id: str,
    allocation_eur: float,
    chapter_quarterly_cost_eur: float,
    chapter_total_food_kg: float,
    chapter_net_avoided_kgco2e: float,
    chapter_households_served_quarter: float,
    period: DateRange,
) -> Attribution:
    factor = min(allocation_eur / chapter_quarterly_cost_eur, 1.0)
    return Attribution(
        commitment_id=commitment_id,
        chapter_id=chapter_id,
        attribution_factor=factor,
        attributed_food_kg=chapter_total_food_kg * factor,
        attributed_net_avoided_kgco2e=chapter_net_avoided_kgco2e * factor,
        attributed_households_supported=chapter_households_served_quarter * factor,
        chapter_total_food_kg=chapter_total_food_kg,
        chapter_total_avoided_kgco2e=chapter_net_avoided_kgco2e,
        chapter_quarterly_op_cost_eur=chapter_quarterly_cost_eur,
    )


def check_chapter_overcommitment(
    chapter_id: str,
    chapter_quarterly_cost_eur: float,
    allocations: List[Tuple[str, float]],
) -> OvercommitmentResult:
    total_allocated = sum(amount for _, amount in allocations)
    excess = max(total_allocated - chapter_quarterly_cost_eur, 0)
    return OvercommitmentResult(
        is_overcommitted=excess > 0,
        total_allocated_eur=total_allocated,
        chapter_quarterly_cost_eur=chapter_quarterly_cost_eur,
        excess_eur=excess,
    )
```

### Test layer 4: Operations data ingestion (`tests/test_operations_ingestor.py`)

This replaces the volunteer PWA. Food banks submit periodic operational data via CSV upload, spreadsheet, or direct manual entry. The ingestor parses, validates, and persists.

```python
# tests/test_operations_ingestor.py

import pytest
from io import StringIO
from datetime import date
from app.services.operations_ingestor import (
    parse_operations_csv,
    validate_operations_record,
    OperationsRecord,
    ValidationError,
)


class TestOperationsIngestor:
    """
    Test contract: parse operational data submissions from food banks.
    Accept CSV with category-level kg breakdown plus operational metadata.
    Validate against business rules, surface errors clearly.
    """

    def test_parse_well_formed_csv(self):
        csv_content = """chapter_id,period_start,period_end,fresh_produce_kg,bread_bakery_kg,dairy_kg,meat_processed_kg,ready_meals_kg,dry_goods_kg,canned_kg,frozen_kg,households_served,distribution_count,transport_km,refrigeration_kwh,operational_cost_eur
VB-AMS-OOST,2026-01-06,2026-03-30,52000,29250,22750,9750,6500,26000,11375,4875,4940,65,2400,3850,58270"""
        records = parse_operations_csv(StringIO(csv_content))
        assert len(records) == 1
        r = records[0]
        assert r.chapter_id == "VB-AMS-OOST"
        assert r.period_start == date(2026, 1, 6)
        assert r.category_breakdown["fresh_produce"] == 52000
        assert r.households_served == 4940
        assert r.transport_km == 2400

    def test_parse_rejects_negative_kg(self):
        csv_content = """chapter_id,period_start,period_end,fresh_produce_kg,bread_bakery_kg,dairy_kg,meat_processed_kg,ready_meals_kg,dry_goods_kg,canned_kg,frozen_kg,households_served,distribution_count,transport_km,refrigeration_kwh,operational_cost_eur
VB-AMS-OOST,2026-01-06,2026-03-30,-5000,29250,22750,9750,6500,26000,11375,4875,4940,65,2400,3850,58270"""
        with pytest.raises(ValidationError, match="negative"):
            parse_operations_csv(StringIO(csv_content))

    def test_parse_rejects_unknown_chapter(self):
        csv_content = """chapter_id,period_start,period_end,fresh_produce_kg,bread_bakery_kg,dairy_kg,meat_processed_kg,ready_meals_kg,dry_goods_kg,canned_kg,frozen_kg,households_served,distribution_count,transport_km,refrigeration_kwh,operational_cost_eur
VB-FAKE-CHAPTER,2026-01-06,2026-03-30,1000,1000,1000,1000,1000,1000,1000,1000,100,10,100,100,1000"""
        with pytest.raises(ValidationError, match="unknown chapter"):
            parse_operations_csv(StringIO(csv_content))

    def test_parse_rejects_overlapping_periods(self):
        """A chapter cannot submit two records with overlapping periods."""
        existing_record = OperationsRecord(
            chapter_id="VB-AMS-OOST",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 3, 31),
            category_breakdown={"fresh_produce": 1000.0},
            households_served=100,
        )
        new_record = OperationsRecord(
            chapter_id="VB-AMS-OOST",
            period_start=date(2026, 2, 1),  # Overlaps existing period
            period_end=date(2026, 4, 30),
            category_breakdown={"fresh_produce": 500.0},
            households_served=50,
        )
        with pytest.raises(ValidationError, match="overlapping period"):
            validate_operations_record(new_record, existing=[existing_record])

    def test_parse_handles_empty_categories(self):
        """A chapter that doesn't receive a category in this period should default to 0."""
        csv_content = """chapter_id,period_start,period_end,fresh_produce_kg,bread_bakery_kg,dairy_kg,meat_processed_kg,ready_meals_kg,dry_goods_kg,canned_kg,frozen_kg,households_served,distribution_count,transport_km,refrigeration_kwh,operational_cost_eur
VB-AMS-OOST,2026-01-06,2026-03-30,52000,29250,22750,0,0,26000,11375,0,4940,65,2400,3850,58270"""
        records = parse_operations_csv(StringIO(csv_content))
        assert records[0].category_breakdown["meat_processed"] == 0
        assert records[0].category_breakdown["frozen"] == 0

    def test_excel_upload_supported(self):
        """Excel files (.xlsx) are accepted as alternative to CSV."""
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append([
            "chapter_id", "period_start", "period_end",
            "fresh_produce_kg", "bread_bakery_kg", "dairy_kg",
            "meat_processed_kg", "ready_meals_kg", "dry_goods_kg",
            "canned_kg", "frozen_kg", "households_served",
            "distribution_count", "transport_km", "refrigeration_kwh",
            "operational_cost_eur",
        ])
        ws.append([
            "VB-AMS-OOST", "2026-01-06", "2026-03-30",
            52000, 29250, 22750, 9750, 6500, 26000, 11375, 4875,
            4940, 65, 2400, 3850, 58270,
        ])

        from io import BytesIO
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        from app.services.operations_ingestor import parse_operations_xlsx
        records = parse_operations_xlsx(buf)
        assert len(records) == 1
        assert records[0].chapter_id == "VB-AMS-OOST"
```

**Implementation file: `backend/app/services/operations_ingestor.py`**

The parser must produce strict, auditable records. Validation errors should be specific enough that a chapter coordinator (not a developer) can correct them. Implementation hints:

- Use `csv.DictReader` for CSV. Use `openpyxl` for xlsx.
- Validate categories against the canonical eight (fresh_produce, bread_bakery, dairy, meat_processed, ready_meals, dry_goods, canned, frozen).
- Validate chapter_id against the chapters table at parse time.
- For overlap detection, query existing operations_records for the chapter and check date ranges.
- Raise ValidationError with specific row/column information for UI display.

The chapter coordinator's experience: they upload a spreadsheet, the system parses it and either accepts everything or shows specific errors with row numbers and corrective suggestions ("Row 3: chapter_id 'VB-AMSTER' not found, did you mean 'VB-AMS-OOST'?"). LLM-assisted error correction (Haiku 4.5) is a nice-to-have, not required.

### Test layer 5: Report generator (`tests/test_report_generator.py`)

This is where the LLM enters the pipeline. Tests must isolate the LLM-dependent parts to keep test runs fast and deterministic.

```python
# tests/test_report_generator.py

import pytest
from datetime import date
from app.services.report_generator import (
    assemble_report_data,
    generate_section,
    render_methodology_section,
    render_audit_appendix,
    ReportData,
)


class TestReportDataAssembly:
    """
    The non-LLM parts of report generation must be deterministic and
    fully testable. LLM calls are tested separately with mocking.
    """

    def test_assemble_report_data_for_corp_x(self):
        """End-to-end: load Corp X commitment, produce structured ReportData."""
        from tests.fixtures import setup_test_database, load_simulation_seed

        with setup_test_database() as db:
            commitment_id = load_simulation_seed("q1_2026", db=db)
            data = assemble_report_data(
                commitment_id=commitment_id,
                period_start=date(2026, 1, 6),
                period_end=date(2026, 3, 30),
                db=db,
            )

            assert data.buyer.name == "Corporation X"
            assert data.totals.total_food_rescued_kg == pytest.approx(268_419, abs=500)
            assert data.totals.total_net_avoided_tco2e == pytest.approx(561.7, abs=5)
            assert data.totals.total_households_supported == pytest.approx(8_598, abs=20)
            assert len(data.attributions) == 5

    def test_methodology_section_is_deterministic(self):
        """The methodology section is templated, not LLM-generated. Same input => same output."""
        section_a = render_methodology_section("KKM-2026.1")
        section_b = render_methodology_section("KKM-2026.1")
        assert section_a == section_b
        assert "Poore & Nemecek 2018" in section_a
        assert "EPA WARM v15" in section_a

    def test_audit_appendix_lists_all_records(self):
        """Audit appendix index must reference all operations records in period."""
        from tests.fixtures import setup_test_database, load_simulation_seed
        with setup_test_database() as db:
            commitment_id = load_simulation_seed("q1_2026", db=db)
            appendix = render_audit_appendix(
                commitment_id=commitment_id,
                period_start=date(2026, 1, 6),
                period_end=date(2026, 3, 30),
                db=db,
            )
            # Five chapters in the simulation; appendix should reference all
            assert "VB-AMS-OOST" in appendix
            assert "VB-RDM-ZUID" in appendix
            assert "VB-LEI-CTR" in appendix
            assert "VB-FRL-NRD" in appendix
            assert "VB-EHV-CTR" in appendix


class TestReportSectionGeneration:
    """LLM-dependent section generation. Mocked in unit tests."""

    @pytest.fixture
    def mock_anthropic_client(self, monkeypatch):
        """Mock Anthropic API responses for deterministic tests."""
        class MockClient:
            async def messages_create(self, **kwargs):
                from types import SimpleNamespace
                return SimpleNamespace(content=[
                    SimpleNamespace(text="Mock-generated section text.")
                ])
        client = MockClient()
        monkeypatch.setattr("app.services.report_generator._anthropic_client", client)
        return client

    @pytest.mark.asyncio
    async def test_section_generation_passes_data_to_prompt(self, mock_anthropic_client):
        """Verify the structured data is included in the prompt."""
        # The implementation should pass numeric data into the LLM prompt
        # so all claims in generated text are grounded.
        # Use a recording mock to inspect the prompt.
        # ... implementation
        pass

    @pytest.mark.asyncio
    async def test_no_hallucinated_numbers_in_output(self, mock_anthropic_client):
        """
        Generated sections must reference only numbers from the structured input.
        Implementation: parse numbers from the LLM output, verify each one
        appears in the input data.
        """
        # ... implementation
        pass
```

**Implementation notes for `backend/app/services/report_generator.py`:**

The non-LLM parts of report generation (data assembly, methodology section, audit appendix, ESRS table) must be pure functions over the database. Tests for these run fast and deterministically. The LLM-dependent parts (executive summary narrative, allocation explanation prose, narrative impact section) are isolated behind interfaces that can be mocked.

The final report PDF generation uses Puppeteer (called from Python via `pyppeteer`) to render a styled HTML template. The HTML template is checked into the repository under `backend/app/templates/report.html` and uses Jinja2 for variable substitution.

**Pre-generation strategy.** Before any demo, run `scripts/pre_generate_reports.py` to produce a complete cached report for the demo buyer. The cached report sits in Supabase Storage. The "Generate Q1 Report" button in the buyer dashboard checks for a cached report first and serves it if present. If the LLM hangs or rate-limits during the live demo, the cached version is served. Non-optional for stage demo reliability.

### Test layer 6: End-to-end pipeline (`tests/test_pipeline_e2e.py`)

```python
# tests/test_pipeline_e2e.py

import pytest
from datetime import date
from app.services.pipeline import run_full_pipeline


class TestEndToEndPipeline:
    """
    Test the full data flow:
    1. Operations data ingested for 5 chapters
    2. Buyer commits with allocation preferences
    3. Allocation engine routes commitment
    4. Attribution computed against actual operations data
    5. Report generated with verified numbers
    """

    @pytest.mark.asyncio
    async def test_full_pipeline_corp_x(self):
        """The canonical end-to-end test against the simulation reference."""
        from tests.fixtures import setup_test_database, load_simulation_csv

        with setup_test_database() as db:
            # Step 1: ingest operations data for Q1 2026
            for chapter_id in ["VB-AMS-OOST", "VB-RDM-ZUID", "VB-LEI-CTR",
                               "VB-FRL-NRD", "VB-EHV-CTR"]:
                load_simulation_csv(chapter_id, "q1_2026", db=db)

            # Step 2: create Corporation X with commitment
            buyer = await create_buyer(
                name="Corporation X",
                industry="Financial Services",
                employees=1200,
                turnover_eur_m=540,
                db=db,
            )
            commitment = await create_commitment(
                buyer_id=buyer.id,
                amount_eur=100_000,
                preferences={
                    "max_climate_impact": 0.4,
                    "max_social_need": 0.4,
                    "balanced_distribution": 0.2,
                },
                rationale="Blended preference for dual climate and social impact.",
                db=db,
            )

            # Step 3: run pipeline
            result = await run_full_pipeline(
                commitment_id=commitment.id,
                period_start=date(2026, 1, 6),
                period_end=date(2026, 3, 30),
                db=db,
            )

            # Step 4: verify
            assert abs(result.total_food_rescued_kg - 268_419) / 268_419 < 0.01
            assert abs(result.total_net_avoided_kgco2e - 561_670) / 561_670 < 0.01
            assert abs(result.total_households_supported - 8_598) / 8_598 < 0.01

            # Step 5: verify report exists with correct content
            report = await get_report(commitment.id, db=db)
            assert report is not None
            assert "268.4 tonnes" in report.markdown_content
            assert "561.7" in report.markdown_content or "562" in report.markdown_content
            assert report.methodology_version == "KKM-2026.1"
```

The end-to-end test is the canonical assurance. If it passes, the whole pipeline produces the documented numbers. If it fails, the demo numbers are wrong. Run it before every commit to main.

## Frontend implementation order

The frontend follows the test pyramid less strictly because UI testing is more brittle. Component tests cover the critical interactive surfaces; visual regression is done manually.

**Allocation slider component (`frontend/components/allocation/AllocationSliders.tsx`).** This is the most important interactive component. The JS allocation-preview library (`frontend/lib/allocation-preview.ts`) must produce numerically identical results to the Python `allocation_engine.py`. A regression test suite (`frontend/tests/allocation-preview.test.ts`) loads the same fixture data and asserts the JS computation matches the Python.

**Chapter operations upload page (`frontend/app/(app)/chapters/page.tsx`).** Drag-and-drop CSV/xlsx upload, server-side parse, error display with row/column references. Test with the simulation fixtures.

**Buyer fund page (`frontend/app/(app)/fund/page.tsx`).** Sliders bound to the allocation preview library. Live chart updates as sliders move. Commit button triggers backend API call.

**Buyer portfolio dashboard (`frontend/app/(app)/portfolio/page.tsx`).** Shows commitment status, real-time impact based on attribution data, report download. Updates poll the backend every 30 seconds for fresh attribution data.

**Methodology page (`frontend/app/(marketing)/methodology/page.tsx`).** Long-form, citation-heavy. Half a person-day to write properly. Markdown source in `frontend/content/methodology.md`, rendered through Next.js MDX support.

## Critical correctness invariants

A handful of properties must hold across the system. Each has a corresponding test that runs in CI and fails the build if violated.

**Invariant 1: Sum of attribution factors per chapter ≤ 1.0.** No double-counting across buyers. Implemented as a database-level check trigger and a service-level assertion. Test: `test_no_double_counting_invariant`.

**Invariant 2: Sum of allocations equals commitment amount within EUR 1.** No funds lost or gained in routing. Test: `test_allocation_sums_to_amount`.

**Invariant 3: Methodology version is monotonic.** Once a version is published and used in a report, it cannot be silently changed. New versions get new identifiers. Test: schema-level uniqueness on (category, version).

**Invariant 4: Report regeneration produces the same numbers.** Given the same operations data, the same commitment, and the same methodology version, two report-generation runs produce numerically identical impact figures (the LLM-generated narrative may differ). Test: `test_report_regeneration_idempotent`.

**Invariant 5: Frontend allocation preview matches backend.** Same input data, same preferences, same numerical output. Test: cross-language fixture-based regression.

These five invariants are the spine of the system's credibility. If any of them fails in production, the audit defense collapses.

## What I'd want feedback on before starting implementation

Three points where reasonable disagreement is possible:

**Submission cadence.** I've assumed quarterly reporting periods aligned with corporate financial reporting, with operations data ingested monthly inside each quarter. Some food banks may report less frequently (annual only). The schema accommodates this but the demo flow assumes quarterly. Worth confirming with at least one real chapter before fixing.

**Operational footprint computation.** The implementation supports two paths: (a) chapter provides direct transport_km and refrigeration_kwh, computed via emission factors; (b) chapter provides only total_kg, footprint estimated via per-tonne baseline from chapter type. Path (a) is more accurate; path (b) reduces friction for chapters with weak data. The fallback logic needs explicit precedence rules in the implementation.

**Report PDF generation.** I've recommended Puppeteer via pyppeteer. ReportLab is a pure-Python alternative that's more reliable but produces less beautiful output. For a hackathon demo, the beautiful output matters more. For production, the reliability matters more. Worth picking deliberately.
