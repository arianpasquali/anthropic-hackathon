import "server-only"
import { promises as fs } from "fs"
import path from "path"
import Link from "next/link"
import { CoverageMap } from "@/components/marketing/CoverageMap"

export const metadata = {
  title: "Coverage · Kavel",
  description:
    "Where Dutch poverty is concentrated, where Kavel's foodbanks reach, and where the gap is widest. Gemeente-level CBS poverty data overlaid with the demo cohort.",
}

interface Gemeente {
  code: string
  name: string
  path: string
  persons_in_poverty: number | null
  households_in_poverty: number | null
  persons_in_poverty_pct: number | null
  households_in_poverty_pct: number | null
}

interface Bank {
  id: string
  name: string
  region?: string
  lat: number
  lng: number
  x: number
  y: number
  annual_tco2e?: number
  annual_kg_rescued?: number
  households_weekly?: number | null
  is_rdc?: boolean
  rdc_satellite_count?: number | null
  in_demo_cohort: boolean
}

interface CoverageData {
  svg: { width: number; height: number }
  scale: {
    pct_min: number
    pct_max: number
    source_label: string
    source_url: string
  }
  gemeenten: Gemeente[]
  banks: Bank[]
  demo_regions: string[]
}

async function loadCoverage(): Promise<CoverageData> {
  const p = path.join(process.cwd(), "public", "coverage-data.json")
  const raw = await fs.readFile(p, "utf-8")
  return JSON.parse(raw) as CoverageData
}

const LEGEND_BUCKETS = [
  { label: "< 2%", color: "oklch(96.5% 0.008 155)" },
  { label: "2–3%", color: "oklch(91% 0.013 155)" },
  { label: "3–4%", color: "oklch(88% 0.07 75)" },
  { label: "4–5.5%", color: "oklch(72% 0.15 75)" },
  { label: "≥ 5.5%", color: "oklch(48% 0.13 55)" },
]

function fmtInt(n: number): string {
  return new Intl.NumberFormat("en-NL").format(Math.round(n))
}

