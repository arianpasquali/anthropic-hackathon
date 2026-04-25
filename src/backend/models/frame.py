import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class FrameResult(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    co2e_total_kg: float
    co2e_produce_kg: float
    co2e_meat_fish_kg: float
    co2e_dairy_eggs_kg: float
    co2e_dry_goods_kg: float
    co2e_bread_kg: float

    emission_factor_source: str
    methodology_version: str
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
