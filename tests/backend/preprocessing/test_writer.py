from datetime import date
from decimal import Decimal

import pytest
from sqlmodel import Session, select

from src.backend.models import (
    AnnualReport, Foodbank,
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
)
from src.backend.models.enums import RegionEnum, SourceEnum
from src.backend.preprocessing.schemas import (
    DonationsExtraction,
    ExtractionResult,
    FoodCategoriesExtraction,
    FoodVolumeExtraction,
    OperationsExtraction,
    PeopleServedExtraction,
)
from src.backend.preprocessing.writer import write_report


def _make_result(
    kg_total: float = 500000.0,
    households: int = 300,
) -> ExtractionResult:
    return ExtractionResult(
        food_volume=FoodVolumeExtraction(
            kg_received_total=kg_total,
            kg_received_total_method="p.10 'test'",
            waste_pct=0.006,
            waste_pct_method="p.10 '0.6%'",
        ),
        food_categories=FoodCategoriesExtraction(
            kg_produce=185000.0,
            kg_produce_method="p.11 'groente'",
        ),
        people_served=PeopleServedExtraction(
            households_weekly=households,
            households_weekly_method="p.8 'huishoudens'",
            pct_under_18=0.37,
            pct_under_18_method="national average",
        ),
        operations=OperationsExtraction(
            volunteers_count=108,
            volunteers_count_method="p.4 'vrijwilligers'",
        ),
        donations=DonationsExtraction(
            money_individuals_eur=45000.0,
            money_individuals_eur_method="p.19 financieel",
        ),
    )


def test_write_creates_foodbank_and_report(session: Session):
    result = _make_result()
    report = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="archive/df/data/breda-2024.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    assert report.id is not None
    assert report.year == 2024

    fb = session.exec(select(Foodbank).where(Foodbank.name == "Voedselbank Breda")).one()
    assert fb.city == "Breda"


def test_write_populates_food_volume(session: Session):
    result = _make_result(kg_total=507496.0)
    report = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="archive/df/data/breda-2024.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report.id)).one()
    assert fv.kg_received_total == 507496.0
    assert fv.kg_received_total_source == SourceEnum.extracted
    assert fv.kg_received_total_method == "p.10 'test'"
    assert fv.waste_pct == 0.006


def test_write_populates_people_served(session: Session):
    result = _make_result(households=335)
    report = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="archive/df/data/breda-2024.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    ps = session.exec(select(PeopleServed).where(PeopleServed.report_id == report.id)).one()
    assert ps.households_weekly == 335
    assert ps.households_weekly_source == SourceEnum.extracted


def test_write_skips_existing_by_default(session: Session):
    result = _make_result(kg_total=100.0)
    report1 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="first.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )

    # Second ingest — same bank + year, no --force
    report2 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="second.pdf",
        result=_make_result(kg_total=999.0),
        model="claude-haiku-4-5-20251001",
    )

    # Returns original report unchanged
    assert report2.id == report1.id
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report1.id)).one()
    assert fv.kg_received_total == 100.0  # not overwritten


def test_write_force_overwrites(session: Session):
    result = _make_result(kg_total=100.0)
    report1 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="first.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )

    report2 = write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="second.pdf",
        result=_make_result(kg_total=999.0),
        model="claude-haiku-4-5-20251001",
        force=True,
    )

    # New report row, fresh data
    assert report2.id != report1.id
    fv = session.exec(select(FoodVolume).where(FoodVolume.report_id == report2.id)).one()
    assert fv.kg_received_total == 999.0


def test_get_or_create_foodbank_reuses_existing(session: Session):
    result = _make_result()
    write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2023,
        pdf_path="a.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    write_report(
        session=session,
        foodbank_name="Voedselbank Breda",
        city="Breda",
        region=RegionEnum.zuid,
        year=2024,
        pdf_path="b.pdf",
        result=result,
        model="claude-haiku-4-5-20251001",
    )
    banks = session.exec(select(Foodbank).where(Foodbank.name == "Voedselbank Breda")).all()
    assert len(banks) == 1  # same bank reused
