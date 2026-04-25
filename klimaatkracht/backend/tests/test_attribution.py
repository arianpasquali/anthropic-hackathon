"""Test contract: given a commitment, a chapter, and a reporting period,
compute the attribution factor and apply it to the chapter's actual impact.

Critical invariant: sum of attribution factors across all commitments
for a single chapter in a period must be <= 1.0 (no double-counting).
"""

from datetime import date

import pytest

from app.services.attribution import (
    DateRange,
    check_chapter_overcommitment,
    compute_attribution,
)


@pytest.fixture
def q1_period() -> DateRange:
    return DateRange(start=date(2026, 1, 6), end=date(2026, 3, 30))


class TestAttribution:
    def test_partial_funding_attribution_factor(self, q1_period):
        """Chapter quarterly cost: 420 households/wk * EUR 10.80 * 13 weeks = EUR 58,968.
        Allocation: EUR 29,106 → factor 29,106 / 58,968 ≈ 0.4936.
        """
        attr = compute_attribution(
            commitment_id="commit-uuid-1",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=29_106,
            chapter_quarterly_cost_eur=58_968,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        assert abs(attr.attribution_factor - 0.4936) < 0.001
        assert abs(attr.attributed_food_kg - 71_867) < 100
        assert abs(attr.attributed_net_avoided_kgco2e - 121_899) < 200

    def test_attribution_factor_capped_at_one(self, q1_period):
        """No funder may claim more than 100% of a chapter's impact."""
        attr = compute_attribution(
            commitment_id="commit-uuid-1",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=200_000,
            chapter_quarterly_cost_eur=58_968,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        assert attr.attribution_factor == 1.0
        assert attr.attributed_food_kg == 145_600
        assert attr.attributed_net_avoided_kgco2e == 247_000

    def test_no_double_counting_invariant(self, q1_period):
        """Multiple buyers funding the same chapter: combined factors <= 1.0."""
        chapter_cost = 58_968
        attr_a = compute_attribution(
            commitment_id="commit-a",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=25_000,
            chapter_quarterly_cost_eur=chapter_cost,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        attr_b = compute_attribution(
            commitment_id="commit-b",
            chapter_id="VB-RDM-ZUID",
            allocation_eur=30_000,
            chapter_quarterly_cost_eur=chapter_cost,
            chapter_total_food_kg=145_600,
            chapter_net_avoided_kgco2e=247_000,
            chapter_households_served_quarter=5_460,
            period=q1_period,
        )
        assert (attr_a.attribution_factor + attr_b.attribution_factor) <= 1.0

    def test_overcommitted_chapter_warning(self):
        """Sum of allocations > chapter cost → surface warning with excess."""
        result = check_chapter_overcommitment(
            chapter_id="VB-RDM-ZUID",
            chapter_quarterly_cost_eur=58_968,
            allocations=[
                ("commit-a", 30_000),
                ("commit-b", 35_000),
            ],
        )
        assert result.is_overcommitted
        assert result.excess_eur == pytest.approx(6_032, abs=10)

    def test_undercommitted_chapter_not_flagged(self):
        result = check_chapter_overcommitment(
            chapter_id="VB-RDM-ZUID",
            chapter_quarterly_cost_eur=58_968,
            allocations=[("commit-a", 30_000)],
        )
        assert not result.is_overcommitted
        assert result.excess_eur == 0

    def test_zero_chapter_cost_raises(self, q1_period):
        with pytest.raises(ValueError, match="positive"):
            compute_attribution(
                commitment_id="x",
                chapter_id="x",
                allocation_eur=100,
                chapter_quarterly_cost_eur=0,
                chapter_total_food_kg=1,
                chapter_net_avoided_kgco2e=1,
                chapter_households_served_quarter=1,
                period=q1_period,
            )

    def test_corp_x_full_quarter_attribution(self, q1_period):
        """Regression test: Corp X's attribution across 5 chapters must hit
        the documented total within 1%."""
        from tests.fixtures import load_simulation_seed

        seed = load_simulation_seed("q1_2026")
        target_tco2e = seed["expected_totals"]["corp_x_attributed_tco2e"]

        total_attributed = 0.0
        for chapter_data in seed["chapters"]:
            allocation = seed["corp_x_allocations"][chapter_data["id"]]
            attr = compute_attribution(
                commitment_id="corp-x-commit",
                chapter_id=chapter_data["id"],
                allocation_eur=allocation,
                chapter_quarterly_cost_eur=chapter_data["quarterly_cost_eur"],
                chapter_total_food_kg=chapter_data["total_food_kg"],
                chapter_net_avoided_kgco2e=chapter_data["net_avoided_kgco2e"],
                chapter_households_served_quarter=chapter_data["households_quarter"],
                period=q1_period,
            )
            total_attributed += attr.attributed_net_avoided_kgco2e

        assert abs(total_attributed / 1000 - target_tco2e) / target_tco2e < 0.01
