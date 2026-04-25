import uuid
from sqlmodel import Field, SQLModel


class Allocation(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    subscription_id: uuid.UUID = Field(foreign_key="fundsubscription.id", index=True)
    foodbank_id: uuid.UUID = Field(foreign_key="foodbank.id", index=True)
    weight_pct: float
