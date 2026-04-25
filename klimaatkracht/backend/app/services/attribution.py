from dataclasses import dataclass
from datetime import date


@dataclass
class DateRange:
    start: date
    end: date

    def weeks_count(self) -> int:
        return (self.end - self.start).days // 7 + 1


@dataclass
class Attribution:
    commitment_id: str
    chapter_id: str
    attribution_factor: float
    attributed_food_kg: float
    attributed_net_avoided_kgco2e: float
    attributed_households_supported: float
    chapter_total_food_kg: float
    chapter_total_avoided_kgco2e: float
    chapter_quarterly_op_cost_eur: float


@dataclass
class OvercommitmentResult:
    is_overcommitted: bool
    total_allocated_eur: float
    chapter_quarterly_cost_eur: float
    excess_eur: float


def compute_attribution(
    commitment_id: str,
    chapter_id: str,
    allocation_eur: float,
    chapter_quarterly_cost_eur: float,
    chapter_total_food_kg: float,
    chapter_net_avoided_kgco2e: float,
    chapter_households_served_quarter: float,
    period: DateRange,
) -> Attribution:
    """Compute attribution factor and apply to chapter impact.

    Invariant: factor is capped at 1.0. No funder may claim more than 100%
    of a chapter's quarterly impact, regardless of allocation amount.
    """
    del period
    if chapter_quarterly_cost_eur <= 0:
        raise ValueError("chapter_quarterly_cost_eur must be positive")
    factor = min(allocation_eur / chapter_quarterly_cost_eur, 1.0)
    return Attribution(
        commitment_id=commitment_id,
        chapter_id=chapter_id,
        attribution_factor=factor,
        attributed_food_kg=chapter_total_food_kg * factor,
        attributed_net_avoided_kgco2e=chapter_net_avoided_kgco2e * factor,
        attributed_households_supported=chapter_households_served_quarter * factor,
        chapter_total_food_kg=chapter_total_food_kg,
        chapter_total_avoided_kgco2e=chapter_net_avoided_kgco2e,
        chapter_quarterly_op_cost_eur=chapter_quarterly_cost_eur,
    )


def check_chapter_overcommitment(
    chapter_id: str,
    chapter_quarterly_cost_eur: float,
    allocations: list[tuple[str, float]],
) -> OvercommitmentResult:
    """Surface a warning when sum of allocations exceeds chapter cost.

    Allocations stay valid (factors capped at 1.0); the excess EUR must be
    reallocated elsewhere or returned. The chapter coordinator and funders
    both need visibility into the overcommitment.
    """
    del chapter_id
    total_allocated = sum(amount for _, amount in allocations)
    excess = max(total_allocated - chapter_quarterly_cost_eur, 0)
    return OvercommitmentResult(
        is_overcommitted=excess > 0,
        total_allocated_eur=total_allocated,
        chapter_quarterly_cost_eur=chapter_quarterly_cost_eur,
        excess_eur=excess,
    )
