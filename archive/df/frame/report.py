"""
Report generation: turn a FRAME calculation payload into an audit-ready
CSR impact report using Claude.

The prompt is engineered around three constraints:
  1. Claude composes narrative — it does not invent numbers. Every figure
     cited in the report must be present in the structured payload.
  2. The output structure mirrors CSRD / ESRS E1 disclosure conventions
     so a Big-4 auditor can drop sections directly into the corporate's
     annual sustainability statement.
  3. The methodology trail is reproduced verbatim in an appendix, with
     every emission factor source cited.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date

from frame.calculator import FrameCalculation, to_report_payload
from frame.factors import EMISSION_FACTORS, factor_table_markdown


SYSTEM_PROMPT = """You are an audit-grade sustainability reporter producing CSR climate-impact disclosures aligned with CSRD / ESRS E1 (climate change) and ESRS S3 (affected communities).

Your primary reader is a Big-4 sustainability auditor.

Strict rules:
- Every quantitative claim must trace to the structured payload provided. Do not introduce numbers that are not in the payload.
- You may translate, frame, contextualise and structure. You may not invent numbers or sources.
- The methodology trail must appear verbatim in the appendix.
- No marketing language. No emojis. Restrained, precise, defensible tone.
- UK English spelling.

Output format: one markdown document, no preamble, no closing commentary. Begin directly with the H1 heading.

Structure (use these exact section headings):

# {Corporate} — Climate-Action Package Impact Report
## {Quarter} — {Foodbank}

### Executive Summary
Two to three paragraphs. State the sponsor, foodbank, package amount, and primary impact figures (attributed tCO2e, kg food rescued, attribution share). Frame the disclosure in CSRD ESRS E1 terms.

### Methodology Overview
One paragraph. State that the report is methodology-aligned with the Global Foodbanking Network's FRAME framework (not certified). Explain pro-rata attribution by package economics. Name the NL counterfactual basis (incineration-with-energy-recovery mix vs. US-default landfill).

### Quantified Climate Impact (ESRS E1)
Tabular and prose. Cover:
- Attributed tCO2e (sponsor's share)
- Attributed kg food rescued
- Attribution share of foodbank annual operations
- Foodbank annual baseline tCO2e
- Weighted emission factor used

### Social Impact (ESRS S3)
Brief Just Transition framing. Cite households served weekly. Cite people served only if `people_served` is non-null in the payload — otherwise omit and rely on households as the canonical metric (do not estimate). If `rdc_satellite_count` is set, mention that the foodbank serves as a regional distribution centre for that many satellite banks. If `cluster_banks` is non-empty, name the alliance banks. Position the sponsorship within the corporate's broader human-rights / affected-communities disclosure.

### Category Breakdown
Markdown table with columns: Category | kg Food (attributed) | tCO2e (attributed) | Emission factor (kg CO2e/kg).

### Methodology Appendix
Subsection "Calculation Trail" — reproduce the methodology_trail field VERBATIM as a code block.
Subsection "Emission Factors" — reproduce the factor table with sources.
Subsection "Counterfactual Basis" — quote the NL counterfactual source.
Subsection "Data Sources" — list all entries from the sources field.

### Disclaimers and Limitations
- Methodology alignment statement (not certification)
- Counterfactual assumption transparency
- Data freshness and quarterly review schedule
- Independent verification status

End with a single-line signature: "Prepared by Climate-Action Packages platform on {date}. Sponsor copy. For audit queries: audit@climate-action-packages.eu"
"""


@dataclass
class ReportRequest:
    payload: dict
    factor_table_md: str
    today_iso: str


def build_user_message(calc: FrameCalculation) -> str:
    payload = to_report_payload(calc)
    return (
        "Generate the CSR impact report from the payload below. "
        "The factor_table_md is provided pre-rendered for use in the "
        "Methodology Appendix → Emission Factors subsection.\n\n"
        f"```json\n{json.dumps(payload, indent=2)}\n```\n\n"
        "Pre-rendered factor table for the Emission Factors subsection:\n\n"
        f"{factor_table_markdown()}\n\n"
        f"Today's date (for signature line): {date.today().isoformat()}"
    )


def generate(
    calc: FrameCalculation,
    model: str = "claude-sonnet-4-6",
    max_tokens: int = 4096,
) -> str:
    """
    Call Claude to compose the report.

    Requires ANTHROPIC_API_KEY in env. The hackathon credit form provides one.
    """
    try:
        import anthropic
    except ImportError as e:
        raise RuntimeError(
            "anthropic SDK not installed. Run: .venv/bin/pip install anthropic"
        ) from e

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY not set. Get one from the Anthropic Console "
            "(hackathon credits form) and: export ANTHROPIC_API_KEY=sk-ant-..."
        )

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_message(calc)}],
    )
    # Concatenate any text blocks
    return "".join(
        block.text for block in message.content if block.type == "text"
    )


def dry_run(calc: FrameCalculation) -> tuple[str, str]:
    """Return (system_prompt, user_message) without calling the API."""
    return SYSTEM_PROMPT, build_user_message(calc)
