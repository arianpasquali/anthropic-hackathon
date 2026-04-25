"""Full chain: ingest report → FRAME → User buys Package → CsrReport generated."""
import uuid
from datetime import date
from sqlmodel import Session, select

from src.backend.models import (
    User, Foodbank, AnnualReport,
    FoodVolume, FoodCategories, PeopleServed, Operations, Donations,
    FrameResult, Package, PackageFoodbank, FundSubscription, CsrReport,
)
from src.backend.models.enums import (
    RegionEnum, RoleEnum, StatusEnum, SourceEnum,
    CounterfactualEnum, TemplateEnum,
)


def test_full_breda_chain(session: Session):
    # 1. Create foodbank
    fb = Foodbank(name="Voedselbank Breda", city="Breda", region=RegionEnum.zuid, is_regional_dc=False)
    session.add(fb)
    session.commit()

    # 2. Ingest annual report
    report = AnnualReport(
        foodbank_id=fb.id, year=2024,
        period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
        raw_file_path="df/data/breda-2024-fin.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()

    # 3. Store extracted measurements
    session.add(FoodVolume(
        report_id=report.id,
        kg_received_total=507496.0,
        kg_received_total_source=SourceEnum.extracted,
        kg_received_total_method="PDF p.10",
        waste_pct=0.6,
        waste_pct_source=SourceEnum.extracted,
        waste_pct_method="PDF p.10 '0,6 procent naar de stort'",
    ))
    session.add(FoodCategories(
        report_id=report.id,
        kg_produce=185036.0,
        kg_produce_source=SourceEnum.extracted,
        kg_produce_method="PDF p.11 category table",
        kg_meat_fish=30437.0,
        kg_meat_fish_source=SourceEnum.extracted,
        kg_meat_fish_method="PDF p.11 category table",
        kg_dairy_eggs=47819.0,
        kg_dairy_eggs_source=SourceEnum.extracted,
        kg_dairy_eggs_method="PDF p.11 category table",
        kg_dry_goods=91349.0,
        kg_dry_goods_source=SourceEnum.inferred_national_avg,
        kg_dry_goods_method="NL avg 18% applied to total 507496kg",
    ))
    session.add(PeopleServed(
        report_id=report.id,
        households_weekly=327,
        households_weekly_source=SourceEnum.extracted,
        households_weekly_method="PDF p.8 '17748 / 52'",
        pct_under_18=0.37,
        pct_under_18_source=SourceEnum.inferred_national_avg,
        pct_under_18_method="NL national average Feiten & Cijfers 2024",
    ))
    session.add(Operations(
        report_id=report.id,
        volunteers_count=108,
        volunteers_count_source=SourceEnum.extracted,
        volunteers_count_method="PDF p.4",
        distribution_locations=3,
        distribution_locations_source=SourceEnum.extracted,
        distribution_locations_method="PDF p.4",
        counterfactual_route=CounterfactualEnum.incineration_energy_recovery,
    ))
    session.add(Donations(
        report_id=report.id,
        food_supermarket_kg=200000.0,
        food_supermarket_kg_source=SourceEnum.inferred_calculation,
        food_supermarket_kg_method="estimated from partner list + national DC proportion",
    ))
    session.commit()

    # 4. FRAME engine output
    frame = FrameResult(
        report_id=report.id,
        co2e_total_kg=1268740.0,
        co2e_produce_kg=462590.0,
        co2e_meat_fish_kg=304370.0,
        co2e_dairy_eggs_kg=191276.0,
        co2e_dry_goods_kg=182698.0,
        co2e_bread_kg=127806.0,
        emission_factor_source="FAO Food Wastage Footprint 2013 + WRAP UK 2022",
        methodology_version="FRAME-NL-v1.0",
    )
    session.add(frame)
    session.commit()

    # 5. Corporate buys package
    user = User(email="esg@acme.com", hashed_password="hashed_x", role=RoleEnum.corporate, org_name="ACME")
    pkg = Package(name="Breda Climate Package", region=RegionEnum.zuid, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(user)
    session.add(pkg)
    session.commit()

    session.add(PackageFoodbank(package_id=pkg.id, foodbank_id=fb.id, weight_pct=1.0))
    session.commit()

    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=25000.0, status=StatusEnum.paid, solvimon_id="solv_xyz")
    session.add(sub)
    session.commit()

    # 6. Generate CSR report
    csr = CsrReport(
        subscription_id=sub.id,
        frame_result_id=frame.id,
        file_path="reports/acme-breda-2024.pdf",
        template=TemplateEnum.csrd,
    )
    session.add(csr)
    session.commit()

    sub.csr_report_id = csr.id
    session.add(sub)
    session.commit()
    session.refresh(sub)

    # Assert full chain integrity
    assert sub.csr_report_id == csr.id
    result_sub = session.exec(select(FundSubscription).where(FundSubscription.id == sub.id)).one()
    assert result_sub.status == StatusEnum.paid
    result_frame = session.exec(select(FrameResult).where(FrameResult.report_id == report.id)).one()
    assert result_frame.co2e_total_kg == 1268740.0
