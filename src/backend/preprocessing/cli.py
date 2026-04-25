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
from src.backend.preprocessing.writer import write_report

load_dotenv()

app = typer.Typer(name="ingest", help="Foodbank report ingestion pipeline")

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
    with Session(engine) as session:
        for file, (bank_name, city, region_enum), year in queued:
            logger.info(f"Processing {file.name} → {bank_name} {year}")
            try:
                text = extract_text(file)
            except ExtractionError as e:
                logger.error(f"Skipping {file.name}: {e}")
                continue

            result = asyncio.run(extract_all(text, model=model))
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

    logger.success("Batch ingest complete")


if __name__ == "__main__":
    app()
