import uuid
from decimal import Decimal
from typing import Self

from pydantic import model_validator
from sqlmodel import Field, SQLModel

from src.backend.models.enums import SourceEnum

_PROVENANCE_SKIP = frozenset({"id", "report_id"})
_METHOD_MAX_LEN = 500  # max chars for citation strings
_EVIDENCE_MAX_LEN = 1000


def _check_provenance(instance: Self) -> Self:
    """If a measurement value is set, its _source sibling must also be set."""
    fields = type(instance).model_fields
    for field_name in fields:
        if field_name.endswith(("_source", "_method", "_evidence", "_confidence")) or field_name in _PROVENANCE_SKIP:
            continue
        source_field = f"{field_name}_source"
        if source_field in fields:
            value = getattr(instance, field_name)
            source = getattr(instance, source_field)
            if value is not None and source is None:
                raise ValueError(f"{field_name} requires {source_field} when value is set")
    return instance


class FoodVolume(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    kg_received_total: float | None = None
    kg_received_total_source: SourceEnum | None = None
    kg_received_total_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_received_total_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_received_total_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_via_national_dc: float | None = None
    kg_via_national_dc_source: SourceEnum | None = None
    kg_via_national_dc_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_via_national_dc_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_via_national_dc_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_direct: float | None = None
    kg_direct_source: SourceEnum | None = None
    kg_direct_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_direct_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_direct_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    # fraction 0–1 (e.g. 0.006 = 0.6% waste)
    waste_pct: float | None = Field(default=None, ge=0.0, le=1.0)
    waste_pct_source: SourceEnum | None = None
    waste_pct_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    waste_pct_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    waste_pct_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    parcels_distributed: int | None = None
    parcels_distributed_source: SourceEnum | None = None
    parcels_distributed_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    parcels_distributed_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    parcels_distributed_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    avg_products_per_parcel: float | None = None
    avg_products_per_parcel_source: SourceEnum | None = None
    avg_products_per_parcel_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    avg_products_per_parcel_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    avg_products_per_parcel_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    # fraction 0–1
    pct_schijf_van_vijf: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_schijf_van_vijf_source: SourceEnum | None = None
    pct_schijf_van_vijf_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    pct_schijf_van_vijf_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    pct_schijf_van_vijf_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    food_value_eur: Decimal | None = None
    food_value_eur_source: SourceEnum | None = None
    food_value_eur_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    food_value_eur_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    food_value_eur_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_non_food: float | None = None
    kg_non_food_source: SourceEnum | None = None
    kg_non_food_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_non_food_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_non_food_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        return _check_provenance(self)


class FoodCategories(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    kg_produce: float | None = None
    kg_produce_source: SourceEnum | None = None
    kg_produce_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_produce_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_produce_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_meat_fish: float | None = None
    kg_meat_fish_source: SourceEnum | None = None
    kg_meat_fish_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_meat_fish_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_meat_fish_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_dairy_eggs: float | None = None
    kg_dairy_eggs_source: SourceEnum | None = None
    kg_dairy_eggs_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_dairy_eggs_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_dairy_eggs_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_dry_goods: float | None = None
    kg_dry_goods_source: SourceEnum | None = None
    kg_dry_goods_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_dry_goods_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_dry_goods_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_bread_bakery: float | None = None
    kg_bread_bakery_source: SourceEnum | None = None
    kg_bread_bakery_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_bread_bakery_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_bread_bakery_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    kg_prepared: float | None = None
    kg_prepared_source: SourceEnum | None = None
    kg_prepared_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    kg_prepared_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    kg_prepared_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        return _check_provenance(self)


class PeopleServed(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    households_weekly: int | None = None
    households_weekly_source: SourceEnum | None = None
    households_weekly_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    households_weekly_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    households_weekly_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    individuals_total: int | None = None
    individuals_total_source: SourceEnum | None = None
    individuals_total_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    individuals_total_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    individuals_total_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    children_count: int | None = None
    children_count_source: SourceEnum | None = None
    children_count_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    children_count_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    children_count_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    # all fractions 0–1
    pct_under_18: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_under_18_source: SourceEnum | None = None
    pct_under_18_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    pct_under_18_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    pct_under_18_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    pct_single_adults: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_single_adults_source: SourceEnum | None = None
    pct_single_adults_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    pct_single_adults_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    pct_single_adults_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    pct_single_parent: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_single_parent_source: SourceEnum | None = None
    pct_single_parent_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    pct_single_parent_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    pct_single_parent_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    pct_families: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_families_source: SourceEnum | None = None
    pct_families_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    pct_families_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    pct_families_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    pct_couples: float | None = Field(default=None, ge=0.0, le=1.0)
    pct_couples_source: SourceEnum | None = None
    pct_couples_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    pct_couples_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    pct_couples_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        return _check_provenance(self)


class Operations(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    volunteers_count: int | None = None
    volunteers_count_source: SourceEnum | None = None
    volunteers_count_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    volunteers_count_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    volunteers_count_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    distribution_locations: int | None = None
    distribution_locations_source: SourceEnum | None = None
    distribution_locations_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    distribution_locations_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    distribution_locations_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    satellite_banks_served: int | None = None
    satellite_banks_served_source: SourceEnum | None = None
    satellite_banks_served_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    satellite_banks_served_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    satellite_banks_served_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    annual_budget_eur: Decimal | None = None
    annual_budget_eur_source: SourceEnum | None = None
    annual_budget_eur_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    annual_budget_eur_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    annual_budget_eur_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    total_expenditure_eur: Decimal | None = None
    total_expenditure_eur_source: SourceEnum | None = None
    total_expenditure_eur_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    total_expenditure_eur_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    total_expenditure_eur_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        return _check_provenance(self)


class Donations(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    food_supermarket_kg: float | None = None
    food_supermarket_kg_source: SourceEnum | None = None
    food_supermarket_kg_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    food_supermarket_kg_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    food_supermarket_kg_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    food_company_kg: float | None = None
    food_company_kg_source: SourceEnum | None = None
    food_company_kg_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    food_company_kg_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    food_company_kg_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    food_dc_kg: float | None = None
    food_dc_kg_source: SourceEnum | None = None
    food_dc_kg_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    food_dc_kg_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    food_dc_kg_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    money_individuals_eur: Decimal | None = None
    money_individuals_eur_source: SourceEnum | None = None
    money_individuals_eur_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    money_individuals_eur_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    money_individuals_eur_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    money_companies_eur: Decimal | None = None
    money_companies_eur_source: SourceEnum | None = None
    money_companies_eur_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    money_companies_eur_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    money_companies_eur_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    money_orgs_eur: Decimal | None = None
    money_orgs_eur_source: SourceEnum | None = None
    money_orgs_eur_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    money_orgs_eur_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    money_orgs_eur_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    money_government_eur: Decimal | None = None
    money_government_eur_source: SourceEnum | None = None
    money_government_eur_method: str | None = Field(default=None, max_length=_METHOD_MAX_LEN)
    money_government_eur_evidence: str | None = Field(default=None, max_length=_EVIDENCE_MAX_LEN)
    money_government_eur_confidence: float | None = Field(default=None, ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_provenance(self) -> Self:
        return _check_provenance(self)
