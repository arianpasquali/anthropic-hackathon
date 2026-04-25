import uuid
from datetime import date
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.enums import ImpactProfileEnum, RegionEnum, RoleEnum, SourceEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import PeopleServed
from src.backend.models.user import User
from src.backend.services.auth import COOKIE_NAME, hash_password, make_session_cookie


def _setup(client: TestClient):
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    user = User(email="corp@test.nl", hashed_password=hash_password("pass"), role=RoleEnum.corporate, org_name="ACME")
    session.add(user)
    pkg = Package(name="Test Fund", region=RegionEnum.west, price_eur=10000.0,
                  co2e_claim_kg=200000.0, impact_profile=ImpactProfileEnum.co2_focus, top_n=5)
    session.add(pkg)
    session.commit()
    client.cookies.set(COOKIE_NAME, make_session_cookie(str(user.id)))
    return user, pkg, session


def _seed_foodbanks(session: Session, count=3):
    for i in range(count):
        fb = Foodbank(name=f"Bank {i}", city="Test", region=RegionEnum.west, is_regional_dc=False)
        session.add(fb)
        session.flush()
        rep = AnnualReport(foodbank_id=fb.id, year=2024, period_start=date(2024,1,1),
                           period_end=date(2024,12,31), raw_file_path="test.txt", ingestion_model="test")
        session.add(rep)
        session.flush()
        session.add(FrameResult(report_id=rep.id, co2e_total_kg=float(i+1)*100,
                                co2e_produce_kg=float(i+1)*40, co2e_meat_fish_kg=float(i+1)*20,
                                co2e_dairy_eggs_kg=float(i+1)*15, co2e_dry_goods_kg=float(i+1)*15,
                                co2e_bread_kg=float(i+1)*10,
                                emission_factor_source="test", methodology_version="FRAME-NL-v1.0"))
        session.add(PeopleServed(report_id=rep.id, households_weekly=i*100+50,
                                  households_weekly_source=SourceEnum.extracted,
                                  households_weekly_method="test"))
    session.commit()


def test_checkout_creates_pending_subscription(client: TestClient):
    user, pkg, session = _setup(client)
    resp = client.post(f"/packages/{pkg.id}/checkout")
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "pending"
    assert body["package_id"] == str(pkg.id)


def test_checkout_requires_auth(client: TestClient):
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    pkg = Package(name="Fund", region=RegionEnum.west, price_eur=5000.0, co2e_claim_kg=100000.0)
    session.add(pkg)
    session.commit()
    resp = client.post(f"/packages/{pkg.id}/checkout")
    assert resp.status_code in (303, 401)


def test_pay_sets_status_paid(client: TestClient):
    user, pkg, session = _setup(client)
    _seed_foodbanks(session)
    resp = client.post(f"/packages/{pkg.id}/checkout")
    sub_id = resp.json()["id"]
    resp2 = client.post(f"/checkout/{sub_id}/pay")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "paid"


def test_pay_creates_allocations(client: TestClient):
    user, pkg, session = _setup(client)
    _seed_foodbanks(session, count=3)
    resp = client.post(f"/packages/{pkg.id}/checkout")
    sub_id = resp.json()["id"]
    client.post(f"/checkout/{sub_id}/pay")
    allocations = session.exec(select(Allocation).where(Allocation.subscription_id == uuid.UUID(sub_id))).all()
    assert len(allocations) > 0
    assert abs(sum(a.weight_pct for a in allocations) - 1.0) < 1e-6


def test_confirm_returns_subscription_detail(client: TestClient):
    user, pkg, session = _setup(client)
    resp = client.post(f"/packages/{pkg.id}/checkout")
    sub_id = resp.json()["id"]
    resp2 = client.get(f"/checkout/{sub_id}/confirm")
    assert resp2.status_code == 200
    assert resp2.json()["id"] == sub_id
