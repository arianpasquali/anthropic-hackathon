from pydantic import BaseModel, ConfigDict, Field, create_model


def _value_field(description: str, **kwargs):
    return Field(default=None, description=description, **kwargs)


def _method_field(field_name: str):
    return Field(
        default=None,
        description=f"Short note describing how `{field_name}` was extracted or calculated.",
    )


def _evidence_field(field_name: str):
    return Field(
        default=None,
        description=f"Direct supporting quote or excerpt for `{field_name}` from the report.",
    )


def _confidence_field(field_name: str):
    return Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=f"Confidence score for `{field_name}` as a fraction from 0 to 1.",
    )


FOOD_VOLUME_DESCRIPTIONS = {
    "kg_received_total": "Total kilograms of food received by the foodbank during the reporting year.",
    "kg_via_national_dc": "Kilograms of food received via the national or regional distributiecentrum (DC/RDC).",
    "kg_direct": "Kilograms of food received directly from donors rather than via the DC.",
    "waste_pct": "Fraction from 0 to 1 of received food that was wasted or sent to disposal.",
    "parcels_distributed": "Total number of food parcels, food packages, or shopping moments distributed.",
    "avg_products_per_parcel": "Average number of products included per parcel or per household visit.",
    "pct_schijf_van_vijf": "Fraction from 0 to 1 of distributed food that falls within Schijf van Vijf or healthy food guidance.",
    "food_value_eur": "Estimated euro value of the food distributed or received.",
}

FOOD_CATEGORIES_DESCRIPTIONS = {
    "kg_produce": "Kilograms of produce, vegetables, fruit, and potatoes.",
    "kg_meat_fish": "Kilograms of meat and fish.",
    "kg_dairy_eggs": "Kilograms of dairy and eggs. Do not use liters unless the report explicitly converts to kilograms.",
    "kg_dry_goods": "Kilograms of dry goods or pantry goods such as pasta, rice, canned goods, and shelf-stable groceries.",
    "kg_bread_bakery": "Kilograms of bread and bakery products.",
    "kg_prepared": "Kilograms of prepared foods or ready meals.",
}

PEOPLE_SERVED_DESCRIPTIONS = {
    "households_weekly": "Average or current weekly number of households served.",
    "individuals_total": "Total number of individual people served.",
    "children_count": "Number of children under 18 served.",
    "pct_under_18": "Fraction from 0 to 1 of beneficiaries who are under 18.",
    "pct_single_adults": "Fraction from 0 to 1 of beneficiary households that are single adults.",
    "pct_single_parent": "Fraction from 0 to 1 of beneficiary households that are single-parent households.",
    "pct_families": "Fraction from 0 to 1 of beneficiary households that are families.",
    "pct_couples": "Fraction from 0 to 1 of beneficiary households that are couples.",
}

OPERATIONS_DESCRIPTIONS = {
    "volunteers_count": "Number of volunteers active at the foodbank.",
    "distribution_locations": "Number of distribution locations, stores, or issue points.",
    "satellite_banks_served": "Number of satellite foodbanks or partner foodbanks served by this bank or RDC.",
    "annual_budget_eur": "Annual budget in euros.",
    "total_expenditure_eur": "Total annual expenditure or costs in euros.",
}

DONATIONS_DESCRIPTIONS = {
    "food_supermarket_kg": "Kilograms of food donated by supermarkets.",
    "food_company_kg": "Kilograms of food donated by companies, suppliers, or producers.",
    "food_dc_kg": "Kilograms of food received via the national or regional distributiecentrum (DC/RDC).",
    "money_individuals_eur": "Euro donations from individuals or private donors.",
    "money_companies_eur": "Euro donations from companies or businesses.",
    "money_orgs_eur": "Euro donations from non-profit organisations, foundations, churches, or associations.",
    "money_government_eur": "Euro donations or subsidies from municipalities, government, or public bodies.",
}


