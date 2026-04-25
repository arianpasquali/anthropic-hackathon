from fastapi.testclient import TestClient
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.enums import RegionEnum, RoleEnum
from src.backend.models.foodbank import Foodbank
from src.backend.models.user import User
from src.backend.services.auth import COOKIE_NAME, hash_password, make_session_cookie


def _login_as(client, role):
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    user = User(email=f"{role.value}@test.nl", hashed_password=hash_password("pass"), role=role)
    session.add(user)
    session.commit()
    client.cookies.set(COOKIE_NAME, make_session_cookie(str(user.id)))
    return user


def test_admin_foodbanks_returns_list(client: TestClient):
    session_gen = client.app.dependency_overrides[get_session]()
    session = next(session_gen)
    _login_as(client, RoleEnum.admin)
    fb = Foodbank(name="Test Bank", city="Amsterdam", region=RegionEnum.randstad, is_regional_dc=True)
    session.add(fb)
    session.commit()
    resp = client.get("/admin/foodbanks")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_admin_foodbanks_403_for_corporate(client: TestClient):
    _login_as(client, RoleEnum.corporate)
    resp = client.get("/admin/foodbanks")
    assert resp.status_code == 403


def test_admin_foodbanks_redirects_unauthenticated(client: TestClient):
    resp = client.get("/admin/foodbanks")
    assert resp.status_code in (303, 401)
