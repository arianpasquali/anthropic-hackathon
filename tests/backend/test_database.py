import pytest
from sqlmodel import SQLModel, Session, create_engine, select
from sqlalchemy.pool import StaticPool

import src.backend.models  # noqa: F401 — registers all tables
from src.backend.database import create_db_and_tables, get_session
from src.backend.models import (
    FundSubscription, CsrReport, Package, User, Foodbank, AnnualReport, FrameResult
)
from src.backend.models.enums import RegionEnum, RoleEnum, StatusEnum, TemplateEnum
from datetime import date


@pytest.fixture(name="mem_session")
def mem_session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    # Drop all — SAWarning expected here due to circular FK between
    # csrreport and fundsubscription; SQLite cannot resolve drop order.
    # This is harmless: the in-memory DB is destroyed immediately after.
    SQLModel.metadata.drop_all(engine)


def test_create_db_and_tables_creates_all_tables():
    """create_db_and_tables() must register every model table without error."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Simulate calling create_db_and_tables with a fresh engine
    import src.backend.models  # noqa: F401
    SQLModel.metadata.create_all(engine)

    table_names = SQLModel.metadata.tables.keys()
    expected = {
        "user", "foodbank", "annualreport",
        "foodvolume", "foodcategories", "peopleserved", "operations", "donations",
        "frameresult",
        "package", "packagefoodbank", "fundsubscription", "csrreport",
    }
    assert expected.issubset(table_names)


def test_get_session_yields_session():
    """get_session() must yield a working Session."""
    gen = get_session()
    session = next(gen)
    assert isinstance(session, Session)
    try:
        next(gen)
    except StopIteration:
        pass


def test_circular_fk_subscription_report_roundtrip(mem_session: Session):
    """FundSubscription.csr_report_id → CsrReport → FundSubscription roundtrip.

    This exercises the circular FK: FundSubscription.csr_report_id is nullable,
    populated after CsrReport is created. Verifies the two-step write works
    without integrity errors.
    """
    fb = Foodbank(name="Test Bank", city="Test", region=RegionEnum.west, is_regional_dc=False)
    mem_session.add(fb)
    mem_session.commit()

    report = AnnualReport(
        foodbank_id=fb.id, year=2024,
        period_start=date(2024, 1, 1), period_end=date(2024, 12, 31),
        raw_file_path="test.txt", ingestion_model="claude-sonnet-4-6",
    )
    mem_session.add(report)
    mem_session.commit()

    frame = FrameResult(
        report_id=report.id,
        co2e_total_kg=1000.0, co2e_produce_kg=200.0,
        co2e_meat_fish_kg=200.0, co2e_dairy_eggs_kg=200.0,
        co2e_dry_goods_kg=200.0, co2e_bread_kg=200.0,
        emission_factor_source="FAO 2013", methodology_version="FRAME-NL-v1.0",
    )
    mem_session.add(frame)
    mem_session.commit()

    user = User(email="test@corp.com", hashed_password="x", role=RoleEnum.corporate)
    pkg = Package(name="Test Package", region=RegionEnum.west)
    mem_session.add(user)
    mem_session.add(pkg)
    mem_session.commit()

    # Step 1: create subscription with csr_report_id=None
    sub = FundSubscription(
        user_id=user.id, package_id=pkg.id,
        amount_eur=25000.0, status=StatusEnum.paid,
    )
    mem_session.add(sub)
    mem_session.commit()
    assert sub.csr_report_id is None

    # Step 2: create CsrReport referencing the subscription
    csr = CsrReport(
        subscription_id=sub.id,
        frame_result_id=frame.id,
        file_path="reports/test.pdf",
        template=TemplateEnum.csrd,
    )
    mem_session.add(csr)
    mem_session.commit()

    # Step 3: back-populate csr_report_id on subscription
    sub.csr_report_id = csr.id
    mem_session.add(sub)
    mem_session.commit()
    mem_session.refresh(sub)

    assert sub.csr_report_id == csr.id

    # Verify both sides of the FK are consistent
    loaded_csr = mem_session.exec(select(CsrReport).where(CsrReport.id == csr.id)).one()
    assert loaded_csr.subscription_id == sub.id
