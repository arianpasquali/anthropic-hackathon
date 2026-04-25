"""Tests for the deterministic parts of report generation.

LLM-dependent narrative sections are isolated and tested separately with
mocked clients; they're not exercised here.
"""

from datetime import date

from app.services.llm_client import StubLLMClient
from app.services.report_generator import (
    BuyerInfo,
    assemble_report_data_from_seed,
    build_executive_summary_prompt,
    extract_numbers,
    generate_executive_summary,
    render_audit_appendix,
    render_full_report_markdown,
    render_methodology_section,
)
from tests.fixtures import load_simulation_seed


class TestMethodologySection:
    def test_methodology_section_is_deterministic(self):
        a = render_methodology_section("KKM-2026.1")
        b = render_methodology_section("KKM-2026.1")
        assert a == b

    def test_methodology_section_cites_sources(self):
        section = render_methodology_section("KKM-2026.1")
        assert "Poore & Nemecek 2018" in section
        assert "EPA WARM v15" in section
        assert "DEFRA 2024" in section
        assert "KKM-2026.1" in section

    def test_methodology_section_versions_distinguish(self):
        a = render_methodology_section("KKM-2026.1")
        b = render_methodology_section("KKM-2026.2")
        assert a != b


class TestReportAssembly:
    def test_assemble_report_data_from_seed(self):
        """End-to-end seed-driven assembly produces totals consistent with
        the simulation's expected values.
        """
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)

        assert data.buyer.name == "Corporation X"
        assert data.period_start == date(2026, 1, 6)
        assert data.period_end == date(2026, 3, 30)
        assert data.methodology_version == "KKM-2026.1"
        assert len(data.attributions) == 5

        expected = seed["expected_totals"]
        assert abs(data.totals.total_net_avoided_tco2e - expected["corp_x_attributed_tco2e"]) < 0.5
        assert abs(data.totals.total_food_rescued_kg - expected["corp_x_attributed_food_kg"]) < 100
        assert abs(data.totals.total_households_supported - expected["corp_x_attributed_households"]) < 5

    def test_attribution_factors_capped(self):
        """No attribution row may exceed 1.0 even with massive allocation."""
        seed = load_simulation_seed("q1_2026")
        # Mutate allocations to exceed every chapter's cost
        seed = {**seed, "corp_x_allocations": {
            cid: 999_999_999 for cid in seed["corp_x_allocations"]
        }}
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)
        for row in data.attributions:
            assert row.attribution_factor == 1.0


class TestAuditAppendix:
    def test_audit_appendix_lists_all_chapters(self):
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)
        appendix = render_audit_appendix(data)

        assert "VB-AMS-OOST" in appendix
        assert "VB-RDM-ZUID" in appendix
        assert "VB-LEI-CTR" in appendix
        assert "VB-FRL-NRD" in appendix
        assert "VB-EHV-CTR" in appendix
        assert "Methodology version" in appendix
        assert "Audit Appendix" in appendix

    def test_audit_appendix_references_buyer_and_period(self):
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)
        appendix = render_audit_appendix(data)
        assert "Corporation X" in appendix
        assert "2026-01-06" in appendix
        assert "2026-03-30" in appendix


class TestExecutiveSummaryGeneration:
    def test_prompt_contains_buyer_and_totals(self):
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)
        prompt = build_executive_summary_prompt(data)

        assert "Corporation X" in prompt
        assert "CSRD" in prompt
        assert "2026-01-06" in prompt
        assert "KKM-2026.1" in prompt
        # net avoided to 1dp must appear in the prompt
        assert f"{data.totals.total_net_avoided_tco2e:.1f}" in prompt

    def test_stub_client_records_call_and_returns_summary(self):
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)
        stub = StubLLMClient()
        summary = generate_executive_summary(data, llm_client=stub)
        assert "[STUB]" in summary
        assert len(stub.calls) == 1
        assert "Corporation X" in stub.calls[0]

    def test_no_hallucinated_numbers_in_stub_output(self):
        """The stub echoes the prompt — every number in the output must
        also exist in the prompt. This is the same invariant we'll apply
        to real LLM output.
        """
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)
        stub = StubLLMClient()
        summary = generate_executive_summary(data, llm_client=stub)
        prompt = build_executive_summary_prompt(data)

        prompt_numbers = extract_numbers(prompt)
        for num in extract_numbers(summary):
            if num in {"", "0"}:
                continue
            assert num in prompt_numbers, f"Number {num!r} not in prompt"


class TestFullReportRender:
    def test_markdown_includes_all_sections(self):
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)
        summary = generate_executive_summary(data, llm_client=StubLLMClient())
        markdown = render_full_report_markdown(data, summary)

        assert "# Quarterly Impact Report — Corporation X" in markdown
        assert "## Executive Summary" in markdown
        assert "## Headline Figures" in markdown
        assert "## Methodology" in markdown
        assert "## Audit Appendix" in markdown
        assert "VB-AMS-OOST" in markdown
        assert "KKM-2026.1" in markdown

    def test_markdown_is_stable_for_same_input(self):
        """Same buyer, same period, same seed, same stub — identical output.
        Drives Invariant 4 (regeneration produces same numbers).
        """
        seed = load_simulation_seed("q1_2026")
        buyer = BuyerInfo(id="corp-x", name="Corporation X", industry="Financial Services")
        data = assemble_report_data_from_seed(seed, buyer)

        a = render_full_report_markdown(
            data,
            generate_executive_summary(data, llm_client=StubLLMClient()),
        )
        b = render_full_report_markdown(
            data,
            generate_executive_summary(data, llm_client=StubLLMClient()),
        )
        assert a == b
