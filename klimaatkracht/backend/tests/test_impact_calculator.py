"""Test contract for impact_calculator.

Inputs: category breakdown (kg by food category), CO2e coefficients,
operational footprint per tonne.
Output: ImpactResult with gross, operational, net, and per-category breakdown.
"""

import pytest

from app.services.impact_calculator import (
    calculate_avoided_emissions,
    calculate_operational_footprint,
)


class TestImpactCalculator:
    def test_empty_intake_yields_zero_impact(self):
        result = calculate_avoided_emissions(
            category_kg={},
            coefficients={"fresh_produce": 1.4},
            operational_footprint_per_tonne=38.0,
        )
        assert result.gross_avoided_kgco2e == 0
        assert result.operational_kgco2e == 0
        assert result.net_avoided_kgco2e == 0

    def test_single_category_calculation(self):
        """1000 kg fresh produce at 1.4 coefficient = 1400 kg gross avoided."""
        result = calculate_avoided_emissions(
            category_kg={"fresh_produce": 1000.0},
            coefficients={"fresh_produce": 1.4},
            operational_footprint_per_tonne=38.0,
        )
        assert result.gross_avoided_kgco2e == 1400.0
        assert result.operational_kgco2e == 38.0
        assert result.net_avoided_kgco2e == 1362.0

    def test_multi_category_aggregation(self):
        """Per-category contributions sum to gross."""
        result = calculate_avoided_emissions(
            category_kg={
                "fresh_produce": 500.0,
                "dairy": 200.0,
                "bread_bakery": 300.0,
            },
            coefficients={
                "fresh_produce": 1.4,
                "dairy": 3.2,
                "bread_bakery": 1.1,
            },
            operational_footprint_per_tonne=38.0,
        )
        assert result.gross_avoided_kgco2e == 1670.0
        assert result.operational_kgco2e == 38.0
        assert result.net_avoided_kgco2e == 1632.0
        assert result.category_contributions == {
            "fresh_produce": 700.0,
            "dairy": 640.0,
            "bread_bakery": 330.0,
        }

    def test_unknown_category_raises_error(self):
        """Unknown category should raise rather than silently zero out."""
        with pytest.raises(KeyError, match="unknown_category"):
            calculate_avoided_emissions(
                category_kg={"unknown_category": 100.0},
                coefficients={"fresh_produce": 1.4},
                operational_footprint_per_tonne=38.0,
            )

    def test_negative_net_when_operational_exceeds_gross(self):
        """Poor-efficiency chapter yields negative net (warning state)."""
        result = calculate_avoided_emissions(
            category_kg={"fresh_produce": 100.0},
            coefficients={"fresh_produce": 1.4},
            operational_footprint_per_tonne=2000.0,
        )
        assert result.gross_avoided_kgco2e == 140.0
        assert result.operational_kgco2e == 200.0
        assert result.net_avoided_kgco2e == -60.0

    def test_simulation_q1_2026_total_matches_seed(self):
        """Regression: sum of net avoided across the 5 simulation chapters
        must hit the documented network total within 1%.
        """
        from tests.fixtures import load_simulation_seed

        seed = load_simulation_seed("q1_2026")
        total_net_avoided = 0.0
        for chapter in seed["chapters"]:
            result = calculate_avoided_emissions(
                category_kg=chapter["category_breakdown"],
                coefficients=seed["coefficients"],
                operational_footprint_per_tonne=chapter["operational_footprint_per_tonne"],
            )
            total_net_avoided += result.net_avoided_kgco2e

        target_tco2e = seed["expected_totals"]["net_avoided_tco2e"]
        assert abs(total_net_avoided / 1000 - target_tco2e) / target_tco2e < 0.01


class TestOperationalFootprint:
    def test_transport_and_refrigeration_combine(self):
        # 1000 km * 0.27 = 270; 500 kWh * 0.27 = 135; total 405
        assert calculate_operational_footprint(
            total_kg=10_000,
            transport_km=1000,
            refrigeration_kwh=500,
        ) == pytest.approx(405.0)

    def test_zero_inputs_yield_zero(self):
        assert calculate_operational_footprint(
            total_kg=0, transport_km=0, refrigeration_kwh=0
        ) == 0
