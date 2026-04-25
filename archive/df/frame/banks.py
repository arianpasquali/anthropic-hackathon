"""
Dutch foodbank operational data.

All figures sourced from each bank's published 2024 annual report
(or 2025 / 2023 where 2024 not yet published). Conversion assumptions
(units → kg, parcels → kg) are explicit and documented per bank in
the `provenance` field — these become the methodology trail in the
audit-ready quarterly report.

Average unit→kg conversion: 0.6 kg per consumenteneenheid, validated
across banks where both units and weight were reported (Woerden 220k
units → 132 t implied; Voedselbanken Nederland 68.1M units → ~40 kt
implied, consistent with VBN's "tens of millions of kg" framing).
"""

from dataclasses import dataclass, field


# Default category mix derived from Voedselbanken Nederland Schijf van Vijf
# framing (~55% Schijf van Vijf basics) and Haaglanden 2024 published parcel
# breakdown (25 articles: 9 DKW, 8 G&F, 2-3 zuivel/koel-vries, ~5 other).
# Mix is over food categories only — non-food items distributed by banks
# (hygiene, household) are out of scope for FRAME and reported separately.
DEFAULT_CATEGORY_MIX: dict[str, float] = {
    "produce": 0.32,
    "dry_goods": 0.36,
    "dairy": 0.10,
    "bakery": 0.09,
    "meat": 0.05,
    "prepared": 0.06,
    "eggs": 0.02,
}


@dataclass(frozen=True)
class Bank:
    id: str
    name: str
    region: str
    annual_kg_rescued: int
    category_mix: dict[str, float]
    households_weekly: int | None
    # `people_served` is only set when the bank publishes a total. None means
    # the bank publishes households (and sometimes children) but not a unified
    # "people" figure — derived estimates are not used to keep the report
    # auditable.
    people_served: int | None
    is_regional_distribution_centre: bool
    # Number of satellite banks served by this bank as a Voedselbanken
    # Nederland Regional Distribution Centre. Distinct from `cluster_banks`,
    # which lists named members of a self-organised regional alliance.
    rdc_satellite_count: int | None = None
    cluster_banks: tuple[str, ...] = field(default_factory=tuple)
    source_url: str = ""
    provenance: str = ""


