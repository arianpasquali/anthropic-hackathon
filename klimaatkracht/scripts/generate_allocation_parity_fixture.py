"""Generate frontend/tests/fixtures/allocation-cases.json from Python.

The Vitest parity test loads this file and runs the JS allocation-preview
library against each case, asserting it matches the Python output to
within 1e-6. That guards Invariant 5 from the implementation plan
("frontend allocation preview matches backend").

Run:
    python scripts/generate_allocation_parity_fixture.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
FRONTEND_ROOT = REPO_ROOT / "frontend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.services.allocation_engine import (  # noqa: E402
    AllocationPreferences,
    ChapterSnapshot,
    compute_allocation,
)

OUTPUT_PATH = FRONTEND_ROOT / "tests" / "fixtures" / "allocation-cases.json"

CHAPTERS = [
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

CASES = [
    ("blended_400_400_200", AllocationPreferences(0.4, 0.4, 0.2), 100_000),
    ("climate_only", AllocationPreferences(1.0, 0.0, 0.0), 100_000),
    ("social_only", AllocationPreferences(0.0, 1.0, 0.0), 100_000),
    ("balanced_only", AllocationPreferences(0.0, 0.0, 1.0), 100_000),
    ("small_amount_climate_heavy", AllocationPreferences(0.7, 0.2, 0.1), 5_000),
    ("rural_focus_social_heavy", AllocationPreferences(0.1, 0.7, 0.2), 250_000),
]


def main() -> None:
    fixture: list[dict] = []
    for label, prefs, amount in CASES:
        result = compute_allocation(CHAPTERS, prefs, amount)
        fixture.append({
            "label": label,
            "amount_eur": amount,
            "preferences": {
                "max_climate_impact": prefs.max_climate_impact,
                "max_social_need": prefs.max_social_need,
                "balanced_distribution": prefs.balanced_distribution,
            },
            "expected": [
                {
                    "chapter_id": cid,
                    "weight": r.weight,
                    "amount_eur": r.amount_eur,
                    "axis_weights": r.axis_weights,
                }
                for cid, r in result.items()
            ],
        })

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "chapters": [asdict(c) for c in CHAPTERS],
        "cases": fixture,
    }
    OUTPUT_PATH.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {OUTPUT_PATH}")
    print(f"  chapters: {len(payload['chapters'])}")
    print(f"  cases:    {len(payload['cases'])}")


if __name__ == "__main__":
    main()
