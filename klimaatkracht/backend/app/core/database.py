"""SQLAlchemy engine and session setup.

Uses the database URL from Settings. For local dev this points at the
docker-compose Postgres; in tests, swap via the `DATABASE_URL` env var
(e.g. SQLite in-memory) before importing this module.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(settings.database_url, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
