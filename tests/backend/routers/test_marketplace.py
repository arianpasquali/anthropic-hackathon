import uuid
from fastapi.testclient import TestClient
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.enums import ImpactProfileEnum, RegionEnum, RoleEnum
from src.backend.models.marketplace import Package
from src.backend.models.user import User
from src.backend.services.auth import COOKIE_NAME, hash_password, make_session_cookie


def _seed_package(client: TestClient, profile=ImpactProfileEnum.balanced) -> str:
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    pkg = Package(
        name="Test CO2 Fund",
        region=RegionEnum.west,
        price_eur=25000.0,
        co2e_claim_kg=600000.0,
        impact_profile=profile,
        top_n=5,
    )
    session.add(pkg)
    session.commit()
    return str(pkg.id)


def test_list_packages_returns_200(client: TestClient):
    resp = client.get("/packages")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_list_packages_shows_seeded_package(client: TestClient):
    _seed_package(client)
    resp = client.get("/packages")
    assert len(resp.json()) == 1
    assert resp.json()[0]["name"] == "Test CO2 Fund"


def test_list_packages_filter_by_profile(client: TestClient):
    _seed_package(client, ImpactProfileEnum.co2_focus)
    _seed_package(client, ImpactProfileEnum.social_focus)
    resp = client.get("/packages?profile=co2_focus")
    assert len(resp.json()) == 1
    assert resp.json()[0]["impact_profile"] == "co2_focus"


def test_get_package_returns_200(client: TestClient):
    pkg_id = _seed_package(client)
    resp = client.get(f"/packages/{pkg_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == pkg_id


def test_get_package_404_on_missing(client: TestClient):
    resp = client.get(f"/packages/{uuid.uuid4()}")
    assert resp.status_code == 404


def test_get_package_includes_projected_allocations(client: TestClient):
    """PackageDetail must expose projected_allocations for the Fund detail page."""
    from datetime import date
    from src.backend.models.enums import SourceEnum
    from src.backend.models.foodbank import AnnualReport, Foodbank
    from src.backend.models.frame import FrameResult
    from src.backend.models.measurements import PeopleServed

    pkg_id = _seed_package(client, ImpactProfileEnum.co2_focus)
    session = next(client.app.dependency_overrides[get_session]())
    for i, (city, co2) in enumerate([("Rotterdam", 5e6), ("Amsterdam", 3e6), ("Utrecht", 1e6)]):
        fb = Foodbank(name=f"VB {city}", city=city, region=RegionEnum.west)
        session.add(fb); session.commit()
        report = AnnualReport(
            foodbank_id=fb.id, year=2024,
            period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
            raw_file_path="x.pdf", ingestion_model="test",
        )
        session.add(report); session.commit()
        session.add(FrameResult(
            report_id=report.id, co2e_total_kg=co2,
            co2e_produce_kg=co2 * 0.4, co2e_meat_fish_kg=co2 * 0.2,
            co2e_dairy_eggs_kg=co2 * 0.15, co2e_dry_goods_kg=co2 * 0.15,
            co2e_bread_kg=co2 * 0.1,
            emission_factor_source="t", methodology_version="v1",
        ))
        session.add(PeopleServed(
            report_id=report.id, households_weekly=1000,
            households_weekly_source=SourceEnum.extracted,
            households_weekly_method="seed",
        ))
        session.commit()

    resp = client.get(f"/packages/{pkg_id}")
    body = resp.json()
    assert "projected_allocations" in body
    allocations = body["projected_allocations"]
    assert len(allocations) == 3
    assert allocations[0]["foodbank"]["city"] == "Rotterdam"  # highest CO2 first
    assert allocations[0]["weight_pct"] > allocations[-1]["weight_pct"]
    assert abs(sum(a["weight_pct"] for a in allocations) - 1.0) < 1e-6
    assert allocations[0]["attributed_eur"] > 0
