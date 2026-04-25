from pydantic import BaseModel

from src.backend.preprocessing.claude import detect_drift
from src.backend.preprocessing.schemas import (
    FoodVolumeExtraction,
    PeopleServedExtraction,
)


def test_detect_drift_no_drift():
    raw = {
        "households_weekly": 335,
        "individuals_total": 2046,
        "pct_under_18": 0.157,
    }
    assert detect_drift(raw, PeopleServedExtraction) is False


def test_detect_drift_wrong_schema():
    # Haiku returned food_volume fields for a people_served call
    raw = {
        "kg_received_total": 507496,
        "waste_pct": 0.006,
        "parcels_distributed": 17748,
    }
    assert detect_drift(raw, PeopleServedExtraction) is True


def test_detect_drift_empty_result():
    # All nulls — Claude found nothing; this is not drift, just no data
    assert detect_drift({}, PeopleServedExtraction) is False


def test_detect_drift_partial_overlap():
    # 1 out of 3 keys matches — below 50% threshold → drift
    raw = {
        "households_weekly": 335,   # correct field
        "kg_received_total": 507496,  # wrong field
        "waste_pct": 0.006,           # wrong field
    }
    assert detect_drift(raw, PeopleServedExtraction) is True


def test_detect_drift_majority_correct():
    # 3 out of 4 keys match → not drift
    raw = {
        "households_weekly": 335,
        "individuals_total": 2046,
        "children_count": 321,
        "kg_received_total": None,  # stray field but only 1 of 4
    }
    assert detect_drift(raw, PeopleServedExtraction) is False
