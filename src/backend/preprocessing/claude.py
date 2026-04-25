import asyncio
import base64
import re
import time
from pathlib import Path
from typing import Any

import anthropic
from loguru import logger
from pydantic import BaseModel, TypeAdapter

from src.backend.preprocessing.extractor import MIN_TEXT_CHARS
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
    source_label: str | None = None,
) -> dict[str, Any]:
    schema_cls = TOOL_SCHEMA_MAP[tool_name]
    system_prompt = SECTION_PROMPTS[tool_name]
    context = f"[{tool_name}]"
    if source_label:
        context = f"{context} [{source_label}]"
    if not text.strip():
        logger.warning(f"{context} empty text — skipping API call")
        return {}

    logger.debug(f"{context} calling {model} ({len(text)} chars)")

    _MAX_DRIFT_RETRIES = 3
    drift_count = 0

    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=[
                    {"name": tool_name, "input_schema": schema_cls.model_json_schema()}
                ],
                tool_choice={"type": "tool", "name": tool_name},
                messages=[
                    {
                        "role": "user",
                        "content": f"<document>\n{text}\n</document>",
                    }
                ],
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
                f"{context} rate limited, retrying in {delay}s (attempt {attempt + 1}/{len(_RETRY_DELAYS)})"
            )
            time.sleep(delay)
            continue
        raw = _extract_tool_input(response)
        logger.debug(
            f"{context} {model} → stop={response.stop_reason} "
            f"in={response.usage.input_tokens} out={response.usage.output_tokens}"
        )
        logger.debug(f"{context} raw output: {raw}")
        if raw is None:
            logger.warning(f"{context} no tool_use block returned, retrying")
            continue
        if detect_drift(raw, schema_cls):
            drift_count += 1
            if drift_count >= _MAX_DRIFT_RETRIES:
                logger.warning(f"{context} schema drift persists after {drift_count} attempts — document likely lacks this data, returning empty")
                return {}
            logger.warning(f"{context} schema drift detected, retrying")
            continue
        return raw

    raise RuntimeError(f"{context} exhausted retries")


def _call_claude_pdf(
    client: anthropic.Anthropic,
    pdf_path: Path,
    tool_name: str,
    model: str,
    source_label: str | None = None,
) -> dict[str, Any]:
    schema_cls = TOOL_SCHEMA_MAP[tool_name]
    system_prompt = SECTION_PROMPTS[tool_name]
    context = f"[{tool_name}]"
    if source_label:
        context = f"{context} [{source_label}]"

    pdf_bytes = Path(pdf_path).read_bytes()
    pdf_b64 = base64.standard_b64encode(pdf_bytes).decode()
    logger.debug(f"{context} sending PDF document ({len(pdf_bytes)} bytes) to {model}")

    _MAX_DRIFT_RETRIES = 3
    drift_count = 0

    for attempt in range(len(_RETRY_DELAYS) + 1):
        try:
            response = client.messages.create(
                model=model,
                max_tokens=2048,
                system=[
                    {
                        "type": "text",
                        "text": system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=[
                    {"name": tool_name, "input_schema": schema_cls.model_json_schema()}
                ],
                tool_choice={"type": "tool", "name": tool_name},
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_b64,
                                },
                            }
                        ],
                    }
                ],
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
                f"{context} rate limited, retrying in {delay}s (attempt {attempt + 1}/{len(_RETRY_DELAYS)})"
            )
            time.sleep(delay)
            continue
        raw = _extract_tool_input(response)
        logger.debug(
            f"{context} {model} → stop={response.stop_reason} "
            f"in={response.usage.input_tokens} out={response.usage.output_tokens}"
        )
        logger.debug(f"{context} raw output: {raw}")
        if raw is None:
            logger.warning(f"{context} no tool_use block returned, retrying")
            continue
        if detect_drift(raw, schema_cls):
            drift_count += 1
            if drift_count >= _MAX_DRIFT_RETRIES:
                logger.warning(f"{context} schema drift persists after {drift_count} attempts — document likely lacks this data, returning empty")
                return {}
            logger.warning(f"{context} schema drift detected, retrying")
            continue
        return raw

    raise RuntimeError(f"{context} exhausted retries (PDF mode)")


