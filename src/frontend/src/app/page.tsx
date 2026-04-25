import Link from "next/link"
import { api } from "@/lib/api"
import { NLProvinceFoodbankHeatMapDynamic } from "@/components/map/NLProvinceFoodbankHeatMapDynamic"

import { Badge } from "@/components/ui/Badge"
import { formatNumber, formatTCO2e } from "@/lib/format"

export default async function Home() {
  const banks = await api.listFoodbanks().catch(() => [])
  const totalKg = banks.reduce((s, b) => s + (b.annual_kg_rescued ?? 0), 0)
  const totalTco2e = banks.reduce((s, b) => s + (b.annual_tco2e ?? 0), 0)
  const totalHouseholds = banks.reduce((s, b) => s + (b.households_weekly ?? 0), 0)

  return (
    <div className="overflow-hidden">
      {/* Hero */}
      <section className="mx-auto max-w-[1280px] px-6 pt-12 md:pt-20 pb-20 grid lg:grid-cols-[1.4fr_1fr] gap-x-12 gap-y-10 items-end">
        <div>
          <Badge variant="default" className="mb-6">
            Klimaatkracht · CSRD-aligned
          </Badge>
          <h1 className="display text-[52px] md:text-[78px] leading-[1.02] tracking-[-0.03em] max-w-[16ch]">
            Verified avoided emissions,{" "}
            <span className="display-italic text-emerald-deep">audit-ready.</span>
          </h1>
          <p className="mt-7 text-[16px] text-text-muted leading-[1.55] max-w-[58ch]">
            Klimaatkracht turns Dutch food rescue into ESRS&nbsp;E1 + S3 disclosures.
            Buy a fund, and a single quarterly purchase is allocated across the top
            food banks in the Netherlands — weighted by the FRAME-computed CO₂e baseline
            we extract from each bank&apos;s annual report. Sources cited; provenance
            tagged; counterfactual disclosed.
          </p>
          <div className="mt-10 flex flex-wrap gap-3">
            <Link
              href="/marketplace"
              className="bg-emerald text-text-on-emerald h-12 px-6 inline-flex items-center text-[14.5px] font-medium hover:bg-emerald-deep transition-colors"
            >
              Browse funds →
            </Link>
            <Link
              href="/dashboard/foodbank"
              className="border border-line h-12 px-6 inline-flex items-center text-[14.5px] hover:bg-surface-2 transition-colors"
            >
              Join as a food bank
            </Link>
          </div>
          <div className="mt-10 flex flex-wrap items-center gap-x-5 gap-y-2 text-[12px] text-text-faint">
            <span>FRAME aligned</span>
            <span aria-hidden>·</span>
            <span>ESRS E1 + S3</span>
            <span aria-hidden>·</span>
            <span>CSRD ready</span>
            <span aria-hidden>·</span>
            <span>NL counterfactual</span>
          </div>
        </div>

        {/* Stats stack — typographic, no card chrome */}
        <dl className="grid grid-cols-2 gap-x-8 gap-y-8 lg:pl-8 lg:border-l lg:border-line">
          <Stat label="Avoided / yr" value={formatTCO2e(totalTco2e)} />
          <Stat label="Rescued / yr" value={`${formatNumber(totalKg / 1_000_000, { maximumFractionDigits: 1 })}M kg`} />
          <Stat label="Households / wk" value={formatNumber(totalHouseholds)} />
          <Stat label="Food banks" value={formatNumber(banks.length)} />
        </dl>
      </section>

      {/* Audience split — narrative trust */}
      <section className="border-y border-line bg-surface-2">
        <div className="mx-auto max-w-[1280px] px-6 py-20 grid md:grid-cols-2 gap-x-12 gap-y-10">
          <Pitch
            kicker="For corporates"
            title="Buy a fund."
            italic="Receive an audit-grade disclosure."
            body="The fund subscribes you to a quarterly impact stream. The allocation engine ranks Dutch food banks by FRAME-computed CO₂e baseline or social reach — and weights your purchase accordingly. Every quarter, Claude generates an ESRS E1 + S3 disclosure with full FRAME workings, source citations, and provenance ledger."
            href="/marketplace"
            cta="Browse funds →"
          />
          <Pitch
            kicker="For food banks"
            title="Upload your annual report."
            italic="Unlock corporate funding."
            body="Drop your annual report PDF. Claude extracts food volumes, categories, and people served — every measurement tagged with extracted, inferred, or computed. FRAME does the rest. Once your data is in, you appear in the marketplace and corporates can sponsor your operations."
            href="/dashboard/foodbank"
            cta="Join as a food bank →"
          />
        </div>
      </section>

      {/* How it works */}
      <section className="mx-auto max-w-[1280px] px-6 py-24">
        <p className="eyebrow">Pipeline</p>
        <h2 className="display text-4xl md:text-5xl mt-3 tracking-[-0.025em] max-w-[18ch]">
          From annual report{" "}
          <span className="display-italic text-emerald-deep">to audit trail.</span>
        </h2>

        <ol className="mt-14 grid grid-cols-1 md:grid-cols-3 gap-10">
          <Step
            n="01"
            title="Extract"
            body="Claude reads each food bank's annual report PDF section-by-section, structuring food volumes, categories, demographics, and operations into typed measurements with provenance."
          />
          <Step
            n="02"
            title="Compute"
            body="FRAME multiplies each kg by its category emission factor and the NL counterfactual (0.93, incineration with energy recovery — RIVM Afvalmonitor 2024)."
          />
          <Step
            n="03"
            title="Disclose"
            body="On purchase, the allocation engine assigns weights across the top-N banks. Claude composes the ESRS E1 + S3 disclosure, streamed back to the buyer in real time."
          />
        </ol>
      </section>

      {/* Map */}
      <section className="border-t border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-20 grid lg:grid-cols-[1fr_1.4fr] gap-x-12 gap-y-10 items-start">
          <div>
            <p className="eyebrow">The network</p>
            <h2 className="display text-4xl mt-3 tracking-[-0.02em] max-w-[16ch]">
              {formatNumber(banks.length)} food banks. One audit trail.
            </h2>
            <p className="text-text-muted text-[14.5px] mt-5 max-w-[44ch] leading-relaxed">
              Province fill scales with the count of food banks we ingest data
              for. Open the marketplace to drill into any operator&apos;s public
              transparency profile — extraction, FRAME computation, and
              provenance ledger you can cite directly in your audit trail.
            </p>
            <Link
              href="/marketplace"
              className="mt-8 inline-flex items-center gap-2 text-[14px] font-medium text-emerald hover:underline"
            >
              Open marketplace →
            </Link>
          </div>
          <NLProvinceFoodbankHeatMapDynamic banks={banks} height={640} />
        </div>
      </section>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <dt className="eyebrow">{label}</dt>
      <dd className="display tabular text-[34px] md:text-[42px] leading-none mt-1">{value}</dd>
    </div>
  )
}

function Pitch({
  kicker,
  title,
  italic,
  body,
  href,
  cta,
}: {
  kicker: string
  title: string
  italic: string
  body: string
  href: string
  cta: string
}) {
  return (
    <div className="flex flex-col">
      <p className="eyebrow">{kicker}</p>
      <h3 className="display text-[36px] md:text-[44px] mt-3 tracking-[-0.025em] leading-[1.05]">
        {title}{" "}
        <span className="display-italic text-emerald-deep">{italic}</span>
      </h3>
      <p className="text-text-muted text-[14.5px] mt-5 leading-relaxed max-w-[52ch]">
        {body}
      </p>
      <Link
        href={href}
        className="mt-7 inline-flex items-center gap-2 text-[14px] font-medium text-emerald hover:underline"
      >
        {cta}
      </Link>
    </div>
  )
}

function Step({ n, title, body }: { n: string; title: string; body: string }) {
  return (
    <li className="flex flex-col gap-3 border-t border-line pt-6">
      <span className="eyebrow tabular">{n}</span>
      <h3 className="display text-2xl tracking-[-0.02em]">{title}</h3>
      <p className="text-text-muted text-[14px] leading-relaxed">{body}</p>
    </li>
  )
}
