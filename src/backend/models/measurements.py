import uuid
from sqlmodel import Field, SQLModel
from src.backend.models.enums import SourceEnum, CounterfactualEnum


class FoodVolume(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    kg_received_total: float | None = None
    kg_received_total_source: SourceEnum | None = None
    kg_received_total_method: str | None = None

    kg_via_national_dc: float | None = None
    kg_via_national_dc_source: SourceEnum | None = None
    kg_via_national_dc_method: str | None = None

    kg_direct: float | None = None
    kg_direct_source: SourceEnum | None = None
    kg_direct_method: str | None = None

    waste_pct: float | None = None
    waste_pct_source: SourceEnum | None = None
    waste_pct_method: str | None = None

    parcels_distributed: int | None = None
    parcels_distributed_source: SourceEnum | None = None
    parcels_distributed_method: str | None = None

    avg_products_per_parcel: float | None = None
    avg_products_per_parcel_source: SourceEnum | None = None
    avg_products_per_parcel_method: str | None = None

    pct_schijf_van_vijf: float | None = None
    pct_schijf_van_vijf_source: SourceEnum | None = None
    pct_schijf_van_vijf_method: str | None = None

    food_value_eur: float | None = None
    food_value_eur_source: SourceEnum | None = None
    food_value_eur_method: str | None = None


class FoodCategories(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    kg_produce: float | None = None
    kg_produce_source: SourceEnum | None = None
    kg_produce_method: str | None = None

    kg_meat_fish: float | None = None
    kg_meat_fish_source: SourceEnum | None = None
    kg_meat_fish_method: str | None = None

    kg_dairy_eggs: float | None = None
    kg_dairy_eggs_source: SourceEnum | None = None
    kg_dairy_eggs_method: str | None = None

    kg_dry_goods: float | None = None
    kg_dry_goods_source: SourceEnum | None = None
    kg_dry_goods_method: str | None = None

    kg_bread_bakery: float | None = None
    kg_bread_bakery_source: SourceEnum | None = None
    kg_bread_bakery_method: str | None = None

    kg_prepared: float | None = None
    kg_prepared_source: SourceEnum | None = None
    kg_prepared_method: str | None = None

    kg_non_food: float | None = None
    kg_non_food_source: SourceEnum | None = None
    kg_non_food_method: str | None = None


class PeopleServed(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    households_weekly: int | None = None
    households_weekly_source: SourceEnum | None = None
    households_weekly_method: str | None = None

    individuals_total: int | None = None
    individuals_total_source: SourceEnum | None = None
    individuals_total_method: str | None = None

    children_count: int | None = None
    children_count_source: SourceEnum | None = None
    children_count_method: str | None = None

    pct_under_18: float | None = None
    pct_under_18_source: SourceEnum | None = None
    pct_under_18_method: str | None = None

    pct_single_adults: float | None = None
    pct_single_adults_source: SourceEnum | None = None
    pct_single_adults_method: str | None = None

    pct_single_parent: float | None = None
    pct_single_parent_source: SourceEnum | None = None
    pct_single_parent_method: str | None = None

    pct_families: float | None = None
    pct_families_source: SourceEnum | None = None
    pct_families_method: str | None = None

    pct_couples: float | None = None
    pct_couples_source: SourceEnum | None = None
    pct_couples_method: str | None = None


class Operations(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    volunteers_count: int | None = None
    volunteers_count_source: SourceEnum | None = None
    volunteers_count_method: str | None = None

    distribution_locations: int | None = None
    distribution_locations_source: SourceEnum | None = None
    distribution_locations_method: str | None = None

    satellite_banks_served: int | None = None
    satellite_banks_served_source: SourceEnum | None = None
    satellite_banks_served_method: str | None = None

    annual_budget_eur: float | None = None
    annual_budget_eur_source: SourceEnum | None = None
    annual_budget_eur_method: str | None = None

    total_expenditure_eur: float | None = None
    total_expenditure_eur_source: SourceEnum | None = None
    total_expenditure_eur_method: str | None = None

    # Always set explicitly for FRAME audit trail
    counterfactual_route: CounterfactualEnum = CounterfactualEnum.incineration_energy_recovery


class Donations(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    food_supermarket_kg: float | None = None
    food_supermarket_kg_source: SourceEnum | None = None
    food_supermarket_kg_method: str | None = None

    food_company_kg: float | None = None
    food_company_kg_source: SourceEnum | None = None
    food_company_kg_method: str | None = None

    food_dc_kg: float | None = None
    food_dc_kg_source: SourceEnum | None = None
    food_dc_kg_method: str | None = None

    money_individuals_eur: float | None = None
    money_individuals_eur_source: SourceEnum | None = None
    money_individuals_eur_method: str | None = None

    money_companies_eur: float | None = None
    money_companies_eur_source: SourceEnum | None = None
    money_companies_eur_method: str | None = None

    money_orgs_eur: float | None = None
    money_orgs_eur_source: SourceEnum | None = None
    money_orgs_eur_method: str | None = None

    money_government_eur: float | None = None
    money_government_eur_source: SourceEnum | None = None
    money_government_eur_method: str | None = None
