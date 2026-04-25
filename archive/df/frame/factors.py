"""
FRAME-aligned emission factors for food rescue avoided emissions.

Each factor represents kg CO2e avoided per kg of food rescued from waste,
combining (a) avoided wasted production-stage emissions and (b) avoided
disposal-route emissions under the NL counterfactual.

Methodology aligned with the Global Foodbanking Network's FRAME framework
(Food Recovery to Avoid Methane Emissions). Not FRAME-certified — alignment
means we apply the same calculation structure with publicly cited factors.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EmissionFactor:
    category: str
    kg_co2e_per_kg: float
    source: str
    notes: str


# kg CO2e avoided per kg of food rescued
# Conservative end of published ranges; demo-defensible
EMISSION_FACTORS: dict[str, EmissionFactor] = {
    "produce": EmissionFactor(
        category="produce",
        kg_co2e_per_kg=1.0,
        source="FAO Food Wastage Footprint (2013), Table 4.2",
        notes="Mix of fresh fruit and vegetables; weighted toward NL-typical supply.",
    ),
    "bakery": EmissionFactor(
        category="bakery",
        kg_co2e_per_kg=1.5,
        source="WRAP Courtauld Commitment 2030, Bakery sector data",
        notes="Bread and baked goods.",
    ),
    "dairy": EmissionFactor(
        category="dairy",
        kg_co2e_per_kg=3.2,
        source="FAO FWF + RIVM Dutch dairy LCA",
        notes="Mixed milk, yoghurt, cheese; cheese-heavy mix would push higher.",
    ),
    "meat": EmissionFactor(
        category="meat",
        kg_co2e_per_kg=8.5,
        source="FAO FWF (2013) weighted Dutch meat consumption mix",
        notes="Pork-dominant with poultry and beef share; beef-heavy would push to ~15.",
    ),
    "dry_goods": EmissionFactor(
        category="dry_goods",
        kg_co2e_per_kg=2.0,
        source="FAO FWF cereals + Poore & Nemecek (2018) for staples",
        notes="Pasta, rice, legumes, canned goods, cooking oils.",
    ),
    "prepared": EmissionFactor(
        category="prepared",
        kg_co2e_per_kg=3.0,
        source="Composite of Poore & Nemecek (2018) for processed foods",
        notes="Ready meals, sauces, prepared mixes.",
    ),
    "eggs": EmissionFactor(
        category="eggs",
        kg_co2e_per_kg=4.5,
        source="FAO FWF + Dutch egg sector data",
        notes="",
    ),
}

# FRAME is a food-rescue methodology. Hygiene products, baby supplies, and
# other non-food items distributed by foodbanks are out of scope and not
# attributed to a Climate-Action Package — they are reported separately
# under social impact, not climate impact.


# Counterfactual disposal route in NL
# US-based FRAME defaults assume landfill (high methane).
# NL waste mix (2024 estimate, RIVM/CBS): ~78% incineration with energy recovery,
# ~20% composting/AD/animal feed, ~2% landfill.
# This makes the "avoided disposal emissions" component lower than US FRAME,
# but the "avoided wasted production" component (the dominant term) is unchanged.
# Net: NL counterfactual factor of 0.93 reflects slightly lower disposal-stage
# emissions vs. US default, applied to the weighted production-stage average.
COUNTERFACTUAL_FACTOR_NL = 0.93
COUNTERFACTUAL_SOURCE = (
    "RIVM Afvalmonitor 2024 + CBS Waste Statistics; "
    "NL incineration-with-energy-recovery mix vs. US-default landfill assumption."
)


# Package economics (locked)
PACKAGE_PRICE_EUR = 25_000.0
PACKAGE_TCO2E = 600.0
PRICE_PER_TCO2E = PACKAGE_PRICE_EUR / PACKAGE_TCO2E  # €41.67


def factor_table_markdown() -> str:
    """For inclusion in the methodology appendix of audit reports."""
    rows = ["| Category | kg CO2e / kg food | Source |", "|---|---|---|"]
    for ef in EMISSION_FACTORS.values():
        rows.append(f"| {ef.category} | {ef.kg_co2e_per_kg} | {ef.source} |")
    return "\n".join(rows)
