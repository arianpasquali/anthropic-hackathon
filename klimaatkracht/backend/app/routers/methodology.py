"""Methodology: serve the version banner and the rendered methodology section.

The frontend methodology page reads from this endpoint to keep the prose in
sync with the backend version. Bumping the methodology version on the
backend immediately propagates to the page header.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import settings
from app.services.report_generator import render_methodology_section

router = APIRouter(prefix="/api/methodology", tags=["methodology"])


@router.get("")
def get_methodology() -> dict:
    return {
        "version": settings.methodology_version,
        "section_markdown": render_methodology_section(settings.methodology_version),
    }
