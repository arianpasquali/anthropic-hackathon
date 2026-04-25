import uuid
from sqlmodel import Field, SQLModel


class ImpactProfile(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    key: str = Field(unique=True, index=True)  # matches ImpactProfileEnum values
    name: str
    description: str | None = None
    co2_weight: float = 0.5
    social_weight: float = 0.5
    is_active: bool = True
