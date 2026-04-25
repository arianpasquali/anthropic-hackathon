"""
Targeted gap-filler: for each report with missing fields, use Claude to extract
only those specific values and write them directly to the DB.
"""
import asyncio
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
MAX_CONCURRENT = 5

FIELD_DESCRIPTIONS = {
    "kg_received_total": "Total kilograms of food received / distributed in the year (all categories combined). Look for phrases like 'X kilo ontvangen', 'X kilo levensmiddelen', 'X kilo voedsel', 'X ton voedsel' (multiply tons by 1000). Return the number in kg.",
    "households_weekly": "Number of households served per week (huishoudens per week). Look for 'X huishoudens per week', 'X gezinnen per week', 'wekelijks X huishoudens'. If only annual or snapshot figure, use it but note.",
    "individuals_total": "Total number of individual people (persons) served. Look for 'X personen', 'X mensen', 'X individuen'. May be derived from households × avg household size.",
    "volunteers_count": "Number of volunteers (vrijwilligers). Look for 'X vrijwilligers'.",
    "annual_budget_eur": "Annual budget or total income/expenditure in euros. Look for 'begroting X', 'budget X', 'totale baten X', 'totale lasten X', 'omzet X euro'. Return in euros (not thousands).",
}

SYSTEM_PROMPT = """You are a data extraction assistant for Dutch foodbank (voedselbank) annual reports.
Extract ONLY the specific fields listed. Return a JSON object with exactly the requested fields.
If a value is not found in the document, return null for that field.
Return numbers as integers or floats (no units, no thousands separators).
Tons should be converted to kilograms (1 ton = 1000 kg).
Return ONLY the JSON object, nothing else."""


def get_reports_with_missing_fields() -> list[dict]:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        SELECT f.name, f.city, ar.id, ar.year, ar.raw_file_path,
          fv.kg_received_total,
          ps.households_weekly, ps.individuals_total,
          op.volunteers_count, op.annual_budget_eur
        FROM foodbank f
        JOIN annualreport ar ON ar.foodbank_id = f.id
        LEFT JOIN foodvolume fv ON fv.report_id = ar.id
        LEFT JOIN peopleserved ps ON ps.report_id = ar.id
        LEFT JOIN operations op ON op.report_id = ar.id
        ORDER BY f.name, ar.year
    """)
    results = []
    fields = ["kg_received_total", "households_weekly", "individuals_total", "volunteers_count", "annual_budget_eur"]
    for r in cur.fetchall():
        missing = [f for f, v in zip(fields, r[5:]) if v is None]
        if missing:
            results.append({
                "name": r[0], "city": r[1], "report_id": r[2],
                "year": r[3], "file": r[4], "missing": missing,
            })
    conn.close()
    return results


def read_text(file_path: str) -> str:
    p = Path(file_path)
    # Try txt sidecar first
    txt = p.with_suffix(".txt")
    if txt.exists():
        text = txt.read_text(encoding="utf-8").strip()
        if len(text) > 200:
            return text
    if p.suffix.lower() == ".txt" and p.exists():
        return p.read_text(encoding="utf-8")
    return ""


async def extract_fields(
    client: anthropic.AsyncAnthropic,
    sem: asyncio.Semaphore,
    report: dict,
) -> dict[str, float | int | None]:
    async with sem:
        text = read_text(report["file"])
        missing = report["missing"]
        city = report["city"]
        year = report["year"]

        field_specs = "\n".join(
            f'- "{f}": {FIELD_DESCRIPTIONS[f]}' for f in missing
        )
        user_msg = f"""Extract these fields from the {year} annual report of Voedselbank {city}:
{field_specs}

Return JSON with exactly these keys: {json.dumps(missing)}

Document:
{text[:60000]}"""

        for attempt in range(5):
            try:
                response = await client.messages.create(
                    model=MODEL,
                    max_tokens=512,
                    system=SYSTEM_PROMPT,
                    messages=[{"role": "user", "content": user_msg}],
                )
                raw = response.content[0].text.strip()
                # Strip markdown code fences if present
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
                return json.loads(raw)
            except anthropic.RateLimitError:
                wait = [1, 2, 5, 10, 20][min(attempt, 4)]
                print(f"  [{city} {year}] rate limited, waiting {wait}s")
                await asyncio.sleep(wait)
            except Exception as e:
                print(f"  [{city} {year}] error: {e}")
                return {}
        return {}


def write_to_db(report_id: str, field: str, value: float | int) -> None:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    table_map = {
        "kg_received_total": ("foodvolume", "kg_received_total"),
        "households_weekly": ("peopleserved", "households_weekly"),
        "individuals_total": ("peopleserved", "individuals_total"),
        "volunteers_count": ("operations", "volunteers_count"),
        "annual_budget_eur": ("operations", "annual_budget_eur"),
    }

    if field not in table_map:
        return
    table, col = table_map[field]

    # Only update if still null
    cur.execute(f"SELECT {col} FROM {table} WHERE report_id = ?", (report_id,))
    row = cur.fetchone()
    if row is None:
        print(f"  No row in {table} for report_id={report_id}")
        conn.close()
        return
    if row[0] is not None:
        conn.close()
        return

    cur.execute(
        f"UPDATE {table} SET {col} = ?, {col}_source = 'extracted', {col}_method = 'claude-targeted-fill' WHERE report_id = ?",
        (value, report_id),
    )
    conn.commit()
    conn.close()


async def process_report(
    client: anthropic.AsyncAnthropic,
    sem: asyncio.Semaphore,
    report: dict,
) -> None:
    city, year = report["city"], report["year"]
    print(f"Processing {city} {year} — missing: {report['missing']}")

    extracted = await extract_fields(client, sem, report)
    if not extracted:
        print(f"  [{city} {year}] nothing extracted")
        return

    filled = 0
    for field in report["missing"]:
        value = extracted.get(field)
        if value is not None:
            write_to_db(report["report_id"], field, value)
            print(f"  [{city} {year}] {field} = {value}")
            filled += 1

    if filled == 0:
        print(f"  [{city} {year}] no values found in document")


async def main() -> None:
    client = anthropic.AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    sem = asyncio.Semaphore(MAX_CONCURRENT)
    reports = get_reports_with_missing_fields()
    print(f"Found {len(reports)} reports with missing fields")
    await asyncio.gather(*[process_report(client, sem, r) for r in reports])
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
