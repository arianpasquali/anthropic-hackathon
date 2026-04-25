import Link from "next/link"
import { api, ApiError } from "@/lib/api"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/dashboard/StatCard"
import { DashboardAllocationsTable } from "@/components/dashboard/AllocationsTable"
import { ReportCard } from "@/components/dashboard/ReportCard"
import { Progress } from "@/components/ui/Progress"
import { CategoryBars } from "@/components/charts/CategoryBars"
import { CF_NL, EMISSION_FACTORS } from "@/lib/methodology"
import { formatEur, formatNumber, formatPercent, formatTCO2e } from "@/lib/format"
import { redirect } from "next/navigation"

export default async function CorporateDashboardPage() {
  let subscriptions
  try {
    subscriptions = await api.listSubscriptions()
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) redirect("/login?next=/dashboard/corporate")
    throw e
  }

  const me = await api.me().catch(() => null)

  if (!subscriptions.length) {
    return <EmptyState />
  }

  const primary = subscriptions[0]
  const detail = await api.getSubscriptionDetail(primary.id)

  // Need bank category mixes for the chart — pull foodbanks list and look up.
  const allBanks = await api.listFoodbanks().catch(() => [])
  const banksByName = new Map(allBanks.map((b) => [b.name, b]))

  const totalCo2eT = detail.total_co2e_kg / 1000
  const fundedKg = detail.allocations.reduce((s, a) => s + (a.co2e_attributed_kg / Math.max(0.01, EMISSION_FACTORS.produce)), 0)

  // Aggregate per-category tCO2e using each bank's mix
  const categoryTotals: Record<string, number> = {
    produce: 0, dry_goods: 0, dairy: 0, bakery: 0, meat: 0, prepared: 0, eggs: 0,
  }
  for (const alloc of detail.allocations) {
    const bank = banksByName.get(alloc.foodbank_name)
    if (!bank?.category_mix || !bank.annual_kg_rescued) continue
    const attributedKg = bank.annual_kg_rescued * alloc.weight_pct
    for (const k of Object.keys(categoryTotals) as (keyof typeof EMISSION_FACTORS)[]) {
      const frac = bank.category_mix[k] ?? 0
      categoryTotals[k] += (attributedKg * frac * EMISSION_FACTORS[k] * CF_NL) / 1000
    }
  }

  const peopleReached = Math.round(
    detail.allocations.reduce((s, a) => {
      const bank = banksByName.get(a.foodbank_name)
      return s + (bank?.households_weekly ?? 0) * a.weight_pct * 52 * 2.3
    }, 0),
  )

  return (
    <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24">
      <header className="flex items-end justify-between flex-wrap gap-6 pb-10 border-b border-line">
        <div>
          <p className="eyebrow">Corporate dashboard</p>
          <h1 className="display text-5xl mt-3 tracking-[-0.025em]">
            {me?.org_name ?? "Your organisation"}
          </h1>
          <p className="text-text-muted mt-3 text-[14.5px]">
            <Badge variant="default" className="mr-2">{detail.package_name}</Badge>
            <Badge variant={detail.status === "paid" ? "emerald" : "warning"}>{detail.status}</Badge>
            <span className="ml-3 tabular">{formatEur(detail.amount_eur)} · quarterly</span>
          </p>
        </div>
        <Link
          href={`/reports/${detail.id}`}
          className="bg-emerald text-text-on-emerald h-11 px-5 inline-flex items-center text-[14px] font-medium"
        >
          View CSR report →
        </Link>
      </header>

      <section className="grid grid-cols-2 lg:grid-cols-4 gap-5 mt-10">
        <StatCard label="Avoided" value={formatTCO2e(totalCo2eT)} hint={`across ${detail.allocations.length} banks`} emphasis />
        <StatCard label="Rescued" value={`${formatNumber(fundedKg / 1_000_000, { maximumFractionDigits: 1 })}M kg`} hint="kg of food, this quarter" />
        <StatCard label="People reached" value={formatNumber(peopleReached)} hint="estimated, this quarter" />
        <StatCard label="Invested" value={formatEur(detail.amount_eur)} hint="paid via Solvimon" />
      </section>

      <section className="mt-16 grid lg:grid-cols-[1.6fr_1fr] gap-x-12 gap-y-10 items-start">
        <div>
          <p className="eyebrow">CO₂e by category</p>
          <h2 className="display text-3xl mt-3 tracking-[-0.02em]">
            Where the rescue avoids emissions.
          </h2>
          <p className="text-text-muted text-[14px] mt-4 max-w-[52ch]">
            Computed across your portfolio: each bank&apos;s category mix × kg attributed to
            you × FRAME emission factor × NL counterfactual ({CF_NL}).
          </p>
          <div className="mt-6">
            <CategoryBars data={categoryTotals} />
          </div>
        </div>

        <div>
          <p className="eyebrow">Attribution</p>
          <h2 className="display text-2xl mt-3 tracking-[-0.02em]">
            Your share of {detail.package_name}.
          </h2>
          <div className="mt-6 flex flex-col gap-3">
            <Progress value={Math.min(1, detail.amount_eur / Math.max(detail.amount_eur, 1) )} />
            <p className="text-[13px] text-text-muted">
              {formatPercent(1 / Math.max(1, subscriptions.length), 1)} of total subscriber pool
            </p>
          </div>
          <div className="mt-8 border-t border-line pt-6">
            <h3 className="eyebrow mb-4">Subscription history</h3>
            <ul className="flex flex-col gap-3 text-[13.5px]">
              {subscriptions.map((s) => (
                <li key={s.id} className="flex items-center justify-between border-b border-line/60 pb-2 last:border-b-0 last:pb-0">
                  <span className="text-text">{s.package_name}</span>
                  <span className="tabular text-text-muted">{formatEur(s.amount_eur)}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      <section className="mt-16">
        <p className="eyebrow">Allocation breakdown</p>
        <h2 className="display text-3xl mt-3 tracking-[-0.02em]">
          Per food bank in your fund.
        </h2>
        <div className="mt-6">
          <DashboardAllocationsTable allocations={detail.allocations} />
        </div>
      </section>

      <section className="mt-16">
        <ReportCard subId={detail.id} hasReport={!!detail.report_id} />
      </section>
    </div>
  )
}

function EmptyState() {
  return (
    <div className="mx-auto max-w-[820px] px-6 pt-24 pb-24 text-center">
      <p className="eyebrow">No subscriptions yet</p>
      <h1 className="display text-5xl mt-4 tracking-[-0.025em]">
        Pick a fund to see your dashboard come to life.
      </h1>
      <p className="text-text-muted text-[14.5px] mt-6 max-w-[44ch] mx-auto leading-relaxed">
        Once you subscribe, this dashboard shows your live allocation, CO₂e attribution,
        and CSR report — generated on demand by Claude.
      </p>
      <div className="mt-8">
        <Link
          href="/marketplace"
          className="bg-emerald text-text-on-emerald h-11 px-5 inline-flex items-center text-[14px] font-medium"
        >
          Browse funds →
        </Link>
      </div>
    </div>
  )
}
