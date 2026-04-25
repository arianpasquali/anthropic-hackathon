import pytest
from decimal import Decimal
from pydantic import ValidationError
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError

from src.backend.models.foodbank import AnnualReport
from src.backend.models.measurements import (
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
)
from src.backend.models.enums import SourceEnum


def test_food_volume_with_provenance(session: Session, report: AnnualReport):
    fv = FoodVolume(
        report_id=report.id,
        kg_received_total=507496.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="extracted from PDF p.10 'Ontvangen voedsel'",
        waste_pct=0.006,
        waste_pct_source=SourceEnum.extracted,
        waste_pct_method="extracted from PDF p.10 '0,6 procent naar de stort'",
    )
    session.add(fv)
    session.commit()
    session.refresh(fv)
    assert fv.kg_received_total == 507496.0
    assert fv.kg_received_total_source == SourceEnum.extracted
    assert fv.kg_received_total_method == "extracted from PDF p.10 'Ontvangen voedsel'"
    assert fv.waste_pct == 0.006


def test_food_volume_nullable_fields(session: Session, report: AnnualReport):
    fv = FoodVolume(report_id=report.id)
    session.add(fv)
    session.commit()
    session.refresh(fv)
    assert fv.kg_received_total is None
    assert fv.kg_received_total_source is None


def test_food_volume_unique_constraint(session: Session, report: AnnualReport):
    session.add(FoodVolume(report_id=report.id))
    session.commit()
    session.add(FoodVolume(report_id=report.id))
    with pytest.raises(IntegrityError):
        session.commit()


def test_food_volume_provenance_coupling_enforced(report: AnnualReport):
    # SQLModel table=True bypasses Pydantic __init__; use model_validate (the
    # path the ingestion pipeline takes when building from Claude's output).
    with pytest.raises(ValidationError, match="kg_received_total requires kg_received_total_source"):
        FoodVolume.model_validate({"report_id": str(report.id), "kg_received_total": 100.0})


def test_waste_pct_range_rejected(report: AnnualReport):
    with pytest.raises(ValidationError):
        FoodVolume.model_validate({
            "report_id": str(report.id),
            "waste_pct": 1.5,
            "waste_pct_source": "extracted",
        })
    with pytest.raises(ValidationError):
        FoodVolume.model_validate({
            "report_id": str(report.id),
            "waste_pct": -0.1,
            "waste_pct_source": "extracted",
        })


def test_food_categories_inferred(session: Session, report: AnnualReport):
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
        kg_dry_goods_source=SourceEnum.inferred_national_avg,
        kg_dry_goods_method="NL avg 18% applied to total 507496kg",
    )
    session.add(fc)
    session.commit()
    session.refresh(fc)
    assert fc.kg_produce == 185036.0
    assert fc.kg_dry_goods is None
    assert fc.kg_dry_goods_source == SourceEnum.inferred_national_avg
    assert fc.kg_dry_goods_method == "NL avg 18% applied to total 507496kg"


def test_people_served(session: Session, report: AnnualReport):
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
    assert ps.pct_under_18_method == "NL national average from Feiten & Cijfers 2024"


def test_pct_range_rejected(report: AnnualReport):
    with pytest.raises(ValidationError):
        PeopleServed.model_validate({
            "report_id": str(report.id),
            "pct_under_18": 1.5,
            "pct_under_18_source": "inferred_national_avg",
        })


def test_operations(session: Session, report: AnnualReport):
    ops = Operations(
        report_id=report.id,
        volunteers_count=108,
        volunteers_count_source=SourceEnum.extracted,
        volunteers_count_method="extracted from PDF p.4",
        annual_budget_eur=Decimal("150000.00"),
        annual_budget_eur_source=SourceEnum.extracted,
        annual_budget_eur_method="extracted from financial section",
    )
    session.add(ops)
    session.commit()
    session.refresh(ops)
    assert ops.volunteers_count == 108
    assert ops.annual_budget_eur == Decimal("150000.00")


def test_operations_has_no_counterfactual_route(report: AnnualReport):
    assert "counterfactual_route" not in Operations.model_fields, (
        "counterfactual_route belongs in FrameResult, not Operations"
    )


def test_donations(session: Session, report: AnnualReport):
    d = Donations(
        report_id=report.id,
        food_supermarket_kg=320000.0,
        food_supermarket_kg_source=SourceEnum.extracted,
        food_supermarket_kg_method="extracted from PDF p.8",
        food_company_kg=85000.0,
        food_company_kg_source=SourceEnum.extracted,
        food_company_kg_method="extracted from PDF p.8",
        food_dc_kg=102496.0,
        food_dc_kg_source=SourceEnum.extracted,
        food_dc_kg_method="extracted from PDF p.8",
        money_individuals_eur=Decimal("45000.00"),
        money_individuals_eur_source=SourceEnum.extracted,
        money_individuals_eur_method="extracted from financial section",
        money_companies_eur=Decimal("62186.00"),
        money_companies_eur_source=SourceEnum.extracted,
        money_companies_eur_method="extracted from financial section",
    )
    session.add(d)
    session.commit()
    session.refresh(d)
    assert d.food_supermarket_kg == 320000.0
    assert d.food_company_kg == 85000.0
    assert d.money_individuals_eur == Decimal("45000.00")
    assert d.money_companies_eur == Decimal("62186.00")
