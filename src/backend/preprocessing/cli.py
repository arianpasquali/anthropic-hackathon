import asyncio
import json
import sys
from pathlib import Path

import typer
from dotenv import load_dotenv
from loguru import logger
from sqlmodel import Session, select

from src.backend.database import create_db_and_tables, engine
from src.backend.models import IngestionRecord
from src.backend.models.enums import IngestionStatus, RegionEnum, SourceEnum
from src.backend.preprocessing.claude import DEFAULT_MODEL, extract_all
from src.backend.preprocessing.extractor import MIN_TEXT_CHARS, ExtractionError, extract_text
from src.backend.preprocessing.openai_compat import (
    DEFAULT_MODEL as ORQ_DEFAULT_MODEL,
)
from src.backend.preprocessing.openai_compat import extract_all_openai_compat
from src.backend.models.foodbank import AnnualReport, Foodbank
from datetime import datetime, timezone
from src.backend.models.frame import FrameResult
from src.backend.models.measurements import (
    Donations,
    FoodCategories,
    FoodVolume,
    Operations,
    PeopleServed,
)
from src.backend.preprocessing.db_inspect import app as db_app
from src.backend.preprocessing.regex_extract import (
    extract_all_regex,
    merge_extraction_results,
)
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
    "den-haag":       ("Voedselbank Haaglanden",        "Den Haag",       RegionEnum.west),
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
    "ede":            ("Voedselbank Ede",              "Ede",            RegionEnum.oost),
    "alphen":         ("Voedselbank Alphen",           "Alphen aan den Rijn", RegionEnum.west),
    "schiedam":       ("Voedselbank Schiedam",         "Schiedam",       RegionEnum.west),
    "purmerend":      ("Voedselbank Purmerend",        "Purmerend",      RegionEnum.randstad),
    "almelo":         ("Voedselbank Almelo",           "Almelo",         RegionEnum.oost),
    "denhelder":      ("Voedselbank Den Helder",       "Den Helder",     RegionEnum.randstad),
    "waalwijk":       ("Voedselbank Waalwijk",         "Waalwijk",       RegionEnum.zuidoost),
    "drachten":       ("Voedselbank Smallingerland",   "Drachten",       RegionEnum.noord),
}

# National federation docs — never ingest as individual bank reports
_NATIONAL_PREFIXES = {"jaarverslag", "feiten"}

# Stem parts that indicate financial-only docs (skip; prefer the jaarverslag)
_SKIP_PARTS = {"fin", "jr"}


def _extract_with_provider(
    text: str,
    provider: str,
    model: str,
    source_label: str | None = None,
    pdf_path: Path | None = None,
):
    if provider == "anthropic":
        return extract_all(text, model=model, source_label=source_label, pdf_path=pdf_path)
    if provider == "orq":
        if pdf_path is not None:
            logger.warning("orq provider does not support PDF document fallback — proceeding with sparse text")
        return extract_all_openai_compat(
            text, model=model, source_label=source_label
        )
    raise ValueError(f"Unknown provider '{provider}'")


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


def _resolve_report_file(report: AnnualReport, foodbank: Foodbank | None) -> Path:
    path = Path(report.raw_file_path)
    if path.exists():
        return path

    candidates: list[Path] = []
    if foodbank is not None:
        for key, (bank_name, _, _) in BANK_MAP.items():
            if bank_name != foodbank.name:
                continue
            candidates.extend(sorted(Path("data").glob(f"{key}-{report.year}*.txt")))
            candidates.extend(sorted(Path("data").glob(f"{key}-{report.year}*.pdf")))
            break

    stem = path.stem.lower()
    for candidate in candidates:
        if stem and stem in candidate.stem.lower():
            return candidate

    if foodbank is not None:
        city_slug = foodbank.city.lower().replace(" ", "-")
        city_matches = sorted(Path("data").glob(f"*{city_slug}*{report.year}*.txt"))
        city_matches.extend(sorted(Path("data").glob(f"*{city_slug}*{report.year}*.pdf")))
        if city_matches:
            return city_matches[0]

    if candidates:
        return candidates[0]

    raise ExtractionError(f"File not found: {report.raw_file_path}")