def _parse_section(
    raw: dict,
    schema_cls: type[BaseModel],
    source_label: str | None = None,
) -> BaseModel:
    context = f" [{source_label}]" if source_label else ""
    cleaned: dict[str, Any] = {}
    for field_name in schema_cls.model_fields:
        raw_value = raw.get(field_name)
        try:
            if raw_value == "" or raw_value is None:
                cleaned[field_name] = None
                continue
            if isinstance(raw_value, str):
                stripped = raw_value.strip()
                if stripped == "":
                    cleaned[field_name] = None
                    continue
                if field_name.endswith(("_method", "_evidence")):
                    cleaned[field_name] = stripped
                    continue
                if re.fullmatch(r"\d+\s*[-–]\s*\d+", stripped):
                    raise ValueError(f"range value not supported: {stripped}")
                if "%" in stripped and not field_name.endswith("_confidence"):
                    stripped = stripped.replace("%", "")
                stripped = stripped.replace("€", "").replace("\u00a0", " ").strip()
                compact = stripped.replace(" ", "")
                if "," in compact and "." in compact:
                    compact = compact.replace(".", "").replace(",", ".")
                elif "," in compact:
                    compact = compact.replace(",", ".")
                elif re.fullmatch(r"\d{1,3}(?:\.\d{3})+", compact):
                    compact = compact.replace(".", "")
                raw_value = compact if compact else stripped
            if raw_value is not None and (field_name.endswith("pct") or "_pct" in field_name):
                try:
                    pct_value = float(raw_value)
                except (TypeError, ValueError):
                    pct_value = None
                if pct_value is not None and 1 < pct_value <= 100:
                    raw_value = pct_value / 100.0
            cleaned[field_name] = TypeAdapter(
                schema_cls.model_fields[field_name].annotation
            ).validate_python(raw_value)
        except Exception as exc:
            logger.warning(
                f"Validation failed for {schema_cls.__name__}.{field_name}{context}: "
                f"{exc} [input={raw_value!r}] — setting field to null"
            )
            cleaned[field_name] = None
    try:
        return schema_cls.model_validate(cleaned)
    except Exception as e:
        logger.warning(
            f"Validation failed for {schema_cls.__name__}{context}: {e} — returning empty"
        )
        return schema_cls()


async def extract_all(
    text: str,
    model: str = DEFAULT_MODEL,
    source_label: str | None = None,
    pdf_path: Path | None = None,
) -> ExtractionResult:
    client = anthropic.Anthropic()
    loop = asyncio.get_event_loop()

    tool_names = list(TOOL_SCHEMA_MAP.keys())
    context = f" for {source_label}" if source_label else ""

    use_pdf = pdf_path is not None and len(text.strip()) < MIN_TEXT_CHARS
    if use_pdf:
        logger.info(
            f"Sparse text ({len(text.strip())} chars) — falling back to PDF document API{context}"
        )
        call_fn = lambda tool_name: loop.run_in_executor(  # noqa: E731
            None, _call_claude_pdf, client, pdf_path, tool_name, model, source_label
        )
    else:
        logger.info(f"Dispatching {len(tool_names)} parallel extractions with {model}{context}")
        call_fn = lambda tool_name: loop.run_in_executor(  # noqa: E731
            None, _call_claude, client, text, tool_name, model, source_label
        )

    results = await asyncio.gather(*[call_fn(tool_name) for tool_name in tool_names])

    raw_map = dict(zip(tool_names, results))
    logger.info(f"All extractions complete{context}")

    return ExtractionResult(
        food_volume=_parse_section(
            raw_map["extract_food_volume"], FoodVolumeExtraction, source_label
        ),
        food_categories=_parse_section(
            raw_map["extract_food_categories"], FoodCategoriesExtraction, source_label
        ),
        people_served=_parse_section(
            raw_map["extract_people_served"], PeopleServedExtraction, source_label
        ),
        operations=_parse_section(
            raw_map["extract_operations"], OperationsExtraction, source_label
        ),
        donations=_parse_section(
            raw_map["extract_donations"], DonationsExtraction, source_label
        ),
    )
