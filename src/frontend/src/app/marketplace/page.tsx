import { api } from "@/lib/api"
import { MarketplaceFilters } from "@/components/marketing/MarketplaceFilters"
import { NLMapDynamic } from "@/components/map/NLMapDynamic"
import { formatNumber, formatTCO2e } from "@/lib/format"
import Link from "next/link"

export const metadata = {
  title: "Marketplace · Klimaatkracht",
  description:
    "Browse verified avoided-emissions funds. Each fund spreads a single corporate purchase across the top Dutch food banks weighted by CO₂e or social reach.",
}

export default async function MarketplacePage() {
  const [packages, banks] = await Promise.all([
    api.listPackages().catch(() => []),
    api.listFoodbanks().catch(() => []),
  ])

  const totalCo2 = banks.reduce((s, b) => s + (b.annual_tco2e ?? 0), 0)
  const totalKg = banks.reduce((s, b) => s + (b.annual_kg_rescued ?? 0), 0)

  return (
    <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24">
      <header className="grid md:grid-cols-[1.4fr_1fr] gap-12 items-end pb-12 border-b border-line">
        <div>
          <p className="eyebrow">Verified avoided emissions · CSRD-ready</p>
          <h1 className="display text-5xl md:text-6xl mt-4 tracking-[-0.025em] max-w-[18ch]">
            Buy a fund.{" "}
            <span className="display-italic text-emerald-deep">Move the network forward.</span>
          </h1>
        </div>
        <p className="text-text-muted text-[15px] leading-relaxed max-w-[42ch]">
          Each fund spreads a single corporate purchase across the top food banks
          in the Netherlands. The allocation engine ranks banks by their FRAME-computed
          CO₂e baseline, household reach, or both — depending on the impact profile
          you choose.
        </p>
      </header>

      <section className="mt-14">
        <MarketplaceFilters packages={packages} />
      </section>

      <section className="mt-24 grid lg:grid-cols-[1fr_1.2fr] gap-12 items-start">
        <div>
          <p className="eyebrow">Where the rescue happens</p>
          <h2 className="display text-4xl mt-3 tracking-[-0.02em] max-w-[18ch]">
            {formatNumber(banks.length)} food banks across the Netherlands.
          </h2>
          <p className="text-text-muted text-[14.5px] mt-5 max-w-[40ch] leading-relaxed">
            The map shows every operator we ingest data for. Each pin links to its
            transparency profile, including extracted vs inferred provenance per field.
          </p>
          <dl className="grid grid-cols-2 gap-y-5 gap-x-6 mt-10 pt-8 border-t border-line">
            <div>
              <dt className="eyebrow">Annual baseline</dt>
              <dd className="display tabular text-3xl mt-1">{formatTCO2e(totalCo2)}</dd>
            </div>
            <div>
              <dt className="eyebrow">Rescued / yr</dt>
              <dd className="display tabular text-3xl mt-1">
                {formatNumber(totalKg / 1_000_000, { maximumFractionDigits: 1 })}M kg
              </dd>
            </div>
          </dl>
        </div>
        <NLMapDynamic banks={banks} height={460} />
      </section>

      <section className="mt-24 grid md:grid-cols-2 gap-x-12 gap-y-6 border-t border-line pt-10">
        <h2 className="display text-3xl max-w-[20ch]">
          Want a transparency profile for one specific bank?
        </h2>
        <div>
          <p className="text-text-muted text-[14.5px] leading-relaxed max-w-[48ch]">
            Each food bank has a public profile that lists its annual report
            extraction, FRAME computation, and full provenance ledger. Use these to
            cite a specific operator in your audit trail.
          </p>
          <ul className="mt-6 grid grid-cols-2 gap-x-4 gap-y-1.5">
            {banks.slice(0, 8).map((b) => (
              <li key={b.id}>
                <Link
                  href={`/foodbanks/${b.slug}`}
                  className="text-[13.5px] text-text hover:text-emerald transition-colors"
                >
                  {b.name} →
                </Link>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </div>
  )
}
