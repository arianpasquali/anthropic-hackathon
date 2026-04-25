import pytest
from datetime import date
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

# Import all models so SQLModel.metadata is fully populated before create_all
import src.backend.models.user  # noqa: F401
import src.backend.models.foodbank  # noqa: F401
import src.backend.models.measurements  # noqa: F401
import src.backend.models.frame  # noqa: F401
import src.backend.models.marketplace  # noqa: F401
import src.backend.models.allocation  # noqa: F401
import src.backend.models.profile  # noqa: F401

from src.backend.models.foodbank import Foodbank, AnnualReport
from src.backend.models.enums import RegionEnum
from src.backend.models.profile import ImpactProfile


def _seed_profiles(session: Session) -> None:
    for key, name, co2_w, social_w in [
        ("co2_focus", "CO₂ Impact", 1.0, 0.0),
        ("social_focus", "People Impact", 0.0, 1.0),
        ("balanced", "Balanced", 0.5, 0.5),
    ]:
        session.add(ImpactProfile(key=key, name=name, co2_weight=co2_w, social_weight=social_w))
    session.commit()


@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        _seed_profiles(session)
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="report")
def report_fixture(session: Session) -> AnnualReport:
    fb = Foodbank(name="Test Bank", city="Test", region=RegionEnum.noord, is_regional_dc=False)
    session.add(fb)
    session.commit()
    report = AnnualReport(
        foodbank_id=fb.id,
        year=2024,
        period_start=date(2024, 1, 1),
        period_end=date(2024, 12, 31),
        raw_file_path="test.txt",
        ingestion_model="claude-sonnet-4-6",
    )
    session.add(report)
    session.commit()
    return report
