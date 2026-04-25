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
    if not raw:
        return False
    schema_fields = set(schema.model_fields)
    response_fields = set(raw)
    overlap = response_fields & schema_fields
    return len(overlap) / len(response_fields) < 0.5


_RETRY_DELAYS = [1, 2, 5, 10, 20, 30, 60, 120]


def _extract_tool_input(response: Any) -> dict[str, Any] | None:
    for block in response.content:
        if getattr(block, "type", None) == "tool_use":
            return block.input
    return None


def _call_claude(
    client: anthropic.Anthropic,
    text: str,
    tool_name: str,
    model: str,
) -> dict[str, Any]:
    schema_cls = TOOL_SCHEMA_MAP[tool_name]
    system_prompt = SECTION_PROMPTS[tool_name]
    if not text.strip():
        logger.warning(f"[{tool_name}] empty text — skipping API call")
        return {}

    logger.debug(f"[{tool_name}] calling {model} ({len(text)} chars)")

    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=1024,
                system=system_prompt,
                tools=[
                    {"name": tool_name, "input_schema": schema_cls.model_json_schema()}
                ],
                tool_choice={"type": "tool", "name": tool_name},
                messages=[{"role": "user", "content": text}],
            )
        except anthropic.RateLimitError as exc:
            if attempt >= len(_RETRY_DELAYS):
                raise
            retry_after = None
            try:
                retry_after = float(exc.response.headers.get("retry-after", 0))
            except Exception:
                pass
            delay = max(_RETRY_DELAYS[attempt], retry_after or 0)
            logger.warning(
                f"[{tool_name}] rate limited, retrying in {delay}s (attempt {attempt + 1}/{len(_RETRY_DELAYS)})"
            )
            time.sleep(delay)
            continue
        raw = _extract_tool_input(response)
        logger.debug(
            f"[{tool_name}] {model} → stop={response.stop_reason} "
            f"in={response.usage.input_tokens} out={response.usage.output_tokens}"
        )
        logger.debug(f"[{tool_name}] raw output: {raw}")
        if raw is None:
            logger.warning(f"[{tool_name}] no tool_use block returned, retrying")
            continue
        if detect_drift(raw, schema_cls):
            logger.warning(f"[{tool_name}] schema drift detected, retrying")
            continue
        return raw

    raise RuntimeError(f"[{tool_name}] exhausted retries")


def _parse_section(raw: dict, schema_cls: type[BaseModel]) -> BaseModel:
    cleaned = {k: (None if v == "" else v) for k, v in raw.items()}
    try:
        return schema_cls.model_validate(cleaned)
    except Exception as e:
        logger.warning(
            f"Validation failed for {schema_cls.__name__}: {e} — returning empty"
        )
        return schema_cls()


async def extract_all(text: str, model: str = DEFAULT_MODEL) -> ExtractionResult:
    client = anthropic.Anthropic()
    loop = asyncio.get_event_loop()

    tool_names = list(TOOL_SCHEMA_MAP.keys())
    logger.info(f"Dispatching {len(tool_names)} parallel extractions with {model}")

    results = await asyncio.gather(
        *[
            loop.run_in_executor(None, _call_claude, client, text, tool_name, model)
            for tool_name in tool_names
        ]
    )

    raw_map = dict(zip(tool_names, results))
    logger.info("All extractions complete")

    return ExtractionResult(
        food_volume=_parse_section(
            raw_map["extract_food_volume"], FoodVolumeExtraction
        ),
        food_categories=_parse_section(
            raw_map["extract_food_categories"], FoodCategoriesExtraction
        ),
        people_served=_parse_section(
            raw_map["extract_people_served"], PeopleServedExtraction
        ),
        operations=_parse_section(raw_map["extract_operations"], OperationsExtraction),
        donations=_parse_section(raw_map["extract_donations"], DonationsExtraction),
    )
