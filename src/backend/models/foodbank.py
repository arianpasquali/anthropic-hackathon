import uuid
from datetime import date, datetime, timezone
from sqlmodel import Field, SQLModel
from src.backend.models.enums import RegionEnum


class Foodbank(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    city: str
    region: RegionEnum
    is_regional_dc: bool = False
    vbn_member_id: str | None = None


class AnnualReport(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    foodbank_id: uuid.UUID = Field(foreign_key="foodbank.id", index=True)
    year: int = Field(index=True)
    period_start: date
    period_end: date
    raw_file_path: str
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ingestion_model: str
