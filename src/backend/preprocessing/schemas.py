from pydantic import BaseModel, Field


class FoodVolumeExtraction(BaseModel):
    kg_received_total: float | None = None
    kg_received_total_method: str | None = None
    kg_via_national_dc: float | None = None
    kg_via_national_dc_method: str | None = None
    kg_direct: float | None = None
    kg_direct_method: str | None = None
    waste_pct: float | None = Field(default=None, ge=0.0, le=1.0)
    waste_pct_method: str | None = None
    parcels_distributed: int | None = None
    parcels_distributed_method: str | None = None
    avg_products_per_parcel: float | None = None
    avg_products_per_parcel_method: str | None = None
    pct_schijf_van_vijf: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_schijf_van_vijf_method: str | None = None
    food_value_eur: float | None = None
    food_value_eur_method: str | None = None


class FoodCategoriesExtraction(BaseModel):
    kg_produce: float | None = None
    kg_produce_method: str | None = None
    kg_meat_fish: float | None = None
    kg_meat_fish_method: str | None = None
    kg_dairy_eggs: float | None = None
    kg_dairy_eggs_method: str | None = None
    kg_dry_goods: float | None = None
    kg_dry_goods_method: str | None = None
    kg_bread_bakery: float | None = None
    kg_bread_bakery_method: str | None = None
    kg_prepared: float | None = None
    kg_prepared_method: str | None = None


class PeopleServedExtraction(BaseModel):
    households_weekly: int | None = None
    households_weekly_method: str | None = None
    individuals_total: int | None = None
    individuals_total_method: str | None = None
    children_count: int | None = None
    children_count_method: str | None = None
    pct_under_18: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_under_18_method: str | None = None
    pct_single_adults: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_single_adults_method: str | None = None
    pct_single_parent: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_single_parent_method: str | None = None
    pct_families: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_families_method: str | None = None
    pct_couples: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_couples_method: str | None = None


class OperationsExtraction(BaseModel):
    volunteers_count: int | None = None
    volunteers_count_method: str | None = None
    distribution_locations: int | None = None
    distribution_locations_method: str | None = None
    satellite_banks_served: int | None = None
    satellite_banks_served_method: str | None = None
    annual_budget_eur: float | None = None
    annual_budget_eur_method: str | None = None
    total_expenditure_eur: float | None = None
    total_expenditure_eur_method: str | None = None


class DonationsExtraction(BaseModel):
    food_supermarket_kg: float | None = None
    food_supermarket_kg_method: str | None = None
    food_company_kg: float | None = None
    food_company_kg_method: str | None = None
    food_dc_kg: float | None = None
    food_dc_kg_method: str | None = None
    money_individuals_eur: float | None = None
    money_individuals_eur_method: str | None = None
    money_companies_eur: float | None = None
    money_companies_eur_method: str | None = None
    money_orgs_eur: float | None = None
    money_orgs_eur_method: str | None = None
    money_government_eur: float | None = None
    money_government_eur_method: str | None = None


class ExtractionResult(BaseModel):
    food_volume: FoodVolumeExtraction
    food_categories: FoodCategoriesExtraction
    people_served: PeopleServedExtraction
    operations: OperationsExtraction
    donations: DonationsExtraction


_BASE_INSTRUCTIONS = """You extract structured data from Dutch foodbank annual reports.
Extract ONLY values explicitly stated in the text — do not infer or estimate.
For each extracted value, fill the companion _method field with a short citation
(e.g. "p.10 'Ontvangen voedsel 507.496 kilo'").
All percentage/fraction fields must be expressed as fractions 0–1
(e.g. 0.006 for 0.6%, 0.37 for 37%). Return null for any value not found."""

SECTION_PROMPTS: dict[str, str] = {
    "extract_food_volume": f"""{_BASE_INSTRUCTIONS}

Extract ONLY food weight and volume metrics:
total kg received, kg from national DC (distributiecentrum), kg from direct donations,
waste percentage (naar de stort), total parcels/packages distributed,
average products per parcel, percentage healthy foods (Schijf van Vijf), food value in euros.
Do NOT extract household counts, demographics, volunteer counts, or donation money.""",

    "extract_food_categories": f"""{_BASE_INSTRUCTIONS}

Extract ONLY food broken down by category in kilograms:
produce/vegetables/fruit (groente en fruit, aardappelen),
meat and fish (vlees en vis),
dairy and eggs (zuivel en eieren),
dry goods/pantry items (droge kruidenierswaren),
bread and bakery (brood),
prepared foods (bereide maaltijden).
Do NOT extract totals, household counts, or money figures.""",

    "extract_people_served": f"""{_BASE_INSTRUCTIONS}

Extract ONLY beneficiary and demographic data:
weekly household count (huishoudens per week), total individuals (personen),
number of children (kinderen onder 18),
percentage under 18 (as fraction 0–1),
percentage single adults, single-parent households, families, couples.
Do NOT extract food weights, kg figures, or financial data.""",

    "extract_operations": f"""{_BASE_INSTRUCTIONS}

Extract ONLY operational metrics:
number of volunteers (vrijwilligers),
number of distribution locations (locaties, uitgiftepunten),
number of satellite banks served (aangesloten voedselbanken),
annual budget (begroting in euros),
total expenditure/costs (uitgaven, kosten in euros).
Do NOT extract food weights, household counts, or donation breakdowns.""",

    "extract_donations": f"""{_BASE_INSTRUCTIONS}

Extract ONLY donation data — both food and monetary:
food donated by supermarkets (kg), food donated by companies/suppliers (kg),
food received via national DC (kg),
monetary donations from individuals (particulieren in euros),
from companies/businesses (bedrijven in euros),
from non-profit organisations (organisaties in euros),
from government/municipality (gemeente, overheid in euros).
Do NOT extract household counts, volunteer numbers, or food category breakdowns.""",
}

TOOL_SCHEMA_MAP: dict[str, type] = {
    "extract_food_volume": FoodVolumeExtraction,
    "extract_food_categories": FoodCategoriesExtraction,
    "extract_people_served": PeopleServedExtraction,
    "extract_operations": OperationsExtraction,
    "extract_donations": DonationsExtraction,
}
