import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

import src.backend.models  # noqa: F401
from src.backend.app import app
from src.backend.database import get_session


@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def override_get_session():
        with Session(engine, expire_on_commit=False) as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app, follow_redirects=False) as c:
        yield c
    app.dependency_overrides.clear()
    SQLModel.metadata.drop_all(engine)
