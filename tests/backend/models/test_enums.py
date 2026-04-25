from src.backend.models.enums import (
    SourceEnum, RoleEnum, RegionEnum, StatusEnum,
    TemplateEnum, CounterfactualEnum,
)


def test_source_enum_values():
    assert SourceEnum.extracted == "extracted"
    assert SourceEnum.inferred_national_avg == "inferred_national_avg"
    assert SourceEnum.inferred_category_split == "inferred_category_split"
    assert SourceEnum.inferred_calculation == "inferred_calculation"
    assert SourceEnum.manual == "manual"


def test_role_enum_values():
    assert RoleEnum.corporate == "corporate"
    assert RoleEnum.foodbank_op == "foodbank_op"
    assert RoleEnum.admin == "admin"


def test_region_enum_values():
    expected = {"noord", "oost", "zuid", "west", "randstad"}
    assert {r.value for r in RegionEnum} == expected


def test_status_enum_values():
    assert StatusEnum.pending == "pending"
    assert StatusEnum.paid == "paid"
    assert StatusEnum.failed == "failed"
    assert StatusEnum.refunded == "refunded"


def test_counterfactual_enum_values():
    assert CounterfactualEnum.incineration_energy_recovery == "incineration_energy_recovery"
    assert CounterfactualEnum.landfill == "landfill"
    assert CounterfactualEnum.composting == "composting"


def test_template_enum_values():
    expected = {"gri", "csrd", "esrs_e1", "generic"}
    assert {t.value for t in TemplateEnum} == expected


def test_db_import():
    from src.backend.database import create_db_and_tables, get_session
    assert callable(create_db_and_tables)
    assert callable(get_session)
