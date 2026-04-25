import uuid
from datetime import date
from sqlmodel import Session, select
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.measurements import (
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
)
from src.backend.models.enums import RegionEnum, SourceEnum, CounterfactualEnum


def _make_report(session: Session) -> AnnualReport:
    fb = Foodbank(name="Test Bank", city="Test", region=RegionEnum.noord, is_regional_dc=False)
    session.add(fb)
    session.commit()
    report = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="test.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()
    return report


def test_food_volume_with_provenance(session: Session):
    report = _make_report(session)
    fv = FoodVolume(
        report_id=report.id,
        kg_received_total=507496.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="extracted from PDF p.10 'Ontvangen voedsel'",
        waste_pct=0.6,
        waste_pct_source=SourceEnum.extracted,
        waste_pct_method="extracted from PDF p.10 '0,6 procent naar de stort'",
    )
    session.add(fv)
    session.commit()
    session.refresh(fv)
    assert fv.kg_received_total == 507496.0
    assert fv.kg_received_total_source == SourceEnum.extracted
    assert fv.waste_pct == 0.6


def test_food_volume_nullable_fields(session: Session):
    report = _make_report(session)
    fv = FoodVolume(report_id=report.id)
    session.add(fv)
    session.commit()
    session.refresh(fv)
    assert fv.kg_received_total is None
    assert fv.kg_received_total_source is None


def test_food_categories_inferred(session: Session):
    report = _make_report(session)
    fc = FoodCategories(
        report_id=report.id,
        kg_produce=185036.0,
        kg_produce_source=SourceEnum.extracted,
        kg_produce_method="extracted from PDF p.11 category table",
        kg_dairy_eggs=47819.0,
        kg_dairy_eggs_source=SourceEnum.extracted,
        kg_dairy_eggs_method="extracted from PDF p.11 category table",
        kg_meat_fish=30437.0,
        kg_meat_fish_source=SourceEnum.extracted,
        kg_meat_fish_method="extracted from PDF p.11 category table",
        kg_dry_goods=None,
        kg_dry_goods_source=SourceEnum.inferred_national_avg,
        kg_dry_goods_method="NL avg 18% applied to total 507496kg",
    )
    session.add(fc)
    session.commit()
    session.refresh(fc)
    assert fc.kg_produce == 185036.0
    assert fc.kg_dry_goods is None
    assert fc.kg_dry_goods_source == SourceEnum.inferred_national_avg


def test_people_served(session: Session):
    report = _make_report(session)
    ps = PeopleServed(
        report_id=report.id,
        households_weekly=1600,
        households_weekly_source=SourceEnum.extracted,
        households_weekly_method="extracted from PDF p.2",
        pct_under_18=0.37,
        pct_under_18_source=SourceEnum.inferred_national_avg,
        pct_under_18_method="NL national average from Feiten & Cijfers 2024",
    )
    session.add(ps)
    session.commit()
    session.refresh(ps)
    assert ps.households_weekly == 1600
    assert ps.pct_under_18 == 0.37


def test_operations_counterfactual(session: Session):
    report = _make_report(session)
    ops = Operations(
        report_id=report.id,
        volunteers_count=108,
        volunteers_count_source=SourceEnum.extracted,
        volunteers_count_method="extracted from PDF p.4",
        counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
    )
    session.add(ops)
    session.commit()
    session.refresh(ops)
    assert ops.counterfactual_route == CounterfactualEnum.incineration_energy_recovery


def test_donations(session: Session):
    report = _make_report(session)
    d = Donations(
        report_id=report.id,
        money_individuals_eur=45000.0,
        money_individuals_eur_source=SourceEnum.extracted,
        money_individuals_eur_method="extracted from financial section",
        money_companies_eur=62186.0,
        money_companies_eur_source=SourceEnum.extracted,
        money_companies_eur_method="extracted from financial section",
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    assert d.money_individuals_eur == 45000.0
