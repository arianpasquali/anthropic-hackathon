import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from src.backend.models.enums import RegionEnum, StatusEnum, TemplateEnum, ImpactProfileEnum


class Package(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(index=True)
    description: str | None = None
    region: RegionEnum
    price_eur: float = 25000.0
    co2e_claim_kg: float = 600000.0
    impact_profile: ImpactProfileEnum = ImpactProfileEnum.balanced
    top_n: int = 50
    is_active: bool = True


class PackageFoodbank(SQLModel, table=True):
    package_id: uuid.UUID = Field(foreign_key="package.id", primary_key=True)
    foodbank_id: uuid.UUID = Field(foreign_key="foodbank.id", primary_key=True)
    weight_pct: float | None = None


class FundSubscription(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    package_id: uuid.UUID = Field(foreign_key="package.id", index=True)
    amount_eur: float
    status: StatusEnum = StatusEnum.pending
    solvimon_id: str | None = None
    purchased_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    csr_report_id: uuid.UUID | None = Field(default=None, foreign_key="csrreport.id")


class CsrReport(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="fundsubscription.id")
    frame_result_id: uuid.UUID = Field(foreign_key="frameresult.id")
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    file_path: str
    template: TemplateEnum = TemplateEnum.generic
