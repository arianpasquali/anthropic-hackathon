from src.backend.preprocessing.schemas import (
    FoodVolumeExtraction,
    FoodCategoriesExtraction,
    PeopleServedExtraction,
    OperationsExtraction,
    DonationsExtraction,
    ExtractionResult,
    SECTION_PROMPTS,
)


def test_food_volume_schema_fields():
    schema = FoodVolumeExtraction.model_json_schema()
    props = schema["properties"]
    assert "kg_received_total" in props
    assert "kg_received_total_method" in props
    assert "kg_received_total_evidence" in props
    assert "kg_received_total_confidence" in props
    assert "waste_pct" in props
    assert "waste_pct_method" in props
    assert "parcels_distributed" in props


def test_food_categories_schema_fields():
    schema = FoodCategoriesExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["kg_produce", "kg_meat_fish", "kg_dairy_eggs", "kg_dry_goods", "kg_bread_bakery", "kg_prepared"]:
        assert field in props
        assert f"{field}_method" in props
        assert f"{field}_evidence" in props
        assert f"{field}_confidence" in props


def test_people_served_schema_fields():
    schema = PeopleServedExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["households_weekly", "individuals_total", "children_count", "pct_under_18"]:
        assert field in props


def test_operations_schema_fields():
    schema = OperationsExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["volunteers_count", "distribution_locations", "annual_budget_eur", "total_expenditure_eur"]:
        assert field in props


def test_donations_schema_fields():
    schema = DonationsExtraction.model_json_schema()
    props = schema["properties"]
    for field in ["food_supermarket_kg", "food_company_kg", "money_individuals_eur", "money_companies_eur"]:
        assert field in props


def test_all_fields_optional():
    # All extraction schemas must instantiate with zero arguments
    FoodVolumeExtraction()
    FoodCategoriesExtraction()
    PeopleServedExtraction()
    OperationsExtraction()
    DonationsExtraction()


def test_extraction_result_holds_all_sections():
    result = ExtractionResult(
        food_volume=FoodVolumeExtraction(),
        food_categories=FoodCategoriesExtraction(),
        people_served=PeopleServedExtraction(),
        operations=OperationsExtraction(),
        donations=DonationsExtraction(),
    )
    assert result.food_volume is not None
    assert result.people_served is not None


def test_section_prompts_exist_for_all_tools():
    tool_names = [
        "extract_food_volume",
        "extract_food_categories",
        "extract_people_served",
        "extract_operations",
        "extract_donations",
    ]
    for name in tool_names:
        assert name in SECTION_PROMPTS
        assert len(SECTION_PROMPTS[name]) > 50
