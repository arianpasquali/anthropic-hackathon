"""Chapters: list available chapters for the buyer fund page."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import Chapter

router = APIRouter(prefix="/api/chapters", tags=["chapters"])


@router.get("")
def list_chapters(db: Session = Depends(get_db)) -> dict:
    chapters = db.execute(select(Chapter).order_by(Chapter.id)).scalars().all()
    return {
        "chapters": [
            {
                "id": c.id,
                "name": c.name,
                "type": c.type,
                "households_served_per_week": c.households_served_per_week,
                "needs_score": float(c.needs_score),
                "regional_bonus": float(c.regional_bonus),
                "operational_footprint_kgco2e_per_tonne": float(
                    c.operational_footprint_kgco2e_per_tonne
                ),
                "cost_per_household_per_week_eur": float(c.cost_per_household_per_week_eur),
            }
            for c in chapters
        ]
    }
