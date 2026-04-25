import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
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
        ("Klimaatkracht-certificering", "Klimaatkracht B.V. kan een ondertekende datakwaliteitsverklaring afgeven per voedselbank. Neem contact op voor auditondersteuning."),
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
  <span class="font-semibold tracking-wide">Klimaatkracht</span>
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
        {user.org_name} heeft in {reporting_year} via het Klimaatkracht-platform deelgenomen aan het
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
          Alle onderliggende data zijn beschikbaar bij Klimaatkracht B.V.
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
    Dit rapport is gegenereerd door Klimaatkracht B.V. als ondersteuning voor CSRD/ESRS E5-rapportage.
    De vermelde CO₂e-besparingen zijn berekend conform FRAME-NL v1.0 en zijn niet gecertificeerd door een externe auditor.
    Klimaatkracht B.V. aanvaardt geen aansprakelijkheid voor het gebruik van dit document in formele
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
