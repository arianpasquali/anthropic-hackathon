import { loadImpact, fmtInt, fmtEur, type Stat } from "@/lib/impact";
import AdoptionSlider from "./AdoptionSlider";

export const metadata = {
  title: "Impact data — Climate-Action Packages",
  description:
    "How big is the gap, how urgent is the timing, and how much changes if Dutch corporates start counting Dutch foodbanks as climate infrastructure.",
};

export default async function ImpactPage() {
  const data = await loadImpact();
  const csrd = data.csrd_wave;
  const gap = data.avoided_emissions_gap;

  // Y-axis scale for history chart
  const maxPeople = Math.max(...data.history.series.map((p) => p.people));

  return (
    <div className="bg-stone-50">
      <Hero />

      {/* Section 1 — Poverty gap */}
      <Section
        eyebrow="01 — The poverty gap"
        title="One million Dutch people live in poverty. The foodbanks reach 14% of them."
      >
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <BigStat stat={data.poverty.people_under_poverty_line_nl} accent="stone" />
          <BigStat stat={data.poverty.people_helped_2024} accent="stone" />
          <BigStat stat={data.poverty.reach_rate_pct} accent="emerald" />
        </div>
        <p className="mt-8 text-stone-700 leading-relaxed max-w-2xl">
          73% of Dutch people in poverty are not reached by a foodbank.
          The gap is invisible in any official report.
        </p>
      </Section>

      {/* Section 2 — Food paradox */}
      <Section
        eyebrow="02 — The food paradox"
        title="The Netherlands wastes 70 times more food than its foodbanks rescue."
      >
        <PovertyBars
          waste={data.food_paradox.nl_food_waste_kg}
          rescued={data.food_paradox.foodbanks_rescued_kg}
        />
        <p className="mt-8 text-stone-700 leading-relaxed max-w-2xl">
          Foodbanks recover {data.food_paradox.rescue_share_pct.value}% of NL food
          waste. The platform compounds that throughput by paying for it — funding
          banks to rescue more, instead of asking corporates to pay landfill avoidance
          fees that never reach the social side.
        </p>
      </Section>

      {/* Section 3 — Decade of pressure */}
      <Section
        eyebrow="03 — A decade of pressure"
        title="The 2024 numbers fell 20%. The need didn't."
      >
        <HistoryTimeline series={data.history.series} maxPeople={maxPeople} />
        <p className="mt-8 text-stone-700 leading-relaxed max-w-2xl">
          {data.history.annotation_2024}
        </p>
        <SourceLine label={data.history.source_label} url={data.history.source_url} />
      </Section>

      {/* Section 4 — CSRD wave */}
      <Section
        eyebrow="04 — The CSRD wave"
        title="~7,000 Dutch mid-cap corporates are about to need a verified climate-impact disclosure."
      >
        <CsrdTimeline milestones={csrd.milestones} />
        <p className="mt-8 text-stone-700 leading-relaxed max-w-2xl">
          Wave-2 timing was delayed by the EU&apos;s February 2025 Omnibus
          proposal, but the obligation is in scope and assurance is coming.
          The audit-grade infrastructure to disclose ESRS E1 climate impact
          in non-energy sectors does not yet exist. CSR teams reach for the
          same half-defensible carbon credits and offset narratives, and
          auditors push back. The platform fills that gap with measured,
          attributable avoided emissions.
        </p>
        <SourceLine label={csrd.source_label} url={csrd.source_url} />
      </Section>

      {/* Section 5 — Avoided-emissions gap */}
      <Section
        eyebrow="05 — The avoided-emissions gap"
        title="75,000 tonnes of CO₂e avoided every year. None of it on a single corporate report."
      >
        <ImpactFlow gap={gap} />
        <p className="mt-8 text-stone-700 leading-relaxed max-w-2xl">
          Dutch food waste produces ~{fmtInt(gap.nl_food_waste_tco2e / 1_000_000)} million tCO₂e per year.
          Foodbank rescue currently mitigates roughly {gap.current_mitigation_share_pct}% of it.
          None of that mitigation shows up anywhere in the climate-disclosure economy.
        </p>
        <SourceLine label={gap.source_label} url={gap.source_url} />
      </Section>

      {/* Section 6 — What changes */}
      <Section
        eyebrow="06 — What changes"
        title="Where supply caps. And how the platform grows."
      >
        <AdoptionSlider
          scenarios={data.adoption_scenarios.scenarios}
          supplyCap={data.adoption_scenarios.supply_cap}
          packageEur={data.adoption_scenarios.package_eur}
          packageTco2e={data.adoption_scenarios.package_tco2e}
          totalCorporates={data.adoption_scenarios.total_csrd_corporates_nl}
          vbnBudget={data.adoption_scenarios.vbn_annual_budget_eur}
          vbnBudgetSourceLabel={data.adoption_scenarios.vbn_budget_source_label}
          vbnBudgetSourceUrl={data.adoption_scenarios.vbn_budget_source_url}
        />
        <p className="mt-8 text-stone-700 leading-relaxed max-w-2xl">
          The platform is supply-constrained, not demand-constrained. Even modest
          corporate adoption fully books NL foodbank capacity. That is a launch-stage
          asset, not a problem: pricing power, capital efficiency, and a clear
          expansion path through additional banks and EU markets.
        </p>
      </Section>

      <footer className="border-t border-stone-200 bg-white py-8 mt-12">
        <div className="mx-auto max-w-4xl px-6 text-xs text-stone-500">
          Page generated {new Date(data.generated_at).toLocaleDateString("en-NL", { year: "numeric", month: "long", day: "numeric" })}.
          All figures are derived from publicly published Voedselbanken Nederland
          reports, EU regulatory schedules, and the FRAME-aligned methodology
          documented at <a href="/methodology" className="underline hover:text-stone-700">/methodology</a>.
          EU-wide TAM: ~50,000 mid-cap companies; this view scopes to NL only.
        </div>
      </footer>
    </div>
  );
}

