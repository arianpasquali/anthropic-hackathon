"""
Use Claude PDF vision API to extract kg_received_total for reports that
have no weight data in their text sidecar.
"""
import asyncio
import base64
import json
import os
import re
import sqlite3
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

DB = "foodbank.db"
MODEL = "claude-haiku-4-5-20251001"
MAX_CONCURRENT = 3

SYSTEM_PROMPT = """You extract specific numerical data from Dutch foodbank annual reports.
Return ONLY a JSON object. If data not found, use null.
Tons → kg (multiply by 1000). No units in numbers. Integers only for whole numbers."""

QUESTION = """From this Dutch foodbank annual report, extract:
- "kg_received_total": Total kilograms of food received or distributed this year. Look for patterns:
  "X kilo ontvangen", "X kilo levensmiddelen", "X ton voedsel" (× 1000 = kg),
  "X kilo per week" (× 52 = annual), "X.000 kilo", "X miljoen kilo" (× 1,000,000).
  Common Dutch: "ontvangen", "verdeeld", "verwerkt", "kilo/kilogram/ton/tonne"
- "households_weekly": Households served per week (huishoudens per week/wekelijks)
- "individuals_total": Total persons/individuals served (personen, mensen, individuen)
- "annual_budget_eur": Total income/expenditure in euros (baten, lasten, begroting, budget)

Return JSON: {"kg_received_total": <int|null>, "households_weekly": <int|null>, "individuals_total": <int|null>, "annual_budget_eur": <int|null>}"""


def get_reports_needing_pdf_extraction() -> list[dict]:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT f.name, f.city, ar.id, ar.year, ar.raw_file_path,
          fv.kg_received_total,
          ps.households_weekly, ps.individuals_total,
          op.annual_budget_eur
        FROM foodbank f
        JOIN annualreport ar ON ar.foodbank_id = f.id
        LEFT JOIN foodvolume fv ON fv.report_id = ar.id
        LEFT JOIN peopleserved ps ON ps.report_id = ar.id
        LEFT JOIN operations op ON op.report_id = ar.id
        WHERE fv.kg_received_total IS NULL
        ORDER BY f.name, ar.year
    """)
    results = []
    for r in cur.fetchall():
        missing = []
        if r[5] is None: missing.append("kg_received_total")
        if r[6] is None: missing.append("households_weekly")
        if r[7] is None: missing.append("individuals_total")
        if r[8] is None: missing.append("annual_budget_eur")
        if missing:
            # Find PDF file
            raw_path = Path(r[4])
            pdf_path = raw_path.with_suffix(".pdf") if raw_path.suffix != ".pdf" else raw_path
            if not pdf_path.exists():
                # Try alternatives
                stem = raw_path.stem
                for key in ["jr", "fin", "jv"]:
                    stem = stem.replace(f"-{key}", "")
                candidates = list(Path("data").glob(f"{stem}*.pdf"))
                pdf_path = candidates[0] if candidates else pdf_path
            results.append({
                "name": r[0], "city": r[1], "report_id": r[2],
                "year": r[3], "pdf_path": str(pdf_path), "missing": missing,
            })
    conn.close()
    return results


async def extract_from_pdf(
    client: anthropic.AsyncAnthropic,
    sem: asyncio.Semaphore,
    report: dict,
) -> dict:
    async with sem:
        pdf_path = Path(report["pdf_path"])
        if not pdf_path.exists():
            print(f"  [{report['city']} {report['year']}] PDF not found: {pdf_path}")
            return {}

        pdf_data = base64.standard_b64encode(pdf_path.read_bytes()).decode()
        print(f"Processing {report['city']} {report['year']} via PDF ({pdf_path.name}, {pdf_path.stat().st_size // 1024}KB)")

        for attempt in range(5):
            try:
                response = await client.messages.create(
                    model=MODEL,
                    max_tokens=512,
                    system=SYSTEM_PROMPT,
                    messages=[{
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": pdf_data,
                                },
                            },
                            {"type": "text", "text": QUESTION},
                        ],
                    }],
                )
                raw = response.content[0].text.strip()
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                return json.loads(raw)
            except anthropic.RateLimitError:
                wait = [2, 5, 10, 20, 60][min(attempt, 4)]
                print(f"  [{report['city']} {report['year']}] rate limited, waiting {wait}s")
                await asyncio.sleep(wait)
            except Exception as e:
                print(f"  [{report['city']} {report['year']}] error: {e}")
                return {}
        return {}


FIELD_TABLE = {
    "kg_received_total": ("foodvolume", "kg_received_total"),
    "households_weekly": ("peopleserved", "households_weekly"),
    "individuals_total": ("peopleserved", "individuals_total"),
    "annual_budget_eur": ("operations", "annual_budget_eur"),
}


def write_to_db(report_id: str, field: str, value) -> bool:
    if field not in FIELD_TABLE:
        return False
    table, col = FIELD_TABLE[field]
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(f"SELECT {col} FROM {table} WHERE report_id = ?", (report_id,))
    row = cur.fetchone()
    if row is None or row[0] is not None:
        conn.close()
        return False
    cur.execute(
        f"UPDATE {table} SET {col} = ?, {col}_source = 'extracted', {col}_method = 'claude-pdf-vision' WHERE report_id = ?",
        (value, report_id),
    )
    conn.commit()
    conn.close()
    return True


async def process_report(client, sem, report):
    extracted = await extract_from_pdf(client, sem, report)
    if not extracted:
        print(f"  [{report['city']} {report['year']}] nothing extracted")
        return

    filled = 0
    for field in report["missing"]:
        value = extracted.get(field)
        if value is not None:
            if write_to_db(report["report_id"], field, value):
                print(f"  [{report['city']} {report['year']}] {field} = {value:,}")
                filled += 1
    if filled == 0:
        print(f"  [{report['city']} {report['year']}] no new values written")


async def main():
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    reports = get_reports_needing_pdf_extraction()
    print(f"Processing {len(reports)} reports via PDF vision")
    await asyncio.gather(*[process_report(client, sem, r) for r in reports])

    # Print summary
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM foodvolume WHERE kg_received_total IS NOT NULL")
    filled = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM foodvolume")
    total = cur.fetchone()[0]
    conn.close()
    print(f"\nDone. kg_received_total filled: {filled}/{total}")


if __name__ == "__main__":
    asyncio.run(main())
