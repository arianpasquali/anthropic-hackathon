import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from src.backend.models.enums import IngestionStatus


class IngestionRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    file_path: str = Field(index=True, unique=True)
    bank_name: str
    year: int
    model: str
    status: IngestionStatus = IngestionStatus.pending
    started_at: datetime | None = None
    completed_at: datetime | None = None
    error: str | None = Field(default=None, max_length=2000)
    report_id: uuid.UUID | None = Field(default=None, foreign_key="annualreport.id")
    missing_fields: str | None = Field(default=None)  # JSON list of "section.field" keys
