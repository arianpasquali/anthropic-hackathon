"""DB inspection commands: `ingest db <subcommand>`"""
from __future__ import annotations

import typer
from rich import box
from rich.console import Console
from rich.table import Table
from rich.text import Text
from sqlmodel import Session, select

from src.backend.database import engine
from src.backend.models import (
    AnnualReport, Donations, FoodCategories, Foodbank,
    FoodVolume, Operations, PeopleServed,
)
from src.backend.models.frame import FrameResult

app = typer.Typer(name="db", help="Inspect database contents")
console = Console()

# Value fields to track per measurement table (skip _source / _method / id / report_id)
_FOOD_VOLUME_FIELDS = [
    "kg_received_total", "kg_via_national_dc", "kg_direct", "kg_non_food",
    "waste_pct", "parcels_distributed", "avg_products_per_parcel",
    "pct_schijf_van_vijf", "food_value_eur",
]
_FOOD_CAT_FIELDS = [
    "kg_produce", "kg_meat_fish", "kg_dairy_eggs",
    "kg_dry_goods", "kg_bread_bakery", "kg_prepared",
]
_PEOPLE_FIELDS = [
    "households_weekly", "individuals_total", "children_count",
    "pct_under_18", "pct_single_adults", "pct_single_parent",
    "pct_families", "pct_couples",
]
_OPS_FIELDS = [
    "volunteers_count", "distribution_locations", "satellite_banks_served",
    "annual_budget_eur", "total_expenditure_eur",
]
_DONATIONS_FIELDS = [
    "food_supermarket_kg", "food_company_kg", "food_dc_kg",
    "money_individuals_eur", "money_companies_eur",
    "money_orgs_eur", "money_government_eur",
]
_ALL_FIELDS: dict[str, list[str]] = {
    "food_volume": _FOOD_VOLUME_FIELDS,
    "food_categories": _FOOD_CAT_FIELDS,
    "people_served": _PEOPLE_FIELDS,
    "operations": _OPS_FIELDS,
    "donations": _DONATIONS_FIELDS,
}
_MODEL_MAP = {
    "food_volume": FoodVolume,
    "food_categories": FoodCategories,
    "people_served": PeopleServed,
    "operations": Operations,
    "donations": Donations,
}


def _pct_bar(filled: int, total: int, width: int = 12) -> str:
    if total == 0:
        return "─" * width
    ratio = filled / total
    filled_blocks = round(ratio * width)
    bar = "█" * filled_blocks + "░" * (width - filled_blocks)
    return f"{bar} {ratio:.0%}"


def _completeness(row: object, fields: list[str]) -> tuple[int, int]:
    filled = sum(1 for f in fields if getattr(row, f, None) is not None)
    return filled, len(fields)


@app.command()
def overview() -> None:
    """High-level counts: banks, reports, years covered."""
    with Session(engine) as s:
        banks = s.exec(select(Foodbank)).all()
        reports = s.exec(select(AnnualReport)).all()

        years: dict[int, int] = {}
        for r in reports:
            years[r.year] = years.get(r.year, 0) + 1

        fv_count = len(s.exec(select(FoodVolume)).all())
        ps_count = len(s.exec(select(PeopleServed)).all())
        fr_count = len(s.exec(select(FrameResult)).all())

    t = Table(title="Database Overview", box=box.ROUNDED, show_header=False)
    t.add_column("Metric", style="bold cyan")
    t.add_column("Value", justify="right")
    t.add_row("Foodbanks", str(len(banks)))
    t.add_row("Annual reports", str(len(reports)))
    t.add_row("Reports with food_volume", str(fv_count))
    t.add_row("Reports with people_served", str(ps_count))
    t.add_row("Reports with FRAME result", str(fr_count))
    for yr, cnt in sorted(years.items()):
        t.add_row(f"  └─ {yr}", str(cnt))
    console.print(t)