// --- Layout primitives ---

function Hero() {
  return (
    <section className="border-b border-stone-200 bg-white">
      <div className="mx-auto max-w-4xl px-6 py-16 lg:py-20">
        <p className="text-xs uppercase tracking-widest text-emerald-800 font-semibold mb-3">
          Public impact data
        </p>
        <h1 className="text-4xl lg:text-5xl font-semibold tracking-tight text-stone-900 leading-[1.05]">
          Foodbanks are climate infrastructure that nobody counts.
        </h1>
        <p className="mt-5 max-w-2xl text-lg text-stone-600 leading-relaxed">
          Six scrolling sections, six citable arguments. The size of the gap, the
          urgency of the regulatory clock, and the headroom this platform unlocks.
        </p>
      </div>
    </section>
  );
}

function Section({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="border-b border-stone-200 bg-white">
      <div className="mx-auto max-w-4xl px-6 py-16">
        <p className="text-xs uppercase tracking-widest text-emerald-800 font-semibold mb-3">
          {eyebrow}
        </p>
        <h2 className="text-2xl lg:text-3xl font-semibold tracking-tight text-stone-900 max-w-3xl leading-tight mb-10">
          {title}
        </h2>
        {children}
      </div>
    </section>
  );
}

function SourceLine({ label, url }: { label: string; url: string }) {
  return (
    <p className="mt-3 text-xs text-stone-500">
      Source:{" "}
      {url ? (
        <a
          href={url}
          target={url.startsWith("http") ? "_blank" : undefined}
          rel="noreferrer"
          className="underline hover:text-stone-700"
        >
          {label}
        </a>
      ) : (
        <span>{label}</span>
      )}
    </p>
  );
}

// --- Big stat ---

function BigStat({ stat, accent }: { stat: Stat; accent: "stone" | "emerald" }) {
  const accentClass = accent === "emerald" ? "text-emerald-800" : "text-stone-900";
  const display =
    stat.unit === "%"
      ? `${stat.value}%`
      : fmtInt(stat.value);

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6">
      <p className={`text-4xl lg:text-5xl font-semibold tabular-nums tracking-tight ${accentClass}`}>
        {display}
      </p>
      <p className="mt-2 text-sm text-stone-700">{stat.label}</p>
      {stat.source_label && (
        <p className="mt-3 text-xs text-stone-500">
          Source:{" "}
          {stat.source_url ? (
            <a
              href={stat.source_url}
              target="_blank"
              rel="noreferrer"
              className="underline hover:text-stone-700"
            >
              {stat.source_label}
            </a>
          ) : (
            <span>{stat.source_label}</span>
          )}
        </p>
      )}
    </div>
  );
}

