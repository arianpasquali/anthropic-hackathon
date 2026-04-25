"""
End-to-end demo of the FRAME calculator.

Run from the repo root:
    python -m frame.demo
"""

import json

from frame import banks, calculator


def main() -> None:
    # Anchor demo case: Heineken sponsors Voedselbank Rotterdam for Q2 2026
    rotterdam = banks.get("rotterdam")
    calc = calculator.compute(
        bank=rotterdam,
        sponsor_amount_eur=25_000.0,
        quarter="Q2 2026",
        corporate_name="Heineken N.V.",
    )

    print("=" * 70)
    print(f"  {calc.corporate_name} — Climate-Action Package")
    print(f"  {calc.bank.name} | {calc.quarter}")
    print("=" * 70)
    print()
    print(f"  Sponsor amount:        €{calc.sponsor_amount_eur:>12,.0f}")
    print(f"  Attributed tCO2e:       {calc.attributed_tco2e:>12,.1f}")
    print(f"  Attributed kg food:     {calc.attributed_kg_food:>12,.0f}")
    print(f"  Share of bank annual:   {calc.attribution_share:>12.2%}")
    print(f"  Bank annual tCO2e:      {calc.bank_annual_tco2e:>12,.1f}")
    print(f"  Weighted EF:            {calc.weighted_emission_factor:>12.3f} kg CO2e/kg")
    print()
    print("  Category breakdown (tCO2e):")
    for cat, tco2e in calc.category_breakdown_tco2e.items():
        kg = calc.category_breakdown_kg[cat]
        print(f"    {cat:<12} {tco2e:>8.1f} tCO2e   ({kg:>8,.0f} kg food)")
    print()
    print("  Methodology trail:")
    for line in calc.methodology_trail:
        print(f"    {line}")
    print()
    print("  Sources:")
    for src in calc.sources:
        print(f"    - {src}")
    print()
    print("-" * 70)
    print("  Cross-check across all 6 banks at €25k:")
    print("-" * 70)
    print(f"  {'Bank':<32} {'Annual tCO2e':>14} {'Share at €25k':>16}")
    for bank in banks.all_banks():
        c = calculator.compute(bank, 25_000.0, "Q2 2026", "Demo Corp")
        print(
            f"  {bank.name:<32} {c.bank_annual_tco2e:>14,.0f} "
            f"{c.attribution_share:>15.2%}"
        )
    print()

    # Save the structured payload for the report-generation prompt
    payload = calculator.to_report_payload(calc)
    out_path = "frame/sample_payload.json"
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Sample report payload written to: {out_path}")


if __name__ == "__main__":
    main()
