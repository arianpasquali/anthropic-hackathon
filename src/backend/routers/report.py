import uuid
from datetime import date
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from sqlalchemy import func
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
from src.backend.models.measurements import FoodCategories, Operations, PeopleServed
from src.backend.models.user import User
from src.backend.services.auth import get_current_user
from src.backend.services.report import get_report_path, stream_report

router = APIRouter(prefix="/report", tags=["report"])

_T: dict[str, dict] = {
    "nl": {
        "kpi_co2e": "CO₂e vermeden",
        "kpi_investment": "Investering",
        "kpi_economics": "Kostenefficiëntie",
        "kpi_households": "Huishoudens",
        "alloc_h2": "Allocatie",
        "alloc_sub": "Gewogen op basis van {profile}-profiel · FRAME-NL v2.0",
        "cat_h2": "Categorieën",
        "cat_sub": "CO₂e-attributie per voedselcategorie",
        "appendix_h2": "Bijlage",
        "trail_h3": "Berekeningstabel",
        "ef_h3": "Emissiefactoren",
        "cf_h3": "Counterfactual",
        "cf_body": "NL verbrandingsroute met energieterugwinning (CF={cf}, RIVM Afvalmonitor 2024 + CBS Waste Statistics)",
        "disc_h2": "Disclaimers",
        "rec_h2": "Aanbevelingen",
        "rec_sub": "Stappen om dit rapport te versterken voor formele CSRD-opname",
        "col_bank": "Voedselbank",
        "col_alloc": "Allocatie",
        "col_amount": "Bedrag",
        "col_bank_co2e": "CO₂e voedselbank",
        "col_attr_co2e": "CO₂e attr.",
        "col_share": "Aandeel",
        "col_households": "Huish./week",
        "col_kg": "Kg gered",
        "col_total": "Totaal",
        "col_cat": "Categorie",
        "col_kg_attr": "Kg (attr.)",
        "col_tco2e_attr": "tCO₂e (attr.)",
        "col_ef": "EF",
        "col_source": "Bron",
        "footer": "Gegenereerd door Kavel B.V. — {date} — FRAME-NL v2.0 · ESRS E5+S3",
        "data_gap": "{name}: categoriedata wordt verzameld.",
        "trail_header": "Organisatie: {org}\nFonds: {pkg}\nInvestering: €{amount}\nKostenefficiëntie: €{econ}/tCO₂e",
        "trail_footer": "Totaal toerekenbare CO₂e: {co2e} tCO₂e\nTotaal huishoudens/week: {households}\nTotaal personen: {individuals}",
        "trail_template": "• {name} ({city}): bank={bank_co2e} tCO₂e/jr · allocatie={pct}% (€{amount}) · {pct_frac}×{bank_co2e} = {attr_co2e} tCO₂e · {households} huish/wk · {methodology}",
        "summary_body": "<strong>{org}</strong> heeft in {year} via het Kavel-platform geïnvesteerd in het <strong>{pkg}</strong>-fonds (€{amount}). De gewogen allocatie aan {n_banks} voedselbanken levert een toerekenbare CO₂e-besparing van <strong>{co2e} tCO₂e</strong>.",
        "summary_disclaimer": "<strong>Verantwoordingsbasis:</strong> Dit betreft een klimaatbijdrage conform ESRS E5 (circulaire economie / voedselverspilling) en ESRS S3 (getroffen gemeenschappen). De vermeden emissies worden apart gerapporteerd per EFRAG E1-4 §AR-58 en worden <em>niet</em> verrekend met de eigen Scope 1/2/3-voetafdruk van {org}.",
        "methodology_body1": "De FRAME-NL v2.0 methodologie berekent vermeden emissies per voedselcategorie door de geredde massa te vermenigvuldigen met de emissiefactor (kg CO₂e/kg) en de Nederlandse counterfactuele route. Kostenefficiëntie: €{eur_per_tco2e}/tCO₂e.",
        "methodology_body2": "Counterfactual: NL verbrandingsroute met energieterugwinning (CF={cf}, RIVM Afvalmonitor 2024). Alle meetwaarden zijn voorzien van broncitaties en provenanceregistratie.",
        "source_ops": "FRAME-NL v2.0 — Global FoodBanking Network / Carbon Trust (2024)",
        "source_ef": "FAO Food Wastage Footprint (2013); Poore & Nemecek (2018); WRAP Courtauld 2030",
        "source_cf": "RIVM Afvalmonitor 2024 + CBS Waste Statistics (CF=0.93, incineration with energy recovery)",
        "source_frame": "EFRAG ESRS E5 (Resource use & circular economy), EFRAG E1-4 §AR-58",
        "source_esrs": "VCMI Claims Code of Practice; Oxford Principles for Net Zero (contribution-claim track)",
        "disc": [
            ("Klimaatbijdrage, geen compensatie", "De vermeden CO₂e-emissies vormen een klimaatbijdrage en worden niet afgetrokken van de eigen Scope 1-, 2- of 3-emissies van de koper."),
            ("Geen gecertificeerde credits", "Dit rapport is geen VCS-, Gold Standard- of vergelijkbaar gecertificeerd offset-certificaat."),
            ("Methodologische beperkingen", "Emissiebesparingen zijn berekend conform FRAME-NL v2.0. Externe verificatie door een onafhankelijke auditor is aanbevolen voor formeel CSRD-gebruik."),
        ],
        "recs": [
            ("Externe verificatie", "Laat de FRAME-berekeningen valideren door een onafhankelijke auditor voor gebruik in een formeel CSRD-verslag."),
            ("Categoriedata verbeteren", "{n} van de {total} partnerbanken rapporteren geen categorieopsplitsing. Vraag uitgesplitste voedselstromen op voor jaar {year}."),
            ("Sociale impact uitbreiden", "Voeg % kinderen en postcodedata toe voor ESRS S3-rapportage (getroffen gemeenschappen)."),
            ("Jaar-op-jaar vergelijking", "Stel {year} als basisjaar in. Volg CO₂e-besparing jaarlijks om E5-doelstellingen aan te tonen."),
            ("Scope-classificatie vastleggen", "Bepaal of vermeden emissies als Scope 3 cat. 1 of cat. 15 worden gerapporteerd — vereist consistente methodologie."),
            ("Kavel-certificering", "Kavel B.V. kan een ondertekende datakwaliteitsverklaring afgeven per voedselbank."),
        ],
    },
    "en": {
        "kpi_co2e": "CO₂e avoided",
        "kpi_investment": "Investment",
        "kpi_economics": "Cost efficiency",
        "kpi_households": "Households",
        "alloc_h2": "Allocation",
        "alloc_sub": "Weighted by {profile} profile · FRAME-NL v2.0",
        "cat_h2": "Categories",
        "cat_sub": "CO₂e attribution by food category",
        "appendix_h2": "Appendix",
        "trail_h3": "Calculation trail",
        "ef_h3": "Emission factors",
        "cf_h3": "Counterfactual",
        "cf_body": "NL incineration with energy recovery (CF={cf}, RIVM Afvalmonitor 2024 + CBS Waste Statistics)",
        "disc_h2": "Disclaimers",
        "rec_h2": "Recommendations",
        "rec_sub": "Steps to strengthen this report for formal CSRD inclusion",
        "col_bank": "Food bank",
        "col_alloc": "Allocation",
        "col_amount": "Amount",
        "col_bank_co2e": "Foodbank CO₂e",
        "col_attr_co2e": "CO₂e attr.",
        "col_share": "Share",
        "col_households": "Households/wk",
        "col_kg": "Kg rescued",
        "col_total": "Total",
        "col_cat": "Category",
        "col_kg_attr": "Kg (attr.)",
        "col_tco2e_attr": "tCO₂e (attr.)",
        "col_ef": "EF",
        "col_source": "Source",
        "footer": "Generated by Kavel B.V. — {date} — FRAME-NL v2.0 · ESRS E5+S3",
        "data_gap": "{name}: category data being collected.",
        "trail_header": "Organisation: {org}\nFund: {pkg}\nInvestment: €{amount}\nCost efficiency: €{econ}/tCO₂e",
        "trail_footer": "Total attributed CO₂e: {co2e} tCO₂e\nTotal households/week: {households}\nTotal individuals: {individuals}",
        "trail_template": "• {name} ({city}): bank={bank_co2e} tCO₂e/yr · allocation={pct}% (€{amount}) · {pct_frac}×{bank_co2e} = {attr_co2e} tCO₂e · {households} hh/wk · {methodology}",
        "summary_body": "<strong>{org}</strong> invested in {year} via the Kavel platform in the <strong>{pkg}</strong> fund (€{amount}). The weighted allocation to {n_banks} food banks yields an attributed CO₂e saving of <strong>{co2e} tCO₂e</strong>.",
        "summary_disclaimer": "<strong>Disclosure basis:</strong> This is a climate contribution under ESRS E5 (circular economy / food waste) and ESRS S3 (affected communities). Avoided emissions are reported separately per EFRAG E1-4 §AR-58 and are <em>not</em> netted against {org}'s own Scope 1/2/3 footprint.",
        "methodology_body1": "The FRAME-NL v2.0 methodology calculates avoided emissions per food category by multiplying rescued mass by the emission factor (kg CO₂e/kg) and the Dutch counterfactual route. Cost efficiency: €{eur_per_tco2e}/tCO₂e.",
        "methodology_body2": "Counterfactual: NL incineration with energy recovery (CF={cf}, RIVM Afvalmonitor 2024). All measurements carry source citations and provenance records.",
        "source_ops": "FRAME-NL v2.0 — Global FoodBanking Network / Carbon Trust (2024)",
        "source_ef": "FAO Food Wastage Footprint (2013); Poore & Nemecek (2018); WRAP Courtauld 2030",
        "source_cf": "RIVM Afvalmonitor 2024 + CBS Waste Statistics (CF=0.93, incineration with energy recovery)",
        "source_frame": "EFRAG ESRS E5 (Resource use & circular economy), EFRAG E1-4 §AR-58",
        "source_esrs": "VCMI Claims Code of Practice; Oxford Principles for Net Zero (contribution-claim track)",
        "disc": [
            ("Climate contribution, not an offset", "The avoided CO₂e emissions constitute a climate contribution and are not deducted from the buyer's own Scope 1, 2, or 3 emissions."),
            ("No certified credits", "This report is not a VCS, Gold Standard, or equivalent certified offset certificate."),
            ("Methodological limitations", "Emission savings are calculated per FRAME-NL v2.0. Independent third-party verification is recommended for formal CSRD use."),
        ],
        "recs": [
            ("Third-party verification", "Have the FRAME calculations validated by an independent auditor before using this report in a formal CSRD filing."),
            ("Improve category data", "{n} of {total} partner banks do not report a category breakdown. Request itemised food streams for year {year}."),
            ("Expand social impact", "Add % children and postcode data for ESRS S3 (affected communities) reporting."),
            ("Year-on-year comparison", "Set {year} as baseline year. Track CO₂e savings per quarter to demonstrate E5 targets."),
            ("Scope classification", "Determine whether avoided emissions are reported as Scope 3 cat. 1 or cat. 15 — both are defensible but require consistent methodology."),
            ("Kavel certification", "Kavel B.V. can issue a signed data quality declaration per food bank."),
        ],
    },
}


