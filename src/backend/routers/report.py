import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from sqlmodel import Session, select

from src.backend.database import get_session
from src.backend.models.allocation import Allocation
from src.backend.models.foodbank import AnnualReport, Foodbank
from src.backend.models.frame import FrameResult
from src.backend.models.marketplace import FundSubscription, Package
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
    for alloc in sorted(allocs, key=lambda a: a.weight_pct, reverse=True):
        fb = session.get(Foodbank, alloc.foodbank_id)
        annual = session.exec(select(AnnualReport).where(AnnualReport.foodbank_id == alloc.foodbank_id)).first()
        frame = session.exec(select(FrameResult).where(FrameResult.report_id == annual.id)).first() if annual else None
        co2e = frame.co2e_total_kg * alloc.weight_pct if frame else 0.0
        rows_data.append({
            "name": fb.name if fb else "Unknown",
            "city": fb.city if fb else "",
            "weight_pct": alloc.weight_pct * 100,
            "amount_eur": sub.amount_eur * alloc.weight_pct,
            "co2e_kg": co2e,
        })

    total_co2e = sum(r["co2e_kg"] for r in rows_data)
    today = date.today()
    reporting_year = today.year - 1

    alloc_rows = "\n".join(
        f"""<tr>
          <td class="py-3 px-4 font-medium text-gray-900">{r["name"]}</td>
          <td class="py-3 px-4 text-gray-600">{r["city"]}</td>
          <td class="py-3 px-4 text-right">
            <div class="flex items-center justify-end gap-2">
              <div class="w-24 bg-gray-100 rounded-full h-2">
                <div class="bg-green-500 h-2 rounded-full" style="width:{min(r['weight_pct'],100):.1f}%"></div>
              </div>
              <span class="text-gray-700 w-12 text-right">{r["weight_pct"]:.1f}%</span>
            </div>
          </td>
          <td class="py-3 px-4 text-right text-gray-700">€{r["amount_eur"]:,.0f}</td>
          <td class="py-3 px-4 text-right font-mono text-green-700">{r["co2e_kg"]:,.0f}</td>
        </tr>"""
        for r in rows_data
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
  <div class="grid grid-cols-3 gap-5 mb-10">
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Investering</p>
      <p class="text-3xl font-bold text-gray-900">€{sub.amount_eur:,.0f}</p>
      <p class="text-sm text-gray-500 mt-1">{pkg.name if pkg else "—"}</p>
    </div>
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">CO₂e vermeden</p>
      <p class="text-3xl font-bold text-green-700">{total_co2e/1000:,.1f} t</p>
      <p class="text-sm text-gray-500 mt-1">FRAME-NL v1.0 methodologie</p>
    </div>
    <div class="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
      <p class="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-1">Voedselbankpartners</p>
      <p class="text-3xl font-bold text-gray-900">{len(rows_data)}</p>
      <p class="text-sm text-gray-500 mt-1">Profiel: {pkg.impact_profile.value if pkg else "—"}</p>
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

  <!-- Allocation table -->
  <div class="bg-white rounded-2xl shadow-sm border border-gray-100 mb-8">
    <div class="px-6 py-5 border-b border-gray-100">
      <h2 class="text-lg font-semibold text-gray-900">Allocatie per voedselbank</h2>
      <p class="text-sm text-gray-500 mt-0.5">Gewogen op basis van {pkg.impact_profile.value if pkg else "impact"}-profiel</p>
    </div>
    <div class="overflow-x-auto">
      <table class="w-full text-sm">
        <thead>
          <tr class="bg-gray-50 border-b border-gray-100">
            <th class="py-3 px-4 text-left font-semibold text-gray-500 uppercase text-xs tracking-wider">Voedselbank</th>
            <th class="py-3 px-4 text-left font-semibold text-gray-500 uppercase text-xs tracking-wider">Stad</th>
            <th class="py-3 px-4 text-right font-semibold text-gray-500 uppercase text-xs tracking-wider">Allocatie</th>
            <th class="py-3 px-4 text-right font-semibold text-gray-500 uppercase text-xs tracking-wider">Bedrag</th>
            <th class="py-3 px-4 text-right font-semibold text-gray-500 uppercase text-xs tracking-wider">CO₂e kg</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          {alloc_rows}
        </tbody>
        <tfoot class="border-t-2 border-gray-200 bg-gray-50">
          <tr>
            <td colspan="3" class="py-3 px-4 font-semibold text-gray-900">Totaal</td>
            <td class="py-3 px-4 text-right font-semibold text-gray-900">€{sub.amount_eur:,.0f}</td>
            <td class="py-3 px-4 text-right font-semibold text-green-700 font-mono">{total_co2e:,.0f}</td>
          </tr>
        </tfoot>
      </table>
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