class FoodVolumeExtraction(BaseModel):
    kg_received_total: float | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["kg_received_total"])
    kg_received_total_method: str | None = _method_field("kg_received_total")
    kg_received_total_evidence: str | None = _evidence_field("kg_received_total")
    kg_received_total_confidence: float | None = _confidence_field("kg_received_total")
    kg_via_national_dc: float | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["kg_via_national_dc"])
    kg_via_national_dc_method: str | None = _method_field("kg_via_national_dc")
    kg_via_national_dc_evidence: str | None = _evidence_field("kg_via_national_dc")
    kg_via_national_dc_confidence: float | None = _confidence_field("kg_via_national_dc")
    kg_direct: float | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["kg_direct"])
    kg_direct_method: str | None = _method_field("kg_direct")
    kg_direct_evidence: str | None = _evidence_field("kg_direct")
    kg_direct_confidence: float | None = _confidence_field("kg_direct")
    waste_pct: float | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["waste_pct"], ge=0.0, le=1.0)
    waste_pct_method: str | None = _method_field("waste_pct")
    waste_pct_evidence: str | None = _evidence_field("waste_pct")
    waste_pct_confidence: float | None = _confidence_field("waste_pct")
    parcels_distributed: int | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["parcels_distributed"])
    parcels_distributed_method: str | None = _method_field("parcels_distributed")
    parcels_distributed_evidence: str | None = _evidence_field("parcels_distributed")
    parcels_distributed_confidence: float | None = _confidence_field("parcels_distributed")
    avg_products_per_parcel: float | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["avg_products_per_parcel"])
    avg_products_per_parcel_method: str | None = _method_field("avg_products_per_parcel")
    avg_products_per_parcel_evidence: str | None = _evidence_field("avg_products_per_parcel")
    avg_products_per_parcel_confidence: float | None = _confidence_field("avg_products_per_parcel")
    pct_schijf_van_vijf: float | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["pct_schijf_van_vijf"], ge=0.0, le=1.0)
    pct_schijf_van_vijf_method: str | None = _method_field("pct_schijf_van_vijf")
    pct_schijf_van_vijf_evidence: str | None = _evidence_field("pct_schijf_van_vijf")
    pct_schijf_van_vijf_confidence: float | None = _confidence_field("pct_schijf_van_vijf")
    food_value_eur: float | None = _value_field(FOOD_VOLUME_DESCRIPTIONS["food_value_eur"])
    food_value_eur_method: str | None = _method_field("food_value_eur")
    food_value_eur_evidence: str | None = _evidence_field("food_value_eur")
    food_value_eur_confidence: float | None = _confidence_field("food_value_eur")


class FoodCategoriesExtraction(BaseModel):
    kg_produce: float | None = _value_field(FOOD_CATEGORIES_DESCRIPTIONS["kg_produce"])
    kg_produce_method: str | None = _method_field("kg_produce")
    kg_produce_evidence: str | None = _evidence_field("kg_produce")
    kg_produce_confidence: float | None = _confidence_field("kg_produce")
    kg_meat_fish: float | None = _value_field(FOOD_CATEGORIES_DESCRIPTIONS["kg_meat_fish"])
    kg_meat_fish_method: str | None = _method_field("kg_meat_fish")
    kg_meat_fish_evidence: str | None = _evidence_field("kg_meat_fish")
    kg_meat_fish_confidence: float | None = _confidence_field("kg_meat_fish")
    kg_dairy_eggs: float | None = _value_field(FOOD_CATEGORIES_DESCRIPTIONS["kg_dairy_eggs"])
    kg_dairy_eggs_method: str | None = _method_field("kg_dairy_eggs")
    kg_dairy_eggs_evidence: str | None = _evidence_field("kg_dairy_eggs")
    kg_dairy_eggs_confidence: float | None = _confidence_field("kg_dairy_eggs")
    kg_dry_goods: float | None = _value_field(FOOD_CATEGORIES_DESCRIPTIONS["kg_dry_goods"])
    kg_dry_goods_method: str | None = _method_field("kg_dry_goods")
    kg_dry_goods_evidence: str | None = _evidence_field("kg_dry_goods")
    kg_dry_goods_confidence: float | None = _confidence_field("kg_dry_goods")
    kg_bread_bakery: float | None = _value_field(FOOD_CATEGORIES_DESCRIPTIONS["kg_bread_bakery"])
    kg_bread_bakery_method: str | None = _method_field("kg_bread_bakery")
    kg_bread_bakery_evidence: str | None = _evidence_field("kg_bread_bakery")
    kg_bread_bakery_confidence: float | None = _confidence_field("kg_bread_bakery")
    kg_prepared: float | None = _value_field(FOOD_CATEGORIES_DESCRIPTIONS["kg_prepared"])
    kg_prepared_method: str | None = _method_field("kg_prepared")
    kg_prepared_evidence: str | None = _evidence_field("kg_prepared")
    kg_prepared_confidence: float | None = _confidence_field("kg_prepared")


