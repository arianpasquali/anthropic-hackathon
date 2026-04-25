"""
FRAME-aligned attribution calculator.

Given a foodbank, a sponsor amount, and a quarter, compute:
  - tCO2e attributed to the sponsor
  - kg food rescue attributed
  - category breakdown (which slice of impact came from which food category)
  - methodology trail (every assumption, every number, every source)

The calculator is fully deterministic — no LLM. Claude is used downstream
to compose the report narrative around these structured outputs.
"""

from dataclasses import dataclass

from frame.banks import Bank
from frame.factors import (
    EMISSION_FACTORS,
    COUNTERFACTUAL_FACTOR_NL,
    COUNTERFACTUAL_SOURCE,
    PACKAGE_PRICE_EUR,
    PACKAGE_TCO2E,
    PRICE_PER_TCO2E,
)


@dataclass(frozen=True)
class FrameCalculation:
    bank: Bank
    sponsor_amount_eur: float
    quarter: str
    corporate_name: str

    # Bank-level
    weighted_emission_factor: float
    bank_annual_tco2e: float

    # Attribution
    attributed_tco2e: float
    attributed_kg_food: float
    attribution_share: float

    # Breakdown
    category_breakdown_tco2e: dict[str, float]  # category → tCO2e
    category_breakdown_kg: dict[str, float]  # category → kg

    # Audit trail
    methodology_trail: list[str]
    sources: list[str]


def _weighted_emission_factor(category_mix: dict[str, float]) -> float:
    """kg CO2e avoided per kg food rescued, given a bank's category mix."""
    mix_sum = sum(category_mix.values())
    if abs(mix_sum - 1.0) > 0.001:
        raise ValueError(
            f"Category mix must sum to 1.0 over food categories, got {mix_sum:.4f}. "
            f"Non-food items are out of scope for FRAME."
        )
    total = sum(
        share * EMISSION_FACTORS[cat].kg_co2e_per_kg
        for cat, share in category_mix.items()
    )
    return total * COUNTERFACTUAL_FACTOR_NL


