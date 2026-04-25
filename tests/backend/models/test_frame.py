from datetime import datetime
from sqlmodel import Session

from src.backend.models.foodbank import AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.enums import CounterfactualEnum


def test_create_frame_result(session: Session, report: AnnualReport):
    result = FrameResult(
        report_id=report.id,
        co2e_total_kg=1268740.0,
        co2e_produce_kg=462590.0,
        co2e_meat_fish_kg=304370.0,
        co2e_dairy_eggs_kg=191276.0,
        co2e_dry_goods_kg=182698.0,
        co2e_bread_kg=127806.0,
        emission_factor_source="FAO Food Wastage Footprint 2013 + WRAP UK 2022",
        methodology_version="FRAME-NL-v1.0",
    )
    session.add(result)
    session.commit()
    session.refresh(result)

    assert result.id is not None
    assert result.co2e_total_kg == 1268740.0
    assert result.methodology_version == "FRAME-NL-v1.0"
    assert isinstance(result.computed_at, datetime)


def test_counterfactual_default(session: Session, report: AnnualReport):
    result = FrameResult(
        report_id=report.id,
        co2e_total_kg=100.0,
        co2e_produce_kg=100.0,
        co2e_meat_fish_kg=0.0,
        co2e_dairy_eggs_kg=0.0,
        co2e_dry_goods_kg=0.0,
        co2e_bread_kg=0.0,
        emission_factor_source="test",
        methodology_version="FRAME-NL-v1.0",
    )
    session.add(result)
    session.commit()
    session.refresh(result)
    assert result.counterfactual_route == CounterfactualEnum.incineration_energy_recovery


def test_counterfactual_explicit(session: Session, report: AnnualReport):
    result = FrameResult(
        report_id=report.id,
        co2e_total_kg=100.0,
        co2e_produce_kg=100.0,
        co2e_meat_fish_kg=0.0,
        co2e_dairy_eggs_kg=0.0,
        co2e_dry_goods_kg=0.0,
        co2e_bread_kg=0.0,
        counterfactual_route=CounterfactualEnum.landfill,
        emission_factor_source="test",
        methodology_version="FRAME-NL-v1.0",
    )
    session.add(result)
    session.commit()
    session.refresh(result)
    assert result.counterfactual_route == CounterfactualEnum.landfill
