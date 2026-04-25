"""Idempotent local-dev database initialization.

Creates all tables on the configured database and seeds the canonical
chapters + Q1 2026 fund. Safe to re-run; existing rows are not touched.

    python scripts/init_db.py
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BACKEND_ROOT = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Chapter, Fund  # noqa: E402

CHAPTERS = [
    {
        "id": "VB-AMS-OOST",
        "name": "Voedselbank Amsterdam-Oost",
        "type": "urban",
        "households_served_per_week": 380,
        "needs_score": 0.78,
        "regional_bonus": 1.0,
        "operational_footprint_kgco2e_per_tonne": 38.0,
        "cost_per_household_per_week_eur": 10.80,
    },
    {
        "id": "VB-RDM-ZUID",
        "name": "Voedselbank Rotterdam-Zuid",
        "type": "urban",
        "households_served_per_week": 420,
        "needs_score": 0.92,
        "regional_bonus": 1.0,
        "operational_footprint_kgco2e_per_tonne": 38.0,
        "cost_per_household_per_week_eur": 10.80,
    },
    {
        "id": "VB-LEI-CTR",
        "name": "Voedselbank Leiden Centrum",
        "type": "urban",
        "households_served_per_week": 240,
        "needs_score": 0.61,
        "regional_bonus": 1.0,
        "operational_footprint_kgco2e_per_tonne": 38.0,
        "cost_per_household_per_week_eur": 10.80,
    },
    {
        "id": "VB-FRL-NRD",
        "name": "Voedselbank Friesland-Noord",
        "type": "rural",
        "households_served_per_week": 95,
        "needs_score": 0.71,
        "regional_bonus": 1.15,
        "operational_footprint_kgco2e_per_tonne": 42.0,
        "cost_per_household_per_week_eur": 10.80,
    },
    {
        "id": "VB-EHV-CTR",
        "name": "Voedselbank Eindhoven Centrum",
        "type": "urban",
        "households_served_per_week": 285,
        "needs_score": 0.68,
        "regional_bonus": 1.0,
        "operational_footprint_kgco2e_per_tonne": 38.0,
        "cost_per_household_per_week_eur": 10.80,
    },
]


def main() -> None:
    print(f"Creating tables on {engine.url!r}...")
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        for spec in CHAPTERS:
            existing = session.get(Chapter, spec["id"])
            if existing is None:
                session.add(Chapter(**spec))
                print(f"  + chapter {spec['id']}")
            else:
                print(f"  · chapter {spec['id']} already exists")

        if session.get(Fund, "demo-fund-q1-2026") is None:
            session.add(
                Fund(
                    id="demo-fund-q1-2026",
                    name="Klimaatkracht Q1 2026",
                    period_start=date(2026, 1, 6),
                    period_end=date(2026, 3, 30),
                    methodology_version="KKM-2026.1",
                )
            )
            print("  + fund demo-fund-q1-2026")
        else:
            print("  · fund demo-fund-q1-2026 already exists")
        session.commit()
    print("Done.")


if __name__ == "__main__":
    main()
