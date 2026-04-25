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
You are a sustainability reporting specialist writing CSRD/ESRS E5 compliant impact reports.
Write in formal Dutch corporate language. Use ESRS E5 (Circulaire economie & voedselverspilling)
and ESRS E2/S3 framing where relevant. Be precise, cite the numbers provided, avoid fluff.
Output clean Markdown suitable for embedding in a PDF report."""


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
        "Schrijf een CSRD-sectie (ca. 600 woorden) die:",
        "1. De strategische context beschrijft (waarom voedselbanken bijdragen aan circulaire economie)",
        "2. De kwantitatieve impact rapporteert (CO₂e, aantal voedselbanken, regio)",
        "3. Aansluiting bij ESRS E5 en S3 toelicht",
        "4. Eindigt met een forward-looking statement over continuïteit van de maatregel",
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