@app.command()
def banks() -> None:
    """Per-bank table: city | years | households | kg_total | completeness."""
    with Session(engine) as s:
        all_banks = s.exec(select(Foodbank)).all()
        rows = []
        for fb in sorted(all_banks, key=lambda b: b.city):
            reports = s.exec(
                select(AnnualReport).where(AnnualReport.foodbank_id == fb.id)
            ).all()
            if not reports:
                rows.append((fb.city, "—", "—", "—", "—", 0))
                continue

            years_str = ", ".join(str(r.year) for r in sorted(reports, key=lambda r: r.year))
            total_filled = total_possible = 0
            hh_vals, kg_vals = [], []

            for r in reports:
                fv = s.exec(select(FoodVolume).where(FoodVolume.report_id == r.id)).first()
                ps = s.exec(select(PeopleServed).where(PeopleServed.report_id == r.id)).first()
                ops = s.exec(select(Operations).where(Operations.report_id == r.id)).first()
                don = s.exec(select(Donations).where(Donations.report_id == r.id)).first()
                fc = s.exec(select(FoodCategories).where(FoodCategories.report_id == r.id)).first()

                for obj, fields in [
                    (fv, _FOOD_VOLUME_FIELDS), (ps, _PEOPLE_FIELDS),
                    (ops, _OPS_FIELDS), (don, _DONATIONS_FIELDS), (fc, _FOOD_CAT_FIELDS),
                ]:
                    if obj:
                        f, p = _completeness(obj, fields)
                        total_filled += f
                        total_possible += p
                    else:
                        total_possible += len(fields)

                if ps and ps.households_weekly:
                    hh_vals.append(ps.households_weekly)
                if fv and fv.kg_received_total:
                    kg_vals.append(fv.kg_received_total)

            hh_str = f"{max(hh_vals):,}" if hh_vals else "—"
            kg_str = f"{max(kg_vals):,.0f}" if kg_vals else "—"
            rows.append((fb.city, years_str, hh_str, kg_str,
                         _pct_bar(total_filled, total_possible), total_filled))

    t = Table(title="Banks", box=box.SIMPLE_HEAD)
    t.add_column("City", style="bold")
    t.add_column("Years")
    t.add_column("HH/wk (max)", justify="right")
    t.add_column("kg total (max)", justify="right")
    t.add_column("Completeness", justify="left")
    for city, yrs, hh, kg, bar, _ in rows:
        t.add_row(city, yrs, hh, kg, bar)
    console.print(t)


@app.command()
def report(city: str = typer.Argument(..., help="City name (partial match ok)")) -> None:
    """Full extracted data for one bank (all years)."""
    city_lower = city.lower()
    with Session(engine) as s:
        all_banks = s.exec(select(Foodbank)).all()
        matches = [b for b in all_banks if city_lower in b.city.lower()]
        if not matches:
            console.print(f"[red]No bank found matching '{city}'[/red]")
            raise typer.Exit(1)
        if len(matches) > 1:
            console.print(f"[yellow]Multiple matches: {[b.city for b in matches]}[/yellow]")
            console.print("Be more specific.")
            raise typer.Exit(1)

        fb = matches[0]
        console.print(f"\n[bold cyan]{fb.name}[/bold cyan] — {fb.city} ({fb.region})\n")

        reports = s.exec(
            select(AnnualReport).where(AnnualReport.foodbank_id == fb.id)
        ).all()

        for r in sorted(reports, key=lambda x: x.year):
            console.rule(f"[bold]{r.year}[/bold]  ({r.ingestion_model})")

            fv = s.exec(select(FoodVolume).where(FoodVolume.report_id == r.id)).first()
            ps = s.exec(select(PeopleServed).where(PeopleServed.report_id == r.id)).first()
            ops = s.exec(select(Operations).where(Operations.report_id == r.id)).first()
            don = s.exec(select(Donations).where(Donations.report_id == r.id)).first()
            fc = s.exec(select(FoodCategories).where(FoodCategories.report_id == r.id)).first()
            fr = s.exec(select(FrameResult).where(FrameResult.report_id == r.id)).first()

            def _section(title: str, obj: object | None, fields: list[str]) -> None:
                t = Table(title=title, box=box.MINIMAL, show_header=True)
                t.add_column("Field", style="dim")
                t.add_column("Value", justify="right")
                t.add_column("Source", style="dim")
                if obj is None:
                    t.add_row("—", "[dim]not extracted[/dim]", "")
                else:
                    for f in fields:
                        val = getattr(obj, f, None)
                        src = getattr(obj, f"{f}_source", None)
                        val_str = "—" if val is None else f"{val:,.3g}" if isinstance(val, float) else str(val)
                        src_str = src.value if src else ""
                        style = "" if val is not None else "dim"
                        t.add_row(Text(f, style=style), Text(val_str, style=style), Text(src_str, style="dim"))
                console.print(t)

            _section("Food Volume", fv, _FOOD_VOLUME_FIELDS)
            _section("Food Categories (kg)", fc, _FOOD_CAT_FIELDS)
            _section("People Served", ps, _PEOPLE_FIELDS)
            _section("Operations", ops, _OPS_FIELDS)
            _section("Donations", don, _DONATIONS_FIELDS)

            if fr:
                console.print(
                    f"  [green]FRAME[/green]  CO₂e total: [bold]{fr.co2e_total_kg:,.0f}[/bold] kg  "
                    f"({fr.counterfactual_route})"
                )
            console.print()


