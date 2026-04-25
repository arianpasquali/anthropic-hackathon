from dataclasses import dataclass


@dataclass
class AllocationPreferences:
    max_climate_impact: float
    max_social_need: float
    balanced_distribution: float

    def __post_init__(self) -> None:
        total = self.max_climate_impact + self.max_social_need + self.balanced_distribution
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Preferences must sum to 1.0, got {total}")


@dataclass
class ChapterSnapshot:
    id: str
    net_avoided_tco2e: float
    households_served_quarter: float
    needs_score: float
    regional_bonus: float
    total_tonnes: float


@dataclass
class AllocationResult:
    chapter_id: str
    weight: float
    amount_eur: float
    axis_weights: dict[str, float]


def _normalize(d: dict[str, float]) -> dict[str, float]:
    total = sum(d.values())
    if total <= 0:
        return {k: 0.0 for k in d}
    return {k: v / total for k, v in d.items()}


def compute_allocation(
    chapters: list[ChapterSnapshot],
    preferences: AllocationPreferences,
    amount_eur: float,
) -> dict[str, AllocationResult]:
    """Blend three normalized axes into a per-chapter EUR allocation.

    - climate axis: net avoided emissions (rewards efficient chapters)
    - social axis: households × needs × regional bonus (rewards underserved areas)
    - balanced axis: total tonnage (proportional volume)
    """
    climate_w = _normalize({c.id: c.net_avoided_tco2e for c in chapters})
    social_w = _normalize(
        {
            c.id: c.households_served_quarter * c.needs_score * c.regional_bonus
            for c in chapters
        }
    )
    balanced_w = _normalize({c.id: c.total_tonnes for c in chapters})

    blended = {
        c.id: (
            climate_w[c.id] * preferences.max_climate_impact
            + social_w[c.id] * preferences.max_social_need
            + balanced_w[c.id] * preferences.balanced_distribution
        )
        for c in chapters
    }
    blended = _normalize(blended)

    return {
        c.id: AllocationResult(
            chapter_id=c.id,
            weight=blended[c.id],
            amount_eur=amount_eur * blended[c.id],
            axis_weights={
                "climate": climate_w[c.id],
                "social": social_w[c.id],
                "balanced": balanced_w[c.id],
            },
        )
        for c in chapters
    }
