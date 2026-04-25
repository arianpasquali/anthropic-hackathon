"""Smoke tests for the operations upload route."""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook


@pytest.fixture
def client():
    from app.main import app

    return TestClient(app)


def _csv_body() -> str:
    header = (
        "chapter_id,period_start,period_end,"
        "fresh_produce_kg,bread_bakery_kg,dairy_kg,meat_processed_kg,"
        "ready_meals_kg,dry_goods_kg,canned_kg,frozen_kg,"
        "households_served,distribution_count,transport_km,refrigeration_kwh,"
        "operational_cost_eur"
    )
    row = (
        "VB-AMS-OOST,2026-01-06,2026-03-30,"
        "52000,29250,22750,9750,6500,26000,11375,4875,"
        "4940,65,2400,3850,58270"
    )
    return f"{header}\n{row}\n"


class TestOperationsRouter:
    def test_health(self, client):
        response = client.get("/api/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_preview_csv_upload(self, client):
        response = client.post(
            "/api/operations/preview",
            files={"file": ("ops.csv", _csv_body(), "text/csv")},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 1
        record = body["records"][0]
        assert record["chapter_id"] == "VB-AMS-OOST"
        assert record["category_breakdown"]["fresh_produce"] == 52000
        assert record["households_served"] == 4940

    def test_preview_rejects_unknown_chapter(self, client):
        bad = _csv_body().replace("VB-AMS-OOST", "VB-NOT-REAL")
        response = client.post(
            "/api/operations/preview",
            files={"file": ("ops.csv", bad, "text/csv")},
        )
        assert response.status_code == 400
        assert "unknown chapter" in response.json()["detail"]["error"]

    def test_preview_xlsx_upload(self, client):
        wb = Workbook()
        ws = wb.active
        ws.append([
            "chapter_id", "period_start", "period_end",
            "fresh_produce_kg", "bread_bakery_kg", "dairy_kg",
            "meat_processed_kg", "ready_meals_kg", "dry_goods_kg",
            "canned_kg", "frozen_kg", "households_served",
            "distribution_count", "transport_km", "refrigeration_kwh",
            "operational_cost_eur",
        ])
        ws.append([
            "VB-RDM-ZUID", "2026-01-06", "2026-03-30",
            42000, 26500, 18000, 8200, 5500, 24000, 11000, 4500,
            5460, 60, 2200, 3400, 56000,
        ])
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)

        response = client.post(
            "/api/operations/preview",
            files={
                "file": (
                    "ops.xlsx",
                    buf.getvalue(),
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
            },
        )
        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 1
        assert body["records"][0]["chapter_id"] == "VB-RDM-ZUID"
        assert body["records"][0]["submission_method"] == "spreadsheet"
