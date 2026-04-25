"""Shared test fixtures.

Provides an in-memory SQLite database with all tables created and the demo
chapters seeded from the simulation fixture. Tests that need persistence
declare `db_session` as a parameter.
"""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
import app.models as models  # noqa: F401 — register tables on Base.metadata
from tests.fixtures import load_simulation_seed


@pytest.fixture
def db_engine():
    """SQLite in-memory engine that shares one connection across the test.

    A vanilla `sqlite:///:memory:` engine creates a fresh database per
    connection — Base.metadata.create_all writes to one DB, the session
    reads from another, and tables appear missing. StaticPool plus
    `check_same_thread=False` pins all access to a single connection.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        future=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Session:
    Session_ = sessionmaker(bind=db_engine, future=True, expire_on_commit=False)
    session = Session_()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seeded_db(db_session: Session) -> Session:
    """A db_session pre-populated with the five demo chapters and a fund."""
    from datetime import date

    from app.models import Chapter, Fund

    seed = load_simulation_seed("q1_2026")
    for chapter in seed["chapters"]:
        db_session.add(
            Chapter(
                id=chapter["id"],
                name=chapter["name"],
                type="urban" if "CTR" in chapter["id"] or "OOST" in chapter["id"] or "ZUID" in chapter["id"] else "rural",
                households_served_per_week=int(chapter["households_quarter"] / 13),
                needs_score=chapter["needs_score"],
                regional_bonus=chapter["regional_bonus"],
                operational_footprint_kgco2e_per_tonne=chapter["operational_footprint_per_tonne"],
                cost_per_household_per_week_eur=10.80,
            )
        )

    db_session.add(
        Fund(
            id="demo-fund-q1-2026",
            name="Klimaatkracht Q1 2026",
            period_start=date(2026, 1, 6),
            period_end=date(2026, 3, 30),
            methodology_version=seed["methodology_version"],
        )
    )
    db_session.commit()
    return db_session
