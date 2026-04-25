from datetime import date

import pytest
from sqlmodel import Session

from src.backend.models.enums import RegionEnum, SourceEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.measurements import FoodCategories, FoodVolume
from src.backend.services.frame import _DM, _NL_EF_KG_PER_KG_DM, compute_frame


def _make_report(session: Session) -> AnnualReport:
    fb = Foodbank(name="Test", city="Test", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    r = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="t.txt",
        ingestion_model="test",
    )
    session.add(r)
    session.commit()
    return r


def test_compute_frame_with_categories_no_waste(session: Session):
    """100 kg produce only, no waste → BE = AE, leakage = 0."""
    report = _make_report(session)
    fc = FoodCategories(
        report_id=report.id,
        kg_produce=100.0,
        kg_produce_source=SourceEnum.extracted,
        kg_produce_method="test",
        kg_meat_fish=0.0,
        kg_meat_fish_source=SourceEnum.extracted,
        kg_meat_fish_method="test",
        kg_dairy_eggs=0.0,
        kg_dairy_eggs_source=SourceEnum.extracted,
        kg_dairy_eggs_method="test",
        kg_dry_goods=0.0,
        kg_dry_goods_source=SourceEnum.extracted,
        kg_dry_goods_method="test",
        kg_bread_bakery=0.0,
        kg_bread_bakery_source=SourceEnum.extracted,
        kg_bread_bakery_method="test",
    )
    session.add(fc)
    session.commit()

    result = compute_frame(session, report)

    expected_be_produce = 100.0 * _DM["produce"] * _NL_EF_KG_PER_KG_DM
    assert abs(result.co2e_produce_kg - expected_be_produce) < 0.01
    assert result.leakage_co2e_kg == pytest.approx(0.0)
    assert result.avoided_co2e_kg == pytest.approx(result.baseline_co2e_kg)
    assert result.co2e_total_kg == pytest.approx(result.avoided_co2e_kg)


def test_compute_frame_leakage_reduces_avoided(session: Session):
    """10% waste reduces avoided vs baseline."""
    report = _make_report(session)
    fv = FoodVolume(
        report_id=report.id,
        kg_received_total=1000.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="test",
        waste_pct=0.10,
        waste_pct_source=SourceEnum.extracted,
        waste_pct_method="test",
    )
    session.add(fv)
    session.commit()

    result = compute_frame(session, report)

    assert result.leakage_co2e_kg > 0
    assert result.avoided_co2e_kg < result.baseline_co2e_kg
    assert result.co2e_total_kg == pytest.approx(result.avoided_co2e_kg)


def test_compute_frame_no_waste_data_uses_zero_leakage(session: Session):
    """No FoodVolume → leakage defaults to 0."""
    report = _make_report(session)
    fc = FoodCategories(
        report_id=report.id,
        kg_produce=500.0,
        kg_produce_source=SourceEnum.extracted,
        kg_produce_method="test",
        kg_meat_fish=200.0,
        kg_meat_fish_source=SourceEnum.extracted,
        kg_meat_fish_method="test",
        kg_dairy_eggs=100.0,
        kg_dairy_eggs_source=SourceEnum.extracted,
        kg_dairy_eggs_method="test",
        kg_dry_goods=100.0,
        kg_dry_goods_source=SourceEnum.extracted,
        kg_dry_goods_method="test",
        kg_bread_bakery=100.0,
        kg_bread_bakery_source=SourceEnum.extracted,
        kg_bread_bakery_method="test",
    )
    session.add(fc)
    session.commit()

    result = compute_frame(session, report)
    assert result.leakage_co2e_kg == pytest.approx(0.0)
    assert result.avoided_co2e_kg == pytest.approx(result.baseline_co2e_kg)


def test_compute_frame_fallback_to_total_kg(session: Session):
    """No FoodCategories → apply NL split to FoodVolume.kg_received_total."""
    report = _make_report(session)
    fv = FoodVolume(
        report_id=report.id,
        kg_received_total=1000.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="test",
    )
    session.add(fv)
    session.commit()

    result = compute_frame(session, report)
    assert result.co2e_total_kg > 0
    assert result.baseline_co2e_kg > 0
    assert result.methodology_version == "FRAME-NL-v2.0"


def test_compute_frame_raises_with_no_data(session: Session):
    """No FoodCategories and no FoodVolume → ValueError."""
    report = _make_report(session)
    with pytest.raises(ValueError, match="No weight data"):
        compute_frame(session, report)


def test_nl_ef_is_plausible():
    """NL weighted EF should be between incineration (0.131) and landfill-no-flare (6.528)."""
    assert 0.131 < _NL_EF_KG_PER_KG_DM < 6.528
    # With NL mostly incineration+composting, expect low-moderate EF
    assert _NL_EF_KG_PER_KG_DM < 1.0
