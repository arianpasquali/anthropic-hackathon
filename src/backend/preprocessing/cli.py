import asyncio
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from loguru import logger
from sqlmodel import Session

from src.backend.database import create_db_and_tables, engine
from src.backend.models.enums import RegionEnum
from src.backend.preprocessing.claude import DEFAULT_MODEL, extract_all
from src.backend.preprocessing.extractor import ExtractionError, extract_text
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.preprocessing.db_inspect import app as db_app
from src.backend.preprocessing.writer import write_report
from src.backend.services.frame import compute_frame

load_dotenv()

app = typer.Typer(name="ingest", help="Foodbank report ingestion pipeline", invoke_without_command=True)


@app.callback()
def _default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
app.add_typer(db_app, name="db")

logger.remove()
logger.add(sys.stderr, level="INFO", format="<green>{time:HH:mm:ss}</green> | <level>{level:<7}</level> | {message}")
logger.add("logs/ingest.log", level="DEBUG", rotation="10 MB", retention=5)

# key = filename stem prefix (lowercase, longest-first for matching)
# value = (full_bank_name, city, region)
BANK_MAP: dict[str, tuple[str, str, RegionEnum]] = {
    "amsterdam":      ("Voedselbank Amsterdam",        "Amsterdam",      RegionEnum.randstad),
    "amstelveen":     ("Voedselbank Amstelveen",       "Amstelveen",     RegionEnum.randstad),
    "amersfoort":     ("Voedselbank Amersfoort",       "Amersfoort",     RegionEnum.west),
    "alkmaar":        ("Voedselbank Alkmaar",          "Alkmaar",        RegionEnum.randstad),
    "almere":         ("Voedselbank Almere",           "Almere",         RegionEnum.noord),
    "apeldoorn":      ("Voedselbank Apeldoorn",        "Apeldoorn",      RegionEnum.oost),
    "arnhem":         ("Voedselbank Arnhem",           "Arnhem",         RegionEnum.oost),
    "bergen-op-zoom": ("Voedselbank Bergen op Zoom",   "Bergen op Zoom", RegionEnum.zuidoost),
    "breda":          ("Voedselbank Breda",            "Breda",          RegionEnum.zuidoost),
    "delft":          ("Voedselbank Delft",            "Delft",          RegionEnum.west),
    "denbosch":       ("Voedselbank Den Bosch",        "Den Bosch",      RegionEnum.zuidoost),
    "deventer":       ("Voedselbank Deventer",         "Deventer",       RegionEnum.oost),
    "dordrecht":      ("Voedselbank Dordrecht",        "Dordrecht",      RegionEnum.west),
    "eindhoven":      ("Voedselbank Eindhoven",        "Eindhoven",      RegionEnum.zuidoost),
    "emmen":          ("Voedselbank Zuidoost Drenthe", "Emmen",          RegionEnum.noord),
    "enschede":       ("Voedselbank Enschede",         "Enschede",       RegionEnum.oost),
    "gouda":          ("Voedselbank Gouda",            "Gouda",          RegionEnum.west),
    "groningen":      ("Voedselbank Groningen",        "Groningen",      RegionEnum.noord),
    "haaglanden":     ("Voedselbank Haaglanden",       "Den Haag",       RegionEnum.west),
    "haarlem":        ("Voedselbank Haarlem",          "Haarlem",        RegionEnum.randstad),
    "hengelo":        ("Voedselbank Midden Twente",    "Hengelo",        RegionEnum.oost),
    "hoorn":          ("Voedselbank West-Friesland",   "Hoorn",          RegionEnum.randstad),
    "leeuwarden":     ("Voedselbank Leeuwarden",       "Leeuwarden",     RegionEnum.noord),
    "leiden":         ("Voedselbank Leiden",           "Leiden",         RegionEnum.west),
    "lelystad":       ("Voedselbank Lelystad",         "Lelystad",       RegionEnum.noord),
    "nijmegen":       ("Voedselbank Nijmegen",         "Nijmegen",       RegionEnum.oost),
    "oss":            ("Voedselbank Oss",              "Oss",            RegionEnum.zuidoost),
    "roermond":       ("Voedselbank Midden-Limburg",   "Roermond",       RegionEnum.zuidoost),
    "rotterdam":      ("Voedselbank Rotterdam",        "Rotterdam",      RegionEnum.west),
    "tilburg":        ("Voedselbank Tilburg",          "Tilburg",        RegionEnum.zuidoost),
    "utrecht":        ("Voedselbank Utrecht",          "Utrecht",        RegionEnum.west),
    "veenendaal":     ("Voedselbank Veenendaal",       "Veenendaal",     RegionEnum.west),
    "venlo":          ("Voedselbank Venlo",            "Venlo",          RegionEnum.zuidoost),
    "woerden":        ("Voedselbank Woerden",          "Woerden",        RegionEnum.west),
    "zwolle":         ("Voedselbank Zwolle",           "Zwolle",         RegionEnum.oost),
}