export default async function CoveragePage() {
  const data = await loadCoverage()

  const sortedByAbs = [...data.gemeenten]
    .filter((g) => g.persons_in_poverty !== null)
    .sort(
      (a, b) => (b.persons_in_poverty ?? 0) - (a.persons_in_poverty ?? 0),
    )
  const topAbs = sortedByAbs.slice(0, 5)

  const sortedByPct = [...data.gemeenten]
    .filter((g) => g.persons_in_poverty_pct !== null)
    .sort(
      (a, b) =>
        (b.persons_in_poverty_pct ?? 0) - (a.persons_in_poverty_pct ?? 0),
    )
  const topPct = sortedByPct.slice(0, 5)

  const totalPoverty = data.gemeenten.reduce(
    (sum, g) => sum + (g.persons_in_poverty ?? 0),
    0,
  )

  const demoBanks = data.banks.filter((b) => b.in_demo_cohort)
  const totalDemoTco2e = demoBanks.reduce(
    (s, b) => s + (b.annual_tco2e ?? 0),
    0,
  )

  return (
    <div>
      <section className="border-b border-line">
        <div className="mx-auto max-w-[1280px] px-6 pt-16 md:pt-20 pb-14 md:pb-16">
          <p className="eyebrow">Coverage map</p>
          <h1 className="display text-5xl md:text-6xl mt-4 tracking-[-0.025em] leading-[1.05] max-w-[24ch]">
            Where the need is.{" "}
            <span className="display-italic text-emerald-deep">
              Where the gap is.
            </span>
          </h1>
          <p className="mt-6 text-text-muted text-[15.5px] leading-relaxed max-w-[68ch]">
            NL gemeenten shaded by share of population living on a low income
            for at least one year (CBS, 2023). Demo cohort foodbanks overlaid
            as emerald circles, sized by annual climate-contribution capacity.
          </p>
        </div>
      </section>

      <section className="border-b border-line bg-surface-2">
        <div className="mx-auto max-w-[1280px] px-6 py-12 md:py-16">
          <div className="grid lg:grid-cols-[1fr_300px] gap-x-10 gap-y-8 items-start">
            <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-4">
              <CoverageMap
                width={data.svg.width}
                height={data.svg.height}
                gemeenten={data.gemeenten}
                banks={data.banks}
              />
            </div>

            <aside className="flex flex-col gap-6">
              <Legend />
              <Stats
                demoBanks={demoBanks}
                totalDemoTco2e={totalDemoTco2e}
                totalPoverty={totalPoverty}
              />
              <SourceBlock scale={data.scale} />
            </aside>
          </div>
        </div>
      </section>

      <section className="border-b border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-16">
          <p className="eyebrow">Reading the map</p>
          <h2 className="display text-3xl md:text-4xl mt-3 tracking-[-0.02em] max-w-[28ch]">
            Three angles on the same gap.
          </h2>
          <div className="mt-12 grid grid-cols-1 lg:grid-cols-3 gap-x-8 gap-y-10">
            <Insight title="Highest poverty by share">
              <ol className="flex flex-col gap-2 text-[13.5px]">
                {topPct.map((g, i) => (
                  <li
                    key={g.code}
                    className="flex justify-between gap-3 border-b border-line/50 pb-1.5"
                  >
                    <span className="text-text">
                      <span className="text-text-faint tabular mr-2">
                        {i + 1}
                      </span>
                      {g.name}
                    </span>
                    <span className="tabular font-medium text-text">
                      {g.persons_in_poverty_pct?.toFixed(1)}%
                    </span>
                  </li>
                ))}
              </ol>
            </Insight>

            <Insight title="Highest poverty by count">
              <ol className="flex flex-col gap-2 text-[13.5px]">
                {topAbs.map((g, i) => (
                  <li
                    key={g.code}
                    className="flex justify-between gap-3 border-b border-line/50 pb-1.5"
                  >
                    <span className="text-text">
                      <span className="text-text-faint tabular mr-2">
                        {i + 1}
                      </span>
                      {g.name}
                    </span>
                    <span className="tabular font-medium text-text">
                      {fmtInt(g.persons_in_poverty ?? 0)}
                    </span>
                  </li>
                ))}
              </ol>
            </Insight>

            <Insight title="Demo cohort coverage">
              <ul className="flex flex-col gap-2 text-[13.5px]">
                {demoBanks.map((b) => (
                  <li
                    key={b.id}
                    className="flex justify-between gap-3 border-b border-line/50 pb-1.5"
                  >
                    <span className="text-text">
                      {b.name}
                      {b.is_rdc && b.rdc_satellite_count ? (
                        <span className="text-[11.5px] text-text-faint ml-1.5">
                          +{b.rdc_satellite_count} satellites
                        </span>
                      ) : null}
                    </span>
                    <span className="tabular font-medium text-text whitespace-nowrap">
                      {b.annual_tco2e ? fmtInt(b.annual_tco2e) : "—"} tCO₂e
                    </span>
                  </li>
                ))}
              </ul>
              <p className="mt-4 text-[12px] text-text-faint leading-relaxed">
                The 6 demo foodbanks cluster in the Randstad and major regional
                centres, where poverty counts are highest. The other 175 NL
                foodbanks (small dots) extend the network into smaller
                gemeenten.
              </p>
            </Insight>
          </div>
        </div>
      </section>

      <section className="border-b border-line bg-surface-2">
        <div className="mx-auto max-w-[1280px] px-6 py-16 grid md:grid-cols-[1fr_1.6fr] gap-x-12 gap-y-8 items-start">
          <div>
            <p className="eyebrow">What the map argues</p>
            <h2 className="display text-3xl md:text-4xl mt-3 tracking-[-0.02em] max-w-[20ch] leading-[1.1]">
              Coverage today.{" "}
              <span className="display-italic text-emerald-deep">
                Expansion next.
              </span>
            </h2>
          </div>
          <div className="flex flex-col gap-5 text-text-muted text-[14.5px] leading-relaxed max-w-[64ch]">
            <p>
              The 6 demo foodbanks already cover the{" "}
              <strong className="text-text">
                top 3 NL gemeenten on both poverty measures
              </strong>{" "}
              — Amsterdam, Rotterdam, and &apos;s-Gravenhage lead by absolute
              count <em className="display-italic">and</em> by share. Groningen
              and Eindhoven extend coverage into the north and Brabant. Breda
              anchors the south-west.
            </p>
            <p>
              The clearest expansion target visible in the map is{" "}
              <strong className="text-text">Heerlen</strong> in Limburg (4.6%
              poverty rate, 5th-highest in NL by share), where{" "}
              <a
                href="https://www.voedselbanklimburg-zuid.nl/"
                target="_blank"
                rel="noreferrer"
                className="text-emerald hover:underline"
              >
                Voedselbank Limburg Zuid
              </a>{" "}
              already operates a distribution point but is not yet in the demo
              cohort. Onboarding it brings the platform&apos;s reach to the
              top 4 high-share gemeenten plus the top 5 by absolute count.
            </p>
            <p>
              The choropleth uses CBS&apos;s &quot;at least one year on low
              income&quot; measure rather than a single-year snapshot — this
              surfaces structural poverty rather than transient income shocks,
              and matches the audience VBN&apos;s Onder de Radar project is
              trying to reach.
            </p>
            <p className="text-[13px] text-text-faint italic">
              For the macro story behind these gemeente figures — poverty gap,
              decade of pressure, CSRD wave —{" "}
              <Link href="/why" className="text-emerald hover:underline">
                see /why
              </Link>
              .
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

function Legend() {
  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-5">
      <p className="eyebrow text-text-faint mb-3">
        Persons in poverty (share)
      </p>
      <div className="flex flex-col gap-1.5">
        {LEGEND_BUCKETS.map((b) => (
          <div
            key={b.label}
            className="flex items-center gap-2.5 text-[12.5px]"
          >
            <span
              className="inline-block w-5 h-3 border border-line"
              style={{ backgroundColor: b.color }}
            />
            <span className="text-text tabular">{b.label}</span>
          </div>
        ))}
      </div>
      <div className="mt-4 pt-3 border-t border-line/60 flex flex-col gap-2 text-[12.5px]">
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center justify-center w-5 h-5">
            <span
              className="block w-3.5 h-3.5 rounded-full border-2"
              style={{
                backgroundColor: "var(--emerald-deep)",
                borderColor: "var(--surface)",
              }}
            />
          </span>
          <span className="text-text">
            Demo bank · sized by annual tCO₂e
          </span>
        </div>
        <div className="flex items-center gap-2.5">
          <span className="inline-flex items-center justify-center w-5 h-5">
            <span
              className="block w-2 h-2 rounded-full"
              style={{
                backgroundColor: "var(--surface)",
                border: "1px solid var(--text-muted)",
              }}
            />
          </span>
          <span className="text-text">Other NL foodbank</span>
        </div>
      </div>
    </div>
  )
}

function Stats({
  demoBanks,
  totalDemoTco2e,
  totalPoverty,
}: {
  demoBanks: Bank[]
  totalDemoTco2e: number
  totalPoverty: number
}) {
  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-5 flex flex-col gap-3 text-[13px]">
      <Row
        label="Demo banks"
        value={`${demoBanks.length} of 181`}
      />
      <Row
        label="Annual climate contribution"
        value={`${fmtInt(totalDemoTco2e)} tCO₂e`}
      />
      <Row
        label="NL persons in poverty (≥ 1 yr)"
        value={fmtInt(totalPoverty)}
      />
    </div>
  )
}

