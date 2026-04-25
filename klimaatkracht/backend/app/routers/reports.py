"""Reports: fetch a generated report by commitment id."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Report

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{commitment_id}")
def get_report(commitment_id: str, db: Session = Depends(get_db)) -> dict:
    report = (
        db.execute(
            select(Report)
            .where(Report.commitment_id == commitment_id)
            .order_by(Report.generated_at.desc())
        )
        .scalars()
        .first()
    )
    if report is None:
        raise HTTPException(
            status_code=404,
            detail=f"No report yet for commitment {commitment_id}",
        )
    return {
        "report_id": report.id,
        "commitment_id": report.commitment_id,
        "period_start": report.period_start.isoformat(),
        "period_end": report.period_end.isoformat(),
        "methodology_version": report.methodology_version,
        "markdown": report.markdown_content,
        "json_data": report.json_data,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
    }
