from datetime import date

from fastapi.testclient import TestClient
from sqlmodel import Session

from src.backend.database import get_session
from src.backend.models.enums import RegionEnum, SourceEnum
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.measurements import FoodCategories, PeopleServed


def _seed_bank(session: Session, name: str, city: str, with_report: bool = True) -> Foodbank:
    fb = Foodbank(name=name, city=city, region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    if with_report:
        report = AnnualReport(
            foodbank_id=fb.id,
            year=2024,
            period_start=date(2024, 1, 1),
            period_end=date(2024, 12, 31),
            raw_file_path=f"data/{city.lower()}-2024.pdf",
            ingestion_model="claude-sonnet-4-6",
        )
        session.add(report)
        session.commit()
        session.add(FrameResult(
            report_id=report.id,
            co2e_total_kg=1_000_000.0,
            co2e_produce_kg=400_000.0, co2e_meat_fish_kg=200_000.0,
            co2e_dairy_eggs_kg=150_000.0, co2e_dry_goods_kg=150_000.0,
            co2e_bread_kg=100_000.0,
            emission_factor_source="FAO FWF (2013)", methodology_version="FRAME-NL-v1.0",
        ))
        session.add(FoodCategories(
            report_id=report.id,
            kg_produce=400_000.0, kg_produce_source=SourceEnum.extracted, kg_produce_method="annual report p.12",
            kg_meat_fish=50_000.0, kg_meat_fish_source=SourceEnum.extracted, kg_meat_fish_method="annual report p.12",
            kg_dairy_eggs=100_000.0, kg_dairy_eggs_source=SourceEnum.extracted, kg_dairy_eggs_method="p.12",
            kg_dry_goods=200_000.0, kg_dry_goods_source=SourceEnum.extracted, kg_dry_goods_method="p.12",
            kg_bread_bakery=150_000.0, kg_bread_bakery_source=SourceEnum.extracted, kg_bread_bakery_method="p.12",
            kg_prepared=50_000.0, kg_prepared_source=SourceEnum.inferred_calculation, kg_prepared_method="residual",
        ))
        session.add(PeopleServed(
            report_id=report.id,
            households_weekly=1500,
            households_weekly_source=SourceEnum.extracted, households_weekly_method="annual report p.4",
            individuals_total=3500,
            individuals_total_source=SourceEnum.inferred_national_avg,
            individuals_total_method="CBS household size",
        ))
        session.commit()
    return fb


def test_list_empty(client: TestClient):
    res = client.get("/foodbanks")
    assert res.status_code == 200
    assert res.json() == []


def test_list_returns_banks_without_reports(client: TestClient):
    engine_session_dep = list(client.app.dependency_overrides.values())[0]
    with next(engine_session_dep()) as session:
        _seed_bank(session, "Voedselbank Rotterdam", "Rotterdam", with_report=False)

    res = client.get("/foodbanks")
    assert res.status_code == 200
    body = res.json()
    assert len(body) == 1
    assert body[0]["slug"] == "rotterdam"
    assert body[0]["lat"] is not None
    assert body[0]["annual_kg_rescued"] is None


def test_list_returns_full_data_when_report_present(client: TestClient):
    engine_session_dep = list(client.app.dependency_overrides.values())[0]
    with next(engine_session_dep()) as session:
        _seed_bank(session, "Voedselbank Amsterdam", "Amsterdam")

    res = client.get("/foodbanks")
    body = res.json()
    assert len(body) == 1
    bank = body[0]
    assert bank["slug"] == "amsterdam"
    assert bank["lat"] == 52.3676
    assert bank["annual_kg_rescued"] == 950_000.0
    assert bank["annual_tco2e"] == 1000.0
    assert bank["households_weekly"] == 1500
    assert bank["category_mix"]["produce"] > 0
    assert any(p["source"] == "extracted" for p in bank["provenance"])


def test_get_by_slug(client: TestClient):
    engine_session_dep = list(client.app.dependency_overrides.values())[0]
    with next(engine_session_dep()) as session:
        _seed_bank(session, "Voedselbank Den Haag", "Den Haag")

    res = client.get("/foodbanks/den-haag")
    assert res.status_code == 200
    assert res.json()["name"] == "Voedselbank Den Haag"


def test_get_unknown_slug_404(client: TestClient):
    res = client.get("/foodbanks/nonexistent")
    assert res.status_code == 404
