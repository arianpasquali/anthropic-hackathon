from datetime import date, datetime, timezone
from decimal import Decimal

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


def _src(method: str | None) -> SourceEnum | None:
    return SourceEnum.extracted if method is not None else None


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
        kg_received_total=fv.kg_received_total,
        kg_received_total_source=_src(fv.kg_received_total_method),
        kg_received_total_method=fv.kg_received_total_method,
        kg_via_national_dc=fv.kg_via_national_dc,
        kg_via_national_dc_source=_src(fv.kg_via_national_dc_method),
        kg_via_national_dc_method=fv.kg_via_national_dc_method,
        kg_direct=fv.kg_direct,
        kg_direct_source=_src(fv.kg_direct_method),
        kg_direct_method=fv.kg_direct_method,
        waste_pct=fv.waste_pct,
        waste_pct_source=_src(fv.waste_pct_method),
        waste_pct_method=fv.waste_pct_method,
        parcels_distributed=fv.parcels_distributed,
        parcels_distributed_source=_src(fv.parcels_distributed_method),
        parcels_distributed_method=fv.parcels_distributed_method,
        avg_products_per_parcel=fv.avg_products_per_parcel,
        avg_products_per_parcel_source=_src(fv.avg_products_per_parcel_method),
        avg_products_per_parcel_method=fv.avg_products_per_parcel_method,
        pct_schijf_van_vijf=fv.pct_schijf_van_vijf,
        pct_schijf_van_vijf_source=_src(fv.pct_schijf_van_vijf_method),
        pct_schijf_van_vijf_method=fv.pct_schijf_van_vijf_method,
        food_value_eur=Decimal(str(fv.food_value_eur)) if fv.food_value_eur is not None else None,
        food_value_eur_source=_src(fv.food_value_eur_method),
        food_value_eur_method=fv.food_value_eur_method,
    ))

    fc = result.food_categories
    session.add(FoodCategories(
        report_id=report.id,
        kg_produce=fc.kg_produce,
        kg_produce_source=_src(fc.kg_produce_method),
        kg_produce_method=fc.kg_produce_method,
        kg_meat_fish=fc.kg_meat_fish,
        kg_meat_fish_source=_src(fc.kg_meat_fish_method),
        kg_meat_fish_method=fc.kg_meat_fish_method,
        kg_dairy_eggs=fc.kg_dairy_eggs,
        kg_dairy_eggs_source=_src(fc.kg_dairy_eggs_method),
        kg_dairy_eggs_method=fc.kg_dairy_eggs_method,
        kg_dry_goods=fc.kg_dry_goods,
        kg_dry_goods_source=_src(fc.kg_dry_goods_method),
        kg_dry_goods_method=fc.kg_dry_goods_method,
        kg_bread_bakery=fc.kg_bread_bakery,
        kg_bread_bakery_source=_src(fc.kg_bread_bakery_method),
        kg_bread_bakery_method=fc.kg_bread_bakery_method,
        kg_prepared=fc.kg_prepared,
        kg_prepared_source=_src(fc.kg_prepared_method),
        kg_prepared_method=fc.kg_prepared_method,
    ))

    ps = result.people_served
    session.add(PeopleServed(
        report_id=report.id,
        households_weekly=ps.households_weekly,
        households_weekly_source=_src(ps.households_weekly_method),
        households_weekly_method=ps.households_weekly_method,
        individuals_total=ps.individuals_total,
        individuals_total_source=_src(ps.individuals_total_method),
        individuals_total_method=ps.individuals_total_method,
        children_count=ps.children_count,
        children_count_source=_src(ps.children_count_method),
        children_count_method=ps.children_count_method,
        pct_under_18=ps.pct_under_18,
        pct_under_18_source=_src(ps.pct_under_18_method),
        pct_under_18_method=ps.pct_under_18_method,
        pct_single_adults=ps.pct_single_adults,
        pct_single_adults_source=_src(ps.pct_single_adults_method),
        pct_single_adults_method=ps.pct_single_adults_method,
        pct_single_parent=ps.pct_single_parent,
        pct_single_parent_source=_src(ps.pct_single_parent_method),
        pct_single_parent_method=ps.pct_single_parent_method,
        pct_families=ps.pct_families,
        pct_families_source=_src(ps.pct_families_method),
        pct_families_method=ps.pct_families_method,
        pct_couples=ps.pct_couples,
        pct_couples_source=_src(ps.pct_couples_method),
        pct_couples_method=ps.pct_couples_method,
    ))

    ops = result.operations
    session.add(Operations(
        report_id=report.id,
        volunteers_count=ops.volunteers_count,
        volunteers_count_source=_src(ops.volunteers_count_method),
        volunteers_count_method=ops.volunteers_count_method,
        distribution_locations=ops.distribution_locations,
        distribution_locations_source=_src(ops.distribution_locations_method),
        distribution_locations_method=ops.distribution_locations_method,
        satellite_banks_served=ops.satellite_banks_served,
        satellite_banks_served_source=_src(ops.satellite_banks_served_method),
        satellite_banks_served_method=ops.satellite_banks_served_method,
        annual_budget_eur=Decimal(str(ops.annual_budget_eur)) if ops.annual_budget_eur is not None else None,
        annual_budget_eur_source=_src(ops.annual_budget_eur_method),
        annual_budget_eur_method=ops.annual_budget_eur_method,
        total_expenditure_eur=Decimal(str(ops.total_expenditure_eur)) if ops.total_expenditure_eur is not None else None,
        total_expenditure_eur_source=_src(ops.total_expenditure_eur_method),
        total_expenditure_eur_method=ops.total_expenditure_eur_method,
    ))

    don = result.donations
    session.add(Donations(
        report_id=report.id,
        food_supermarket_kg=don.food_supermarket_kg,
        food_supermarket_kg_source=_src(don.food_supermarket_kg_method),
        food_supermarket_kg_method=don.food_supermarket_kg_method,
        food_company_kg=don.food_company_kg,
        food_company_kg_source=_src(don.food_company_kg_method),
        food_company_kg_method=don.food_company_kg_method,
        food_dc_kg=don.food_dc_kg,
        food_dc_kg_source=_src(don.food_dc_kg_method),
        food_dc_kg_method=don.food_dc_kg_method,
        money_individuals_eur=Decimal(str(don.money_individuals_eur)) if don.money_individuals_eur is not None else None,
        money_individuals_eur_source=_src(don.money_individuals_eur_method),
        money_individuals_eur_method=don.money_individuals_eur_method,
        money_companies_eur=Decimal(str(don.money_companies_eur)) if don.money_companies_eur is not None else None,
        money_companies_eur_source=_src(don.money_companies_eur_method),
        money_companies_eur_method=don.money_companies_eur_method,
        money_orgs_eur=Decimal(str(don.money_orgs_eur)) if don.money_orgs_eur is not None else None,
        money_orgs_eur_source=_src(don.money_orgs_eur_method),
        money_orgs_eur_method=don.money_orgs_eur_method,
        money_government_eur=Decimal(str(don.money_government_eur)) if don.money_government_eur is not None else None,
        money_government_eur_source=_src(don.money_government_eur_method),
        money_government_eur_method=don.money_government_eur_method,
    ))

    session.commit()
    logger.info(f"Wrote all measurement tables for {foodbank_name} {year}")
    return report
