import asyncio
from dataclasses import dataclass
from pathlib import Path

from src.backend.preprocessing.claude import DEFAULT_MODEL as CLAUDE_MODEL
from src.backend.preprocessing.claude import extract_all
from src.backend.preprocessing.extractor import extract_text
from src.backend.preprocessing.openai_compat import (
    DEFAULT_MODEL as OPENAI_COMPAT_MODEL,
)
from src.backend.preprocessing.openai_compat import extract_all_openai_compat


@dataclass(frozen=True)
class BenchmarkCase:
    path: str
    expected: dict[str, float | int]


CASES = [
    BenchmarkCase(
        path="data/amsterdam-2024.pdf",
        expected={
            "food_categories.kg_produce": 228939,
            "food_volume.parcels_distributed": 72021,
            "food_volume.avg_products_per_parcel": 30,
        },
    ),
    BenchmarkCase(
        path="data/breda-2025.pdf",
        expected={
            "food_volume.kg_received_total": 507496,
            "food_volume.kg_via_national_dc": 152324,
            "food_volume.waste_pct": 0.006,
            "food_volume.parcels_distributed": 17748,
            "food_categories.kg_produce": 185036,
            "food_categories.kg_meat_fish": 30437,
            "food_categories.kg_dairy_eggs": 47819,
        },
    ),
    BenchmarkCase(
        path="data/deventer-2024.pdf",
        expected={
            "food_volume.kg_received_total": 1352527,
            "food_categories.kg_produce": 309000,
            "food_categories.kg_dry_goods": 44188,
        },
    ),
    BenchmarkCase(
        path="data/woerden-2024.pdf",
        expected={
            "donations.money_individuals_eur": 27343.27,
            "donations.money_companies_eur": 36570.45,
            "donations.money_orgs_eur": 33635.52,
            "donations.money_government_eur": 47790.0,
        },
    ),
]


def _flatten(result: object) -> dict[str, float | int | None]:
    flat: dict[str, float | int | None] = {}
    for section_name in (
        "food_volume",
        "food_categories",
        "people_served",
        "operations",
        "donations",
    ):
        section = getattr(result, section_name)
        for field in type(section).model_fields:
            if field.endswith("_method"):
                continue
            flat[f"{section_name}.{field}"] = getattr(section, field)
    return flat


def _matches(actual: float | int | None, expected: float | int) -> bool:
    if actual is None:
        return False
    if isinstance(expected, float):
        return abs(float(actual) - expected) < 1e-9
    return int(actual) == expected


async def _run_case(case: BenchmarkCase) -> tuple[dict[str, float | int | None], dict[str, float | int | None]]:
    text = extract_text(Path(case.path))
    results = await asyncio.gather(
        asyncio.wait_for(extract_all(text, model=CLAUDE_MODEL), timeout=45),
        asyncio.wait_for(
            extract_all_openai_compat(text, model=OPENAI_COMPAT_MODEL), timeout=45
        ),
        return_exceptions=True,
    )
    claude_result, openai_result = results
    if isinstance(claude_result, Exception):
        print(f"  Claude failed: {claude_result}")
        claude_flat: dict[str, float | int | None] = {}
    else:
        claude_flat = _flatten(claude_result)
    if isinstance(openai_result, Exception):
        print(f"  OpenAI-compatible failed: {openai_result}")
        openai_flat: dict[str, float | int | None] = {}
    else:
        openai_flat = _flatten(openai_result)
    return claude_flat, openai_flat


async def main() -> None:
    claude_hits = 0
    openai_hits = 0
    total = 0

    print(f"Benchmark cases: {len(CASES)}")
    print(f"Claude model: {CLAUDE_MODEL}")
    print(f"OpenAI-compatible model: {OPENAI_COMPAT_MODEL}")
    print()

    for case in CASES:
        claude_flat, openai_flat = await _run_case(case)
        print(case.path)
        for field, expected in case.expected.items():
            total += 1
            claude_value = claude_flat.get(field)
            openai_value = openai_flat.get(field)
            claude_ok = _matches(claude_value, expected)
            openai_ok = _matches(openai_value, expected)
            claude_hits += int(claude_ok)
            openai_hits += int(openai_ok)
            print(
                f"  {field}: expected={expected} | "
                f"claude={claude_value} {'OK' if claude_ok else 'MISS'} | "
                f"openai={openai_value} {'OK' if openai_ok else 'MISS'}"
            )
        print()

    print("Summary")
    print(f"  Claude: {claude_hits}/{total}")
    print(f"  OpenAI-compatible: {openai_hits}/{total}")


if __name__ == "__main__":
    asyncio.run(main())