@app.command()
def ingest(
    file: Path = typer.Argument(..., help="Path to PDF or .txt report"),
    bank_name: str = typer.Option(..., "--bank-name", help="Full bank name"),
    city: str = typer.Option(..., "--city", help="City name"),
    region: str = typer.Option(..., "--region", help="Region: noord|oost|zuidoost|zuid|west|randstad"),
    year: int = typer.Option(..., "--year", help="Report year, e.g. 2024"),
    provider: str = typer.Option("orq", "--provider", help="Extraction provider: orq|anthropic"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Model ID"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing report"),
    save_text: bool = typer.Option(True, "--save-text/--no-save-text", help="Write extracted text as .txt sidecar alongside the PDF"),
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
    if save_text and file.suffix.lower() == ".pdf":
        sidecar = file.with_suffix(".txt")
        if force or not sidecar.exists():
            sidecar.write_text(text, encoding="utf-8")
            logger.debug(f"Saved text sidecar: {sidecar}")

    logger.info(f"Extracted {len(text)} chars from {file.name}")
    if provider == "orq" and model == DEFAULT_MODEL:
        model = ORQ_DEFAULT_MODEL

    sparse = len(text.strip()) < MIN_TEXT_CHARS
    pdf_path = file if (sparse and file.suffix.lower() == ".pdf") else None
    if sparse and pdf_path is None and file.suffix.lower() != ".pdf":
        # txt file given directly but sparse — look for sibling PDF
        sibling = file.with_suffix(".pdf")
        if sibling.exists():
            pdf_path = sibling

    result = asyncio.run(
        _extract_with_provider(
            text, provider=provider, model=model, source_label=str(file), pdf_path=pdf_path
        )
    )
    result = merge_extraction_results(result, extract_all_regex(text))

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
    provider: str = typer.Option("orq", "--provider", help="Extraction provider: orq|anthropic"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", help="Model ID"),
    force: bool = typer.Option(False, "--force", help="Overwrite existing reports"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print plan without ingesting"),
    max_concurrent: int = typer.Option(10, "--max-concurrent", help="Max parallel file ingestions"),
    save_text: bool = typer.Option(True, "--save-text/--no-save-text", help="Write extracted text as .txt sidecar alongside each PDF"),
) -> None:
    """Batch ingest all jaarverslag reports in a directory (skips financial-only and national docs)."""
    if not directory.is_dir():
        logger.error(f"Not a directory: {directory}")
        raise typer.Exit(code=1)
    if provider == "orq" and model == DEFAULT_MODEL:
        model = ORQ_DEFAULT_MODEL

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
                if field.endswith(("_source", "_method", "_evidence", "_confidence")):
                    continue
                key = f"{section_name}.{field}"
                counts[key] = 0 if getattr(section, field) is None else 1
        return counts

    def _missing_field_list(result: "ExtractionResult") -> list[str]:
        return [k for k, v in _count_fields(result).items() if v == 0]

    async def _ingest_one(
        sem: asyncio.Semaphore,
        file: Path,
        bank_name: str,
        city: str,
        region_enum: RegionEnum,
        year: int,
    ) -> None:
        async with sem:
            file_path = str(file)
            logger.info(f"Processing {file.name} → {bank_name} {year}")

            # Create or update ingestion record
            with Session(engine) as session:
                rec = session.exec(
                    select(IngestionRecord).where(IngestionRecord.file_path == file_path)
                ).first()
                if rec is None:
                    rec = IngestionRecord(file_path=file_path, bank_name=bank_name, year=year, model=model)
                    session.add(rec)
                if rec.status == IngestionStatus.done and not force:
                    logger.info(f"Already ingested {file.name} — skipping (use --force)")
                    return
                rec.status = IngestionStatus.running
                rec.started_at = datetime.now(timezone.utc)
                rec.error = None
                session.commit()

            try:
                text = extract_text(file)
                if save_text and file.suffix.lower() == ".pdf":
                    sidecar = file.with_suffix(".txt")
                    if force or not sidecar.exists():
                        sidecar.write_text(text, encoding="utf-8")
                        logger.debug(f"Saved text sidecar: {sidecar}")
            except ExtractionError as e:
                logger.error(f"Skipping {file.name}: {e}")
                with Session(engine) as session:
                    rec = session.exec(
                        select(IngestionRecord).where(IngestionRecord.file_path == file_path)
                    ).first()
                    if rec:
                        rec.status = IngestionStatus.failed
                        rec.error = str(e)
                        rec.completed_at = datetime.now(timezone.utc)
                        session.commit()
                return

            try:
                sparse = len(text.strip()) < MIN_TEXT_CHARS
                pdf_path = file if (sparse and file.suffix.lower() == ".pdf") else None
                result = await _extract_with_provider(
                    text,
                    provider=provider,
                    model=model,
                    source_label=file_path,
                    pdf_path=pdf_path,
                )
                result = merge_extraction_results(result, extract_all_regex(text))
                with Session(engine) as session:
                    report = write_report(
                        session=session,
                        foodbank_name=bank_name,
                        city=city,
                        region=region_enum,
                        year=year,
                        pdf_path=file_path,
                        result=result,
                        model=model,
                        force=force,
                    )
                    report_id = report.id
                missing = _missing_field_list(result)
                with Session(engine) as session:
                    rec = session.exec(
                        select(IngestionRecord).where(IngestionRecord.file_path == file_path)
                    ).first()
                    if rec:
                        rec.status = IngestionStatus.done
                        rec.completed_at = datetime.now(timezone.utc)
                        rec.report_id = report_id
                        rec.missing_fields = json.dumps(missing)
                        session.commit()
            except Exception as e:
                logger.error(f"Failed {file.name}: {e}")
                with Session(engine) as session:
                    rec = session.exec(
                        select(IngestionRecord).where(IngestionRecord.file_path == file_path)
                    ).first()
                    if rec:
                        rec.status = IngestionStatus.failed
                        rec.error = str(e)[:2000]
                        rec.completed_at = datetime.now(timezone.utc)
                        session.commit()
                return

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


@app.command(name="backfill-regex")
def backfill_regex(
    city: str | None = typer.Option(None, "--city", help="Limit to one bank (partial city match)"),
    year: int | None = typer.Option(None, "--year", help="Limit to one year"),
) -> None:
    """Fill currently-missing fields in existing reports using deterministic regex extraction."""
    create_db_and_tables()

    with Session(engine) as session:
        reports = session.exec(select(AnnualReport)).all()
        bank_by_id = {b.id: b for b in session.exec(select(Foodbank)).all()}

        if city:
            city_lower = city.lower()
            reports = [
                report for report in reports
                if city_lower in bank_by_id.get(report.foodbank_id).city.lower()
            ]
        if year is not None:
            reports = [report for report in reports if report.year == year]

        updated_reports = 0
        updated_fields = 0

        section_specs = [
            ("food_volume", FoodVolume),
            ("food_categories", FoodCategories),
            ("people_served", PeopleServed),
            ("operations", Operations),
            ("donations", Donations),
        ]

        def _apply_backfill(row: object, extraction_section: object) -> int:
            changed = 0
            for field_name in type(extraction_section).model_fields:
                if field_name.endswith(("_method", "_evidence", "_confidence")):
                    continue
                if getattr(row, field_name, None) is not None:
                    continue
                value = getattr(extraction_section, field_name, None)
                if value is None:
                    continue
                setattr(row, field_name, value)
                setattr(row, f"{field_name}_source", SourceEnum.extracted)
                setattr(row, f"{field_name}_method", getattr(extraction_section, f"{field_name}_method", None))
                setattr(row, f"{field_name}_evidence", getattr(extraction_section, f"{field_name}_evidence", None))
                setattr(row, f"{field_name}_confidence", getattr(extraction_section, f"{field_name}_confidence", None))
                changed += 1
            return changed

        for report in reports:
            foodbank = bank_by_id.get(report.foodbank_id)
            try:
                text = extract_text(_resolve_report_file(report, foodbank))
            except ExtractionError as exc:
                logger.warning(f"Skip report {report.id}: {exc}")
                continue

            regex_result = extract_all_regex(text)
            report_changed = 0

            for section_name, model_cls in section_specs:
                row = session.exec(
                    select(model_cls).where(model_cls.report_id == report.id)  # type: ignore[attr-defined]
                ).first()
                extraction_section = getattr(regex_result, section_name)
                if row is None:
                    continue
                report_changed += _apply_backfill(row, extraction_section)

            if report_changed == 0:
                continue

            updated_reports += 1
            updated_fields += report_changed

            rec = session.exec(
                select(IngestionRecord).where(IngestionRecord.report_id == report.id)
            ).first()
            if rec:
                missing = []
                for section_name, model_cls in section_specs:
                    row = session.exec(
                        select(model_cls).where(model_cls.report_id == report.id)  # type: ignore[attr-defined]
                    ).first()
                    if row is None:
                        continue
                    for field_name in type(getattr(regex_result, section_name)).model_fields:
                        if field_name.endswith(("_method", "_evidence", "_confidence")):
                            continue
                        if getattr(row, field_name, None) is None:
                            missing.append(f"{section_name}.{field_name}")
                rec.missing_fields = json.dumps(missing)

        session.commit()

    logger.success(f"Regex backfill complete — updated {updated_fields} fields across {updated_reports} reports")


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