def compute(
    bank: Bank,
    sponsor_amount_eur: float,
    quarter: str,
    corporate_name: str = "Sponsor Corporation",
) -> FrameCalculation:
    weighted_ef = _weighted_emission_factor(bank.category_mix)
    bank_annual_tco2e = (bank.annual_kg_rescued * weighted_ef) / 1000.0

    attributed_tco2e = sponsor_amount_eur / PRICE_PER_TCO2E
    attributed_kg_food = (attributed_tco2e * 1000.0) / weighted_ef
    attribution_share = attributed_tco2e / bank_annual_tco2e

    # Pro-rata across categories by their contribution to the weighted factor
    category_breakdown_tco2e: dict[str, float] = {}
    category_breakdown_kg: dict[str, float] = {}
    for cat, share in bank.category_mix.items():
        cat_factor = EMISSION_FACTORS[cat].kg_co2e_per_kg * COUNTERFACTUAL_FACTOR_NL
        cat_contribution = (share * cat_factor) / weighted_ef if weighted_ef else 0.0
        category_breakdown_tco2e[cat] = attributed_tco2e * cat_contribution
        category_breakdown_kg[cat] = attributed_kg_food * share

    methodology_trail = [
        f"Sponsor: {corporate_name}",
        f"Quarter: {quarter}",
        f"Foodbank: {bank.name} ({bank.region})",
        f"Sponsor amount: €{sponsor_amount_eur:,.0f}",
        f"Package economics: €{PACKAGE_PRICE_EUR:,.0f} per {PACKAGE_TCO2E:.0f} tCO2e "
        f"(€{PRICE_PER_TCO2E:.2f} per tCO2e)",
        "",
        "Step 1 — Bank operational throughput",
        f"  Annual food rescued: {bank.annual_kg_rescued:,} kg",
        f"  Households served weekly: {bank.households_weekly:,}"
        if bank.households_weekly
        else "  Households: not published",
        f"  Source: {bank.provenance}",
        "",
        "Step 2 — Category mix and weighted emission factor",
        *[
            f"  {cat}: {share:.0%} × {EMISSION_FACTORS[cat].kg_co2e_per_kg} kg CO2e/kg = "
            f"{share * EMISSION_FACTORS[cat].kg_co2e_per_kg:.3f}"
            for cat, share in bank.category_mix.items()
        ],
        f"  Weighted factor before counterfactual: {weighted_ef / COUNTERFACTUAL_FACTOR_NL:.3f} kg CO2e/kg",
        f"  NL counterfactual factor: ×{COUNTERFACTUAL_FACTOR_NL}",
        f"  Final weighted factor: {weighted_ef:.3f} kg CO2e/kg food rescued",
        "",
        "Step 3 — Bank-level annual avoided emissions",
        f"  {bank.annual_kg_rescued:,} kg × {weighted_ef:.3f} kg CO2e/kg = "
        f"{bank_annual_tco2e:,.1f} tCO2e/yr",
        "",
        "Step 4 — Sponsor attribution (pro-rata by package economics)",
        f"  Attributed tCO2e = €{sponsor_amount_eur:,.0f} ÷ €{PRICE_PER_TCO2E:.2f}/tCO2e "
        f"= {attributed_tco2e:.1f} tCO2e",
        f"  Attributed kg food = {attributed_tco2e:.1f} tCO2e × 1000 ÷ "
        f"{weighted_ef:.3f} = {attributed_kg_food:,.0f} kg",
        f"  Attribution share = {attributed_tco2e:.1f} ÷ {bank_annual_tco2e:.1f} "
        f"= {attribution_share:.2%} of bank annual rescue",
    ]

    sources = [
        f"Foodbank operational data: {bank.source_url}",
        "Emission factors: FAO Food Wastage Footprint (2013); WRAP Courtauld 2030; "
        "RIVM Dutch dairy LCA; Poore & Nemecek (2018)",
        f"Counterfactual disposal route: {COUNTERFACTUAL_SOURCE}",
        "Methodology framework: Global Foodbanking Network FRAME (Food Recovery to "
        "Avoid Methane Emissions) — alignment, not certification",
    ]

    return FrameCalculation(
        bank=bank,
        sponsor_amount_eur=sponsor_amount_eur,
        quarter=quarter,
        corporate_name=corporate_name,
        weighted_emission_factor=weighted_ef,
        bank_annual_tco2e=bank_annual_tco2e,
        attributed_tco2e=attributed_tco2e,
        attributed_kg_food=attributed_kg_food,
        attribution_share=attribution_share,
        category_breakdown_tco2e=category_breakdown_tco2e,
        category_breakdown_kg=category_breakdown_kg,
        methodology_trail=methodology_trail,
        sources=sources,
    )


def to_report_payload(calc: FrameCalculation) -> dict:
    """Structured payload for the Claude report-generation prompt."""
    return {
        "corporate_name": calc.corporate_name,
        "quarter": calc.quarter,
        "foodbank": {
            "name": calc.bank.name,
            "region": calc.bank.region,
            "households_weekly": calc.bank.households_weekly,
            "people_served": calc.bank.people_served,
            "annual_kg_rescued": calc.bank.annual_kg_rescued,
            "is_rdc": calc.bank.is_regional_distribution_centre,
            "rdc_satellite_count": calc.bank.rdc_satellite_count,
            "cluster_banks": list(calc.bank.cluster_banks),
        },
        "package": {
            "amount_eur": calc.sponsor_amount_eur,
            "price_per_tco2e": round(PRICE_PER_TCO2E, 2),
        },
        "impact": {
            "attributed_tco2e": round(calc.attributed_tco2e, 1),
            "attributed_kg_food": round(calc.attributed_kg_food, 0),
            "attribution_share_pct": round(calc.attribution_share * 100, 2),
            "bank_annual_tco2e": round(calc.bank_annual_tco2e, 1),
            "weighted_emission_factor": round(calc.weighted_emission_factor, 3),
        },
        "category_breakdown": {
            cat: {
                "tco2e": round(calc.category_breakdown_tco2e[cat], 2),
                "kg_food": round(calc.category_breakdown_kg[cat], 0),
                "emission_factor": EMISSION_FACTORS[cat].kg_co2e_per_kg,
            }
            for cat in calc.bank.category_mix
        },
        "methodology_trail": calc.methodology_trail,
        "sources": calc.sources,
    }