class PeopleServedExtraction(BaseModel):
    households_weekly: int | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["households_weekly"])
    households_weekly_method: str | None = _method_field("households_weekly")
    households_weekly_evidence: str | None = _evidence_field("households_weekly")
    households_weekly_confidence: float | None = _confidence_field("households_weekly")
    individuals_total: int | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["individuals_total"])
    individuals_total_method: str | None = _method_field("individuals_total")
    individuals_total_evidence: str | None = _evidence_field("individuals_total")
    individuals_total_confidence: float | None = _confidence_field("individuals_total")
    children_count: int | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["children_count"])
    children_count_method: str | None = _method_field("children_count")
    children_count_evidence: str | None = _evidence_field("children_count")
    children_count_confidence: float | None = _confidence_field("children_count")
    pct_under_18: float | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["pct_under_18"], ge=0.0, le=1.0)
    pct_under_18_method: str | None = _method_field("pct_under_18")
    pct_under_18_evidence: str | None = _evidence_field("pct_under_18")
    pct_under_18_confidence: float | None = _confidence_field("pct_under_18")
    pct_single_adults: float | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["pct_single_adults"], ge=0.0, le=1.0)
    pct_single_adults_method: str | None = _method_field("pct_single_adults")
    pct_single_adults_evidence: str | None = _evidence_field("pct_single_adults")
    pct_single_adults_confidence: float | None = _confidence_field("pct_single_adults")
    pct_single_parent: float | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["pct_single_parent"], ge=0.0, le=1.0)
    pct_single_parent_method: str | None = _method_field("pct_single_parent")
    pct_single_parent_evidence: str | None = _evidence_field("pct_single_parent")
    pct_single_parent_confidence: float | None = _confidence_field("pct_single_parent")
    pct_families: float | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["pct_families"], ge=0.0, le=1.0)
    pct_families_method: str | None = _method_field("pct_families")
    pct_families_evidence: str | None = _evidence_field("pct_families")
    pct_families_confidence: float | None = _confidence_field("pct_families")
    pct_couples: float | None = _value_field(PEOPLE_SERVED_DESCRIPTIONS["pct_couples"], ge=0.0, le=1.0)
    pct_couples_method: str | None = _method_field("pct_couples")
    pct_couples_evidence: str | None = _evidence_field("pct_couples")
    pct_couples_confidence: float | None = _confidence_field("pct_couples")


