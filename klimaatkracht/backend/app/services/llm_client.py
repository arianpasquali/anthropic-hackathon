"""Thin Anthropic client wrapper with a swappable interface.

Tests use the StubLLMClient — deterministic, no network. Production code
uses AnthropicLLMClient which talks to the real API. The interface stays
narrow on purpose: one method, `generate_section(prompt: str) -> str`.
"""

from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    def generate_section(self, prompt: str) -> str: ...


class StubLLMClient:
    """In-process stub used by tests and the offline demo path.

    Echoes the structured numbers from the prompt back as a one-paragraph
    summary, so downstream "no hallucinated numbers" checks can verify
    every number in the output also appears in the input.
    """

    def __init__(self, marker: str = "STUB") -> None:
        self.marker = marker
        self.calls: list[str] = []

    def generate_section(self, prompt: str) -> str:
        self.calls.append(prompt)
        return (
            f"[{self.marker}] Quarterly impact summary generated from the "
            f"structured input below.\n\n{prompt[:200]}"
        )


class AnthropicLLMClient:
    """Real Anthropic SDK client. Imported lazily so tests don't need the API key."""

    def __init__(self, api_key: str, model: str = "claude-sonnet-4-6") -> None:
        from anthropic import Anthropic

        self._client = Anthropic(api_key=api_key)
        self._model = model

    def generate_section(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if hasattr(block, "text"))
