import Link from "next/link"
import { redirect } from "next/navigation"
import { api, ApiError } from "@/lib/api"
import { Badge } from "@/components/ui/Badge"
import { DashboardAllocationsTable } from "@/components/dashboard/AllocationsTable"
import { ReportCard } from "@/components/dashboard/ReportCard"
import { ProvenanceScorecard } from "@/components/dashboard/ProvenanceScorecard"
import { CostEffectivenessGauge } from "@/components/dashboard/CostEffectivenessGauge"
import { Equivalents } from "@/components/dashboard/Equivalents"
import { PacingBar } from "@/components/dashboard/PacingBar"
import { MethodologyInline } from "@/components/dashboard/MethodologyInline"
import { NLProvinceHeatMapDynamic } from "@/components/map/NLProvinceHeatMapDynamic"
import { formatEur, formatNumber, formatPercent, formatTCO2e } from "@/lib/format"

const REGION_LABEL: Record<string, string> = {
  noord: "Noord",
  oost: "Oost",
  zuidoost: "Zuidoost",
  zuid: "Zuid",
  west: "West",
  randstad: "Randstad",
}

export default async function CorporateDashboardPage() {
  let subscriptions
  try {
    subscriptions = await api.listSubscriptions()
  } catch (e) {
    if (e instanceof ApiError && e.status === 401) redirect("/login?next=/dashboard/corporate")
    throw e
  }

  const me = await api.me().catch(() => null)
  if (!subscriptions.length) return <EmptyState />

  const primary = subscriptions[0]
  const [detail, metrics, pacing, allBanks] = await Promise.all([
    api.getSubscriptionDetail(primary.id),
    api.getDashboardMetrics(primary.id).catch(() => null),
    api.getDashboardPacing(primary.id).catch(() => null),
    api.listFoodbanks().catch(() => []),
  ])

  const banksByName = new Map(allBanks.map((b) => [b.name, b]))

  const periodTco2e = (metrics?.period_co2e_kg ?? 0) / 1000
  const cumulativeTco2e = (metrics?.cumulative_co2e_kg ?? 0) / 1000

  return (
    <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24">
      {/* Header */}
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

      {/* Tier 1 — disclosure-grade stats, typographic row */}
      <section className="mt-10 grid grid-cols-2 lg:grid-cols-4 divide-y lg:divide-y-0 lg:divide-x divide-line border-y border-line">
        <DashStat
          label="Contribution this quarter"
          value={formatTCO2e(periodTco2e)}
          hint="ESRS E5 + S3 · period-locked"
          delta={metrics?.period_delta_pct ?? null}
          emphasis
        />
        <DashStat
          label="Cumulative since inception"
          value={formatTCO2e(cumulativeTco2e)}
          hint={`${detail.allocations.length} banks · multi-year carryover`}
        />
        <DashStat
          label="€ / tCO₂e"
          value={metrics?.eur_per_tco2e != null ? formatEur(metrics.eur_per_tco2e) : "—"}
          hint="cost effectiveness benchmark"
        />
        <DashStat
          label="Households served"
          value={formatNumber(metrics?.households_weighted ?? 0)}
          hint={`weekly · ${formatNumber(metrics?.individuals_weighted ?? 0)} individuals (S3-1)`}
        />
      </section>

      {/* Methodology disclosure inline (audit signal) */}
      <section className="mt-8">
        <MethodologyInline />
      </section>

      {/* Pacing + Equivalents */}
      <section className="mt-6 grid lg:grid-cols-[1fr_2fr] gap-6 items-stretch">
        {pacing ? <PacingBar pacing={pacing} /> : null}
        {metrics ? <Equivalents metrics={metrics} /> : null}
      </section>

      {/* Trust + cost row */}
      <section className="mt-16 grid lg:grid-cols-2 gap-6 items-start">
        {metrics ? (
          <>
            <ProvenanceScorecard provenance={metrics.provenance} />
            <CostEffectivenessGauge
              eurPerTco2e={metrics.eur_per_tco2e}
              profile={primary.package_name.toLowerCase().includes("co2") ? "co2_focus" : undefined}
            />
          </>
        ) : null}
      </section>

      {/* Coverage + right rail */}
      <section className="mt-16 grid lg:grid-cols-[1.4fr_1fr] gap-x-12 gap-y-10 items-start">
        <div className="min-w-0">
          <p className="eyebrow">Geographic coverage</p>
          <h2 className="display text-2xl mt-3 tracking-[-0.02em]">
            Where the fund lands, by province.
          </h2>
          <p className="text-text-muted text-[13px] mt-3 max-w-[44ch] leading-relaxed">
            Province fill scaled to the fund&apos;s allocation weight in that region.
            Basemap: PDOK BRT (Kadaster).
          </p>
          <div className="mt-5">
            <NLProvinceHeatMapDynamic regions={metrics?.regions ?? []} height={360} />
          </div>
          <ul className="mt-5 grid grid-cols-2 gap-x-6 gap-y-2 text-[12.5px]">
            {(metrics?.regions ?? []).map((r) => (
              <li key={r.region} className="flex items-center justify-between border-b border-line/60 pb-1.5">
                <span className="text-text-muted">{REGION_LABEL[r.region] ?? r.region}</span>
                <span className="tabular text-text">
                  {formatPercent(r.weight_pct, 1)} · {r.foodbanks} banks
                </span>
              </li>
            ))}
          </ul>
        </div>

        {/* Right rail — at-a-glance, top foodbanks, subscription history */}
        <aside className="lg:sticky lg:top-20 flex flex-col gap-8 min-w-0">
          {/* Panel 1: at-a-glance numerics */}
          <div className="border border-line rounded-[var(--radius-lg)] bg-surface p-5">
            <p className="eyebrow mb-3">At a glance</p>
            <dl className="grid grid-cols-2 gap-x-4 gap-y-4 text-[12.5px]">
              <div>
                <dt className="text-text-faint">Foodbanks funded</dt>
                <dd className="display tabular text-2xl mt-0.5">{detail.allocations.length}</dd>
              </div>
              <div>
                <dt className="text-text-faint">Provinces covered</dt>
                <dd className="display tabular text-2xl mt-0.5">{(metrics?.regions ?? []).length}</dd>
              </div>
              <div>
                <dt className="text-text-faint">Annual contribution</dt>
                <dd className="display tabular text-2xl mt-0.5">{formatEur(detail.amount_eur * 4)}</dd>
              </div>
              <div>
                <dt className="text-text-faint">Cumulative tCO₂e</dt>
                <dd className="display tabular text-2xl mt-0.5">{formatTCO2e(cumulativeTco2e)}</dd>
              </div>
            </dl>
          </div>

          {/* Panel 2: top foodbanks by allocation weight */}
          <div className="border border-line rounded-[var(--radius-lg)] bg-surface p-5">
            <div className="flex items-baseline justify-between gap-3">
              <p className="eyebrow">Top foodbanks</p>
              <a
                href="#allocation-breakdown"
                className="text-[11.5px] text-text-faint hover:text-text"
              >
                See all →
              </a>
            </div>
            <ol className="mt-4 flex flex-col">
              {[...detail.allocations]
                .sort((a, b) => b.weight_pct - a.weight_pct)
                .slice(0, 5)
                .map((a, i) => {
                  const slug = banksByName.get(a.foodbank_name)?.slug
                  const NameEl = slug ? (
                    <Link
                      href={`/foodbanks/${slug}`}
                      className="text-[13px] text-text hover:text-emerald transition-colors truncate"
                    >
                      {a.foodbank_name}
                    </Link>
                  ) : (
                    <span className="text-[13px] text-text truncate">{a.foodbank_name}</span>
                  )
                  return (
                    <li
                      key={a.foodbank_id}
                      className="flex items-baseline justify-between gap-3 py-2 border-b border-line/60 last:border-b-0"
                    >
                      <span className="flex items-baseline gap-2 min-w-0">
                        <span className="tabular text-text-faint text-[11px] w-4 shrink-0">{i + 1}</span>
                        {NameEl}
                      </span>
                      <span className="tabular text-[12.5px] text-text-muted shrink-0">
                        {formatPercent(a.weight_pct, 1)}
                      </span>
                    </li>
                  )
                })}
            </ol>
          </div>

          {/* Panel 3: subscription history (lifted from below map) */}
          <div className="border border-line rounded-[var(--radius-lg)] bg-surface p-5">
            <p className="eyebrow mb-3">Subscription history</p>
            <ul className="flex flex-col text-[13px]">
              {subscriptions.map((s) => (
                <li
                  key={s.id}
                  className="flex items-center justify-between gap-3 py-2 border-b border-line/60 last:border-b-0"
                >
                  <span className="text-text truncate">{s.package_name}</span>
                  <span className="tabular text-text-muted shrink-0">{formatEur(s.amount_eur)}</span>
                </li>
              ))}
            </ul>
          </div>
        </aside>
      </section>

      {/* Allocation breakdown */}
      <section id="allocation-breakdown" className="mt-16 scroll-mt-20">
        <p className="eyebrow">Allocation breakdown</p>
        <h2 className="display text-3xl mt-3 tracking-[-0.02em]">
          Per food bank in your fund.
        </h2>
        <div className="mt-6">
          <DashboardAllocationsTable allocations={detail.allocations} />
        </div>
      </section>

      {/* CSR report */}
      <section className="mt-16">
        <ReportCard subId={detail.id} hasReport={!!detail.report_id} />
      </section>
    </div>
  )
}

function DashStat({
  label,
  value,
  hint,
  delta,
  emphasis = false,
}: {
  label: string
  value: React.ReactNode
  hint?: React.ReactNode
  delta?: number | null
  emphasis?: boolean
}) {
  return (
    <div className="flex flex-col gap-1.5 px-6 py-7">
      <span className="eyebrow">{label}</span>
      <span
        className={
          "display tabular text-[40px] md:text-[44px] leading-none " +
          (emphasis ? "text-emerald-deep" : "text-text")
        }
      >
        {value}
      </span>
      <div className="flex items-center gap-2 text-[12px] text-text-muted mt-0.5">
        {hint ? <span>{hint}</span> : null}
        {delta != null && Number.isFinite(delta) ? (
          <span
            className={
              "tabular font-medium " +
              (delta >= 0 ? "text-emerald-deep" : "text-warning")
            }
          >
            {delta >= 0 ? "↑" : "↓"} {(Math.abs(delta) * 100).toFixed(1)}%{" "}
            <span className="text-text-faint font-normal">YoY</span>
          </span>
        ) : null}
      </div>
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
