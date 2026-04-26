import { promises as fs } from "fs"
import path from "path"
import { api } from "@/lib/api"
import { MarketplaceFilters } from "@/components/marketing/MarketplaceFilters"
import { CoverageMap } from "@/components/marketing/CoverageMap"
import { formatNumber, formatTCO2e } from "@/lib/format"
import Image from "next/image"
import Link from "next/link"

interface CoverageGemeente {
  code: string
  name: string
  path: string
  persons_in_poverty: number | null
  households_in_poverty: number | null
  persons_in_poverty_pct: number | null
  households_in_poverty_pct: number | null
}

interface CoverageBank {
  id: string
  name: string
  region?: string
  x: number
  y: number
  annual_tco2e?: number
  households_weekly?: number | null
  is_rdc?: boolean
  rdc_satellite_count?: number | null
  in_demo_cohort: boolean
}

interface CoverageData {
  svg: { width: number; height: number }
  scale: { source_label: string; source_url: string }
  gemeenten: CoverageGemeente[]
  banks: CoverageBank[]
}

async function loadCoverage(): Promise<CoverageData> {
  const p = path.join(process.cwd(), "public", "coverage-data.json")
  const raw = await fs.readFile(p, "utf-8")
  return JSON.parse(raw) as CoverageData
}

export const metadata = {
  title: "Funds · Kavel",
  description:
    "Browse verified climate-contribution funds. Each fund spreads a single corporate contribution across the top Dutch food banks weighted by CO₂e or social reach. Contribution claim, not offsetting.",
}

export default async function MarketplacePage() {
  const [packages, banks, coverage] = await Promise.all([
    api.listPackages().catch(() => []),
    api.listFoodbanks().catch(() => []),
    loadCoverage(),
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
        <header className="mx-auto max-w-[1280px] px-6 pt-12 md:pt-20 pb-16 md:pb-20 min-h-[480px] md:min-h-[520px] flex flex-col justify-end max-w-[1280px]">
          <div className="max-w-[60ch]">
            <p className="eyebrow">Verified climate contribution · ESRS-aligned</p>
            <h1 className="display text-5xl md:text-7xl mt-4 tracking-[-0.03em] max-w-[18ch]">
              Buy a fund.{" "}
              <span className="display-italic text-emerald-deep">Move the network forward.</span>
            </h1>
            <p className="mt-7 text-text-muted text-[15.5px] leading-relaxed max-w-[52ch]">
              Each fund spreads a single corporate purchase across the top food banks
              in the Netherlands. The allocation engine ranks food banks by their FRAME-computed
              CO₂e baseline, household reach, or both — depending on the impact profile
              you choose.
            </p>
          </div>
        </header>
      </section>
      <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24">

      <section className="mt-14">
        <MarketplaceFilters packages={packages} />
      </section>

      <section className="mt-24 grid lg:grid-cols-[1.6fr_1fr] gap-x-10 gap-y-8 items-start">
        <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-3 order-2 lg:order-1">
          <CoverageMap
            width={coverage.svg.width}
            height={coverage.svg.height}
            gemeenten={coverage.gemeenten}
            banks={coverage.banks}
          />
        </div>
        <aside className="order-1 lg:order-2 lg:sticky lg:top-20 flex flex-col gap-6">
          <div>
            <p className="eyebrow">Fund coverage</p>
            <h2 className="display text-3xl md:text-4xl mt-3 tracking-[-0.02em]">
              Where the funds land.{" "}
              <span className="display-italic text-emerald-deep">
                Where the need is.
              </span>
            </h2>
            <p className="mt-4 text-text-muted text-[14px] leading-relaxed">
              Gemeenten shaded by share of population on a low income for ≥1
              year (CBS&nbsp;2023). Demo cohort foodbanks overlaid as emerald
              circles, sized by annual climate-contribution capacity.
            </p>
          </div>
          <dl className="grid grid-cols-2 gap-x-6 gap-y-5 border-t border-line pt-5">
            <div>
              <dt className="eyebrow">Annual baseline</dt>
              <dd className="display tabular text-2xl mt-1">{formatTCO2e(totalCo2)}</dd>
            </div>
            <div>
              <dt className="eyebrow">Rescued / yr</dt>
              <dd className="display tabular text-2xl mt-1">
                {formatNumber(totalKg / 1_000_000, { maximumFractionDigits: 1 })}M kg
              </dd>
            </div>
            <div>
              <dt className="eyebrow">Foodbanks</dt>
              <dd className="display tabular text-2xl mt-1">{coverage.banks.length}</dd>
            </div>
            <div>
              <dt className="eyebrow">Gemeenten covered</dt>
              <dd className="display tabular text-2xl mt-1">{coverage.gemeenten.length}</dd>
            </div>
          </dl>
          <div className="border-t border-line pt-5">
            <p className="text-[13px] text-text-muted leading-relaxed">
              Detailed gemeente-level analysis + insight columns + Heerlen
              expansion narrative on the full coverage page.
            </p>
            <Link
              href="/coverage"
              className="mt-4 inline-flex items-center gap-2 text-[13.5px] font-medium text-emerald hover:underline"
            >
              Open full coverage →
            </Link>
          </div>
        </aside>
      </section>

      <section className="mt-24 grid md:grid-cols-2 gap-x-12 gap-y-6 border-t border-line pt-10">
        <h2 className="display text-3xl max-w-[20ch]">
          Want a transparency profile for one specific foodbank?
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