def _get_owned_sub(sub_id: uuid.UUID, session: Session, user: User) -> FundSubscription:
    sub = session.get(FundSubscription, sub_id)
    if not sub or sub.user_id != user.id:
        raise HTTPException(status_code=404)
    return sub


@router.post("/{sub_id}/generate")
def generate_report(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _get_owned_sub(sub_id, session, user)
    return {"sub_id": str(sub_id), "stream_url": f"/report/{sub_id}/stream"}


@router.get("/{sub_id}/stream")
async def stream_report_sse(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _get_owned_sub(sub_id, session, user)
    return StreamingResponse(
        stream_report(session, sub_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/{sub_id}/data")
async def get_report_data(
    sub_id: uuid.UUID,
    lang: Literal["nl", "en"] = Query("nl"),
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    t = _T[lang]
    sub = _get_owned_sub(sub_id, session, user)
    pkg = session.get(Package, sub.package_id)
    allocs = session.exec(select(Allocation).where(Allocation.subscription_id == sub_id)).all()

    EF = {"produce": 1.0, "meat_fish": 8.5, "dairy_eggs": 3.2, "dry_goods": 2.0, "bread_bakery": 1.5, "prepared": 3.0}
    EF_SOURCE = {
        "produce": "FAO Food Wastage Footprint (2013) Table 4.2",
        "meat_fish": "FAO FWF gewogen NL vleesmix" if lang == "nl" else "FAO FWF weighted NL meat mix",
        "dairy_eggs": "FAO FWF + RIVM Dutch dairy LCA",
        "dry_goods": "FAO FWF + Poore & Nemecek (2018)",
        "bread_bakery": "WRAP Courtauld Commitment 2030",
        "prepared": "Poore & Nemecek (2018)",
    }
    NL_CF = 0.93

    rows_data = []
    data_gaps: list[str] = []

    for alloc in sorted(allocs, key=lambda a: a.weight_pct, reverse=True):
        fb = session.get(Foodbank, alloc.foodbank_id)
        latest_year = session.exec(
            select(func.max(AnnualReport.year))
            .join(FrameResult, FrameResult.report_id == AnnualReport.id)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id)
        ).first()
        annual = session.exec(
            select(AnnualReport)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id, AnnualReport.year == latest_year)
        ).first() if latest_year else None
        frame = session.exec(select(FrameResult).where(FrameResult.report_id == annual.id)).first() if annual else None
        people = session.exec(select(PeopleServed).where(PeopleServed.report_id == annual.id)).first() if annual else None
        cats = session.exec(select(FoodCategories).where(FoodCategories.report_id == annual.id)).first() if annual else None

        fb_name = fb.name if fb else "Unknown"
        attributed_co2e = (frame.co2e_total_kg if frame else 0.0) * alloc.weight_pct
        total_kg = (
            (cats.kg_produce or 0) + (cats.kg_meat_fish or 0) + (cats.kg_dairy_eggs or 0)
            + (cats.kg_dry_goods or 0) + (cats.kg_bread_bakery or 0) + (cats.kg_prepared or 0)
        ) if cats else None

        cat_fallback = (
            frame is not None and cats is not None
            and (cats.kg_meat_fish is None or cats.kg_meat_fish == 0)
            and (cats.kg_dairy_eggs is None or cats.kg_dairy_eggs == 0)
        )
        if cat_fallback:
            data_gaps.append(t["data_gap"].format(name=fb_name))

        cat_rows = []
        if cats and frame:
            for cat, ef in EF.items():
                kg_bank = getattr(cats, f"kg_{cat}", None) or 0.0
                co2e_attr = (getattr(frame, f"co2e_{cat}_kg", 0.0) or 0.0) * alloc.weight_pct
                if kg_bank > 0:
                    cat_rows.append({
                        "category": cat.replace("_", " "),
                        "kg_attr": round(kg_bank * alloc.weight_pct, 1),
                        "tco2e_attr": round(co2e_attr / 1000, 3),
                        "ef": ef,
                        "source": EF_SOURCE[cat],
                    })

        city = fb.city if fb else ""
        slug = city.lower().replace(" ", "-") if city else ""
        rows_data.append({
            "name": fb_name,
            "city": city,
            "slug": slug,
            "year": latest_year or "—",
            "weight_pct": round(alloc.weight_pct * 100, 2),
            "amount_eur": round(sub.amount_eur * alloc.weight_pct, 2),
            "bank_co2e_t": round((frame.co2e_total_kg if frame else 0.0) / 1000, 2),
            "attributed_co2e_t": round(attributed_co2e / 1000, 3),
            "attribution_share_pct": round(alloc.weight_pct * 100, 2),
            "households": people.households_weekly if people else None,
            "individuals": people.individuals_total if people else None,
            "kg_rescued_attr": round(total_kg * alloc.weight_pct) if total_kg else None,
            "cat_rows": cat_rows,
            "methodology": frame.methodology_version if frame else "FRAME-NL v2.0",
        })

    total_co2e_t = sum(r["attributed_co2e_t"] for r in rows_data)
    total_households = sum(r["households"] for r in rows_data if r["households"])
    total_individuals = sum(r["individuals"] for r in rows_data if r["individuals"])
    eur_per_tco2e = sub.amount_eur / total_co2e_t if total_co2e_t > 0 else 0.0
    today = date.today()
    reporting_year = today.year - 1

    trail_lines = []
    for r in rows_data:
        trail_lines.append(t["trail_template"].format(
            name=r["name"], city=r["city"],
            bank_co2e=f"{r['bank_co2e_t']:,.1f}",
            pct=f"{r['weight_pct']:.2f}",
            amount=f"{r['amount_eur']:,.0f}",
            pct_frac=f"{r['weight_pct'] / 100:.4f}",
            attr_co2e=f"{r['attributed_co2e_t']:.3f}",
            households=r["households"] or "—",
            methodology=r["methodology"],
        ))
    trail_header = t["trail_header"].format(
        org=user.org_name, pkg=pkg.name if pkg else "—",
        amount=f"{sub.amount_eur:,.0f}", econ=f"{eur_per_tco2e:,.2f}",
    )
    trail_footer = t["trail_footer"].format(
        co2e=f"{total_co2e_t:,.3f}",
        households=f"{total_households:,}",
        individuals=f"{total_individuals:,}",
    )

    recs = [
        {"title": title, "body": body.format(year=reporting_year, n=0, total=len(rows_data))}
        for title, body in t["recs"]
    ]

    return {
        "lang": lang,
        "meta": {
            "org": user.org_name,
            "package_name": pkg.name if pkg else "—",
            "impact_profile": pkg.impact_profile.value if pkg else "—",
            "amount_eur": sub.amount_eur,
            "sub_id": str(sub_id),
            "period": reporting_year,
            "generated": today.strftime("%-d %B %Y"),
        },
        "kpis": {
            "total_co2e_t": round(total_co2e_t, 2),
            "investment_eur": sub.amount_eur,
            "eur_per_tco2e": round(eur_per_tco2e, 2),
            "households_per_week": total_households,
            "individuals": total_individuals,
        },
        "summary": {
            "body_html": t["summary_body"].format(
                org=user.org_name, year=reporting_year,
                amount=f"{sub.amount_eur:,.0f}",
                pkg=pkg.name if pkg else "—",
                co2e=f"{total_co2e_t:,.2f}",
                n_banks=len(rows_data),
            ),
            "disclaimer_html": t["summary_disclaimer"].format(org=user.org_name),
        },
        "methodology": {
            "body1_html": t["methodology_body1"].format(eur_per_tco2e=f"{eur_per_tco2e:,.2f}"),
            "body2_html": t["methodology_body2"].format(cf=NL_CF),
        },
        "allocations": rows_data,
        "data_gaps": data_gaps,
        "calc_trail": f"{trail_header}\n\n{chr(10).join(trail_lines)}\n{trail_footer}",
        "emission_factors": [
            {"category": cat.replace("_", " "), "ef": ef, "source": EF_SOURCE[cat]}
            for cat, ef in EF.items()
        ],
        "nl_cf": NL_CF,
        "disclaimers": [{"title": title, "body": body} for title, body in t["disc"]],
        "recommendations": recs,
        "texts": {
            "alloc_h2": t["alloc_h2"],
            "alloc_sub": t["alloc_sub"].format(profile=pkg.impact_profile.value if pkg else "—"),
            "cat_h2": t["cat_h2"],
            "cat_sub": t["cat_sub"],
            "appendix_h2": t["appendix_h2"],
            "trail_h3": t["trail_h3"],
            "ef_h3": t["ef_h3"],
            "cf_h3": t["cf_h3"],
            "cf_body": t["cf_body"].format(cf=NL_CF),
            "disc_h2": t["disc_h2"],
            "rec_h2": t["rec_h2"],
            "rec_sub": t["rec_sub"],
            "col_bank": t["col_bank"],
            "col_alloc": t["col_alloc"],
            "col_amount": t["col_amount"],
            "col_bank_co2e": t["col_bank_co2e"],
            "col_attr_co2e": t["col_attr_co2e"],
            "col_share": t["col_share"],
            "col_households": t["col_households"],
            "col_kg": t["col_kg"],
            "col_total": t["col_total"],
            "col_cat": t["col_cat"],
            "col_kg_attr": t["col_kg_attr"],
            "col_tco2e_attr": t["col_tco2e_attr"],
            "col_ef": t["col_ef"],
            "col_source": t["col_source"],
            "footer": t["footer"].format(date=today.strftime("%-d %B %Y")),
            "kpi_co2e": t["kpi_co2e"],
            "kpi_investment": t["kpi_investment"],
            "kpi_economics": t["kpi_economics"],
            "kpi_households": t["kpi_households"],
            "sources": [t["source_ops"], t["source_ef"], t["source_cf"], t["source_frame"], t["source_esrs"]],
        },
    }


@router.get("/{sub_id}/mock", response_class=HTMLResponse)
def mock_report(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    sub = _get_owned_sub(sub_id, session, user)
    pkg = session.get(Package, sub.package_id)
    allocs = session.exec(select(Allocation).where(Allocation.subscription_id == sub_id)).all()

    rows_data = []
    data_gaps: list[str] = []
    for alloc in sorted(allocs, key=lambda a: a.weight_pct, reverse=True):
        fb = session.get(Foodbank, alloc.foodbank_id)
        latest_year = session.exec(
            select(func.max(AnnualReport.year))
            .join(FrameResult, FrameResult.report_id == AnnualReport.id)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id)
        ).first()
        annual = session.exec(
            select(AnnualReport)
            .where(AnnualReport.foodbank_id == alloc.foodbank_id, AnnualReport.year == latest_year)
        ).first() if latest_year else None
        frame = session.exec(select(FrameResult).where(FrameResult.report_id == annual.id)).first() if annual else None
        people = session.exec(select(PeopleServed).where(PeopleServed.report_id == annual.id)).first() if annual else None
        ops = session.exec(select(Operations).where(Operations.report_id == annual.id)).first() if annual else None
        cats = session.exec(select(FoodCategories).where(FoodCategories.report_id == annual.id)).first() if annual else None

        co2e = frame.co2e_total_kg * alloc.weight_pct if frame else 0.0
        fb_name = fb.name if fb else "Unknown"

        # Detect category data quality issue: all CO2e in produce → fallback split used
        cat_fallback = (
            frame is not None
            and cats is not None
            and (cats.kg_meat_fish is None or cats.kg_meat_fish == 0)
            and (cats.kg_dairy_eggs is None or cats.kg_dairy_eggs == 0)
            and (cats.kg_dry_goods is None or cats.kg_dry_goods == 0)
        )
        if cat_fallback:
            data_gaps.append(f"{fb_name}: voedselcategorieën niet uitgesplitst in jaarverslag — CO₂e berekend op basis van nationale gemiddelden")

        rows_data.append({
            "name": fb_name,
            "city": fb.city if fb else "",
            "year": latest_year or "—",
            "weight_pct": alloc.weight_pct * 100,
            "amount_eur": sub.amount_eur * alloc.weight_pct,
            "co2e_kg": co2e,
            "co2e_per_kg": (frame.co2e_total_kg / (frame.co2e_total_kg / 3.5)) if frame else None,  # placeholder ratio
            "kg_rescued": (cats.kg_produce or 0) + (cats.kg_meat_fish or 0) + (cats.kg_dairy_eggs or 0) + (cats.kg_dry_goods or 0) + (cats.kg_bread_bakery or 0) + (cats.kg_prepared or 0) if cats else None,
            "households": people.households_weekly if people else None,
            "individuals": people.individuals_total if people else None,
            "children_pct": people.pct_under_18 if people else None,
            "volunteers": ops.volunteers_count if ops else None,
            "locations": ops.distribution_locations if ops else None,
            "cat_fallback": cat_fallback,
        })

    total_co2e = sum(r["co2e_kg"] for r in rows_data)
    total_households = sum(r["households"] for r in rows_data if r["households"])
    total_individuals = sum(r["individuals"] for r in rows_data if r["individuals"])
    today = date.today()
    reporting_year = today.year - 1

    def _fmt(v, fmt="{:,.0f}", fallback="—"):
        return fmt.format(v) if v is not None else fallback

    alloc_rows = "\n".join(
        f"""<tr class="{'bg-amber-50' if r['cat_fallback'] else ''}">
          <td class="py-3 px-4">
            <div class="font-medium text-gray-900">{r["name"]}</div>
            <div class="text-xs text-gray-400">{r["city"]} · {r["year"]}</div>
          </td>
          <td class="py-3 px-4 text-right">
            <div class="flex items-center justify-end gap-2">
              <div class="w-20 bg-gray-100 rounded-full h-2">
                <div class="bg-green-500 h-2 rounded-full" style="width:{min(r['weight_pct'],100):.1f}%"></div>
              </div>
              <span class="text-gray-700 w-10 text-right text-sm">{r["weight_pct"]:.1f}%</span>
            </div>
          </td>
          <td class="py-3 px-4 text-right text-gray-700 text-sm">€{r["amount_eur"]:,.0f}</td>
          <td class="py-3 px-4 text-right font-mono text-green-700 text-sm">{r["co2e_kg"]:,.0f}</td>
          <td class="py-3 px-4 text-right text-gray-600 text-sm">{_fmt(r["households"])}</td>
          <td class="py-3 px-4 text-right text-gray-600 text-sm">{_fmt(r["individuals"])}</td>
          <td class="py-3 px-4 text-right text-gray-600 text-sm">{"⚠" if r["cat_fallback"] else _fmt(r["kg_rescued"])}</td>
          <td class="py-3 px-4 text-right text-gray-600 text-sm">{_fmt(r["volunteers"])}</td>
        </tr>"""
        for r in rows_data
    )

    gap_items = "\n".join(
        f'<li class="flex gap-2"><span class="text-amber-500 mt-0.5">⚠</span><span>{g}</span></li>'
        for g in data_gaps
    ) if data_gaps else ""

    recs = [
        ("Externe verificatie", "CO₂e-besparingen zijn zelfgerapporteerd. Laat de FRAME-berekeningen valideren door een onafhankelijke auditor voor gebruik in een formeel CSRD-verslag."),
        ("Voedselcategorisering verbeteren", f"{sum(1 for r in rows_data if r['cat_fallback'])} van de {len(rows_data)} partnervoedselbanken rapporteren geen categorieopsplitsing. Vraag jaarverslagen op die uitgesplitste voedselstromen bevatten (vers/vlees/zuivel/droog)."),
        ("Sociale impact uitbreiden", "Voeg % kinderen, huishoudsamenstelling en postcodedata toe voor ESRS S3-rapportage (getroffen gemeenschappen)."),
        ("Jaar-op-jaar vergelijking", f"Stel {reporting_year} als basisjaar in. Volg CO₂e-besparing en bereik per kwartaal om E5-2-doelstellingen aan te tonen."),
        ("Scope-classificatie vastleggen", "Bepaal of de vermeden emissies als Scope 3 categorie 1 (ingekochte goederen) of categorie 15 (investeringen) worden gerapporteerd — beide zijn verdedigbaar maar vereisen consistente methodologie."),
        ("Kavel-certificering", "Kavel B.V. kan een ondertekende datakwaliteitsverklaring afgeven per voedselbank. Neem contact op voor auditondersteuning."),
    ]

    rec_items = "\n".join(
        f"""<div class="flex gap-4 p-4 rounded-xl border border-gray-100 bg-gray-50">
          <div class="w-6 h-6 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold flex-shrink-0 mt-0.5">{i+1}</div>
          <div>
            <p class="font-semibold text-gray-900 text-sm">{title}</p>
            <p class="text-gray-600 text-sm mt-0.5">{body}</p>
          </div>
        </div>"""
        for i, (title, body) in enumerate(recs)
    )

    html = f"""<!DOCTYPE html>
<html lang="nl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CSRD Klimaatrapport — {user.org_name}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body {{ font-family: 'Inter', sans-serif; }}
    @media print {{ .no-print {{ display: none; }} }}
  </style>
</head>
<body class="bg-gray-50 text-gray-800">

<!-- Top bar -->
<div class="bg-green-700 text-white py-3 px-8 flex justify-between items-center no-print">
  <span class="font-semibold tracking-wide">Kavel</span>
  <button onclick="window.print()" class="text-sm bg-white text-green-700 px-4 py-1.5 rounded-full font-medium hover:bg-green-50 transition">
    Afdrukken / PDF
  </button>
</div>

<div class="max-w-4xl mx-auto py-12 px-6">

  <!-- Header -->
  <div class="mb-10">
    <div class="flex items-start justify-between">
      <div>
        <p class="text-sm font-medium text-green-700 uppercase tracking-widest mb-1">CSRD / ESRS E5 — Circulaire economie</p>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">Klimaatimpactrapport</h1>
        <p class="text-xl text-gray-500">{user.org_name}</p>
      </div>
      <div class="text-right text-sm text-gray-400">
        <p>Rapportageperiode: {reporting_year}</p>
        <p>Gegenereerd: {today.strftime("%-d %B %Y")}</p>
        <p class="mt-1 font-mono text-xs text-gray-300">{str(sub_id)[:8]}…</p>
      </div>
    </div>
    <div class="mt-6 h-px bg-gradient-to-r from-green-500 to-transparent"></div>
  </div>

  <!-- KPI cards -->
  <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Investering</p>
      <p class="text-2xl font-bold text-gray-900">€{sub.amount_eur:,.0f}</p>
      <p class="text-xs text-gray-500 mt-1">{pkg.name if pkg else "—"}</p>
    </div>
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">CO₂e vermeden</p>
      <p class="text-2xl font-bold text-green-700">{total_co2e/1000:,.1f} t</p>
      <p class="text-xs text-gray-500 mt-1">FRAME-NL v1.0</p>
    </div>
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Huishoudens bereikt</p>
      <p class="text-2xl font-bold text-gray-900">{total_households:,}</p>
      <p class="text-xs text-gray-500 mt-1">per week (gecombineerd)</p>
    </div>
    <div class="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Partnerbanken</p>
      <p class="text-2xl font-bold text-gray-900">{len(rows_data)}</p>
      <p class="text-xs text-gray-500 mt-1">Profiel: {pkg.impact_profile.value if pkg else "—"}</p>
    </div>
  </div>

  <!-- ESRS E5 section -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 mb-8">
    <div class="px-6 py-5 border-b border-gray-100">
      <h2 class="text-lg font-semibold text-gray-900">ESRS E5 — Materiaalgebruik en circulaire economie</h2>
      <p class="text-sm text-gray-500 mt-0.5">Disclosure E5-4: Toerekenbare CO₂e-besparing via voedselherstel</p>
    </div>
    <div class="px-6 py-5 space-y-4 text-sm text-gray-700 leading-relaxed">
      <p>
        {user.org_name} heeft in {reporting_year} via het Kavel-platform deelgenomen aan het
        <strong>{pkg.name if pkg else "klimaatimpactfonds"}</strong>. De investering van
        <strong>€{sub.amount_eur:,.0f}</strong> is gealloceerd aan {len(rows_data)} Nederlandse voedselbanken
        op basis van geverifieerde CO₂e-besparingen conform de FRAME-NL v1.0 methodologie.
      </p>
      <p>
        Door voedseloverschotten te herverdelen in plaats van te verwerken als afval, vermijden de
        aangesloten voedselbanken samen <strong>{total_co2e/1000:,.1f} ton CO₂e</strong> per jaar.
        Het aandeel toerekenbaar aan {user.org_name} bedraagt
        <strong>{total_co2e/1000:,.1f} ton CO₂e</strong> op basis van gewogen allocatiefracties.
      </p>
      <div class="bg-green-50 border border-green-200 rounded-xl p-4 text-green-800">
        <p class="font-semibold mb-1">Verantwoordingsgrondslag (ESRS E5-4)</p>
        <p class="text-xs">
          Emissiebesparingen zijn berekend op basis van de counterfactuele verwerkingsroute per
          voedselcategorie (stortplaats / vergisting / compostering), vermenigvuldigd met de
          emissiefactoren uit de nationale CO₂e-database. Methodologie: FRAME-NL v1.0.
          Alle onderliggende data zijn beschikbaar bij Kavel B.V.
        </p>
      </div>
    </div>
  </div>

  <!-- Allocation + impact table -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 mb-8">
    <div class="px-6 py-5 border-b border-gray-100 flex items-center justify-between">
      <div>
        <h2 class="text-lg font-semibold text-gray-900">Allocatie &amp; impact per voedselbank</h2>
        <p class="text-sm text-gray-500 mt-0.5">Gewogen op basis van {pkg.impact_profile.value if pkg else "impact"}-profiel · FRAME-NL v1.0</p>
      </div>
      {"<span class='text-xs bg-amber-100 text-amber-700 px-3 py-1 rounded-full font-medium'>⚠ Datakwaliteitswaarschuwingen</span>" if data_gaps else ""}
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider">
            <th class="py-3 px-4 text-left">Voedselbank</th>
            <th class="py-3 px-4 text-right">Allocatie</th>
            <th class="py-3 px-4 text-right">Bedrag</th>
            <th class="py-3 px-4 text-right">CO₂e (kg)</th>
            <th class="py-3 px-4 text-right">Huish./week</th>
            <th class="py-3 px-4 text-right">Personen</th>
            <th class="py-3 px-4 text-right">Kg gered</th>
            <th class="py-3 px-4 text-right">Vrijwill.</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          {alloc_rows}
        </tbody>
        <tfoot class="border-t-2 border-gray-200 bg-gray-50 text-sm font-semibold">
          <tr>
            <td class="py-3 px-4 text-gray-900">Totaal</td>
            <td class="py-3 px-4"></td>
            <td class="py-3 px-4 text-right text-gray-900">€{sub.amount_eur:,.0f}</td>
            <td class="py-3 px-4 text-right text-green-700 font-mono">{total_co2e:,.0f}</td>
            <td class="py-3 px-4 text-right text-gray-700">{total_households:,}</td>
            <td class="py-3 px-4 text-right text-gray-700">{total_individuals:,}</td>
            <td colspan="2" class="py-3 px-4"></td>
          </tr>
        </tfoot>
      </table>
    </div>
    {"<div class='px-6 py-4 border-t border-amber-100 bg-amber-50 rounded-b-2xl'><p class='text-xs font-semibold text-amber-700 mb-2'>Datakwaliteitswaarschuwingen</p><ul class='space-y-1 text-xs text-amber-800'>" + gap_items + "</ul></div>" if data_gaps else ""}
  </div>

  <!-- Recommendations -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 mb-8">
    <div class="px-6 py-5 border-b border-gray-100">
      <h2 class="text-lg font-semibold text-gray-900">Aanbevelingen voor rapportage</h2>
      <p class="text-sm text-gray-500 mt-0.5">Stappen om dit rapport te versterken voor formele CSRD-opname</p>
    </div>
    <div class="px-6 py-5 space-y-3">
      {rec_items}
    </div>
  </div>

  <!-- Disclaimer -->
  <p class="text-xs text-gray-400 text-center leading-relaxed">
    Dit rapport is gegenereerd door Kavel B.V. als ondersteuning voor CSRD/ESRS E5-rapportage.
    De vermelde CO₂e-besparingen zijn berekend conform FRAME-NL v1.0 en zijn niet gecertificeerd door een externe auditor.
    Kavel B.V. aanvaardt geen aansprakelijkheid voor het gebruik van dit document in formele
    duurzaamheidsverslagen zonder aanvullende verificatie.
  </p>

</div>
</body>
</html>"""
    return HTMLResponse(content=html)


@router.get("/{sub_id}/download")
def download_report(
    sub_id: uuid.UUID,
    session: Session = Depends(get_session),
    user: User = Depends(get_current_user),
):
    _get_owned_sub(sub_id, session, user)
    path = get_report_path(session, sub_id)
    if not path or not path.exists():
        raise HTTPException(status_code=404, detail="Report not yet generated")
    return FileResponse(path, media_type="text/markdown", filename=f"csrd-report-{sub_id}.md")
