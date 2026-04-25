import pytest
from fastapi.testclient import TestClient
from src.backend.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_llms_txt():
    r = client.get("/llms.txt")
    assert r.status_code == 200
    assert "Klimaatkracht" in r.text
    assert r.headers["content-type"].startswith("text/plain")


def test_llms_full_txt():
    r = client.get("/llms-full.txt")
    assert r.status_code == 200
    assert "/packages" in r.text


def test_robots_txt():
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert "ClaudeBot" in r.text
    assert "Allow: /" in r.text


def test_sitemap_xml():
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert "/openapi.json" in r.text


def test_ai_plugin_json():
    r = client.get("/.well-known/ai-plugin.json")
    assert r.status_code == 200
    data = r.json()
    assert data["name_for_model"] == "klimaatkracht"
    assert "openapi.json" in data["api"]["url"]


def test_agent_json():
    r = client.get("/.well-known/agent.json")
    assert r.status_code == 200
    data = r.json()
    assert "llms_txt" in data


def test_link_header_on_packages():
    """Discovery Link header present on all responses."""
    r = client.get("/packages")
    assert "llms.txt" in r.headers.get("link", "")
