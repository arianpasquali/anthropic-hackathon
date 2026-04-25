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
import { QuarterlyTimelineChart } from "@/components/charts/QuarterlyTimelineChart"
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
  const [detail, timeline, metrics, pacing, allBanks] = await Promise.all([
    api.getSubscriptionDetail(primary.id),
    api.getDashboardTimeline(primary.id, 8).catch(() => []),
    api.getDashboardMetrics(primary.id).catch(() => null),
    api.getDashboardPacing(primary.id).catch(() => null),
    api.listFoodbanks().catch(() => []),
  ])

  const banksByName = new Map(allBanks.map((b) => [b.name, b]))

  // Quarterly forecast totals (for the timeline header)
  const realisedTotalT = timeline.filter((p) => p.realised).reduce((s, p) => s + p.co2e_kg, 0) / 1000
  const forecastTotalT = timeline.filter((p) => !p.realised).reduce((s, p) => s + p.co2e_kg, 0) / 1000

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
      <section className="mt-6 grid lg:grid-cols-[1fr_2fr] gap-6 items-start">
        {pacing ? <PacingBar pacing={pacing} /> : null}
        {metrics ? <Equivalents metrics={metrics} /> : null}
      </section>

      {/* Subscription runway — option C, no fictional past */}
      {timeline.length > 0 ? (
        <section className="mt-16 min-w-0">
          <div className="flex items-end justify-between flex-wrap gap-3">
            <div>
              <p className="eyebrow">Subscription runway</p>
              <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[28ch]">
                From your purchase date,{" "}
                <span className="display-italic text-emerald-deep">forward only.</span>
              </h2>
            </div>
            <div className="grid grid-cols-2 gap-x-8 text-right">
              <div>
                <p className="eyebrow">Realised</p>
                <p className="display tabular text-2xl mt-1">{formatTCO2e(realisedTotalT)}</p>
              </div>
              <div>
                <p className="eyebrow">Forecast (8q)</p>
                <p className="display-italic tabular text-2xl text-emerald-deep mt-1">
                  +{formatTCO2e(forecastTotalT)}
                </p>
              </div>
            </div>
          </div>
          <p className="text-text-muted text-[14px] mt-4 max-w-[68ch] leading-relaxed">
            Realised quarters cover the period since your subscription was paid; no
            retroactive attribution. Forecast extends the linear fit through your
            allocation&apos;s historical bank trajectories — useful for budgeting next
            year&apos;s disclosure. For the fund&apos;s pre-purchase track record, see the{" "}
            <Link href={`/funds/${primary.package_id}`} className="text-emerald hover:underline">
              fund page
            </Link>
            .
          </p>
          <div className="mt-6">
            <QuarterlyTimelineChart data={timeline} height={340} />
          </div>
        </section>
      ) : null}

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

      {/* Coverage + history */}
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

          <div className="mt-8 border-t border-line pt-6">
            <p className="eyebrow mb-3">Subscription history</p>
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

      {/* Allocation breakdown */}
      <section className="mt-16">
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