# National federation docs — never ingest as individual bank reports
_NATIONAL_PREFIXES = {"jaarverslag", "feiten"}

# Stem parts that indicate financial-only docs (skip; prefer the jaarverslag)
_SKIP_PARTS = {"fin", "jr"}


def _should_skip(stem: str) -> str | None:
    """Return skip reason or None if file should be ingested."""
    lower = stem.lower()
    if any(lower.startswith(p) for p in _NATIONAL_PREFIXES):
        return "national federation document"
    parts = set(lower.split("-"))
    hit = parts & _SKIP_PARTS
    if hit:
        return f"financial-only ({', '.join(hit)})"
    return None


def _year_from_stem(stem: str) -> int | None:
    for part in stem.split("-"):
        if part.isdigit() and len(part) == 4:
            return int(part)
    return None


def _bank_from_stem(stem: str) -> tuple[str, str, RegionEnum] | None:
    lower = stem.lower()
    # Longest key first so "bergen-op-zoom" matches before "bergen"
    for key in sorted(BANK_MAP, key=len, reverse=True):
        if lower.startswith(key):
            return BANK_MAP[key]
    return None


@app.command()
def ingest(
    file: Path = typer.Argument(..., help="Path to PDF or .txt report"),
    bank_name: str = typer.Option(..., "--bank-name", help="Full bank name"),
    city: str = typer.Option(..., "--city", help="City name"),
    region: str = typer.Option(..., "--region", help="Region: noord|oost|zuidoost|zuid|west|randstad"),
    year: int = typer.Option(..., "--year", help="Report year, e.g. 2024"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Claude model ID"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing report"),
) -> None:
    """Ingest a single foodbank annual report."""
    if not file.exists():
        logger.error(f"File not found: {file}")
        raise typer.Exit(code=1)

    try:
        region_enum = RegionEnum(region)
    except ValueError:
        logger.error(f"Invalid region '{region}'. Valid: {[r.value for r in RegionEnum]}")
        raise typer.Exit(code=1)

    try:
        text = extract_text(file)
    except ExtractionError as e:
        logger.error(f"Text extraction failed: {e}")
        raise typer.Exit(code=1)

    logger.info(f"Extracted {len(text)} chars from {file.name}")
    result = asyncio.run(extract_all(text, model=model))

    create_db_and_tables()
    with Session(engine) as session:
        report = write_report(
            session=session,
            foodbank_name=bank_name,
            city=city,
            region=region_enum,
            year=year,
            pdf_path=str(file),
            result=result,
            model=model,
            force=force,
        )
        report_id = report.id
    logger.info(f"Done — report id={report_id}")