class OperationsExtraction(BaseModel):
    volunteers_count: int | None = _value_field(OPERATIONS_DESCRIPTIONS["volunteers_count"])
    volunteers_count_method: str | None = _method_field("volunteers_count")
    volunteers_count_evidence: str | None = _evidence_field("volunteers_count")
    volunteers_count_confidence: float | None = _confidence_field("volunteers_count")
    distribution_locations: int | None = _value_field(OPERATIONS_DESCRIPTIONS["distribution_locations"])
    distribution_locations_method: str | None = _method_field("distribution_locations")
    distribution_locations_evidence: str | None = _evidence_field("distribution_locations")
    distribution_locations_confidence: float | None = _confidence_field("distribution_locations")
    satellite_banks_served: int | None = _value_field(OPERATIONS_DESCRIPTIONS["satellite_banks_served"])
    satellite_banks_served_method: str | None = _method_field("satellite_banks_served")
    satellite_banks_served_evidence: str | None = _evidence_field("satellite_banks_served")
    satellite_banks_served_confidence: float | None = _confidence_field("satellite_banks_served")
    annual_budget_eur: float | None = _value_field(OPERATIONS_DESCRIPTIONS["annual_budget_eur"])
    annual_budget_eur_method: str | None = _method_field("annual_budget_eur")
    annual_budget_eur_evidence: str | None = _evidence_field("annual_budget_eur")
    annual_budget_eur_confidence: float | None = _confidence_field("annual_budget_eur")
    total_expenditure_eur: float | None = _value_field(OPERATIONS_DESCRIPTIONS["total_expenditure_eur"])
    total_expenditure_eur_method: str | None = _method_field("total_expenditure_eur")
    total_expenditure_eur_evidence: str | None = _evidence_field("total_expenditure_eur")
    total_expenditure_eur_confidence: float | None = _confidence_field("total_expenditure_eur")


class DonationsExtraction(BaseModel):
    food_supermarket_kg: float | None = _value_field(DONATIONS_DESCRIPTIONS["food_supermarket_kg"])
    food_supermarket_kg_method: str | None = _method_field("food_supermarket_kg")
    food_supermarket_kg_evidence: str | None = _evidence_field("food_supermarket_kg")
    food_supermarket_kg_confidence: float | None = _confidence_field("food_supermarket_kg")
    food_company_kg: float | None = _value_field(DONATIONS_DESCRIPTIONS["food_company_kg"])
    food_company_kg_method: str | None = _method_field("food_company_kg")
    food_company_kg_evidence: str | None = _evidence_field("food_company_kg")
    food_company_kg_confidence: float | None = _confidence_field("food_company_kg")
    food_dc_kg: float | None = _value_field(DONATIONS_DESCRIPTIONS["food_dc_kg"])
    food_dc_kg_method: str | None = _method_field("food_dc_kg")
    food_dc_kg_evidence: str | None = _evidence_field("food_dc_kg")
    food_dc_kg_confidence: float | None = _confidence_field("food_dc_kg")
    money_individuals_eur: float | None = _value_field(DONATIONS_DESCRIPTIONS["money_individuals_eur"])
    money_individuals_eur_method: str | None = _method_field("money_individuals_eur")
    money_individuals_eur_evidence: str | None = _evidence_field("money_individuals_eur")
    money_individuals_eur_confidence: float | None = _confidence_field("money_individuals_eur")
    money_companies_eur: float | None = _value_field(DONATIONS_DESCRIPTIONS["money_companies_eur"])
    money_companies_eur_method: str | None = _method_field("money_companies_eur")
    money_companies_eur_evidence: str | None = _evidence_field("money_companies_eur")
    money_companies_eur_confidence: float | None = _confidence_field("money_companies_eur")
    money_orgs_eur: float | None = _value_field(DONATIONS_DESCRIPTIONS["money_orgs_eur"])
    money_orgs_eur_method: str | None = _method_field("money_orgs_eur")
    money_orgs_eur_evidence: str | None = _evidence_field("money_orgs_eur")
    money_orgs_eur_confidence: float | None = _confidence_field("money_orgs_eur")
    money_government_eur: float | None = _value_field(DONATIONS_DESCRIPTIONS["money_government_eur"])
    money_government_eur_method: str | None = _method_field("money_government_eur")
    money_government_eur_evidence: str | None = _evidence_field("money_government_eur")
    money_government_eur_confidence: float | None = _confidence_field("money_government_eur")


class ExtractionResult(BaseModel):
    food_volume: FoodVolumeExtraction
    food_categories: FoodCategoriesExtraction
    people_served: PeopleServedExtraction
    operations: OperationsExtraction
    donations: DonationsExtraction


