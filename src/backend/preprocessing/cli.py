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

# key = filename stem prefix (lowercase), value = (bank_name, city, region)
BANK_MAP: dict[str, tuple[str, str, RegionEnum]] = {
    "breda":      ("Voedselbank Breda",      "Breda",      RegionEnum.zuid),
    "rotterdam":  ("Voedselbank Rotterdam",  "Rotterdam",  RegionEnum.west),
    "amsterdam":  ("Voedselbank Amsterdam",  "Amsterdam",  RegionEnum.randstad),
    "eindhoven":  ("Voedselbank Eindhoven",  "Eindhoven",  RegionEnum.oost),
    "groningen":  ("Voedselbank Groningen",  "Groningen",  RegionEnum.noord),
    "haaglanden": ("Voedselbank Haaglanden", "Den Haag",   RegionEnum.west),
    "utrecht":    ("Voedselbank Utrecht",    "Utrecht",    RegionEnum.west),
    "tilburg":    ("Voedselbank Tilburg",    "Tilburg",    RegionEnum.zuid),
    "denbosch":   ("Voedselbank Den Bosch",  "Den Bosch",  RegionEnum.zuid),
    "nijmegen":   ("Voedselbank Nijmegen",   "Nijmegen",   RegionEnum.oost),
    "amstelveen": ("Voedselbank Amstelveen", "Amstelveen", RegionEnum.randstad),
    "lelystad":   ("Voedselbank Lelystad",   "Lelystad",   RegionEnum.noord),
    "woerden":    ("Voedselbank Woerden",    "Woerden",    RegionEnum.west),
}


def _year_from_stem(stem: str) -> int | None:
    """Extract 4-digit year from filename stem like 'breda-2025' or 'amsterdam-2024-fin'."""
    for part in stem.split("-"):
        if part.isdigit() and len(part) == 4:
            return int(part)
    return None


def _bank_from_stem(stem: str) -> tuple[str, str, RegionEnum] | None:
    lower = stem.lower()
    for key, info in BANK_MAP.items():
        if lower.startswith(key):
            return info
    return None


@app.command()
def ingest(
    file: Path = typer.Argument(..., help="Path to PDF or .txt report"),
    bank_name: str = typer.Option(..., "--bank-name", help="Full bank name, e.g. 'Voedselbank Breda'"),
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
        logger.error(f"Invalid region '{region}'. Must be one of: {[r.value for r in RegionEnum]}")
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

    logger.info(f"Done — report id={report.id}")


@app.command(name="ingest-dir")
def ingest_dir(
    directory: Path = typer.Argument(..., help="Directory containing PDF/txt files"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Claude model ID"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing reports"),
) -> None:
    """Batch ingest all known reports in a directory."""
    if not directory.is_dir():
        logger.error(f"Not a directory: {directory}")
        raise typer.Exit(code=1)

    # Glob PDFs only — extract_text() automatically uses .txt sidecar if present
    to_process = sorted(directory.glob("*.pdf"))

    create_db_and_tables()

    with Session(engine) as session:
        for file in to_process:
            bank_info = _bank_from_stem(file.stem)
            year = _year_from_stem(file.stem)

            if bank_info is None or year is None:
                logger.warning(f"Skipping {file.name} — no bank/year mapping found")
                continue

            bank_name, city, region_enum = bank_info
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

    logger.info("Batch ingest complete")


if __name__ == "__main__":
    app()