@app.command(name="ingest-dir")
def ingest_dir(
    directory: Path = typer.Argument(..., help="Directory containing PDF/txt files"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Claude model ID"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing reports"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print plan without ingesting"),
    max_concurrent: int = typer.Option(10, "--max-concurrent", help="Max parallel file ingestions"),
) -> None:
    """Batch ingest all jaarverslag reports in a directory (skips financial-only and national docs)."""
    if not directory.is_dir():
        logger.error(f"Not a directory: {directory}")
        raise typer.Exit(code=1)

    skipped: list[tuple[str, str]] = []
    queued: list[tuple[Path, tuple[str, str, RegionEnum], int]] = []

    for file in sorted(directory.glob("*.pdf")):
        skip_reason = _should_skip(file.stem)
        if skip_reason:
            skipped.append((file.name, skip_reason))
            continue

        bank_info = _bank_from_stem(file.stem)
        year = _year_from_stem(file.stem)

        if bank_info is None or year is None:
            skipped.append((file.name, "no BANK_MAP entry — add key to cli.py"))
            continue

        queued.append((file, bank_info, year))

    logger.info(f"Plan: {len(queued)} to ingest, {len(skipped)} skipped")
    for name, reason in skipped:
        logger.debug(f"  SKIP {name}: {reason}")

    if dry_run:
        for file, (bank_name, city, _), year in queued:
            typer.echo(f"  WOULD INGEST  {file.name:<35}  →  {bank_name} {year}")
        typer.echo(f"\n  SKIPPED ({len(skipped)}):")
        for name, reason in skipped:
            typer.echo(f"  SKIP          {name:<35}  ({reason})")
        return

    create_db_and_tables()

    # field_name → (found_count, missing_count) across all files
    field_stats: dict[str, list[int]] = {}
    stats_lock = asyncio.Lock()

    def _count_fields(result: "ExtractionResult") -> dict[str, int]:
        counts: dict[str, int] = {}
        for section_name in ("food_volume", "food_categories", "people_served", "operations", "donations"):
            section = getattr(result, section_name)
            for field in type(section).model_fields:
                if field.endswith(("_source", "_method")):
                    continue
                key = f"{section_name}.{field}"
                counts[key] = 0 if getattr(section, field) is None else 1
        return counts

    async def _ingest_one(
        sem: asyncio.Semaphore,
        file: Path,
        bank_name: str,
        city: str,
        region_enum: RegionEnum,
        year: int,
    ) -> None:
        async with sem:
            logger.info(f"Processing {file.name} → {bank_name} {year}")
            try:
                text = extract_text(file)
            except ExtractionError as e:
                logger.error(f"Skipping {file.name}: {e}")
                return
            result = await extract_all(text, model=model)
            with Session(engine) as session:
                write_report(
                    session=session,
                    foodbank_name=bank_name,
                    city=city,
                    region=region_enum,
                    year=year,
                    pdf_path=str(file),
                    result=result,
                    model=model,
                    force=force,
                )
            counts = _count_fields(result)
            async with stats_lock:
                for key, found in counts.items():
                    if key not in field_stats:
                        field_stats[key] = [0, 0]
                    field_stats[key][found] += 1

    async def _run_all() -> None:
        sem = asyncio.Semaphore(max_concurrent)
        tasks = [
            _ingest_one(sem, file, bank_name, city, region_enum, year)
            for file, (bank_name, city, region_enum), year in queued
        ]
        await asyncio.gather(*tasks)

    asyncio.run(_run_all())
    logger.success("Batch ingest complete")

    total = len(queued)
    typer.echo(f"\n{'Field':<45} {'Found':>7} {'Missing':>8} {'Fill%':>7}")
    typer.echo("─" * 72)
    for key in sorted(field_stats):
        missing, found = field_stats[key]
        pct = 100 * found / total if total else 0
        marker = " ◄" if pct == 0 else ""
        typer.echo(f"{key:<45} {found:>7} {missing:>8} {pct:>6.0f}%{marker}")
    typer.echo("─" * 72)


@app.command(name="recalculate-frame")
def recalculate_frame(
    city: str | None = typer.Option(None, "--city", help="Limit to one bank (partial match)"),
    year: int | None = typer.Option(None, "--year", help="Limit to one year"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing FrameResult rows"),
) -> None:
    """Recalculate FRAME CO2e table from FoodCategories / FoodVolume source data."""
    from sqlmodel import select as sql_select

    create_db_and_tables()
    with Session(engine) as session:
        banks = session.exec(sql_select(Foodbank)).all()
        if city:
            city_lower = city.lower()
            banks = [b for b in banks if city_lower in b.city.lower()]
            if not banks:
                logger.error(f"No bank matching '{city}'")
                raise typer.Exit(1)

        reports = session.exec(sql_select(AnnualReport)).all()
        if city:
            bank_ids = {b.id for b in banks}
            reports = [r for r in reports if r.foodbank_id in bank_ids]
        if year:
            reports = [r for r in reports if r.year == year]

        bank_by_id = {b.id: b for b in session.exec(sql_select(Foodbank)).all()}
        ok = skipped = errors = 0

        for report in reports:
            fb = bank_by_id.get(report.foodbank_id)
            label = f"{fb.city if fb else '?'} {report.year}"

            existing = session.exec(
                sql_select(FrameResult).where(FrameResult.report_id == report.id)
            ).first()
            if existing and not force:
                logger.debug(f"Skip {label} — already computed (--force to redo)")
                skipped += 1
                continue
            if existing:
                session.delete(existing)
                session.flush()

            try:
                frame = compute_frame(session, report)
                session.add(frame)
                session.flush()
                logger.info(f"{label}: {frame.co2e_total_kg:,.0f} kg CO2e")
                ok += 1
            except ValueError as e:
                logger.warning(f"{label}: skipped — {e}")
                errors += 1

        session.commit()

    logger.success(f"Done — {ok} computed, {skipped} skipped, {errors} no data")


if __name__ == "__main__":
    app()
