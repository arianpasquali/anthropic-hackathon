from dataclasses import dataclass


@dataclass
class ImpactResult:
    gross_avoided_kgco2e: float
    operational_kgco2e: float
    net_avoided_kgco2e: float
    category_contributions: dict[str, float]


def calculate_avoided_emissions(
    category_kg: dict[str, float],
    coefficients: dict[str, float],
    operational_footprint_per_tonne: float,
) -> ImpactResult:
    """Pure function. No I/O, no globals.

    Raises KeyError if a category has no coefficient — silent zero-out
    would mask data quality issues.
    """
    contributions = {cat: kg * coefficients[cat] for cat, kg in category_kg.items()}
    gross = sum(contributions.values())
    total_kg = sum(category_kg.values())
    operational = (total_kg / 1000) * operational_footprint_per_tonne
    return ImpactResult(
        gross_avoided_kgco2e=gross,
        operational_kgco2e=operational,
        net_avoided_kgco2e=gross - operational,
        category_contributions=contributions,
    )


def calculate_operational_footprint(
    total_kg: float,
    transport_km: float,
    refrigeration_kwh: float,
    transport_factor: float = 0.27,
    grid_intensity: float = 0.27,
) -> float:
    """Operational footprint from raw data.

    Defaults: DEFRA 2024 light van (kg CO2e/km) and Klimaatmonitor 2025
    Dutch grid intensity (kg CO2e/kWh).
    """
    del total_kg
    return (transport_km * transport_factor) + (refrigeration_kwh * grid_intensity)
