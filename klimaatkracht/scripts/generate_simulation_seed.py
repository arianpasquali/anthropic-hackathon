"""Generate a self-consistent simulation seed for the regression tests.

This is the single source of numerical truth for the demo. The script reads
the canonical chapter snapshot and Corporation X commitment, runs the impact
calculator and allocation engine to derive expected aggregates, then writes
tests/fixtures/simulation_q1_2026.json.

The chapter category breakdowns are crafted so each chapter's net avoided
emissions match the allocation-engine snapshot values (274, 247, 174.5, 64.8,
199.2 tCO2e). The seed is regenerated whenever the canonical inputs change.

Run:
    python scripts/generate_simulation_seed.py

The script is idempotent — running it twice produces byte-identical JSON.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.allocation_engine import (  # noqa: E402
    AllocationPreferences,
    ChapterSnapshot,
    compute_allocation,
)
from app.services.impact_calculator import calculate_avoided_emissions  # noqa: E402

OUTPUT_PATH = BACKEND_ROOT / "tests" / "fixtures" / "simulation_q1_2026.json"

# Poore & Nemecek 2018 + WUR Dutch food-LCA aligned (illustrative, hackathon-grade).
COEFFICIENTS: dict[str, float] = {
    "fresh_produce": 1.4,
    "bread_bakery": 1.1,
    "dairy": 3.2,
    "meat_processed": 6.0,
    "ready_meals": 2.5,
    "dry_goods": 1.0,
    "canned": 1.5,
    "frozen": 2.0,
}

OPERATIONAL_FOOTPRINT_PER_TONNE = 38.0  # kg CO2e/tonne baseline
COST_PER_HOUSEHOLD_PER_WEEK_EUR = 10.80
WEEKS_IN_QUARTER = 13

# Canonical 5-chapter snapshot. Values match the allocation-engine test fixture.
CHAPTERS_META: list[dict] = [
    {
        "id": "VB-AMS-OOST",
        "name": "Voedselbank Amsterdam-Oost",
        "households_quarter": 4940,
        "needs_score": 0.78,
        "regional_bonus": 1.0,
        "total_tonnes": 162.5,
        "target_net_avoided_tco2e": 274.0,
    },
    {
        "id": "VB-RDM-ZUID",
        "name": "Voedselbank Rotterdam-Zuid",
        "households_quarter": 5460,
        "needs_score": 0.92,
        "regional_bonus": 1.0,
        "total_tonnes": 145.6,
        "target_net_avoided_tco2e": 247.0,
    },
    {
        "id": "VB-LEI-CTR",
        "name": "Voedselbank Leiden Centrum",
        "households_quarter": 3120,
        "needs_score": 0.61,
        "regional_bonus": 1.0,
        "total_tonnes": 101.4,
        "target_net_avoided_tco2e": 174.5,
    },
    {
        "id": "VB-FRL-NRD",
        "name": "Voedselbank Friesland-Noord",
        "households_quarter": 1235,
        "needs_score": 0.71,
        "regional_bonus": 1.15,
        "total_tonnes": 44.2,
        "target_net_avoided_tco2e": 64.8,
    },
    {
        "id": "VB-EHV-CTR",
        "name": "Voedselbank Eindhoven Centrum",
        "households_quarter": 3705,
        "needs_score": 0.68,
        "regional_bonus": 1.0,
        "total_tonnes": 118.3,
        "target_net_avoided_tco2e": 199.2,
    },
]

# Realistic share by category for a Dutch food bank (sums to 1.0).
CATEGORY_SHARES: dict[str, float] = {
    "fresh_produce": 0.36,
    "bread_bakery": 0.22,
    "dairy": 0.10,
    "meat_processed": 0.04,
    "ready_meals": 0.04,
    "dry_goods": 0.17,
    "canned": 0.05,
    "frozen": 0.02,
}

CORP_X_COMMITMENT_EUR = 100_000
CORP_X_PREFERENCES = AllocationPreferences(
    max_climate_impact=0.4,
    max_social_need=0.4,
    balanced_distribution=0.2,
)


def _category_breakdown_for_chapter(chapter: dict) -> dict[str, float]:
    """Scale category shares to hit the chapter's target net avoided.

    Approach: start from the realistic share mix, compute the net avoided that
    would yield, then scale all categories uniformly so the chapter hits its
    target. Uniform scaling preserves the realistic mix.
    """
    total_kg = chapter["total_tonnes"] * 1000
    base_breakdown = {cat: share * total_kg for cat, share in CATEGORY_SHARES.items()}
    base_result = calculate_avoided_emissions(
        category_kg=base_breakdown,
        coefficients=COEFFICIENTS,
        operational_footprint_per_tonne=OPERATIONAL_FOOTPRINT_PER_TONNE,
    )
    target_net_kgco2e = chapter["target_net_avoided_tco2e"] * 1000
    op_kgco2e = base_result.operational_kgco2e
    target_gross_kgco2e = target_net_kgco2e + op_kgco2e

    if base_result.gross_avoided_kgco2e == 0:
        raise RuntimeError("Cannot scale a zero-impact baseline")

    scale = target_gross_kgco2e / base_result.gross_avoided_kgco2e
    scaled_breakdown = {cat: round(kg * scale, 1) for cat, kg in base_breakdown.items()}
    return scaled_breakdown


def main() -> None:
    snapshots: list[ChapterSnapshot] = [
        ChapterSnapshot(
            id=c["id"],
            net_avoided_tco2e=c["target_net_avoided_tco2e"],
            households_served_quarter=c["households_quarter"],
            needs_score=c["needs_score"],
            regional_bonus=c["regional_bonus"],
            total_tonnes=c["total_tonnes"],
        )
        for c in CHAPTERS_META
    ]
    allocations = compute_allocation(snapshots, CORP_X_PREFERENCES, CORP_X_COMMITMENT_EUR)

    chapters_out: list[dict] = []
    network_net_kgco2e = 0.0
    network_food_kg = 0.0
    corp_x_attributed_kgco2e = 0.0
    corp_x_attributed_food_kg = 0.0
    corp_x_attributed_households = 0.0

    for chapter in CHAPTERS_META:
        breakdown = _category_breakdown_for_chapter(chapter)
        impact = calculate_avoided_emissions(
            category_kg=breakdown,
            coefficients=COEFFICIENTS,
            operational_footprint_per_tonne=OPERATIONAL_FOOTPRINT_PER_TONNE,
        )
        total_food_kg = sum(breakdown.values())
        quarterly_cost_eur = round(
            chapter["households_quarter"] * COST_PER_HOUSEHOLD_PER_WEEK_EUR, 2
        )
        allocation_eur = allocations[chapter["id"]].amount_eur
        attribution_factor = min(allocation_eur / quarterly_cost_eur, 1.0)

        chapter_record = {
            "id": chapter["id"],
            "name": chapter["name"],
            "period_start": "2026-01-06",
            "period_end": "2026-03-30",
            "households_quarter": chapter["households_quarter"],
            "needs_score": chapter["needs_score"],
            "regional_bonus": chapter["regional_bonus"],
            "operational_footprint_per_tonne": OPERATIONAL_FOOTPRINT_PER_TONNE,
            "category_breakdown": breakdown,
            "total_food_kg": round(total_food_kg, 1),
            "gross_avoided_kgco2e": round(impact.gross_avoided_kgco2e, 1),
            "operational_kgco2e": round(impact.operational_kgco2e, 1),
            "net_avoided_kgco2e": round(impact.net_avoided_kgco2e, 1),
            "quarterly_cost_eur": quarterly_cost_eur,
        }
        chapters_out.append(chapter_record)

        network_net_kgco2e += impact.net_avoided_kgco2e
        network_food_kg += total_food_kg
        corp_x_attributed_kgco2e += impact.net_avoided_kgco2e * attribution_factor
        corp_x_attributed_food_kg += total_food_kg * attribution_factor
        corp_x_attributed_households += chapter["households_quarter"] * attribution_factor

    seed = {
        "period": "q1_2026",
        "period_start": "2026-01-06",
        "period_end": "2026-03-30",
        "methodology_version": "KKM-2026.1",
        "coefficients": COEFFICIENTS,
        "chapters": chapters_out,
        "corp_x_commitment_eur": CORP_X_COMMITMENT_EUR,
        "corp_x_preferences": {
            "max_climate_impact": CORP_X_PREFERENCES.max_climate_impact,
            "max_social_need": CORP_X_PREFERENCES.max_social_need,
            "balanced_distribution": CORP_X_PREFERENCES.balanced_distribution,
        },
        "corp_x_allocations": {
            chapter_id: round(result.amount_eur, 2)
            for chapter_id, result in allocations.items()
        },
        "expected_totals": {
            "net_avoided_tco2e": round(network_net_kgco2e / 1000, 2),
            "total_food_kg": round(network_food_kg, 1),
            "corp_x_attributed_tco2e": round(corp_x_attributed_kgco2e / 1000, 2),
            "corp_x_attributed_food_kg": round(corp_x_attributed_food_kg, 1),
            "corp_x_attributed_households": round(corp_x_attributed_households, 1),
        },
    }

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(seed, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")
    print(f"Network net avoided:        {seed['expected_totals']['net_avoided_tco2e']} tCO2e")
    print(f"Network food rescued:       {seed['expected_totals']['total_food_kg']:,.0f} kg")
    print(f"Corp X attributed:          {seed['expected_totals']['corp_x_attributed_tco2e']} tCO2e")
    print(f"Corp X attributed food:     {seed['expected_totals']['corp_x_attributed_food_kg']:,.0f} kg")
    print(f"Corp X households supported: {seed['expected_totals']['corp_x_attributed_households']:,.0f}")


if __name__ == "__main__":
    main()
