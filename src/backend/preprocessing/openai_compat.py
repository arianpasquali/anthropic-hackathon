import asyncio
import os
import re
import time
from typing import Any

from loguru import logger
from pydantic import BaseModel, TypeAdapter

from src.backend.preprocessing.claude import detect_drift
from src.backend.preprocessing.schemas import (
    DonationsExtraction,
    ExtractionResult,
    FoodCategoriesExtraction,
    FoodVolumeExtraction,
    OperationsExtraction,
    PARSE_SCHEMA_MAP,
    PeopleServedExtraction,
    SECTION_PROMPTS,
    TOOL_SCHEMA_MAP,
)

DEFAULT_BASE_URL = os.getenv("ORQ_OPENAI_BASE_URL", "https://api.orq.ai/v3/router")
FALLBACK_BASE_URL = os.getenv("ORQ_OPENAI_FALLBACK_BASE_URL", "https://api.orq.ai/v2/router")
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "anthropic/claude-sonnet-4-6")

_RETRY_DELAYS = [1, 2, 5, 10]


def _format_request_error(exc: Exception) -> str:
    parts = [type(exc).__name__]
    message = str(exc).strip()
    if message:
        parts.append(message)

    response = getattr(exc, "response", None)
    if response is not None:
        status_code = getattr(response, "status_code", None)
        if status_code is not None:
            parts.append(f"status={status_code}")
        body = None
        for attr in ("text",):
            try:
                value = getattr(response, attr)
                body = value() if callable(value) else value
                if body:
                    break
            except Exception:
                continue
        if body:
            body_str = str(body).strip().replace("\n", " ")
            if len(body_str) > 1000:
                body_str = body_str[:1000] + "...[truncated]"
            parts.append(f"body={body_str}")

    return " | ".join(parts)


def _coerce_field_value(
    schema_cls: type[BaseModel],
    field_name: str,
    value: Any,
) -> Any:
    if value == "":
        return None
    if value is None:
        return None

    field = schema_cls.model_fields[field_name]
    annotation = field.annotation

    if isinstance(value, str):
        stripped = value.strip()
        if stripped == "":
            return None
        if field_name.endswith(("_method", "_evidence")):
            return stripped
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
        value = compact if compact else stripped

    if value is not None and (field_name.endswith("pct") or "_pct" in field_name):
        try:
            pct_value = float(value)
        except (TypeError, ValueError):
            pct_value = None
        if pct_value is not None and 1 < pct_value <= 100:
            value = pct_value / 100.0

    return TypeAdapter(annotation).validate_python(value)


def _call_openai_parse(
    text: str,
    tool_name: str,
    model: str,
    base_url: str,
    api_key: str,
    source_label: str | None = None,
) -> dict[str, Any]:
    from openai import OpenAI

    schema_cls = TOOL_SCHEMA_MAP[tool_name]
    parse_cls = PARSE_SCHEMA_MAP[tool_name]
    system_prompt = SECTION_PROMPTS[tool_name]
    context = f"[{tool_name}]"
    if source_label:
        context = f"{context} [{source_label}]"
    if not text.strip():
        logger.warning(f"{context} empty text — skipping API call")
        return {}

    base_urls = [base_url]
    if FALLBACK_BASE_URL and FALLBACK_BASE_URL != base_url:
        base_urls.append(FALLBACK_BASE_URL)

    last_exc: Exception | None = None
    for idx, candidate_base_url in enumerate(base_urls):
        client = OpenAI(base_url=candidate_base_url, api_key=api_key)
        logger.debug(
            f"{context} calling OpenAI parse model {model} via {candidate_base_url} ({len(text)} chars)"
        )

        for attempt in range(len(_RETRY_DELAYS) + 1):
            try:
                completion = client.chat.completions.parse(
                    model=model,
                    temperature=0,
                    messages=[
                        {
                            "role": "system",
                            "content": [
                                {
                                    "type": "text",
                                    "text": system_prompt,
                                    "cache_control": {"type": "ephemeral"},
                                }
                            ],
                        },
                        {
                            "role": "user",
                            "content": f"<document>\n{text}\n</document>",
                        },
                    ],
                    response_format=parse_cls,
                    extra_body={
                        "retry": {
                            "count": 3,
                            "on_codes": [429, 500, 502, 503, 504],
                        }
                    },
                )
            except Exception as exc:
                last_exc = exc
                has_fallback = idx < len(base_urls) - 1
                suffix = (
                    f"trying fallback {base_urls[idx + 1]}"
                    if has_fallback
                    else "no fallback URLs left"
                )
                logger.warning(
                    f"{context} request failed on {candidate_base_url}: "
                    f"{_format_request_error(exc)}; {suffix}"
                )
                break  # HTTP errors handled by ORQ retry; move to fallback URL

            message = completion.choices[0].message
            if refusal := getattr(message, "refusal", None):
                logger.warning(f"{context} parse returned refusal: {refusal}")
                return {}
            parsed = getattr(message, "parsed", None)
            if parsed is None:
                if attempt >= len(_RETRY_DELAYS):
                    break
                delay = _RETRY_DELAYS[attempt]
                logger.warning(f"{context} no structured payload, retrying in {delay}s")
                time.sleep(delay)
                continue
            raw = parsed.model_dump()
            logger.debug(f"{context} OpenAI parse raw output: {raw}")
            if detect_drift(raw, schema_cls):
                if attempt >= len(_RETRY_DELAYS):
                    break
                delay = _RETRY_DELAYS[attempt]
                logger.warning(f"{context} schema drift detected, retrying in {delay}s")
                time.sleep(delay)
                continue
            return raw

    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"[{tool_name}] exhausted retries")


def _parse_section(
    raw: dict[str, Any],
    schema_cls: type[BaseModel],
    source_label: str | None = None,
) -> BaseModel:
    context = f" [{source_label}]" if source_label else ""
    cleaned: dict[str, Any] = {}
    for field_name in schema_cls.model_fields:
        raw_value = raw.get(field_name)
        try:
            cleaned[field_name] = _coerce_field_value(schema_cls, field_name, raw_value)
        except Exception as exc:
            logger.warning(
                f"Validation failed for {schema_cls.__name__}.{field_name}{context}: "
                f"{exc} [input={raw_value!r}] — setting field to null"
            )
            cleaned[field_name] = None
    try:
        return schema_cls.model_validate(cleaned)
    except Exception as exc:
        logger.warning(
            f"Validation failed for {schema_cls.__name__}{context}: {exc} — returning empty"
        )
        return schema_cls()


async def extract_all_openai_compat(
    text: str,
    model: str = DEFAULT_MODEL,
    base_url: str = DEFAULT_BASE_URL,
    api_key: str | None = None,
    source_label: str | None = None,
) -> ExtractionResult:
    api_key = api_key or os.getenv("ORQ_API_KEY")
    if not api_key:
        raise RuntimeError("ORQ_API_KEY is not set")

    tool_names = list(TOOL_SCHEMA_MAP.keys())
    context = f" for {source_label}" if source_label else ""
    logger.info(
        f"Dispatching {len(tool_names)} parallel OpenAI parse extractions with model {model}{context}"
    )
    loop = asyncio.get_event_loop()
    results = await asyncio.gather(
        *[
            loop.run_in_executor(
                None,
                _call_openai_parse,
                text,
                tool_name,
                model,
                base_url,
                api_key,
                source_label,
            )
            for tool_name in tool_names
        ]
    )

    raw_map = dict(zip(tool_names, results))
    logger.info(f"OpenAI parse extractions complete{context}")

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
