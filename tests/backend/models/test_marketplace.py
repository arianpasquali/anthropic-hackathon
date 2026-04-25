import uuid
from datetime import date
from sqlmodel import Session, select
from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import Package, PackageFoodbank, FundSubscription, CsrReport
from src.backend.models.user import User
from src.backend.models.enums import RegionEnum, RoleEnum, StatusEnum, TemplateEnum, ImpactProfileEnum


def _make_user(session: Session) -> User:
    u = User(email="csr@acme.com", hashed_password="x", role=RoleEnum.corporate, org_name="ACME")
    session.add(u)
    session.commit()
    return u


def _make_foodbank(session: Session, name="Test Bank") -> Foodbank:
    fb = Foodbank(name=name, city="Test", region=RegionEnum.west, is_regional_dc=False)
    session.add(fb)
    session.commit()
    return fb


def test_create_package(session: Session):
    fb = _make_foodbank(session)
    pkg = Package(
        name="Rotterdam Climate Package",
        region=RegionEnum.west,
        price_eur=25000.0,
        co2e_claim_kg=600000.0,
        is_active=True,
    )
    session.add(pkg)
    session.commit()

    link = PackageFoodbank(package_id=pkg.id, foodbank_id=fb.id, weight_pct=1.0)
    session.add(link)
    session.commit()

    links = session.exec(select(PackageFoodbank).where(PackageFoodbank.package_id == pkg.id)).all()
    assert len(links) == 1
    assert links[0].foodbank_id == fb.id


def test_create_fund_subscription(session: Session):
    user = _make_user(session)
    fb = _make_foodbank(session, "Rotterdam")
    pkg = Package(name="Rotterdam Package", region=RegionEnum.west, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(pkg)
    session.commit()

    sub = FundSubscription(
        user_id=user.id,
        package_id=pkg.id,
        amount_eur=25000.0,
        status=StatusEnum.paid,
        solvimon_id="solv_abc123",
    )
    session.add(sub)
    session.commit()
    session.refresh(sub)
    assert sub.id is not None
    assert sub.status == StatusEnum.paid
    assert sub.csr_report_id is None  # not yet generated


def test_attach_csr_report_to_subscription(session: Session):
    user = _make_user(session)
    fb = _make_foodbank(session, "Breda")
    pkg = Package(name="Breda Package", region=RegionEnum.zuid, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(pkg)
    session.commit()

    sub = FundSubscription(user_id=user.id, package_id=pkg.id, amount_eur=25000.0, status=StatusEnum.paid)
    session.add(sub)
    session.commit()

    report = AnnualReport(
        foodbank_id=fb.id, year=2024,
        period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
        raw_file_path="test.txt", ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()

    frame = FrameResult(
        report_id=report.id,
        co2e_total_kg=1000000.0, co2e_produce_kg=300000.0,
        co2e_meat_fish_kg=200000.0, co2e_dairy_eggs_kg=200000.0,
        co2e_dry_goods_kg=200000.0, co2e_bread_kg=100000.0,
        emission_factor_source="FAO 2013", methodology_version="FRAME-NL-v1.0",
    )
    session.add(frame)
    session.commit()

    csr = CsrReport(
        subscription_id=sub.id,
        frame_result_id=frame.id,
        file_path="reports/acme-breda-2024.pdf",
        template=TemplateEnum.csrd,
    )
    session.add(csr)
    session.commit()

    # Populate the back-reference on subscription
    sub.csr_report_id = csr.id
    session.add(sub)
    session.commit()
    session.refresh(sub)

    assert sub.csr_report_id == csr.id


def test_cluster_package_multiple_banks(session: Session):
    fb1 = _make_foodbank(session, "Groningen")
    fb2 = _make_foodbank(session, "Leeuwarden")
    pkg = Package(name="North Cluster", region=RegionEnum.noord, price_eur=25000.0, co2e_claim_kg=600000.0)
    session.add(pkg)
    session.commit()

    session.add(PackageFoodbank(package_id=pkg.id, foodbank_id=fb1.id, weight_pct=0.6))
    session.add(PackageFoodbank(package_id=pkg.id, foodbank_id=fb2.id, weight_pct=0.4))
    session.commit()

    links = session.exec(select(PackageFoodbank).where(PackageFoodbank.package_id == pkg.id)).all()
    assert len(links) == 2
    assert sum(l.weight_pct for l in links) == 1.0


def test_package_has_impact_profile(session: Session):
    pkg = Package(
        name="CO2 Package",
        region=RegionEnum.west,
        price_eur=15000.0,
        co2e_claim_kg=300000.0,
        impact_profile=ImpactProfileEnum.co2_focus,
        top_n=10,
    )
    session.add(pkg)
    session.commit()
    session.refresh(pkg)
    assert pkg.impact_profile == ImpactProfileEnum.co2_focus
    assert pkg.top_n == 10


def test_package_impact_profile_defaults_to_balanced(session: Session):
    pkg = Package(name="Default", region=RegionEnum.west, price_eur=5000.0, co2e_claim_kg=100000.0)
    session.add(pkg)
    session.commit()
    session.refresh(pkg)
    assert pkg.impact_profile == ImpactProfileEnum.balanced
    assert pkg.top_n == 50
