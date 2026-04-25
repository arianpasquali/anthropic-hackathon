"""Test fixtures and seed data loaders."""

import json
from pathlib import Path

FIXTURE_DIR = Path(__file__).parent


def load_simulation_seed(period: str) -> dict:
    """Load a JSON simulation seed from the fixtures directory.

    The seed contains:
    - coefficients: category → kgCO2e/kg
    - chapters: list of chapter operational records for the period
    - corp_x_allocations: chapter_id → EUR allocated by Corporation X
    """
    path = FIXTURE_DIR / f"simulation_{period}.json"
    return json.loads(path.read_text())