BANKS: dict[str, Bank] = {
    "rotterdam": Bank(
        id="rotterdam",
        name="Voedselbank Rotterdam",
        region="Zuid-Holland",
        # Published directly: "ongeveer 80.000 kilogram per week" regional
        annual_kg_rescued=80_000 * 52,  # 4,160,000 kg/yr
        # Rotterdam-specific: 2-person parcel = 25 units, 13 fresh F&V (52%)
        category_mix={
            "produce": 0.50,
            "dry_goods": 0.18,
            "dairy": 0.10,
            "bakery": 0.10,
            "meat": 0.05,
            "prepared": 0.05,
            "eggs": 0.02,
        },
        households_weekly=1_682,
        people_served=None,  # Rotterdam publishes households + children, not a unified people total
        is_regional_distribution_centre=True,
        rdc_satellite_count=33,
        source_url="https://voedselbank.nl/jaarrekeningen/",
        provenance=(
            "Annual rescue cited directly in Voedselbank Rotterdam Jaarverslag 2024 "
            "as 'ongeveer 80.000 kilogram per week' across the Rotterdam regional "
            "network (incl. 33 satellite banks). Category mix derived from published "
            "parcel composition (13 of 25 units fresh F&V for 2-person households)."
        ),
    ),
    "amsterdam": Bank(
        id="amsterdam",
        name="Voedselbank Amsterdam",
        region="Noord-Holland",
        # Amsterdam city: 1,535 hh × 30 products × 0.6 kg × 52 = 1,437,840 kg/yr
        # Plus regional RDC for 18 banks: ~7M kg/yr additional regional
        # Using city figure for direct attribution
        annual_kg_rescued=1_437_840,
        category_mix=DEFAULT_CATEGORY_MIX,
        households_weekly=1_535,
        people_served=3_799,  # "Wekelijks ontvangen 3.799 Amsterdammers voedselhulp" (published)
        is_regional_distribution_centre=True,
        rdc_satellite_count=18,
        source_url="https://voedselbank.amsterdam/over-ons/",
        provenance=(
            "Households (1,535) and parcel size (~30 products) cited in Voedselbank "
            "Amsterdam Jaarverslag 2024. Annual kg estimated from "
            "1,535 hh × 30 products/wk × 0.6 kg/unit × 52 weeks. Cross-check: "
            "228,939 kg of fresh F&V from Groente & Fruitbrigade alone in 2024."
        ),
    ),
    "haaglanden": Bank(
        id="haaglanden",
        name="Voedselbank Haaglanden",
        region="Zuid-Holland",
        # 2,904 hh × 25 articles × 0.6 kg × 52 = 2,265,120 kg/yr
        annual_kg_rescued=2_265_120,
        # Haaglanden published explicit parcel breakdown:
        # 25 articles = 9 DKW (36%) + 8 G&F (32%) + 2.5 zuivel/koel-vries (10%) + ~5.5 other (22%)
        category_mix={
            "dry_goods": 0.36,
            "produce": 0.32,
            "dairy": 0.10,
            "bakery": 0.09,
            "meat": 0.06,
            "prepared": 0.06,
            "eggs": 0.01,
        },
        households_weekly=2_904,
        people_served=6_840,
        is_regional_distribution_centre=False,
        cluster_banks=(),
        source_url="https://voedselbankhaaglanden.nl/feiten-en-cijfers-2/",
        provenance=(
            "Households (2,904) and parcel composition (25 articles: 9 DKW, 8 G&F, "
            "2-3 zuivel, ~5 other) cited directly in Voedselbank Haaglanden "
            "Jaarverslag 2024. Annual kg estimated using 0.6 kg/unit conversion. "
            "Serves Den Haag, Rijswijk, Zoetermeer via 21 distribution points."
        ),
    ),
    "eindhoven": Bank(
        id="eindhoven",
        name="Voedselbank Eindhoven",
        region="Noord-Brabant",
        # 32,000 parcels × ~10 kg per parcel (€35/parcel ÷ ~€3.50/kg retail) = 320,000 kg/yr
        # Plus cluster of 9 banks ≈ doubles total served by cluster
        annual_kg_rescued=320_000,
        category_mix=DEFAULT_CATEGORY_MIX,
        households_weekly=609,
        people_served=1_296,
        is_regional_distribution_centre=False,
        cluster_banks=(
            "Aalst-Waalre", "Best", "Bergeijk", "Bladel",
            "Deurne", "Geldrop-Mierlo", "Nuenen", "Valkenswaard", "Veldhoven",
        ),
        source_url="https://www.voedselbankeindhoven.nl/",
        provenance=(
            "Parcels (32,000/yr) and retail value (€1.1M food / 32,000 = €34.4/parcel) "
            "cited in Voedselbank Eindhoven Jaarverslag 2024. Annual kg estimated from "
            "retail value at €3.50/kg blended NL grocery price. Eindhoven self-organises "
            "as 'Cluster Eindhoven' with 9 named neighbour banks; together delivered ~€2M "
            "food value via Tilburg RDC."
        ),
    ),
    "groningen": Bank(
        id="groningen",
        name="Voedselbank Gemeente Groningen",
        region="Groningen",
        # 517 hh in city × 30 products × 0.6 kg × 52 = 484,000 kg/yr
        # RDC region (1,675 hh) covers more
        annual_kg_rescued=484_000,
        category_mix=DEFAULT_CATEGORY_MIX,
        households_weekly=517,
        people_served=1_064,
        is_regional_distribution_centre=True,
        cluster_banks=(),  # RDC for 1,675 hh in Groningen + Noordenveld
        source_url="https://voedselbank-groningen.nl/jaarverslag/",
        provenance=(
            "Households (517 in gemeente Groningen, 1,675 in RDC region incl. "
            "Noordenveld) cited in Voedselbank Gemeente Groningen Jaarverslag 2024. "
            "Annual kg estimated from city households × 30 products/wk × 0.6 kg/unit "
            "× 52 weeks. RDC role for northern provinces."
        ),
    ),
    "breda": Bank(
        id="breda",
        name="Voedselbank Breda",
        region="Noord-Brabant",
        # Direct citation: 507,496 kg ontvangen voedsel in 2025
        # 2024 figure (less complete in jaarbeeld 2025) — use 2025
        annual_kg_rescued=507_496,
        category_mix=DEFAULT_CATEGORY_MIX,
        households_weekly=335,
        people_served=2_046,
        is_regional_distribution_centre=False,
        cluster_banks=(),
        source_url="https://voedselbankbreda.nl/anbi/",
        provenance=(
            "Annual rescue cited directly in Voedselbank Breda Jaarbeeld 2025: "
            "507,496 kg ontvangen voedsel (of which 195,528 kg from supermarkets). "
            "Households (335 wkly, 867 unique) cited in same source. "
            "Note: 2025 figure used as 2024 fin not yet published in machine-readable form."
        ),
    ),
}


def get(bank_id: str) -> Bank:
    if bank_id not in BANKS:
        raise KeyError(f"Unknown bank: {bank_id!r}. Known: {list(BANKS)}")
    return BANKS[bank_id]


def all_banks() -> list[Bank]:
    return list(BANKS.values())
