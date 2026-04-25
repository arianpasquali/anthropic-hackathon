"""Test contract: given chapter impact metrics and buyer preferences, return
EUR allocation per chapter such that:
- Sum of allocations equals the input EUR amount
- Each chapter weight reflects the blended preference axes
- Per-axis weights are returned for transparency
"""

import pytest

from app.services.allocation_engine import (
    AllocationPreferences,
    ChapterSnapshot,
    compute_allocation,
)


@pytest.fixture
def five_chapters() -> list[ChapterSnapshot]:
    """The simulation's five chapters."""
    return [
        ChapterSnapshot(
            id="VB-AMS-OOST",
            net_avoided_tco2e=274.0,
            households_served_quarter=4940,
            needs_score=0.78,
            regional_bonus=1.0,
            total_tonnes=162.5,
        ),
        ChapterSnapshot(
            id="VB-RDM-ZUID",
            net_avoided_tco2e=247.0,
            households_served_quarter=5460,
            needs_score=0.92,
            regional_bonus=1.0,
            total_tonnes=145.6,
        ),
        ChapterSnapshot(
            id="VB-LEI-CTR",
            net_avoided_tco2e=174.5,
            households_served_quarter=3120,
            needs_score=0.61,
            regional_bonus=1.0,
            total_tonnes=101.4,
        ),
        ChapterSnapshot(
            id="VB-FRL-NRD",
            net_avoided_tco2e=64.8,
            households_served_quarter=1235,
            needs_score=0.71,
            regional_bonus=1.15,
            total_tonnes=44.2,
        ),
        ChapterSnapshot(
            id="VB-EHV-CTR",
            net_avoided_tco2e=199.2,
            households_served_quarter=3705,
            needs_score=0.68,
            regional_bonus=1.0,
            total_tonnes=118.3,
        ),
    ]


class TestAllocationEngine:
    def test_allocation_sums_to_amount(self, five_chapters):
        """Total allocated EUR must equal commitment amount within EUR 1."""
        prefs = AllocationPreferences(
            max_climate_impact=0.4,
            max_social_need=0.4,
            balanced_distribution=0.2,
        )
        result = compute_allocation(five_chapters, prefs, 100_000)
        total = sum(r.amount_eur for r in result.values())
        assert abs(total - 100_000) < 1.0

    def test_blended_allocation_matches_simulation(self, five_chapters):
        """Regression: with blended 40/40/20 prefs and EUR 100k,
        Rotterdam-Zuid receives ~EUR 29,400 and Friesland ~EUR 7,070
        (within EUR 200 tolerance — derived from the snapshot fixture).
        """
        prefs = AllocationPreferences(
            max_climate_impact=0.4,
            max_social_need=0.4,
            balanced_distribution=0.2,
        )
        result = compute_allocation(five_chapters, prefs, 100_000)
        assert abs(result["VB-RDM-ZUID"].amount_eur - 29_430) < 200
        assert abs(result["VB-FRL-NRD"].amount_eur - 7_070) < 200

    def test_climate_only_reduces_rural_allocation(self, five_chapters):
        """100% climate preference drops Friesland under 7% (climate-light)."""
        prefs = AllocationPreferences(
            max_climate_impact=1.0,
            max_social_need=0.0,
            balanced_distribution=0.0,
        )
        result = compute_allocation(five_chapters, prefs, 100_000)
        assert result["VB-FRL-NRD"].weight < 0.07

    def test_social_only_includes_regional_bonus(self, five_chapters):
        """100% social preference boosts Friesland via 1.15x regional multiplier."""
        prefs_social = AllocationPreferences(
            max_climate_impact=0.0,
            max_social_need=1.0,
            balanced_distribution=0.0,
        )
        prefs_climate = AllocationPreferences(
            max_climate_impact=1.0,
            max_social_need=0.0,
            balanced_distribution=0.0,
        )
        result_social = compute_allocation(five_chapters, prefs_social, 100_000)
        result_climate = compute_allocation(five_chapters, prefs_climate, 100_000)
        assert result_social["VB-FRL-NRD"].weight > result_climate["VB-FRL-NRD"].weight

    def test_axis_weights_are_returned(self, five_chapters):
        """Each chapter result includes per-axis weights for transparency."""
        prefs = AllocationPreferences(0.4, 0.4, 0.2)
        result = compute_allocation(five_chapters, prefs, 100_000)
        for r in result.values():
            assert "climate" in r.axis_weights
            assert "social" in r.axis_weights
            assert "balanced" in r.axis_weights

    def test_preferences_must_sum_to_one(self):
        """Invalid preferences should raise."""
        with pytest.raises(ValueError, match="must sum to 1"):
            AllocationPreferences(
                max_climate_impact=0.5,
                max_social_need=0.4,
                balanced_distribution=0.4,
            )
