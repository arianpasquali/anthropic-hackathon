import asyncio
import os
import time
from typing import Any

from loguru import logger
from pydantic import BaseModel, ConfigDict

from src.backend.preprocessing.claude import detect_drift
from src.backend.preprocessing.schemas import (
    DonationsExtraction,
    ExtractionResult,
    FoodCategoriesExtraction,
    FoodVolumeExtraction,
    OperationsExtraction,
    PeopleServedExtraction,
    SECTION_PROMPTS,
    TOOL_SCHEMA_MAP,
)

DEFAULT_BASE_URL = os.getenv("ORQ_OPENAI_BASE_URL", "https://api.orq.ai/v3/router")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "openai/gpt-4o")

_RETRY_DELAYS = [1, 2, 5, 10]


class FoodVolumeParse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kg_received_total: float | None = None
    kg_received_total_method: str | None = None
    kg_via_national_dc: float | None = None
    kg_via_national_dc_method: str | None = None
    kg_direct: float | None = None
    kg_direct_method: str | None = None
    waste_pct: float | None = None
    waste_pct_method: str | None = None
    parcels_distributed: int | None = None
    parcels_distributed_method: str | None = None
    avg_products_per_parcel: float | None = None
    avg_products_per_parcel_method: str | None = None
    pct_schijf_van_vijf: float | None = None
    pct_schijf_van_vijf_method: str | None = None
    food_value_eur: float | None = None
    food_value_eur_method: str | None = None


class FoodCategoriesParse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kg_produce: float | None = None
    kg_produce_method: str | None = None
    kg_meat_fish: float | None = None
    kg_meat_fish_method: str | None = None
    kg_dairy_eggs: float | None = None
    kg_dairy_eggs_method: str | None = None
    kg_dry_goods: float | None = None
    kg_dry_goods_method: str | None = None
    kg_bread_bakery: float | None = None
    kg_bread_bakery_method: str | None = None
    kg_prepared: float | None = None
    kg_prepared_method: str | None = None


class PeopleServedParse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    households_weekly: int | None = None
    households_weekly_method: str | None = None
    individuals_total: int | None = None
    individuals_total_method: str | None = None
    children_count: int | None = None
    children_count_method: str | None = None
    pct_under_18: float | None = None
    pct_under_18_method: str | None = None
    pct_single_adults: float | None = None
    pct_single_adults_method: str | None = None
    pct_single_parent: float | None = None
    pct_single_parent_method: str | None = None
    pct_families: float | None = None
    pct_families_method: str | None = None
    pct_couples: float | None = None
    pct_couples_method: str | None = None


class OperationsParse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    volunteers_count: int | None = None
    volunteers_count_method: str | None = None
    distribution_locations: int | None = None
    distribution_locations_method: str | None = None
    satellite_banks_served: int | None = None
    satellite_banks_served_method: str | None = None
    annual_budget_eur: float | None = None
    annual_budget_eur_method: str | None = None
    total_expenditure_eur: float | None = None
    total_expenditure_eur_method: str | None = None


class DonationsParse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    food_supermarket_kg: float | None = None
    food_supermarket_kg_method: str | None = None
    food_company_kg: float | None = None
    food_company_kg_method: str | None = None
    food_dc_kg: float | None = None
    food_dc_kg_method: str | None = None
    money_individuals_eur: float | None = None
    money_individuals_eur_method: str | None = None
    money_companies_eur: float | None = None
    money_companies_eur_method: str | None = None
    money_orgs_eur: float | None = None
    money_orgs_eur_method: str | None = None
    money_government_eur: float | None = None
    money_government_eur_method: str | None = None


PARSE_SCHEMA_MAP: dict[str, type[BaseModel]] = {
    "extract_food_volume": FoodVolumeParse,
    "extract_food_categories": FoodCategoriesParse,
    "extract_people_served": PeopleServedParse,
    "extract_operations": OperationsParse,
    "extract_donations": DonationsParse,
}


def _call_openai_parse(
    text: str,
    tool_name: str,
    model: str,
    base_url: str,
    api_key: str,
) -> dict[str, Any]:
    from openai import OpenAI

    schema_cls = TOOL_SCHEMA_MAP[tool_name]
    parse_cls = PARSE_SCHEMA_MAP[tool_name]
    system_prompt = SECTION_PROMPTS[tool_name]
    if not text.strip():
        logger.warning(f"[{tool_name}] empty text — skipping API call")
        return {}

    client = OpenAI(base_url=base_url, api_key=api_key)
    logger.debug(f"[{tool_name}] calling OpenAI parse model {model} ({len(text)} chars)")

    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            completion = client.chat.completions.parse(
                model=model,
                temperature=0,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text},
                ],
                response_format=parse_cls,
            )
        except Exception as exc:
            if attempt >= len(_RETRY_DELAYS):
                raise
            delay = _RETRY_DELAYS[attempt]
            logger.warning(
                f"[{tool_name}] OpenAI parse failed with {type(exc).__name__}, retrying in {delay}s "
                f"(attempt {attempt + 1}/{len(_RETRY_DELAYS)})"
            )
            time.sleep(delay)
            continue

        message = completion.choices[0].message
        parsed = getattr(message, "parsed", None)
        refusal = getattr(message, "refusal", None)
        if refusal:
            logger.warning(f"[{tool_name}] parse returned refusal: {refusal}")
            return {}
        if parsed is None:
            logger.warning(f"[{tool_name}] parse returned no structured payload, retrying")
            continue
        raw = parsed.model_dump()
        logger.debug(f"[{tool_name}] OpenAI parse raw output: {raw}")
        if detect_drift(raw, schema_cls):
            logger.warning(f"[{tool_name}] schema drift detected, retrying")
            continue
        return raw

    raise RuntimeError(f"[{tool_name}] exhausted retries")


def _parse_section(raw: dict[str, Any], schema_cls: type[BaseModel]) -> BaseModel:
    cleaned = {k: (None if v == "" else v) for k, v in raw.items()}
    try:
        return schema_cls.model_validate(cleaned)
    except Exception as exc:
        logger.warning(
            f"Validation failed for {schema_cls.__name__}: {exc} — returning empty"
        )
        return schema_cls()


async def extract_all_openai_compat(
    text: str,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
) -> ExtractionResult:
    api_key = api_key or os.getenv("ORQ_API_KEY")
    if not api_key:
        raise RuntimeError("ORQ_API_KEY is not set")

    tool_names = list(TOOL_SCHEMA_MAP.keys())
    logger.info(
        f"Dispatching {len(tool_names)} parallel OpenAI parse extractions with model {model}"
    )
    loop = asyncio.get_event_loop()
    results = await asyncio.gather(
        *[
            loop.run_in_executor(
                None, _call_openai_parse, text, tool_name, model, base_url, api_key
            )
            for tool_name in tool_names
        ]
    )

    raw_map = dict(zip(tool_names, results))
    logger.info("OpenAI parse extractions complete")

    return ExtractionResult(
        food_volume=_parse_section(raw_map["extract_food_volume"], FoodVolumeExtraction),
        food_categories=_parse_section(
            raw_map["extract_food_categories"], FoodCategoriesExtraction
        ),
        people_served=_parse_section(
            raw_map["extract_people_served"], PeopleServedExtraction
        ),
        operations=_parse_section(raw_map["extract_operations"], OperationsExtraction),
        donations=_parse_section(raw_map["extract_donations"], DonationsExtraction),
    )
