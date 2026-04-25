"""Generate quarterly impact reports.

The LLM-dependent narrative sections (executive summary, narrative impact,
ESRS prose) live behind interfaces that can be mocked in tests. The
deterministic sections — methodology, audit appendix, ESRS index table —
are pure functions over structured input so they're stable and reproducible.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date

from app.services.llm_client import LLMClient, StubLLMClient

METHODOLOGY_TEMPLATE = """
## Methodology

This report applies methodology version **{version}** of the Klimaatkracht
Climate-and-Social Attribution Framework. The framework rests on four data
sources, treated as version-controlled reference assets:

- **CO2e coefficients per food category** are drawn from Poore & Nemecek 2018
  ("Reducing food's environmental impacts through producers and consumers",
  *Science*), adjusted for Dutch supply chain characteristics using WUR
  food-LCA data.
- **Counterfactual avoided emissions** assume the rescued food would have
  been disposed of via mixed-waste landfill or incineration as represented
  in the EPA WARM v15 model.
- **Operational footprint** combines transport (DEFRA 2024 light van
  emission factors) and refrigeration (Klimaatmonitor 2025 Dutch grid
  intensity).
- **Disclosure mappings** trace each metric to its corresponding ESRS E1, E5,
  and S3 disclosure requirement and CSRD double-materiality classification.

Net avoided emissions per chapter are computed as gross category-weighted
avoided emissions minus the operational footprint of moving and storing
the rescued food. Buyer attribution applies a funding-share factor capped
at 1.0 to prevent double-counting across funders contributing to the same
chapter in the same period.
""".strip()


@dataclass
class ReportTotals:
    total_food_rescued_kg: float
    total_net_avoided_tco2e: float
    total_households_supported: float
    total_operational_kgco2e: float


@dataclass
class ChapterAttributionRow:
    chapter_id: str
    chapter_name: str
    period_start: date
    period_end: date
    allocation_eur: float
    chapter_total_food_kg: float
    chapter_net_avoided_kgco2e: float
    chapter_quarterly_op_cost_eur: float
    attribution_factor: float
    attributed_food_kg: float
    attributed_net_avoided_kgco2e: float
    attributed_households_supported: float


@dataclass
class BuyerInfo:
    id: str
    name: str
    industry: str
    csr_framework: str = "CSRD"


@dataclass
class ReportData:
    buyer: BuyerInfo
    period_start: date
    period_end: date
    methodology_version: str
    totals: ReportTotals
    attributions: list[ChapterAttributionRow] = field(default_factory=list)


def render_methodology_section(version: str) -> str:
    """Templated methodology section. Same input produces the same output."""
    return METHODOLOGY_TEMPLATE.format(version=version)


def render_audit_appendix(report_data: ReportData) -> str:
    """Index of every operations record contributing to the report.

    Auditors read this appendix first. Each row links a chapter, its period,
    and its raw aggregate values back to the attribution computation, so a
    third party can recompute the figures without trusting the platform.
    """
    lines: list[str] = []
    lines.append("## Audit Appendix")
    lines.append("")
    lines.append(
        f"Buyer: **{report_data.buyer.name}** ({report_data.buyer.csr_framework}). "
        f"Period: {report_data.period_start.isoformat()} → "
        f"{report_data.period_end.isoformat()}. "
        f"Methodology version: **{report_data.methodology_version}**."
    )
    lines.append("")
    lines.append(
        "| Chapter | Period | Total food (kg) | Net avoided (kgCO2e) | "
        "Op cost (EUR) | Allocation (EUR) | Attribution factor | "
        "Attributed food (kg) | Attributed CO2e (kg) | Attributed households |"
    )
    lines.append(
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"
    )
    for row in report_data.attributions:
        lines.append(
            f"| {row.chapter_id} ({row.chapter_name}) "
            f"| {row.period_start.isoformat()}–{row.period_end.isoformat()} "
            f"| {row.chapter_total_food_kg:,.0f} "
            f"| {row.chapter_net_avoided_kgco2e:,.0f} "
            f"| {row.chapter_quarterly_op_cost_eur:,.2f} "
            f"| {row.allocation_eur:,.2f} "
            f"| {row.attribution_factor:.4f} "
            f"| {row.attributed_food_kg:,.0f} "
            f"| {row.attributed_net_avoided_kgco2e:,.0f} "
            f"| {row.attributed_households_supported:,.1f} |"
        )
    return "\n".join(lines)


def assemble_report_data_from_seed(seed: dict, buyer: BuyerInfo) -> ReportData:
    """Build ReportData from the simulation seed JSON.

    Used by tests and by the demo pre-generation script to produce a
    cached report independent of the database layer. The DB-backed
    counterpart (`assemble_report_data`) lives in the report router and
    pulls the same shape from `attributions` rows.
    """
    period_start = date.fromisoformat(seed["period_start"])
    period_end = date.fromisoformat(seed["period_end"])

    attributions: list[ChapterAttributionRow] = []
    total_food = 0.0
    total_net = 0.0
    total_households = 0.0
    total_operational = 0.0

    for chapter in seed["chapters"]:
        allocation_eur = seed["corp_x_allocations"][chapter["id"]]
        attribution_factor = min(allocation_eur / chapter["quarterly_cost_eur"], 1.0)
        attributed_food = chapter["total_food_kg"] * attribution_factor
        attributed_net = chapter["net_avoided_kgco2e"] * attribution_factor
        attributed_households = chapter["households_quarter"] * attribution_factor

        attributions.append(
            ChapterAttributionRow(
                chapter_id=chapter["id"],
                chapter_name=chapter["name"],
                period_start=period_start,
                period_end=period_end,
                allocation_eur=allocation_eur,
                chapter_total_food_kg=chapter["total_food_kg"],
                chapter_net_avoided_kgco2e=chapter["net_avoided_kgco2e"],
                chapter_quarterly_op_cost_eur=chapter["quarterly_cost_eur"],
                attribution_factor=attribution_factor,
                attributed_food_kg=attributed_food,
                attributed_net_avoided_kgco2e=attributed_net,
                attributed_households_supported=attributed_households,
            )
        )
        total_food += attributed_food
        total_net += attributed_net
        total_households += attributed_households
        total_operational += chapter["operational_kgco2e"] * attribution_factor

    totals = ReportTotals(
        total_food_rescued_kg=total_food,
        total_net_avoided_tco2e=total_net / 1000,
        total_households_supported=total_households,
        total_operational_kgco2e=total_operational,
    )

    return ReportData(
        buyer=buyer,
        period_start=period_start,
        period_end=period_end,
        methodology_version=seed["methodology_version"],
        totals=totals,
        attributions=attributions,
    )


EXECUTIVE_SUMMARY_PROMPT = """\
You are writing the executive summary section of a quarterly climate-and-social
impact report for {buyer_name} ({csr_framework}). Use only the figures below;
do not invent numbers or add unstated context.