// --- Section 2 — Bars ---

function PovertyBars({ waste, rescued }: { waste: Stat; rescued: Stat }) {
  const max = waste.value;
  const ratio = (rescued.value / max) * 100;

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6 lg:p-8">
      <Bar
        label="NL food waste / year"
        valueLabel={`${(waste.value / 1_000_000_000).toFixed(1)} billion kg`}
        widthPct={100}
        color="bg-stone-300"
        sourceLabel={waste.source_label}
        sourceUrl={waste.source_url}
      />
      <div className="h-6" />
      <Bar
        label="Rescued by foodbanks"
        valueLabel={`${(rescued.value / 1_000_000).toFixed(0)} million kg`}
        widthPct={Math.max(ratio, 1.5)}
        color="bg-emerald-700"
        sourceLabel={rescued.source_label}
        sourceUrl={rescued.source_url}
      />
    </div>
  );
}

function Bar({
  label,
  valueLabel,
  widthPct,
  color,
  sourceLabel,
  sourceUrl,
}: {
  label: string;
  valueLabel: string;
  widthPct: number;
  color: string;
  sourceLabel: string;
  sourceUrl: string;
}) {
  return (
    <div>
      <div className="flex justify-between items-baseline mb-1.5">
        <span className="text-sm text-stone-700">{label}</span>
        <span className="text-sm font-medium tabular-nums text-stone-900">{valueLabel}</span>
      </div>
      <div className="h-8 bg-stone-50 rounded">
        <div className={`h-8 ${color} rounded`} style={{ width: `${widthPct}%` }} />
      </div>
      <p className="mt-2 text-xs text-stone-500">
        Source:{" "}
        <a
          href={sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-stone-700"
        >
          {sourceLabel}
        </a>
      </p>
    </div>
  );
}

// --- Section 3 — History timeline ---

function HistoryTimeline({
  series,
  maxPeople,
}: {
  series: { year: number; people: number; note: string }[];
  maxPeople: number;
}) {
  const W = 720;
  const H = 280;
  const PAD = { top: 30, right: 20, bottom: 40, left: 40 };
  const innerW = W - PAD.left - PAD.right;
  const innerH = H - PAD.top - PAD.bottom;

  const x = (year: number) => {
    const minY = series[0].year;
    const maxY = series[series.length - 1].year;
    return PAD.left + ((year - minY) / (maxY - minY)) * innerW;
  };
  const y = (people: number) =>
    PAD.top + innerH - (people / maxPeople) * innerH;

  const path = series
    .map((p, i) => `${i === 0 ? "M" : "L"} ${x(p.year)} ${y(p.people)}`)
    .join(" ");

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6 lg:p-8 overflow-x-auto">
      <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-auto">
        {/* gridlines + y labels */}
        {[0, 0.5, 1].map((t) => {
          const yy = PAD.top + (1 - t) * innerH;
          const val = Math.round(t * maxPeople);
          return (
            <g key={t}>
              <line
                x1={PAD.left}
                x2={W - PAD.right}
                y1={yy}
                y2={yy}
                stroke="#e7e5e4"
              />
              <text
                x={PAD.left - 6}
                y={yy + 4}
                fontSize="10"
                fill="#78716c"
                textAnchor="end"
              >
                {fmtInt(val)}
              </text>
            </g>
          );
        })}
        {/* line */}
        <path d={path} fill="none" stroke="#065f46" strokeWidth={2} />
        {/* points + year labels */}
        {series.map((p) => {
          const cx = x(p.year);
          const cy = y(p.people);
          const is2022 = p.year === 2022;
          const is2024 = p.year === 2024;
          const highlight = is2022 || is2024;
          return (
            <g key={p.year}>
              <circle
                cx={cx}
                cy={cy}
                r={highlight ? 5 : 3.5}
                fill={highlight ? "#065f46" : "#fff"}
                stroke="#065f46"
                strokeWidth={2}
              />
              <text
                x={cx}
                y={H - PAD.bottom + 18}
                fontSize="11"
                fill="#57534e"
                textAnchor="middle"
              >
                {p.year}
              </text>
              {highlight && (
                <text
                  x={cx}
                  y={cy - 12}
                  fontSize="11"
                  fontWeight="600"
                  fill="#0c0a09"
                  textAnchor="middle"
                >
                  {fmtInt(p.people)}
                </text>
              )}
            </g>
          );
        })}
      </svg>
    </div>
  );
}

