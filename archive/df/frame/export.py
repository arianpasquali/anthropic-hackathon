"""
Export bank data + FRAME pre-computations to JSON for the marketplace UI.

The Next.js app reads /banks.json from /web/public, so this is the single
source of truth shared between the Python calculator and the JS frontend.

Run from the repo root:
    .venv/bin/python -m frame.export
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from frame import banks, calculator
from frame.factors import (
    COUNTERFACTUAL_FACTOR_NL,
    COUNTERFACTUAL_SOURCE,
    EMISSION_FACTORS,
    PACKAGE_PRICE_EUR,
    PACKAGE_TCO2E,
    PRICE_PER_TCO2E,
)


OUT_PATH = Path("web/public/banks.json")


def main() -> None:
    bank_records = []
    for bank in banks.all_banks():
        # Pre-compute canonical €25k attribution for the card view
        calc = calculator.compute(
            bank=bank,
            sponsor_amount_eur=25_000.0,
            quarter="Q2 2026",
            corporate_name="Sample Sponsor",
        )

        # Cluster status: a bank is "solo capable" if a single €25k package
        # consumes <50% of its annual avoided emissions. Otherwise the
        # marketplace shows it as a regional cluster sponsorship.
        is_solo_capable = calc.attribution_share <= 0.5

        record = {
            "id": bank.id,
            "name": bank.name,
            "region": bank.region,
            "annual_kg_rescued": bank.annual_kg_rescued,
            "annual_tco2e": round(calc.bank_annual_tco2e, 1),
            "weighted_emission_factor": round(calc.weighted_emission_factor, 3),
            "households_weekly": bank.households_weekly,
            "people_served": bank.people_served,
            "is_rdc": bank.is_regional_distribution_centre,
            "rdc_satellite_count": bank.rdc_satellite_count,
            "cluster_banks": list(bank.cluster_banks),
            "category_mix": bank.category_mix,
            "source_url": bank.source_url,
            "provenance": bank.provenance,
            "standard_package": {
                "amount_eur": 25_000,
                "attributed_tco2e": round(calc.attributed_tco2e, 1),
                "attributed_kg_food": round(calc.attributed_kg_food, 0),
                "attribution_share": round(calc.attribution_share, 4),
                "is_solo_capable": is_solo_capable,
                "category_breakdown": {
                    cat: {
                        "tco2e": round(calc.category_breakdown_tco2e[cat], 2),
                        "kg_food": round(calc.category_breakdown_kg[cat], 0),
                    }
                    for cat in bank.category_mix
                },
            },
        }
        bank_records.append(record)

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "package": {
            "price_eur": PACKAGE_PRICE_EUR,
            "tco2e": PACKAGE_TCO2E,
            "price_per_tco2e": round(PRICE_PER_TCO2E, 2),
        },
        "methodology": {
            "framework": "Global Foodbanking Network FRAME — alignment, not certification",
            "counterfactual_factor_nl": COUNTERFACTUAL_FACTOR_NL,
            "counterfactual_source": COUNTERFACTUAL_SOURCE,
            "emission_factors": [
                {
                    "category": ef.category,
                    "kg_co2e_per_kg": ef.kg_co2e_per_kg,
                    "source": ef.source,
                    "notes": ef.notes,
                }
                for ef in EMISSION_FACTORS.values()
            ],
        },
        "banks": bank_records,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2))
    print(f"Wrote {OUT_PATH} ({len(bank_records)} banks, {OUT_PATH.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
