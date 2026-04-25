from sqlmodel import SQLModel, Session, create_engine

DATABASE_URL = "sqlite:///./foodbank.db"

engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    # Import all models so SQLModel.metadata is populated before create_all
    import src.backend.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
