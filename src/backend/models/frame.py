import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel

from src.backend.models.enums import CounterfactualEnum


class FrameResult(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    report_id: uuid.UUID = Field(foreign_key="annualreport.id", unique=True)

    # Avoided emissions = baseline − leakage (the auditable claim)
    co2e_total_kg: float  # = avoided_co2e_kg; kept for backward compat
    co2e_produce_kg: float
    co2e_meat_fish_kg: float
    co2e_dairy_eggs_kg: float
    co2e_dry_goods_kg: float
    co2e_bread_kg: float
    co2e_prepared_kg: float | None = None

    # Full FRAME breakdown (GFN/Carbon Trust 2024)
    baseline_co2e_kg: float | None = None   # BE before leakage
    leakage_co2e_kg: float | None = None    # LE = foodbank waste
    avoided_co2e_kg: float | None = None    # AE = BE − LE

    counterfactual_route: CounterfactualEnum = CounterfactualEnum.incineration_energy_recovery
    emission_factor_source: str
    methodology_version: str
    computed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
