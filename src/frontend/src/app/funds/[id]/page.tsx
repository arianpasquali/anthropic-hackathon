import { api, ApiError } from "@/lib/api"
import { notFound } from "next/navigation"
import { AllocationTable } from "@/components/funds/AllocationTable"
import { TimelineChart } from "@/components/charts/TimelineChart"
import Link from "next/link"
import { Badge } from "@/components/ui/Badge"
import { formatEur, formatNumber, formatPercent, formatTCO2e } from "@/lib/format"

export default async function FundDetailPage({
  params,
}: {
  params: Promise<{ id: string }>
}) {
  const { id } = await params

  const pkg = await api.getPackage(id).catch((e) => {
    if (e instanceof ApiError && e.status === 404) return null
    throw e
  })
  if (!pkg) notFound()
  const timeline = await api.getPackageTimeline(id).catch(() => [])

  const totals = pkg.projected_allocations.reduce(
    (acc, a) => ({
      kg: acc.kg + a.attributed_kg,
      tco2e: acc.tco2e + a.attributed_tco2e,
      banks: acc.banks + 1,
    }),
    { kg: 0, tco2e: 0, banks: 0 },
  )


  return (
    <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24 grid lg:grid-cols-[1fr_360px] gap-x-12">
      <div>
        <p className="eyebrow">{pkg.region.toUpperCase()} · {pkg.impact_profile.replace("_", " ")}</p>
        <h1 className="display text-5xl md:text-6xl mt-4 tracking-[-0.025em] max-w-[20ch]">
          {pkg.name}
        </h1>
        {pkg.description ? (
          <p className="text-text-muted text-[15.5px] mt-5 max-w-[60ch] leading-relaxed">
            {pkg.description}
          </p>
        ) : null}

        <div className="grid grid-cols-3 gap-6 mt-10 pt-8 border-t border-line">
          <Stat label="Total avoided" value={formatTCO2e(pkg.co2e_claim_kg / 1000)} />
          <Stat label="Allocated to" value={`${totals.banks} food banks`} />
          <Stat label="Per-bank avg" value={formatEur(pkg.price_eur / Math.max(1, totals.banks))} />
        </div>

        <section className="mt-14">
          <p className="eyebrow">Projected allocation</p>
          <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[26ch]">
            Where this fund lands.{" "}
            <span className="display-italic text-emerald-deep">Computed at purchase time.</span>
          </h2>
          <p className="text-text-muted text-[14px] mt-4 max-w-[56ch] leading-relaxed">
            The allocation engine ranks every Dutch food bank we ingest data for by{" "}
            {pkg.impact_profile === "co2_focus"
              ? "FRAME-computed CO₂e baseline"
              : pkg.impact_profile === "social_focus"
                ? "weekly household reach"
                : "a balanced score across CO₂e and households"}{" "}
            and takes the top {pkg.top_n}. Weights are normalised so each bank&apos;s share
            is proportional to its contribution.
          </p>

          <div className="mt-8">
            <AllocationTable allocations={pkg.projected_allocations} />
          </div>
        </section>

        {timeline.length > 0 ? (
          <section className="mt-16 min-w-0">
            <div className="flex items-end justify-between flex-wrap gap-3">
              <div>
                <p className="eyebrow">Historical performance</p>
                <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[26ch]">
                  Fund-weighted CO₂e since {timeline[0].year}.
                </h2>
              </div>
              <p className="text-[12.5px] text-text-faint tabular">
                aggregated across top {pkg.top_n} banks
              </p>
            </div>
            <p className="text-text-muted text-[14px] mt-4 max-w-[58ch] leading-relaxed">
              Each year sums every food bank&apos;s baseline weighted by what its
              allocation share would be if the fund had been bought that year.
              Use this to project realised impact for your subscription.
            </p>
            <div className="mt-6">
              <TimelineChart data={timeline} height={280} />
            </div>
          </section>
        ) : null}

        <section className="mt-16">
          <div className="border border-line rounded-[var(--radius-lg)] p-6 bg-surface max-w-[52ch]">
            <p className="eyebrow mb-3">What you receive</p>
            <ul className="flex flex-col gap-3 text-[13.5px]">
              <Item>Quarterly ESRS E1 + S3 disclosure (markdown + PDF)</Item>
              <Item>FRAME workings: kg per category × EF × counterfactual</Item>
              <Item>
                Source citations from {pkg.projected_allocations.length} food bank annual
                reports
              </Item>
              <Item>Provenance ledger per measurement (extracted vs inferred)</Item>
              <Item>Allocation breakdown with bank-level attribution</Item>
            </ul>
          </div>
        </section>

        <section className="mt-16 pt-10 border-t border-line">
          <p className="eyebrow">Methodology</p>
          <div className="grid md:grid-cols-2 gap-x-12 gap-y-6 mt-4 max-w-[68ch]">
            <p className="text-[14px] text-text-muted leading-relaxed">
              All figures derive from extracted Dutch food bank annual reports, processed
              through Claude with section-specific prompts and validated against the
              FRAME methodology used by Global FoodBanking Network.
            </p>
            <p className="text-[14px] text-text-muted leading-relaxed">
              The NL counterfactual is incineration with energy recovery (RIVM Afvalmonitor
              2024 + CBS Waste Statistics), conservative compared to global landfill
              defaults.
            </p>
          </div>
          <div className="mt-6 flex items-center gap-3">
            <Badge variant="outline">FRAME aligned</Badge>
            <Badge variant="outline">CSRD-ready</Badge>
            <Badge variant="outline">ESRS E1 + S3</Badge>
            <Badge variant="outline">NL-specific</Badge>
          </div>
        </section>
      </div>

      <aside className="lg:sticky lg:top-24 flex flex-col items-center justify-center gap-4 p-7 bg-[#f0fdf4] border-2 border-[#bbf7d0] rounded-xl min-w-[200px] text-center">
        <div className="text-[11px] text-[#059669] font-semibold uppercase tracking-wide">From €10k / year</div>
        <Link
          href="/pricing"
          className="block w-full px-8 py-3.5 bg-[#388e3c] text-white rounded-lg text-[14px] font-extrabold hover:bg-[#2e7d32] transition-colors"
        >
          Invest in this fund →
        </Link>
        <div className="text-[11px] text-text-muted leading-relaxed">
          No lock-in · ESRS E1+S3 report included
          <br />
          Invoiced via Solvimon
        </div>
      </aside>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="eyebrow">{label}</span>
      <span className="display tabular text-2xl md:text-3xl">{value}</span>
    </div>
  )
}

function Item({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2">
      <span aria-hidden className="mt-2 block w-1.5 h-1.5 bg-emerald rounded-full shrink-0" />
      <span className="text-text">{children}</span>
    </li>
  )
}

