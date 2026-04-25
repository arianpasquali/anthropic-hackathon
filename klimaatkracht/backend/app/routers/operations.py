"""Food bank operational data ingestion endpoint.

Coordinators upload either CSV or Excel; the route normalizes to the same
record shape and returns either a parsed-records preview or a structured
error payload pointing at the offending row/column. Persistence to the
database is a follow-up step (separate confirm endpoint) so the user can
review before committing.
"""

from __future__ import annotations

from io import BytesIO, StringIO

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.operations_ingestor import (
    OperationsRecord,
    ValidationError,
    parse_operations_csv,
    parse_operations_xlsx,
)

router = APIRouter(prefix="/api/operations", tags=["operations"])


def _record_to_dict(record: OperationsRecord) -> dict:
    return {
        "chapter_id": record.chapter_id,
        "period_start": record.period_start.isoformat(),
        "period_end": record.period_end.isoformat(),
        "category_breakdown": record.category_breakdown,
        "total_kg": record.total_kg,
        "households_served": record.households_served,
        "distribution_count": record.distribution_count,
        "transport_km": record.transport_km,
        "refrigeration_kwh": record.refrigeration_kwh,
        "operational_cost_eur": record.operational_cost_eur,
        "submission_method": record.submission_method,
    }


@router.post("/preview")
async def preview_upload(file: UploadFile = File(...)) -> dict:
    """Parse an upload and return validated records without persisting."""
    payload = await file.read()
    filename = (file.filename or "").lower()

    try:
        if filename.endswith(".xlsx"):
            records = parse_operations_xlsx(BytesIO(payload))
        else:
            records = parse_operations_csv(StringIO(payload.decode("utf-8")))
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except UnicodeDecodeError as exc:
        raise HTTPException(
            status_code=400,
            detail={"error": "Could not decode file as UTF-8 CSV; upload as .xlsx instead."},
        ) from exc

    return {
        "count": len(records),
        "records": [_record_to_dict(r) for r in records],
    }