_BASE_INSTRUCTIONS = """You are a data extraction specialist for Dutch foodbank annual reports.

<rules>
1. Your output must be valid JSON conforming to the provided schema.
2. Extract ONLY values explicitly stated in the document — never infer, calculate, or estimate.
3. Return null for any field not found in the document.
4. ALL percentage and fraction fields must be expressed as decimals between 0 and 1:
   - 0.6% → 0.006
   - 37% → 0.37
   - 100% → 1.0
5. For every extracted value, populate the three companion fields:
   - _method: a short note on how the value was located (e.g. "direct statement on p.10")
   - _evidence: the exact Dutch quote or excerpt that contains the value
   - _confidence: your certainty as a decimal 0–1 (1.0 = unambiguous direct statement)
6. All primary value fields must be a single scalar number, never a range string, list, or prose.
   - If the report gives both an exact value and a range, use the exact value.
   - If the report only gives a range such as "160-170", return the lower bound as the scalar value
     and mention the original range in _method and _evidence with lower confidence.
7. If the same metric appears with conflicting figures, use the most specific one and note
   the discrepancy in _method.
8. The document is in Dutch. Dutch search terms are provided in parentheses to help locate values.
</rules>

<citation_examples>
kg_received_total = 507496.0
kg_received_total_method = "direct statement p.10"
kg_received_total_evidence = "Totaal ontvangen voedsel: 507.496 kilo"
kg_received_total_confidence = 1.0

waste_pct = 0.006
waste_pct_method = "percentage converted to fraction, p.12"
waste_pct_evidence = "Naar de stort gegaan: 0,6% van het ontvangen voedsel"
waste_pct_confidence = 0.95

households_weekly = 1240
households_weekly_method = "direct statement p.5"
households_weekly_evidence = "Wekelijks ontvangen 1.240 huishoudens een voedselpakket"
households_weekly_confidence = 1.0
</citation_examples>"""

