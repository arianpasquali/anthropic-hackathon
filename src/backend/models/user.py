import uuid
from datetime import datetime, timezone
from sqlmodel import Field, SQLModel
from src.backend.models.enums import RoleEnum


class User(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: RoleEnum
    org_name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
