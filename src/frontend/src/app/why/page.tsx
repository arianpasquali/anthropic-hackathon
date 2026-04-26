import Image from "next/image"
import Link from "next/link"
import { loadImpact, fmtInt, type Stat } from "@/lib/impact"

export const metadata = {
  title: "Why · Climate Harvest",
  description:
    "The size of the gap, the urgency of the regulatory clock, and the contribution capacity Climate Harvest funds. Six citable arguments.",
}

export default async function WhyPage() {
  const data = await loadImpact()
  const csrd = data.csrd_wave
  const gap = data.avoided_emissions_gap
  const maxPeople = Math.max(...data.history.series.map((p) => p.people))

  return (
    <div className="overflow-hidden">
      <section className="relative isolate border-b border-line">
        <div aria-hidden className="kk-photo-hero absolute inset-0 -z-10">
          <Image
            src="https://images.unsplash.com/photo-1593113646773-028c64a8f1b8?auto=format&fit=crop&w=2400&q=80"
            alt=""
            fill
            sizes="100vw"
            priority
            className="object-cover"
          />
        </div>
        <div className="mx-auto max-w-[1100px] px-6 pt-16 md:pt-24 pb-16 md:pb-20">
          <p className="eyebrow">Public impact data</p>
          <h1 className="display text-5xl md:text-7xl mt-4 tracking-[-0.03em] leading-[1.02] max-w-[20ch]">
            Foodbanks are climate infrastructure{" "}
            <span className="display-italic text-emerald-deep">nobody counts.</span>
          </h1>
          <p className="mt-7 text-text-muted text-[16px] max-w-[64ch] leading-relaxed">
            Four sections, four citable arguments. The size of the gap, the
            urgency of the regulatory clock, and the contribution capacity this
            platform funds. Every figure derived from publicly published
            Voedselbanken Nederland reports, EU regulatory schedules, and the
            FRAME-aligned methodology documented in{" "}
            <Link href="/methodology" className="text-emerald hover:underline">
              Methodology
            </Link>
            .
          </p>
        </div>
      </section>

      <Section
        kicker="01"
        title="The poverty gap."
        italic="One million Dutch people live in poverty. The foodbanks reach 14%."
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <BigStat stat={data.poverty.people_under_poverty_line_nl} />
          <BigStat stat={data.poverty.people_helped_2024} />
          <BigStat stat={data.poverty.reach_rate_pct} accent />
        </div>
        <p className="mt-10 text-text-muted text-[14.5px] leading-relaxed max-w-[64ch]">
          86% of Dutch people in poverty are not reached by a foodbank. The gap
          is invisible in any official report.{" "}
          <Link href="/coverage" className="text-emerald hover:underline">
            See the gemeente-level map →
          </Link>
        </p>
      </Section>

      <Section
        kicker="02"
        title="A decade of pressure."
        italic="The 2024 numbers fell 20%. The need didn’t."
        tone="muted"
      >
        <HistoryTimeline series={data.history.series} maxPeople={maxPeople} />
        <p className="mt-10 text-text-muted text-[14.5px] leading-relaxed max-w-[64ch]">
          {data.history.annotation_2024}
        </p>
        <SourceLine
          label={data.history.source_label}
          url={data.history.source_url}
        />
      </Section>

      <Section
        kicker="03"
        title="The CSRD wave."
        italic="~7,000 NL mid-cap corporates need a verified climate disclosure."
      >
        <CsrdTimeline milestones={csrd.milestones} />
        <p className="mt-10 text-text-muted text-[14.5px] leading-relaxed max-w-[64ch]">
          Wave-2 timing was delayed by the EU&apos;s February 2025 Omnibus
          proposal, but the obligation is in scope and assurance is coming. The
          auditor-defensible infrastructure to disclose ESRS&nbsp;E5 + S3 climate
          contribution does not yet exist in non-energy sectors. CSR teams
          reach for half-defensible carbon credits and offset narratives;
          auditors push back. Climate Harvest fills that gap with measured,
          attributable climate-contribution disclosures.
        </p>
        <SourceLine label={csrd.source_label} url={csrd.source_url} />
      </Section>

      <Section
        kicker="04"
        title="The contribution-capacity gap."
        italic="75,000 tonnes of CO₂e of climate contribution sits unattributed every year."
        tone="muted"
      >
        <ImpactFlow gap={gap} />
        <p className="mt-10 text-text-muted text-[14.5px] leading-relaxed max-w-[64ch]">
          Dutch food waste produces ~
          {fmtInt(gap.nl_food_waste_tco2e / 1_000_000)} million tCO₂e per year.
          Foodbank rescue currently mitigates roughly{" "}
          {gap.current_mitigation_share_pct}% of it. None of that mitigation
          shows up anywhere in the climate-contribution economy — that is the
          wedge.
        </p>
        <SourceLine label={gap.source_label} url={gap.source_url} />
      </Section>

      <section className="border-t border-line">
        <div className="mx-auto max-w-[1100px] px-6 py-12 flex flex-col md:flex-row md:items-center md:justify-between gap-6">
          <p className="text-[12.5px] text-text-faint leading-relaxed max-w-[68ch]">
            Page generated{" "}
            {new Date(data.generated_at).toLocaleDateString("en-NL", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
            . EU-wide TAM: ~50,000 mid-cap companies; this view scopes to NL
            only. Climate contribution claim, not offsetting.
          </p>
          <Link
            href="/marketplace"
            className="inline-flex items-center text-[14px] font-medium text-emerald hover:text-emerald-deep transition-colors"
          >
            Browse funds →
          </Link>
        </div>
      </section>
    </div>
  )
}

// --- Layout primitives ---

function Section({
  kicker,
  title,
  italic,
  tone = "default",
  children,
}: {
  kicker: string
  title: string
  italic: string
  tone?: "default" | "muted"
  children: React.ReactNode
}) {
  const bg = tone === "muted" ? "bg-surface-2" : "bg-surface"
  return (
    <section className={`border-b border-line ${bg}`}>
      <div className="mx-auto max-w-[1100px] px-6 py-20">
        <div className="flex items-baseline gap-4 mb-6">
          <span className="eyebrow tabular">{kicker}</span>
          <span aria-hidden className="h-px w-10 bg-line-strong" />
        </div>
        <h2 className="display text-4xl md:text-5xl tracking-[-0.025em] max-w-[28ch]">
          {title}{" "}
          <span className="display-italic text-emerald-deep">{italic}</span>
        </h2>
        <div className="mt-12">{children}</div>
      </div>
    </section>
  )
}

function SourceLine({ label, url }: { label: string; url: string }) {
  return (
    <p className="mt-3 text-[11.5px] text-text-faint leading-relaxed">
      Source:{" "}
      {url ? (
        <a
          href={url}
          target={url.startsWith("http") ? "_blank" : undefined}
          rel="noreferrer"
          className="underline underline-offset-2 hover:text-text-muted"
        >
          {label}
        </a>
      ) : (
        <span>{label}</span>
      )}
    </p>
  )
}

// --- Section 1 — Big stat ---

function BigStat({ stat, accent }: { stat: Stat; accent?: boolean }) {
  const display = stat.unit === "%" ? `${stat.value}%` : fmtInt(stat.value)
  return (
    <div className="flex flex-col gap-3 border-t border-line pt-5">
      <p
        className={`display tabular tracking-[-0.03em] leading-[0.95] text-5xl md:text-6xl ${accent ? "text-emerald-deep" : "text-text"}`}
      >
        {display}
      </p>
      <p className="text-[14px] text-text leading-snug max-w-[36ch]">
        {stat.label}
      </p>
      {stat.source_label ? (
        <p className="text-[11.5px] text-text-faint">
          Source:{" "}
          {stat.source_url ? (
            <a
              href={stat.source_url}
              target="_blank"
              rel="noreferrer"
              className="underline underline-offset-2 hover:text-text-muted"
            >
              {stat.source_label}
            </a>
          ) : (
            <span>{stat.source_label}</span>
          )}
        </p>
      ) : null}
    </div>
  )
}

// --- Section 2 — History timeline ---

function HistoryTimeline({
  series,
  maxPeople,
}: {
  series: { year: number; people: number; note: string }[]
  maxPeople: number
}) {
  const W = 720
  const H = 280
  const PAD = { top: 30, right: 20, bottom: 40, left: 50 }
  const innerW = W - PAD.left - PAD.right
  const innerH = H - PAD.top - PAD.bottom

  const x = (year: number) => {
    const minY = series[0].year
    const maxY = series[series.length - 1].year
    return PAD.left + ((year - minY) / (maxY - minY)) * innerW
  }
  const y = (people: number) =>
    PAD.top + innerH - (people / maxPeople) * innerH

  const path = series
    .map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.year)} ${y(p.people)}`)
    .join(" ")

  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-6 lg:p-8 overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
        {[0, 0.5, 1].map((t) => {
          const yy = PAD.top + (1 - t) * innerH
          const val = Math.round(t * maxPeople)
          return (
            <g key={t}>
              <line
                x1={PAD.left}
                x2={W - PAD.right}
                y1={yy}
                y2={yy}
                stroke="var(--line)"
              />
              <text
                x={PAD.left - 8}
                y={yy + 4}
                fontSize="10"
                fill="var(--text-faint)"
                textAnchor="end"
              >
                {fmtInt(val)}
              </text>
            </g>
          )
        })}
        <path
          d={path}
          fill="none"
          stroke="var(--emerald-deep)"
          strokeWidth={1.75}
        />
        {series.map((p) => {
          const cx = x(p.year)
          const cy = y(p.people)
          const highlight = p.year === 2022 || p.year === 2024
          return (
            <g key={p.year}>
              <circle
                cx={cx}
                cy={cy}
                r={highlight ? 5 : 3.5}
                fill={highlight ? "var(--emerald-deep)" : "var(--surface)"}
                stroke="var(--emerald-deep)"
                strokeWidth={1.75}
              />
              <text
                x={cx}
                y={H - PAD.bottom + 18}
                fontSize="10.5"
                fill="var(--text-faint)"
                textAnchor="middle"
              >
                {p.year}
              </text>
              {highlight ? (
                <text
                  x={cx}
                  y={cy - 12}
                  fontSize="11"
                  fontWeight="600"
                  fill="var(--text)"
                  textAnchor="middle"
                >
                  {fmtInt(p.people)}
                </text>
              ) : null}
            </g>
          )
        })}
      </svg>
    </div>
  )
}

// --- Section 3 — CSRD timeline ---

function CsrdTimeline({
  milestones,
}: {
  milestones: {
    year: number
    label: string
    companies_nl: number
    is_current: boolean
  }[]
}) {
  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] overflow-hidden">
      <ol className="grid grid-cols-1 md:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-line">
        {milestones.map((m) => (
          <li key={m.year} className="px-6 py-7 flex flex-col gap-3">
            {m.is_current ? (
              <span className="self-start inline-flex items-center bg-emerald-soft text-emerald-deep text-[10.5px] font-semibold uppercase tracking-[0.12em] px-2 py-0.5 rounded-[2px]">
                We are here
              </span>
            ) : (
              <span aria-hidden className="h-[18px]" />
            )}
            <p
              className={`display tabular text-3xl md:text-4xl tracking-[-0.025em] ${m.is_current ? "text-emerald-deep" : "text-text"}`}
            >
              {m.year}
            </p>
            <p className="text-[13.5px] text-text leading-snug max-w-[28ch]">
              {m.label}
            </p>
            <p className="text-[11.5px] text-text-faint mt-1">
              <span className="tabular text-text">
                {fmtInt(m.companies_nl)}
              </span>{" "}
              NL companies
            </p>
          </li>
        ))}
      </ol>
    </div>
  )
}

// --- Section 4 — Impact flow ---

function ImpactFlow({
  gap,
}: {
  gap: {
    rescued_kg: number
    rescued_tco2e: number
    nl_food_waste_tco2e: number
    currently_disclosed_tco2e: number
  }
}) {
  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-6 lg:p-8">
      <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 md:gap-6 items-stretch">
        <FlowBox
          big={`${fmtInt(gap.rescued_kg / 1_000_000)}M`}
          unit="kg"
          label="Food rescued by Dutch foodbanks per year"
        />
        <FlowArrow direction="horizontal" />
        <FlowBox
          big={fmtInt(gap.rescued_tco2e)}
          unit="tCO₂e"
          label="Climate-contribution capacity per year"
        />
      </div>
      <div className="my-3 flex justify-center text-text-faint text-lg">
        ↓
      </div>
      <FlowBox
        big={fmtInt(gap.currently_disclosed_tco2e)}
        unit="tCO₂e"
        label="Currently attributed on a corporate disclosure"
        tone="warning"
      />
    </div>
  )
}

function FlowBox({
  big,
  unit,
  label,
  tone = "muted",
}: {
  big: string
  unit: string
  label: string
  tone?: "muted" | "warning"
}) {
  const isWarning = tone === "warning"
  return (
    <div
      className={`rounded-[var(--radius)] border p-5 ${isWarning ? "bg-warning-soft border-warning/40" : "bg-surface-2 border-line"}`}
    >
      <p
        className={`display tabular tracking-[-0.025em] text-3xl md:text-4xl leading-[0.95] ${isWarning ? "text-warning-deep" : "text-text"}`}
      >
        {big}
        <span
          className={`text-base font-normal ml-1.5 ${isWarning ? "text-warning-deep/70" : "text-text-faint"}`}
        >
          {unit}
        </span>
      </p>
      <p
        className={`mt-2 text-[13px] leading-snug ${isWarning ? "text-warning-deep" : "text-text-muted"}`}
      >
        {label}
      </p>
    </div>
  )
}

function FlowArrow({ direction }: { direction: "horizontal" }) {
  void direction
  return (
    <div className="flex items-center justify-center text-text-faint text-lg">
      <span className="hidden md:inline">→</span>
      <span className="md:hidden">↓</span>
    </div>
  )
}
