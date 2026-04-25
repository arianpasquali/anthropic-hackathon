# Ingestion Pipeline — Design Spec

**Date:** 2026-04-25
**Project:** Climate-Action Packages for Dutch Foodbanks
**Stack:** Python 3.13, Typer, pdfplumber, Anthropic SDK, asyncio, SQLModel

---

## Scope

CLI pipeline that reads a foodbank annual report (PDF or pre-extracted .txt), uses Claude to extract all measurement sections in parallel, and writes structured data into the existing SQLModel schema.

---

## Key Decisions

| Decision | Choice |
|---|---|
| Trigger | Typer CLI (`python -m src.backend.preprocessing.cli`) |
| Input | `.txt` sidecar if present, else `pdfplumber` PDF extraction |
| Claude extraction | One async call per measurement section (5 parallel) |
| Response format | Pydantic structured output per section |
| Re-ingestion | Skip by default; `--force` overwrites existing records |
| Provenance | `source=extracted`, `method="claude-<model> from <section> — <citation>"` |

---

## File Map

| File | Responsibility |
|---|---|
| `src/backend/preprocessing/cli.py` | Typer app — entry point, arg parsing, orchestration |
| `src/backend/preprocessing/extractor.py` | Text extraction: .txt sidecar → str, or pdfplumber PDF → str |
| `src/backend/preprocessing/schemas.py` | 5 Pydantic extraction schemas (one per measurement section) |
| `src/backend/preprocessing/claude.py` | Async: 5 parallel Claude calls, returns filled schemas |
| `src/backend/preprocessing/writer.py` | Session → upsert Foodbank, AnnualReport, all 5 measurement tables |

---

## CLI Interface

```bash
# Ingest a single report
python -m src.backend.preprocessing.cli ingest \
  archive/df/data/breda-2025.pdf \
  --bank-name "Voedselbank Breda" \
  --city "Breda" \
  --region "zuid" \
  --year 2025

# Force overwrite existing records
python -m src.backend.preprocessing.cli ingest \
  archive/df/data/breda-2025.pdf \
  --bank-name "Voedselbank Breda" \
  --city "Breda" \
  --region "zuid" \
  --year 2025 \
  --force

# Batch ingest a directory (all PDFs)
python -m src.backend.preprocessing.cli ingest-dir \
  archive/df/data/ \
  --force
```

`ingest-dir` uses a hardcoded mapping (bank name + region per filename stem) since filenames don't embed all metadata.

---

## Text Extraction (`extractor.py`)

```python
def extract_text(pdf_path: Path) -> str:
    txt_path = pdf_path.with_suffix(".txt")
    if txt_path.exists():
        return txt_path.read_text(encoding="utf-8")
    # fallback: pdfplumber
    import pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)
```

---

## Extraction Schemas (`schemas.py`)

Five Pydantic models with all fields optional. Each field has a companion `_method: str | None` (Claude fills with a short citation, e.g. `"PDF p.10 'Ontvangen voedsel 507.496 kilo'"`). No `_source` — that's always `SourceEnum.extracted` when coming from this pipeline.

```python
class FoodVolumeExtraction(BaseModel):
    kg_received_total: float | None = None
    kg_received_total_method: str | None = None
    kg_via_national_dc: float | None = None
    kg_via_national_dc_method: str | None = None
    # ... all FoodVolume fields
    waste_pct: float | None = None
    waste_pct_method: str | None = None

class FoodCategoriesExtraction(BaseModel):
    kg_produce: float | None = None
    kg_produce_method: str | None = None
    # ... all FoodCategories fields

class PeopleServedExtraction(BaseModel):
    households_weekly: int | None = None
    households_weekly_method: str | None = None
    # ... all PeopleServed fields

class OperationsExtraction(BaseModel):
    volunteers_count: int | None = None
    volunteers_count_method: str | None = None
    counterfactual_route: str = "incineration_energy_recovery"
    # ... all Operations fields

class DonationsExtraction(BaseModel):
    food_supermarket_kg: float | None = None
    food_supermarket_kg_method: str | None = None
    # ... all Donations fields
```

---

## Claude Parallel Extraction (`claude.py`)

One `async` function per section, all launched with `asyncio.gather`. Each call:
- System prompt: explains the task, the section to extract, and the NL foodbank domain
- User message: the full extracted text
- Response format: the section's Pydantic schema

```python
async def extract_all(text: str, model: str) -> ExtractionResult:
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(extract_section(text, FoodVolumeExtraction, FOOD_VOLUME_PROMPT, model))
        t2 = tg.create_task(extract_section(text, FoodCategoriesExtraction, FOOD_CATEGORIES_PROMPT, model))
        t3 = tg.create_task(extract_section(text, PeopleServedExtraction, PEOPLE_SERVED_PROMPT, model))
        t4 = tg.create_task(extract_section(text, OperationsExtraction, OPERATIONS_PROMPT, model))
        t5 = tg.create_task(extract_section(text, DonationsExtraction, DONATIONS_PROMPT, model))
    return ExtractionResult(t1.result(), t2.result(), t3.result(), t4.result(), t5.result())
```

Default model: `claude-haiku-4-5-20251001` (cheap, fast for structured extraction). Overridable via `--model` flag.

---

## DB Writer (`writer.py`)

```python
def write_report(
    session: Session,
    foodbank_name: str,
    city: str,
    region: RegionEnum,
    year: int,
    pdf_path: str,
    result: ExtractionResult,
    model: str,
    force: bool = False,
) -> AnnualReport:
```

Steps:
1. `get_or_create` Foodbank by name
2. Check if AnnualReport(foodbank_id, year) exists — skip or delete+recreate based on `force`
3. Create AnnualReport with `raw_file_path`, `ingestion_model`
4. Write FoodVolume, FoodCategories, PeopleServed, Operations, Donations — all nullable fields set, `_source=SourceEnum.extracted`, `_method` from extraction schema

---

## Error Handling

- Extraction schema field = `None` if Claude couldn't find it in the text — no error, just null + null method
- PDF extraction failure (pdfplumber can't parse): raises `ExtractionError`, CLI exits with non-zero code and message
- Claude API error: propagates, CLI shows error + exits non-zero
- `--force` on non-existent record: treated same as fresh ingest

---

## Out of Scope

- FRAME CO2e calculation (separate module, reads from FoodCategories/FoodVolume)
- `ingest-dir` filename→metadata mapping for all 13 banks (hardcoded map for 5 demo banks only)
- Progress bar / rich output (plain typer echo is fine)
- Async DB writes (SQLModel is sync; writer runs after gather completes)