@app.command()
def quality() -> None:
    """Per-field fill rate across all ingested reports."""
    with Session(engine) as s:
        reports = s.exec(select(AnnualReport)).all()
        n = len(reports)
        if n == 0:
            console.print("[yellow]No reports in database.[/yellow]")
            return

        # count non-null per field across all reports
        field_counts: dict[str, int] = {}
        for r in reports:
            for section, fields in _ALL_FIELDS.items():
                obj = s.exec(
                    select(_MODEL_MAP[section]).where(
                        _MODEL_MAP[section].report_id == r.id  # type: ignore[attr-defined]
                    )
                ).first()
                for f in fields:
                    key = f"{section}.{f}"
                    if key not in field_counts:
                        field_counts[key] = 0
                    if obj and getattr(obj, f, None) is not None:
                        field_counts[key] += 1

    t = Table(title=f"Field Fill Rate (n={n} reports)", box=box.SIMPLE_HEAD)
    t.add_column("Section", style="dim")
    t.add_column("Field")
    t.add_column("Filled", justify="right")
    t.add_column("Rate", justify="left")

    current_section = None
    for key in sorted(field_counts):
        section, field = key.split(".", 1)
        count = field_counts[key]
        rate = count / n
        sec_str = "" if section == current_section else section
        current_section = section
        color = "green" if rate >= 0.7 else "yellow" if rate >= 0.3 else "red"
        t.add_row(
            sec_str, field,
            f"{count}/{n}",
            Text(_pct_bar(count, n, 10), style=color),
        )
    console.print(t)


@app.command()
def missing() -> None:
    """Show reports with the fewest populated fields (worst completeness first)."""
    with Session(engine) as s:
        all_banks = {b.id: b for b in s.exec(select(Foodbank)).all()}
        reports = s.exec(select(AnnualReport)).all()
        rows = []

        for r in reports:
            fb = all_banks.get(r.foodbank_id)
            total_filled = total_possible = 0
            for section, fields in _ALL_FIELDS.items():
                obj = s.exec(
                    select(_MODEL_MAP[section]).where(
                        _MODEL_MAP[section].report_id == r.id  # type: ignore[attr-defined]
                    )
                ).first()
                if obj:
                    f, p = _completeness(obj, fields)
                    total_filled += f
                    total_possible += p
                else:
                    total_possible += len(fields)
            rows.append((fb.city if fb else "?", r.year, total_filled, total_possible))

    rows.sort(key=lambda x: x[2] / max(x[3], 1))

    t = Table(title="Reports by Completeness (worst first)", box=box.SIMPLE_HEAD)
    t.add_column("City", style="bold")
    t.add_column("Year", justify="right")
    t.add_column("Filled", justify="right")
    t.add_column("Completeness")

    for city, year, filled, possible in rows:
        rate = filled / possible if possible else 0
        color = "green" if rate >= 0.5 else "yellow" if rate >= 0.25 else "red"
        t.add_row(city, str(year), f"{filled}/{possible}",
                  Text(_pct_bar(filled, possible, 10), style=color))
    console.print(t)
