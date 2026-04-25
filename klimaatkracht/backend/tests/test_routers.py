"""Smoke tests for chapters/fund/reports/methodology routers.

Each test overrides the app's `get_db` dependency to point at the seeded
in-memory test database so the routes see realistic data without needing
a Postgres instance.
"""

from datetime import date
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.main import app
from app.models import Buyer, Commitment, OperationsRecord
from tests.fixtures import load_simulation_seed


@pytest.fixture
def api_client(seeded_db: Session):
    def _get_db_override():
        try:
            yield seeded_db
        finally:
            pass

    app.dependency_overrides[get_db] = _get_db_override
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def api_client_with_ops(api_client, seeded_db: Session):
    seed = load_simulation_seed("q1_2026")
    for chapter in seed["chapters"]:
        seeded_db.add(
            OperationsRecord(
                chapter_id=chapter["id"],
                period_start=date.fromisoformat(chapter["period_start"]),
                period_end=date.fromisoformat(chapter["period_end"]),
                submission_method="csv_upload",
                total_kg=sum(chapter["category_breakdown"].values()),
                category_breakdown=chapter["category_breakdown"],
                households_served=chapter["households_quarter"],
                operational_cost_eur=chapter["quarterly_cost_eur"],
            )
        )
    seeded_db.commit()
    return api_client


class TestChaptersRouter:
    def test_list_chapters(self, api_client):
        response = api_client.get("/api/chapters")
        assert response.status_code == 200
        body = response.json()
        ids = {c["id"] for c in body["chapters"]}
        assert ids == {
            "VB-AMS-OOST", "VB-RDM-ZUID", "VB-LEI-CTR", "VB-FRL-NRD", "VB-EHV-CTR",
        }


class TestFundRouter:
    def test_allocation_preview(self, api_client_with_ops):
        response = api_client_with_ops.post(
            "/api/fund/allocation-preview",
            json={
                "amount_eur": 100_000,
                "period_start": "2026-01-06",
                "period_end": "2026-03-30",
                "preferences": {
                    "max_climate_impact": 0.4,
                    "max_social_need": 0.4,
                    "balanced_distribution": 0.2,
                },
            },
        )
        assert response.status_code == 200
        body = response.json()
        total = sum(a["amount_eur"] for a in body["allocations"])
        assert abs(total - 100_000) < 1.0
        rdm = next(a for a in body["allocations"] if a["chapter_id"] == "VB-RDM-ZUID")
        # Same regression check as the unit test
        assert abs(rdm["amount_eur"] - 29_430) < 200

    def test_allocation_preview_rejects_invalid_preferences(self, api_client_with_ops):
        response = api_client_with_ops.post(
            "/api/fund/allocation-preview",
            json={
                "amount_eur": 100_000,
                "period_start": "2026-01-06",
                "period_end": "2026-03-30",
                "preferences": {
                    "max_climate_impact": 0.5,
                    "max_social_need": 0.5,
                    "balanced_distribution": 0.5,
                },
            },
        )
        assert response.status_code == 400

    def test_allocation_preview_no_data_for_period(self, api_client_with_ops):
        response = api_client_with_ops.post(
            "/api/fund/allocation-preview",
            json={
                "amount_eur": 100_000,
                "period_start": "2027-01-06",
                "period_end": "2027-03-30",
                "preferences": {
                    "max_climate_impact": 0.4,
                    "max_social_need": 0.4,
                    "balanced_distribution": 0.2,
                },
            },
        )
        assert response.status_code == 400

    def test_commit_flow_end_to_end(self, api_client_with_ops, seeded_db):
        buyer = Buyer(
            id="buyer-test",
            name="Test Corp",
            industry="Energy",
            contact_email="csr@testcorp.example",
            employees_count=2000,
            turnover_eur_m=900,
            csrd_in_scope=True,
        )
        seeded_db.add(buyer)
        seeded_db.commit()

        response = api_client_with_ops.post(
            "/api/fund/commit",
            json={
                "buyer_id": "buyer-test",
                "fund_id": "demo-fund-q1-2026",
                "amount_eur": 100_000,
                "preferences": {
                    "max_climate_impact": 0.4,
                    "max_social_need": 0.4,
                    "balanced_distribution": 0.2,
                },
                "rationale": "Blended preference",
                "period_start": "2026-01-06",
                "period_end": "2026-03-30",
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["commitment_id"]
        assert body["report_id"]
        # Net avoided should match seed expectation within 1%
        seed = load_simulation_seed("q1_2026")
        target = seed["expected_totals"]["corp_x_attributed_tco2e"]
        assert abs(body["total_net_avoided_tco2e"] - target) / target < 0.01

        # Fetch the generated report via the reports router
        report_response = api_client_with_ops.get(f"/api/reports/{body['commitment_id']}")
        assert report_response.status_code == 200
        report_body = report_response.json()
        assert "VB-AMS-OOST" in report_body["markdown"]
        assert report_body["methodology_version"] == "KKM-2026.1"


class TestMethodologyRouter:
    def test_methodology_endpoint(self, api_client):
        response = api_client.get("/api/methodology")
        assert response.status_code == 200
        body = response.json()
        assert body["version"] == "KKM-2026.1"
        assert "Poore & Nemecek 2018" in body["section_markdown"]


class TestReportsRouter:
    def test_404_when_no_report(self, api_client):
        response = api_client.get("/api/reports/does-not-exist")
        assert response.status_code == 404