SECTION_PROMPTS: dict[str, str] = {
    "extract_food_volume": f"""{_BASE_INSTRUCTIONS}

<task>
Extract food weight and volume metrics from the annual report.

Fields to extract:
- kg_received_total: Total kilograms of food received (totaal ontvangen voedsel, kilo ontvangen)
- kg_via_national_dc: Kilograms received via the national distribution center (distributiecentrum, landelijk DC, RDC)
- kg_direct: Kilograms from direct local donations (directe donaties, lokaal ingezameld)
- waste_pct: Fraction of food disposed as waste (naar de stort, voedselverspilling) — express as 0–1 decimal
- parcels_distributed: Total food parcels or packages distributed (pakketten, manden, voedselpakketten)
- avg_products_per_parcel: Average number of products per parcel (producten per pakket)
- pct_schijf_van_vijf: Fraction of food meeting the Schijf van Vijf healthy eating standard — express as 0–1 decimal
- food_value_eur: Total monetary value of food received in euros (waarde voedsel, euro)
</task>""",

    "extract_food_categories": f"""{_BASE_INSTRUCTIONS}

<task>
Extract food donations broken down by category, all in kilograms.

Fields to extract:
- kg_produce: Kilograms of vegetables, fruit, and potatoes (groente, fruit, aardappelen)
- kg_meat_fish: Kilograms of meat and fish (vlees, vis)
- kg_dairy_eggs: Kilograms of dairy products and eggs (zuivel, eieren, melk, kaas) — convert liters to kg only if the report explicitly does so
- kg_dry_goods: Kilograms of dry pantry staples (droge kruidenierswaren, houdbaar, pasta, rijst)
- kg_bread_bakery: Kilograms of bread and bakery items (brood, banket, gebak)
- kg_prepared: Kilograms of prepared or ready meals (bereide maaltijden, kant-en-klaar)

IMPORTANT: Only extract values that represent the foodbank's own total intake per category across all sources.
Do NOT extract figures attributed to a single named external supplier or partner (e.g. "Groente & Fruitbrigade leverde 50.000 kg" is a supplier subtotal, not the bank's total produce intake).
If the report only mentions a category figure in the context of one named partner, set that field to null.
</task>""",

    "extract_people_served": f"""{_BASE_INSTRUCTIONS}

<task>
Extract beneficiary counts and demographic breakdowns from the annual report.

Fields to extract:
- households_weekly: Number of households served per week (huishoudens per week, gezinnen wekelijks)
- individuals_total: Total number of individuals served (personen, mensen, cliënten)
- children_count: Number of children served (kinderen, jeugd, minderjarigen)
- pct_under_18: Fraction of recipients aged under 18 (onder 18 jaar, kinderen percentage) — express as 0–1 decimal
- pct_single_adults: Fraction who are single adults (alleenstaanden) — express as 0–1 decimal
- pct_single_parent: Fraction who are single-parent households (eenoudergezinnen) — express as 0–1 decimal
- pct_families: Fraction who are two-parent families with children (gezinnen met kinderen) — express as 0–1 decimal
- pct_couples: Fraction who are couples without children (stellen zonder kinderen, echtparen) — express as 0–1 decimal
</task>""",

    "extract_operations": f"""{_BASE_INSTRUCTIONS}

<task>
Extract operational and financial metrics from the annual report.

Fields to extract:
- volunteers_count: Number of active volunteers (vrijwilligers, medewerkers)
- distribution_locations: Number of food distribution locations or issue points (locaties, uitgiftepunten, vestigingen)
- satellite_banks_served: Number of affiliated satellite foodbanks served (aangesloten voedselbanken, satellieten)
- annual_budget_eur: Annual budget in euros (begroting, jaarbudget)
- total_expenditure_eur: Total costs or expenditure in euros (totale uitgaven, kosten, lasten)
</task>""",

    "extract_donations": f"""{_BASE_INSTRUCTIONS}

<task>
Extract donation data — both food quantities in kilograms and monetary amounts in euros.

Fields to extract:
- food_supermarket_kg: Food donated by supermarkets in kg (supermarkten, retail)
- food_company_kg: Food donated by food companies or suppliers in kg (bedrijven, leveranciers, fabrikanten)
- food_dc_kg: Food received via the national distribution center in kg (distributiecentrum, DC, landelijk)
- money_individuals_eur: Monetary donations from private individuals in euros (particulieren, donateurs)
- money_companies_eur: Monetary donations from companies in euros (bedrijven, sponsoren)
- money_orgs_eur: Monetary donations from non-profit organisations in euros (organisaties, fondsen, verenigingen)
- money_government_eur: Monetary grants from government or municipality in euros (gemeente, overheid, subsidie)
</task>""",
}

TOOL_SCHEMA_MAP: dict[str, type] = {
    "extract_food_volume": FoodVolumeExtraction,
    "extract_food_categories": FoodCategoriesExtraction,
    "extract_people_served": PeopleServedExtraction,
    "extract_operations": OperationsExtraction,
    "extract_donations": DonationsExtraction,
}


def _build_parse_model(name: str, schema_cls: type[BaseModel]) -> type[BaseModel]:
    fields: dict[str, tuple[object, Field]] = {}
    for field_name, field_info in schema_cls.model_fields.items():
        fields[field_name] = (
            str,
            Field(default="", description=field_info.description),
        )
    return create_model(name, __config__=ConfigDict(extra="forbid"), **fields)


FoodVolumeParse = _build_parse_model("FoodVolumeParse", FoodVolumeExtraction)
FoodCategoriesParse = _build_parse_model("FoodCategoriesParse", FoodCategoriesExtraction)
PeopleServedParse = _build_parse_model("PeopleServedParse", PeopleServedExtraction)
OperationsParse = _build_parse_model("OperationsParse", OperationsExtraction)
DonationsParse = _build_parse_model("DonationsParse", DonationsExtraction)

PARSE_SCHEMA_MAP: dict[str, type[BaseModel]] = {
    "extract_food_volume": FoodVolumeParse,
    "extract_food_categories": FoodCategoriesParse,
    "extract_people_served": PeopleServedParse,
    "extract_operations": OperationsParse,
    "extract_donations": DonationsParse,
}
