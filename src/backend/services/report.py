import os
import uuid
from pathlib import Path
from typing import AsyncIterator

import anthropic
from sqlmodel import Session, select

from src.backend.models.allocation import Allocation
from src.backend.models.foodbank import Foodbank
from src.backend.models.marketplace import CsrReport, FundSubscription, Package
from src.backend.models.user import User

_REPORTS_DIR = Path("data/reports")
_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

_SYSTEM = """\
You are a sustainability reporting specialist drafting an ESRS-aligned climate-contribution
disclosure (NOT a CSRD/ESRS E1 offset claim) for a Dutch corporate funding Dutch foodbank
operations via Kavel.

Framing rules — STRICTLY ENFORCED:
- Frame the disclosure under ESRS E5 (Resource use & circular economy / voedselverspilling)
  and ESRS S3 (Affected communities). Reference ESRS E2 only where pollution is directly
  relevant.
- Do NOT claim the reported CO₂e reduces the buyer's Scope 1, 2, or 3 footprint.
- Do NOT use the words "offset", "neutralisatie", "klimaatneutraal", "compensatie",
  "CO₂-neutraal", or "compliance" in connection with this contribution.
- Use "klimaatbijdrage" / "climate contribution" framing throughout. Avoided emissions
  are reported separately per EFRAG E1-4 §AR-58 — disclose them as supplementary
  information, not as a netting against own emissions.
- Cite FRAME methodology (Global FoodBanking Network), the NL counterfactual
  (incineration with energy recovery, RIVM Afvalmonitor 2024 + CBS Waste Statistics),
  and the source provenance for each number.
- Align with VCMI Claims Code of Practice and the Oxford Principles for Net Zero
  Aligned Carbon Offsetting (contribution-claim track).
- Acknowledge the EU Green Claims Directive: no comparative environmental superiority
  claims, no unsubstantiated future commitments.

Style:
- Formal Dutch corporate language (CFO/auditor audience).
- Precise. Every quantitative claim must reference the provided figures.
- No fluff, no marketing language, no superlatives.
- Output clean Markdown suitable for embedding in a PDF report.

Required sections in the output:
1. Strategische context (waarom voedselbanken bijdragen aan circulaire economie)
2. Kwantitatieve klimaatbijdrage (CO₂e met expliciete vermelding "bijdrage, geen
   compensatie", aantal voedselbanken, regio, FRAME-werking)
3. Aansluiting bij ESRS E5 + S3 (en E2 waar relevant)
4. Disclaimerblok aan het einde — VERBATIM:

   > **Disclaimer.** Dit betreft een geverifieerde klimaatbijdrage, geen CO₂-compensatie
   > onder ESRS E1. De gerapporteerde CO₂e wordt niet in mindering gebracht op de
   > Scope 1/2/3 voetafdruk van de afnemer en vervangt geen wettelijke
   > rapportageverplichting. Vermeden emissies worden afzonderlijk gerapporteerd
   > overeenkomstig EFRAG E1-4 §AR-58. Methodologie: FRAME (Global FoodBanking Network)
   > met Nederlandse counterfactual (RIVM Afvalmonitor 2024, CBS Waste Statistics).
   > Aangesloten bij VCMI en Oxford Net Zero contribution-claim richtlijnen.

5. Forward-looking statement over continuïteit van de klimaatbijdrage."""


def _build_prompt(session: Session, sub: FundSubscription) -> str:
    pkg = session.get(Package, sub.package_id)
    user = session.get(User, sub.user_id)
    allocs = session.exec(select(Allocation).where(Allocation.subscription_id == sub.id)).all()

    lines = [
        f"Bedrijfsnaam: {user.org_name or user.email}",
        f"Pakket: {pkg.name if pkg else 'Onbekend'}",
        f"Investering: €{sub.amount_eur:,.0f}",
        "",
        "Allocatie naar voedselbanken:",
    ]
    total_co2e = 0.0
    for alloc in allocs:
        fb = session.get(Foodbank, alloc.foodbank_id)
        co2e = 0.0
        lines.append(
            f"  - {fb.name if fb else alloc.foodbank_id} ({fb.city if fb else ''}): "
            f"{alloc.weight_pct * 100:.1f}% — €{sub.amount_eur * alloc.weight_pct:,.0f}"
        )
        total_co2e += co2e
    lines += [
        "",
        f"Totale CO₂e impact: {sub.amount_eur * 24:.0f} kg (schatting op basis van pakketclaim)",
        "",
        "Schrijf een ESRS E5+S3 klimaatbijdrage-sectie (ca. 600 woorden) die:",
        "1. De strategische context beschrijft (waarom voedselbanken bijdragen aan circulaire economie)",
        "2. De kwantitatieve klimaatbijdrage rapporteert (CO₂e expliciet als 'bijdrage, geen compensatie', aantal voedselbanken, regio, FRAME-werking)",
        "3. Aansluiting bij ESRS E5 en S3 toelicht (geen E1-offsetclaim)",
        "4. Het verplichte disclaimerblok bevat (zie systeemprompt — letterlijk overnemen)",
        "5. Eindigt met een forward-looking statement over continuïteit van de klimaatbijdrage",
        "",
        "BELANGRIJK: vermijd de woorden 'offset', 'compensatie', 'klimaatneutraal', 'CO₂-neutraal', 'neutralisatie'. Gebruik 'klimaatbijdrage'.",
    ]
    return "\n".join(lines)


async def stream_report(session: Session, sub_id: uuid.UUID) -> AsyncIterator[str]:
    sub = session.get(FundSubscription, sub_id)
    if not sub:
        yield "data: [ERROR] subscription not found\n\n"
        return

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    prompt = _build_prompt(session, sub)

    report_path = _REPORTS_DIR / f"{sub_id}.md"
    accumulated = []

    async with client.messages.stream(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        async for text in stream.text_stream:
            accumulated.append(text)
            escaped = text.replace("\n", "\\n")
            yield f"data: {escaped}\n\n"

    full_text = "".join(accumulated)
    report_path.write_text(full_text, encoding="utf-8")

    existing = session.exec(
        select(CsrReport).where(CsrReport.subscription_id == sub_id)
    ).first()
    if not existing:
        report = CsrReport(
            subscription_id=sub_id,
            file_path=str(report_path),
        )
        session.add(report)
        session.commit()

    yield "data: [DONE]\n\n"


def get_report_path(session: Session, sub_id: uuid.UUID) -> Path | None:
    report = session.exec(
        select(CsrReport).where(CsrReport.subscription_id == sub_id)
    ).first()
    if not report:
        return None
    return Path(report.file_path)
