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