Period: {period_start} to {period_end}
Total food rescued: {total_food_kg:,.0f} kg
Net avoided emissions: {total_net_avoided_tco2e:.1f} tCO2e
Households supported: {total_households_supported:,.0f}
Chapters funded: {chapter_count}
Methodology version: {methodology_version}

Write three paragraphs:
1. The buyer's contribution this quarter (use the totals above).
2. How the contribution maps to ESRS E1 (climate) and S3 (social) outcomes.
3. A short forward-looking sentence on the next quarter.
"""


def build_executive_summary_prompt(report_data: ReportData) -> str:
    return EXECUTIVE_SUMMARY_PROMPT.format(
        buyer_name=report_data.buyer.name,
        csr_framework=report_data.buyer.csr_framework,
        period_start=report_data.period_start.isoformat(),
        period_end=report_data.period_end.isoformat(),
        total_food_kg=report_data.totals.total_food_rescued_kg,
        total_net_avoided_tco2e=report_data.totals.total_net_avoided_tco2e,
        total_households_supported=report_data.totals.total_households_supported,
        chapter_count=len(report_data.attributions),
        methodology_version=report_data.methodology_version,
    )


def generate_executive_summary(
    report_data: ReportData,
    llm_client: LLMClient | None = None,
) -> str:
    """Render the executive summary via the LLM client (or stub).

    Defaults to StubLLMClient so callers without an API key still get a
    valid, deterministic output. Pass AnthropicLLMClient for production.
    """
    client = llm_client or StubLLMClient()
    prompt = build_executive_summary_prompt(report_data)
    return client.generate_section(prompt)


_NUMBER_RE = re.compile(r"\d[\d,\.]*")


def extract_numbers(text: str) -> set[str]:
    """Pull every number-looking substring from a block of text.

    Used by the no-hallucination check: every number in generated output
    must also appear (perhaps formatted differently) in the prompt input.
    """
    return {match.group(0).rstrip(".").replace(",", "") for match in _NUMBER_RE.finditer(text)}


def render_full_report_markdown(
    report_data: ReportData,
    executive_summary: str,
) -> str:
    """Stitch the deterministic sections and the LLM-generated summary into
    one Markdown document — the canonical report artifact.
    """
    parts: list[str] = []
    parts.append(f"# Quarterly Impact Report — {report_data.buyer.name}")
    parts.append("")
    parts.append(
        f"**Period:** {report_data.period_start.isoformat()} → "
        f"{report_data.period_end.isoformat()}  "
    )
    parts.append(f"**Methodology version:** {report_data.methodology_version}  ")
    parts.append(f"**Disclosure framework:** {report_data.buyer.csr_framework}")
    parts.append("")
    parts.append("## Executive Summary")
    parts.append("")
    parts.append(executive_summary)
    parts.append("")
    parts.append("## Headline Figures")
    parts.append("")
    parts.append(
        f"- **Food rescued (attributed):** {report_data.totals.total_food_rescued_kg:,.0f} kg"
    )
    parts.append(
        f"- **Net avoided emissions:** {report_data.totals.total_net_avoided_tco2e:.1f} tCO2e"
    )
    parts.append(
        f"- **Households supported:** {report_data.totals.total_households_supported:,.0f}"
    )
    parts.append(
        f"- **Operational footprint included:** "
        f"{report_data.totals.total_operational_kgco2e:,.0f} kgCO2e"
    )
    parts.append("")
    parts.append(render_methodology_section(report_data.methodology_version))
    parts.append("")
    parts.append(render_audit_appendix(report_data))
    return "\n".join(parts)
