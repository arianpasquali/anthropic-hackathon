from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any

from loguru import logger
from sqlmodel import Session, select

from src.backend.models import (
    AnnualReport, Donations, Foodbank, FoodCategories,
    FoodVolume, Operations, PeopleServed,
)
from src.backend.models.enums import RegionEnum, SourceEnum
from src.backend.preprocessing.schemas import ExtractionResult


def _get_or_create_foodbank(
    session: Session, name: str, city: str, region: RegionEnum
) -> Foodbank:
    existing = session.exec(select(Foodbank).where(Foodbank.name == name)).first()
    if existing:
        return existing
    fb = Foodbank(name=name, city=city, region=region)
    session.add(fb)
    session.commit()
    logger.debug(f"Created foodbank: {name}")
    return fb


def _delete_report_cascade(session: Session, report: AnnualReport) -> None:
    """Delete a report and all its child measurement rows."""
    for model in (FoodVolume, FoodCategories, PeopleServed, Operations, Donations):
        rows = session.exec(
            select(model).where(model.report_id == report.id)  # type: ignore[attr-defined]
        ).all()
        for row in rows:
            session.delete(row)
    session.delete(report)
    session.commit()
    logger.debug(f"Deleted report {report.id} and all children")


def _src(*markers: object) -> SourceEnum | None:
    return SourceEnum.extracted if any(marker is not None for marker in markers) else None


def _measurement_kwargs(
    obj: object,
    field_names: list[str],
    *,
    decimal_fields: set[str] | None = None,
) -> dict[str, Any]:
    decimal_fields = decimal_fields or set()
    kwargs: dict[str, Any] = {}
    for field in field_names:
        value = getattr(obj, field)
        if field in decimal_fields and value is not None:
            value = Decimal(str(value))
        method = getattr(obj, f"{field}_method", None)
        evidence = getattr(obj, f"{field}_evidence", None)
        confidence = getattr(obj, f"{field}_confidence", None)
        kwargs[field] = value
        kwargs[f"{field}_source"] = _src(method, evidence, confidence)
        kwargs[f"{field}_method"] = method
        kwargs[f"{field}_evidence"] = evidence
        kwargs[f"{field}_confidence"] = confidence
    return kwargs


def write_report(
    session: Session,
    foodbank_name: str,
    city: str,
    region: RegionEnum,
    year: int,
    pdf_path: str,
    result: ExtractionResult,
    model: str,
    force: bool = False,
) -> AnnualReport:
    fb = _get_or_create_foodbank(session, foodbank_name, city, region)

    existing = session.exec(
        select(AnnualReport).where(
            AnnualReport.foodbank_id == fb.id,
            AnnualReport.year == year,
        )
    ).first()

    if existing and not force:
        logger.info(f"Report {foodbank_name} {year} already exists — skipping (use --force to overwrite)")
        return existing

    if existing and force:
        _delete_report_cascade(session, existing)

    report = AnnualReport(
        foodbank_id=fb.id,
        year=year,
        period_start=date(year, 1, 1),
        period_end=date(year, 12, 31),
        raw_file_path=pdf_path,
        ingestion_model=model,
    )
    session.add(report)
    session.commit()
    logger.info(f"Created AnnualReport {foodbank_name} {year} (id={report.id})")

    fv = result.food_volume
    session.add(FoodVolume(
        report_id=report.id,
        **_measurement_kwargs(
            fv,
            [
                "kg_received_total",
                "kg_via_national_dc",
                "kg_direct",
                "waste_pct",
                "parcels_distributed",
                "avg_products_per_parcel",
                "pct_schijf_van_vijf",
                "food_value_eur",
            ],
            decimal_fields={"food_value_eur"},
        ),
    ))

    fc = result.food_categories
    session.add(FoodCategories(
        report_id=report.id,
        **_measurement_kwargs(
            fc,
            [
                "kg_produce",
                "kg_meat_fish",
                "kg_dairy_eggs",
                "kg_dry_goods",
                "kg_bread_bakery",
                "kg_prepared",
            ],
        ),
    ))

    ps = result.people_served
    session.add(PeopleServed(
        report_id=report.id,
        **_measurement_kwargs(
            ps,
            [
                "households_weekly",
                "individuals_total",
                "children_count",
                "pct_under_18",
                "pct_single_adults",
                "pct_single_parent",
                "pct_families",
                "pct_couples",
            ],
        ),
    ))

    ops = result.operations
    session.add(Operations(
        report_id=report.id,
        **_measurement_kwargs(
            ops,
            [
                "volunteers_count",
                "distribution_locations",
                "satellite_banks_served",
                "annual_budget_eur",
                "total_expenditure_eur",
            ],
            decimal_fields={"annual_budget_eur", "total_expenditure_eur"},
        ),
    ))

    don = result.donations
    session.add(Donations(
        report_id=report.id,
        **_measurement_kwargs(
            don,
            [
                "food_supermarket_kg",
                "food_company_kg",
                "food_dc_kg",
                "money_individuals_eur",
                "money_companies_eur",
                "money_orgs_eur",
                "money_government_eur",
            ],
            decimal_fields={
                "money_individuals_eur",
                "money_companies_eur",
                "money_orgs_eur",
                "money_government_eur",
            },
        ),
    ))

    session.commit()
    logger.info(f"Wrote all measurement tables for {foodbank_name} {year}")
    return report
