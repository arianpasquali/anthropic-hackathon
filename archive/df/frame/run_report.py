"""
End-to-end report generation: bank + sponsor amount → audit-ready markdown.

Run from the repo root:
    .venv/bin/python -m frame.run_report

Set ANTHROPIC_API_KEY first. Without it, the script writes the prompt to
prompt.txt so the team can inspect what would be sent.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from frame import banks, calculator, report


OUT_DIR = Path("out")


def main() -> None:
    OUT_DIR.mkdir(exist_ok=True)

    rotterdam = banks.get("rotterdam")
    calc = calculator.compute(
        bank=rotterdam,
        sponsor_amount_eur=25_000.0,
        quarter="Q2 2026",
        corporate_name="Heineken N.V.",
    )

    if not os.getenv("ANTHROPIC_API_KEY"):
        system, user = report.dry_run(calc)
        (OUT_DIR / "system_prompt.txt").write_text(system)
        (OUT_DIR / "user_message.txt").write_text(user)
        print("ANTHROPIC_API_KEY not set — wrote prompt to out/{system_prompt,user_message}.txt")
        print("Set the env var and re-run to generate the actual report:")
        print("    export ANTHROPIC_API_KEY=sk-ant-...")
        print(f"    .venv/bin/python -m frame.run_report")
        sys.exit(0)

    print(f"Generating report: {calc.corporate_name} → {calc.bank.name} ({calc.quarter})")
    md = report.generate(calc)
    out_path = OUT_DIR / f"{calc.bank.id}-{calc.quarter.lower().replace(' ', '-')}.md"
    out_path.write_text(md)
    print(f"Report written: {out_path} ({len(md):,} chars)")
    print()
    print("--- First 60 lines ---")
    print("\n".join(md.splitlines()[:60]))


if __name__ == "__main__":
    main()