// --- Section 4 — CSRD timeline ---

function CsrdTimeline({
  milestones,
}: {
  milestones: { year: number; label: string; companies_nl: number; is_current: boolean }[];
}) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6 lg:p-8">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-0">
        {milestones.map((m, i) => (
          <div
            key={m.year}
            className={
              "relative px-4 py-5 " +
              (i === 0 ? "" : "md:border-l border-stone-200") +
              (i !== 0 ? " border-t md:border-t-0 border-stone-200" : "")
            }
          >
            {m.is_current && (
              <span className="inline-flex items-center rounded-md bg-emerald-50 border border-emerald-200 px-2 py-0.5 text-[11px] font-medium text-emerald-800 uppercase tracking-wide mb-2">
                We are here
              </span>
            )}
            <p className={`text-2xl font-semibold tabular-nums ${m.is_current ? "text-emerald-900" : "text-stone-900"}`}>
              {m.year}
            </p>
            <p className="mt-1.5 text-sm text-stone-700 leading-snug">{m.label}</p>
            <p className="mt-3 text-xs text-stone-500">
              <span className="tabular-nums font-medium text-stone-700">
                {fmtInt(m.companies_nl)}
              </span>{" "}
              NL companies
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

// --- Section 5 — Impact flow ---

function ImpactFlow({
  gap,
}: {
  gap: {
    rescued_kg: number;
    rescued_tco2e: number;
    nl_food_waste_tco2e: number;
    currently_disclosed_tco2e: number;
  };
}) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6 lg:p-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 items-stretch">
        <FlowBox
          big={`${fmtInt(gap.rescued_kg / 1_000_000)}M`}
          unit="kg"
          label="Food rescued by Dutch foodbanks per year"
          tone="muted"
        />
        <FlowArrow />
        <FlowBox
          big={fmtInt(gap.rescued_tco2e)}
          unit="tCO₂e"
          label="Greenhouse-gas emissions avoided per year"
          tone="muted"
        />
      </div>
      <div className="my-3 flex justify-center text-stone-300">↓</div>
      <FlowBox
        big={fmtInt(gap.currently_disclosed_tco2e)}
        unit="tCO₂e"
        label="Currently disclosed on a corporate CSR report"
        tone="alert"
        wide
      />
    </div>
  );
}

function FlowBox({
  big,
  unit,
  label,
  tone,
  wide,
}: {
  big: string;
  unit: string;
  label: string;
  tone: "muted" | "alert";
  wide?: boolean;
}) {
  const isAlert = tone === "alert";
  return (
    <div
      className={
        "rounded-lg border p-5 " +
        (wide ? "col-span-3 " : "") +
        (isAlert
          ? "bg-red-50 border-red-200"
          : "bg-stone-50 border-stone-200")
      }
    >
      <p className={`text-3xl font-semibold tabular-nums ${isAlert ? "text-red-900" : "text-stone-900"}`}>
        {big}
        <span className={`text-base font-normal ml-1 ${isAlert ? "text-red-700" : "text-stone-500"}`}>
          {unit}
        </span>
      </p>
      <p className={`mt-1 text-sm ${isAlert ? "text-red-800" : "text-stone-600"}`}>{label}</p>
    </div>
  );
}

function FlowArrow() {
  return (
    <div className="flex items-center justify-center text-stone-300 text-2xl">
      <span className="hidden md:inline">→</span>
      <span className="md:hidden">↓</span>
    </div>
  );
}
