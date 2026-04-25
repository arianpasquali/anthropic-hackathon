# `out/` — Generated artifacts

## Purpose

Holds artifacts produced by the `frame/` pipeline. Everything in this directory is regenerable from source; nothing here should be hand-edited. Treat it as build output.

Two sets of artifacts live here:

1. **Prompt files** — what `frame/run_report.py` would send to Claude. Useful for inspecting the contract before paying for an API call, and for debugging when reports come back wrong.
2. **Generated reports** — Claude-composed audit-grade CSR documents in markdown, one per (bank, quarter) pair.

## Files

| File | Producer | Purpose | Lifecycle |
|---|---|---|---|
| `system_prompt.txt` | `frame.run_report` (always) | Full system prompt sent to Claude — audit-grade reporter spec, no-hallucination contract, exact section layout | Refreshed on every `run_report` invocation |
| `user_message.txt` | `frame.run_report` (always) | User message — JSON payload + pre-rendered factor table + today's date | Refreshed on every `run_report` invocation |
| `rotterdam-q2-2026.md` | `frame.run_report` (when `ANTHROPIC_API_KEY` set) **or** manual | Q2 2026 audit-grade CSR report for Heineken N.V. → Voedselbank Rotterdam | Regenerated when bank data, factors, or prompt change |

The marketplace UI (`web/`) reads `rotterdam-q2-2026.md` from `web/public/reports/` (a copy lives there). Keep both copies in sync when regenerating: `cp out/rotterdam-q2-2026.md web/public/reports/rotterdam-q2-2026.md`.

## How to regenerate

### Prompt files only (no API key needed)

```bash
.venv/bin/python -m frame.run_report
```

Writes `out/system_prompt.txt` and `out/user_message.txt`. Exits without calling Claude when `ANTHROPIC_API_KEY` is not set.

### Full report (API key required)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
.venv/bin/python -m frame.run_report
```

Writes `out/{bank-id}-{quarter}.md` (currently hardcoded to `rotterdam-q2-2026.md` in `run_report.py`).

### Different bank or quarter

Edit the call in `frame/run_report.py:main()`:

```python
bank = banks.get("amsterdam")  # or any bank id from BANKS
calc = calculator.compute(
    bank=bank,
    sponsor_amount_eur=25_000.0,
    quarter="Q3 2026",
    corporate_name="KPN N.V.",
)
```

Output filename is derived from `{bank.id}-{quarter.lower().replace(' ', '-')}.md`.

## Report format contract

Every generated report MUST contain (enforced by the system prompt in `frame/report.py`):

1. `# {Corporate} — Climate-Action Package Impact Report`
2. `## {Quarter} — {Foodbank}`
3. `### Executive Summary` (2-3 paragraphs, ESRS E1 framing)
4. `### Methodology Overview` (1 paragraph, FRAME-aligned-not-certified)
5. `### Quantified Climate Impact (ESRS E1)` (table + prose)
6. `### Social Impact (ESRS S3)` (households, RDC role, cluster banks)
7. `### Category Breakdown` (table)
8. `### Methodology Appendix` with subsections:
   - `#### Calculation Trail` — verbatim methodology trail in code block
   - `#### Emission Factors` — factor table with sources
   - `#### Counterfactual Basis` — quote from `factors.py`
   - `#### Data Sources` — list from payload `sources` field
9. `### Disclaimers and Limitations` (5 bullets)
10. Single-line signature with date and audit contact

The system prompt enforces:
- Every quantitative claim traces to the structured payload
- Methodology trail reproduced verbatim
- UK English, no marketing language, no emojis
- Begins directly at the H1 heading (no preamble)

## When to regenerate

Re-run `frame.run_report` after any of:

- A bank's operational data is updated in `frame/banks.py`
- Emission factors change in `frame/factors.py`
- The NL counterfactual factor changes
- The package economics (`PACKAGE_PRICE_EUR` / `PACKAGE_TCO2E`) change — this is a methodology version bump
- The system prompt in `frame/report.py` is edited

Reports are point-in-time artifacts. The platform commits to regenerating quarterly with refreshed bank data; intermediate edits should be versioned (e.g. `rotterdam-q2-2026-v2.md`) so auditors can trace which snapshot a sponsor cited.

## What does NOT belong here

- Hand-authored markdown (use the project root)
- Bank source PDFs or extracted text (use `data/`)
- Web UI assets (use `web/public/`)
- Plans, specs, architecture docs (use the project root)
