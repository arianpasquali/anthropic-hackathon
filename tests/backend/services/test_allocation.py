import uuid
from datetime import date
from sqlmodel import Session

from src.backend.models.allocation import Allocation
from src.backend.models.enums import (
    ImpactProfileEnum, RegionEnum, RoleEnum, SourceEnum,
)
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import PeopleServed
from src.backend.models.user import User
from src.backend.services.allocation import compute_allocations


def _make_foodbank_with_data(session, name, co2e_kg, households):
    fb = Foodbank(name=name, city="Test", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    report = AnnualReport(
        foodbank_id=fb.id, year=2024,
        period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
        raw_file_path="test.txt", ingestion_model="test",
    )
    session.add(report)
    session.commit()
    frame = FrameResult(
        report_id=report.id,
        co2e_total_kg=co2e_kg,
        co2e_produce_kg=co2e_kg * 0.4, co2e_meat_fish_kg=co2e_kg * 0.2,
        co2e_dairy_eggs_kg=co2e_kg * 0.15, co2e_dry_goods_kg=co2e_kg * 0.15,
        co2e_bread_kg=co2e_kg * 0.1,
        emission_factor_source="test", methodology_version="FRAME-NL-v1.0",
    )
    session.add(frame)
    people = PeopleServed(
        report_id=report.id,
        households_weekly=households,
        households_weekly_source=SourceEnum.extracted,
        households_weekly_method="test",
    )
    session.add(people)
    session.commit()
    return fb


def _make_subscription(session, profile, top_n=3):
    user = User(email=f"corp_{uuid.uuid4().hex[:6]}@test.com", hashed_password="x", role=RoleEnum.corporate)
    session.add(user)
    session.commit()
    pkg = Package(name="Test Package", region=RegionEnum.west, price_eur=10000.0,
                  co2e_claim_kg=200000.0, impact_profile=profile, top_n=top_n)
    session.add(pkg)
    session.commit()
    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=10000.0)
    session.add(sub)
    session.commit()
    return sub


def test_co2_focus_ranks_by_co2e(session: Session):
    _make_foodbank_with_data(session, "High CO2", co2e_kg=1000.0, households=100)
    _make_foodbank_with_data(session, "Low CO2", co2e_kg=200.0, households=500)
    _make_foodbank_with_data(session, "Mid CO2", co2e_kg=600.0, households=300)
    sub = _make_subscription(session, ImpactProfileEnum.co2_focus, top_n=2)

    allocations = compute_allocations(session, sub.id)
    assert len(allocations) == 2
    assert abs(sum(a.weight_pct for a in allocations) - 1.0) < 1e-6
    assert allocations[0].weight_pct > allocations[1].weight_pct


def test_social_focus_ranks_by_households(session: Session):
    _make_foodbank_with_data(session, "Many Families", co2e_kg=100.0, households=2000)
    _make_foodbank_with_data(session, "Few Families", co2e_kg=900.0, households=200)
    sub = _make_subscription(session, ImpactProfileEnum.social_focus, top_n=2)

    allocations = compute_allocations(session, sub.id)
    assert len(allocations) == 2
    assert abs(sum(a.weight_pct for a in allocations) - 1.0) < 1e-6
    assert allocations[0].weight_pct > allocations[1].weight_pct


def test_top_n_limits_allocation_count(session: Session):
    for i in range(5):
        _make_foodbank_with_data(session, f"Bank {i}", co2e_kg=float(i+1)*100, households=i+1)
    sub = _make_subscription(session, ImpactProfileEnum.co2_focus, top_n=3)

    allocations = compute_allocations(session, sub.id)
    assert len(allocations) == 3


def test_allocations_written_to_db(session: Session):
    _make_foodbank_with_data(session, "A", co2e_kg=500.0, households=100)
    _make_foodbank_with_data(session, "B", co2e_kg=300.0, households=200)
    sub = _make_subscription(session, ImpactProfileEnum.co2_focus, top_n=2)

    allocations = compute_allocations(session, sub.id, commit=True)
    assert all(a.id is not None for a in allocations)
