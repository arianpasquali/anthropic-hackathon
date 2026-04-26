import { api } from "@/lib/api"
import { MarketplaceFilters } from "@/components/marketing/MarketplaceFilters"
import { NLProvinceFoodbankHeatMapDynamic } from "@/components/map/NLProvinceFoodbankHeatMapDynamic"
import { ProvinceFoodbankList } from "@/components/map/ProvinceFoodbankList"
import { formatNumber, formatTCO2e } from "@/lib/format"
import Image from "next/image"
import Link from "next/link"

export const metadata = {
  title: "Marketplace · Climate Harvest",
  description:
    "Browse verified climate-contribution funds. Each fund spreads a single corporate contribution across the top Dutch food banks weighted by CO₂e or social reach. Contribution claim, not offsetting.",
}

export default async function MarketplacePage() {
  const [packages, banks] = await Promise.all([
    api.listPackages().catch(() => []),
    api.listFoodbanks().catch(() => []),
  ])

  const totalCo2 = banks.reduce((s, b) => s + (b.annual_tco2e ?? 0), 0)
  const totalKg = banks.reduce((s, b) => s + (b.annual_kg_rescued ?? 0), 0)

  return (
    <div>
      <section className="relative isolate border-b border-line">
        <div aria-hidden className="kk-photo-hero absolute inset-0 -z-10">
          <Image
            src="https://images.unsplash.com/photo-1755599629285-91cc09a185c7?auto=format&fit=crop&w=2400&q=80"
            alt=""
            fill
            sizes="100vw"
            priority
            className="object-cover"
          />
        </div>
        <header className="mx-auto max-w-[1280px] px-6 pt-12 md:pt-20 pb-16 md:pb-20 grid md:grid-cols-[1.4fr_1fr] gap-12 items-end">
          <div>
            <p className="eyebrow">Verified climate contribution · ESRS-aligned</p>
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
      </section>
      <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24">

      <section className="mt-14">
        <MarketplaceFilters packages={packages} />
      </section>

      <section className="mt-24">
        <div className="flex flex-col md:flex-row md:items-end gap-6 mb-10">
          <div className="flex-1">
            <p className="eyebrow">Fund coverage</p>
            <h2 className="display text-4xl mt-3 tracking-[-0.02em] max-w-[24ch]">
              Provinces tinted by{" "}
              <span className="display-italic text-emerald-deep">CO₂e baseline</span>{" "}
              reachable through funds.
            </h2>
          </div>
          <dl className="flex gap-10 pb-1 shrink-0">
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
        <NLProvinceFoodbankHeatMapDynamic
          banks={banks}
          colorBy="co2e"
          totalFunds={packages.length}
        />
        <div className="mt-6">
          <ProvinceFoodbankList banks={banks} />
        </div>
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
    </div>
  )
}
