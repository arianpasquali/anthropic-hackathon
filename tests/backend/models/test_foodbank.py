import uuid
from datetime import date
from sqlmodel import Session, select
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.enums import RegionEnum


def test_create_foodbank(session: Session):
    fb = Foodbank(
        name="Voedselbank Rotterdam",
        city="Rotterdam",
        region=RegionEnum.west,
        is_regional_dc=True,
    )
    session.add(fb)
    session.commit()
    session.refresh(fb)
    assert fb.id is not None
    assert fb.is_regional_dc is True


def test_create_annual_report(session: Session):
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
    session.refresh(report)
    assert report.id is not None
    assert report.foodbank_id == fb.id


def test_foodbank_annual_report_relationship(session: Session):
    fb = Foodbank(name="Voedselbank Amsterdam", city="Amsterdam", region=RegionEnum.randstad, is_regional_dc=True)
    session.add(fb)
    session.commit()

    for year in [2023, 2024]:
        session.add(AnnualReport(
            foodbank_id=fb.id,
            year=year,
            period_start=date(year, 1, 1),
            period_end=date(year, 12, 31),
            raw_file_path=f"df/data/amsterdam-{year}.txt",
            ingestion_model="claude-sonnet-4-6",
        ))
    session.commit()

    reports = session.exec(select(AnnualReport).where(AnnualReport.foodbank_id == fb.id)).all()
    assert len(reports) == 2
