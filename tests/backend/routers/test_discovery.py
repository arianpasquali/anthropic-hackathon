import pytest
from fastapi.testclient import TestClient
from src.backend.app import app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_llms_txt(client):
    r = client.get("/llms.txt")
    assert r.status_code == 200
    assert "Climate Harvest" in r.text
    assert r.headers["content-type"].startswith("text/plain")


def test_llms_full_txt(client):
    r = client.get("/llms-full.txt")
    assert r.status_code == 200
    assert "/packages" in r.text


def test_robots_txt(client):
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert "ClaudeBot" in r.text
    assert "Allow: /" in r.text


def test_sitemap_xml(client):
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert "/openapi.json" in r.text


def test_ai_plugin_json(client):
    r = client.get("/.well-known/ai-plugin.json")
    assert r.status_code == 200
    data = r.json()
    assert data["name_for_model"] == "klimaatkracht"
    assert "openapi.json" in data["api"]["url"]


def test_agent_json(client):
    r = client.get("/.well-known/agent.json")
    assert r.status_code == 200
    data = r.json()
    assert "llms_txt" in data


def test_link_header_on_packages(client):
    """Discovery Link header present on all responses."""
    r = client.get("/packages")
    assert "llms.txt" in r.headers.get("link", "")


def test_openapi_tags_present(client):
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    tags_used = {
        tag
        for path in spec["paths"].values()
        for method in path.values()
        for tag in method.get("tags", [])
    }
    for expected_tag in ["auth", "packages", "checkout", "dashboard", "report", "insights"]:
        assert expected_tag in tags_used, f"tag '{expected_tag}' missing from OpenAPI spec"


def test_openapi_summaries_present(client):
    r = client.get("/openapi.json")
    spec = r.json()
    missing = []
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            if "summary" not in op:
                missing.append(f"{method.upper()} {path}")
    assert missing == [], f"Endpoints missing summaries: {missing}"


def test_packages_markdown_negotiation(client):
    r = client.get("/packages", headers={"Accept": "text/markdown"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/markdown")
    assert "## Impact Packages" in r.text


def test_aggregate_markdown_negotiation(client):
    r = client.get("/insights/aggregate", headers={"Accept": "text/markdown"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/markdown")
    assert "tCO" in r.text or "CO2" in r.text or "CO₂" in r.text
