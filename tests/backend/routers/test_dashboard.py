import uuid
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.enums import ImpactProfileEnum, RegionEnum, RoleEnum, SourceEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import PeopleServed
from src.backend.models.user import User
from src.backend.services.auth import COOKIE_NAME, hash_password, make_session_cookie


def _setup_with_paid_sub(client: TestClient):
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    user = User(email="dash@test.nl", hashed_password=hash_password("pass"), role=RoleEnum.corporate, org_name="DashCo")
    session.add(user)
    pkg = Package(name="Test Fund", region=RegionEnum.west, price_eur=10000.0,
                  co2e_claim_kg=200000.0, impact_profile=ImpactProfileEnum.co2_focus, top_n=3)
    session.add(pkg)
    session.commit()

    # Food bank with frame data
    fb = Foodbank(name="Test Bank", city="Rotterdam", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.flush()
    rep = AnnualReport(foodbank_id=fb.id, year=2024, period_start=date(2024,1,1),
                       period_end=date(2024,12,31), raw_file_path="test.txt", ingestion_model="test")
    session.add(rep)
    session.flush()
    session.add(FrameResult(report_id=rep.id, co2e_total_kg=500000.0,
                            co2e_produce_kg=200000.0, co2e_meat_fish_kg=100000.0,
                            co2e_dairy_eggs_kg=75000.0, co2e_dry_goods_kg=75000.0,
                            co2e_bread_kg=50000.0,
                            emission_factor_source="test", methodology_version="FRAME-NL-v1.0"))
    session.add(PeopleServed(report_id=rep.id, households_weekly=1000,
                              households_weekly_source=SourceEnum.extracted,
                              households_weekly_method="test"))

    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=10000.0)
    session.add(sub)
    session.flush()
    session.add(Allocation(subscription_id=sub.id, foodbank_id=fb.id, weight_pct=1.0))
    session.commit()

    client.cookies.set(COOKIE_NAME, make_session_cookie(str(user.id)))
    return user, pkg, sub, fb


def test_dashboard_lists_subscriptions(client: TestClient):
    _setup_with_paid_sub(client)
    resp = client.get("/dashboard")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_dashboard_detail_returns_allocations(client: TestClient):
    _, _, sub, fb = _setup_with_paid_sub(client)
    resp = client.get(f"/dashboard/{sub.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["allocations"]) == 1
    assert body["allocations"][0]["foodbank_name"] == "Test Bank"
    assert body["allocations"][0]["weight_pct"] == 1.0
    assert body["total_co2e_kg"] == 500000.0


def test_dashboard_detail_404_wrong_user(client: TestClient):
    _, _, sub, _ = _setup_with_paid_sub(client)
    # Create another user and set their cookie
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    other_user = User(email="other@test.nl", hashed_password="x", role=RoleEnum.corporate)
    session.add(other_user)
    session.commit()
    client.cookies.set(COOKIE_NAME, make_session_cookie(str(other_user.id)))
    resp = client.get(f"/dashboard/{sub.id}")
    assert resp.status_code == 404
