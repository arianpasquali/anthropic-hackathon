from fastapi.testclient import TestClient


def test_register_creates_user(client: TestClient):
    resp = client.post("/auth/register", json={"email": "test@corp.nl", "password": "pass1234", "org_name": "Test BV"})
    assert resp.status_code == 201
    assert resp.json()["email"] == "test@corp.nl"


def test_register_duplicate_email_fails(client: TestClient):
    client.post("/auth/register", json={"email": "dupe@corp.nl", "password": "pass1234", "org_name": "Test"})
    resp = client.post("/auth/register", json={"email": "dupe@corp.nl", "password": "pass1234", "org_name": "Test"})
    assert resp.status_code == 409


def test_login_sets_cookie(client: TestClient):
    client.post("/auth/register", json={"email": "login@corp.nl", "password": "pass1234", "org_name": "ACME"})
    resp = client.post("/auth/login", json={"email": "login@corp.nl", "password": "pass1234"})
    assert resp.status_code == 200
    assert "session" in resp.cookies


def test_login_wrong_password(client: TestClient):
    client.post("/auth/register", json={"email": "wrong@corp.nl", "password": "pass1234", "org_name": "ACME"})
    resp = client.post("/auth/login", json={"email": "wrong@corp.nl", "password": "wrongpass"})
    assert resp.status_code == 401


def test_logout_clears_cookie(client: TestClient):
    client.post("/auth/register", json={"email": "logout@corp.nl", "password": "pass1234", "org_name": "ACME"})
    client.post("/auth/login", json={"email": "logout@corp.nl", "password": "pass1234"})
    resp = client.post("/auth/logout")
    assert resp.status_code == 200


def test_me_returns_user(client: TestClient):
    client.post("/auth/register", json={"email": "me@corp.nl", "password": "pass1234", "org_name": "ACME"})
    client.post("/auth/login", json={"email": "me@corp.nl", "password": "pass1234"})
    resp = client.get("/auth/me")
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@corp.nl"


def test_me_unauthenticated(client: TestClient):
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 303)