function SourceBlock({ scale }: { scale: CoverageData["scale"] }) {
  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-5 flex flex-col gap-1.5 text-[11.5px] text-text-faint leading-relaxed">
      <p>
        <span className="font-semibold text-text-muted">Poverty data:</span>{" "}
        <a
          href={scale.source_url}
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-2 hover:text-text-muted"
        >
          {scale.source_label}
        </a>
      </p>
      <p>
        <span className="font-semibold text-text-muted">Boundaries:</span>{" "}
        <a
          href="https://github.com/cartomap/nl"
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-2 hover:text-text-muted"
        >
          cartomap/nl
        </a>{" "}
        gemeente_2024 (CBS gegeneraliseerd, public domain).
      </p>
      <p>
        <span className="font-semibold text-text-muted">
          Bank coordinates:
        </span>{" "}
        hand-curated for the 6 demo foodbanks (HQ / regional DC). Other 175 NL
        banks not yet plotted.
      </p>
    </div>
  )
}

function Insight({
  title,
  children,
}: {
  title: string
  children: React.ReactNode
}) {
  return (
    <div className="border-t border-line-strong pt-5">
      <h3 className="eyebrow mb-4">{title}</h3>
      {children}
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-text-muted">{label}</dt>
      <dd className="tabular font-medium text-text whitespace-nowrap">
        {value}
      </dd>
    </div>
  )
}
