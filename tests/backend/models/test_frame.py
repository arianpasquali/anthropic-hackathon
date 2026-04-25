import uuid
from datetime import date, datetime, timezone
from sqlmodel import Session
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.enums import RegionEnum


def test_create_frame_result(session: Session):
    fb = Foodbank(name="Voedselbank Breda", city="Breda", region=RegionEnum.zuid, is_regional_dc=False)
    session.add(fb)
    session.commit()
    report = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="df/data/breda-2024-fin.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()

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
