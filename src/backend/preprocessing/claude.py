import asyncio
import time
from typing import Any

import anthropic
from loguru import logger
from pydantic import BaseModel

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

DEFAULT_MODEL = "claude-sonnet-4-6"


def detect_drift(raw: dict[str, Any], schema: type[BaseModel]) -> bool:
    """Return True if returned keys don't match the target schema (>50% wrong field names)."""
    non_null_keys = {k for k, v in raw.items() if v is not None}
    if not non_null_keys:
        return False
    schema_fields = set(schema.model_fields)
    overlap = non_null_keys & schema_fields
    return len(overlap) / len(non_null_keys) < 0.5


def _call_claude(
    client: anthropic.Anthropic,
    text: str,
    tool_name: str,
    model: str,
) -> dict[str, Any]:
    schema_cls = TOOL_SCHEMA_MAP[tool_name]
    system_prompt = SECTION_PROMPTS[tool_name]
    logger.debug(f"[{tool_name}] calling {model} ({len(text)} chars)")
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
        tools=[{"name": tool_name, "input_schema": schema_cls.model_json_schema()}],
        tool_choice={"type": "tool", "name": tool_name},
        messages=[{"role": "user", "content": text[:20000]}],
    )
    raw = response.content[0].input
    logger.debug(
        f"[{tool_name}] {model} → stop={response.stop_reason} "
        f"in={response.usage.input_tokens} out={response.usage.output_tokens}"
    )
    logger.debug(f"[{tool_name}] raw output: {raw}")
    return raw


def _parse_section(raw: dict, schema_cls: type[BaseModel]) -> BaseModel:
    try:
        return schema_cls.model_validate(raw)
    except Exception as e:
        logger.warning(f"Validation failed for {schema_cls.__name__}: {e} — returning empty")
        return schema_cls()


async def extract_all(text: str, model: str = DEFAULT_MODEL) -> ExtractionResult:
    client = anthropic.Anthropic()
    loop = asyncio.get_event_loop()

    tool_names = list(TOOL_SCHEMA_MAP.keys())
    logger.info(f"Dispatching {len(tool_names)} parallel extractions with {model}")

    results = await asyncio.gather(*[
        loop.run_in_executor(None, _call_claude, client, text, tool_name, model)
        for tool_name in tool_names
    ])

    raw_map = dict(zip(tool_names, results))
    logger.info("All extractions complete")

    return ExtractionResult(
        food_volume=_parse_section(raw_map["extract_food_volume"], FoodVolumeExtraction),
        food_categories=_parse_section(raw_map["extract_food_categories"], FoodCategoriesExtraction),
        people_served=_parse_section(raw_map["extract_people_served"], PeopleServedExtraction),
        operations=_parse_section(raw_map["extract_operations"], OperationsExtraction),
        donations=_parse_section(raw_map["extract_donations"], DonationsExtraction),
    )
