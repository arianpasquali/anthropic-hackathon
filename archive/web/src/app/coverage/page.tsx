import { promises as fs } from "fs";
import path from "path";
import Link from "next/link";
import CoverageMap from "./CoverageMap";

export const metadata = {
  title: "Coverage — Climate-Action Packages",
  description:
    "Where Dutch poverty is concentrated, where the platform's foodbanks are, and where the gap is widest.",
};

interface Gemeente {
  code: string;
  name: string;
  path: string;
  persons_in_poverty: number | null;
  households_in_poverty: number | null;
  persons_in_poverty_pct: number | null;
  households_in_poverty_pct: number | null;
}

interface Bank {
  id: string;
  name: string;
  region?: string;
  lat: number;
  lng: number;
  x: number;
  y: number;
  annual_tco2e?: number;
  annual_kg_rescued?: number;
  households_weekly?: number | null;
  is_rdc?: boolean;
  rdc_satellite_count?: number | null;
  in_demo_cohort: boolean;
}

interface CoverageData {
  svg: { width: number; height: number };
  scale: {
    pct_min: number;
    pct_max: number;
    source_label: string;
    source_url: string;
  };
  gemeenten: Gemeente[];
  banks: Bank[];
  demo_regions: string[];
}

async function loadCoverage(): Promise<CoverageData> {
  const p = path.join(process.cwd(), "public", "coverage-data.json");
  const raw = await fs.readFile(p, "utf-8");
  return JSON.parse(raw) as CoverageData;
}

// Colour bucket logic lives in CoverageMap.tsx (client). Here we just keep
// the legend swatch list to stay in sync visually.
const LEGEND_BUCKETS = [
  { label: "< 2%", color: "#fafaf9" },
  { label: "2–3%", color: "#e7e5e4" },
  { label: "3–4%", color: "#fde68a" },
  { label: "4–5.5%", color: "#f59e0b" },
  { label: "≥ 5.5%", color: "#b45309" },
];

function fmtInt(n: number): string {
  return new Intl.NumberFormat("en-NL").format(Math.round(n));
}

export default async function CoveragePage() {
  const data = await loadCoverage();

  // Top 5 gemeenten by absolute persons in poverty
  const sortedByAbs = [...data.gemeenten]
    .filter((g) => g.persons_in_poverty !== null)
    .sort(
      (a, b) => (b.persons_in_poverty ?? 0) - (a.persons_in_poverty ?? 0)
    );
  const topAbs = sortedByAbs.slice(0, 5);

  // Top 5 by relative %
  const sortedByPct = [...data.gemeenten]
    .filter((g) => g.persons_in_poverty_pct !== null)
    .sort(
      (a, b) =>
        (b.persons_in_poverty_pct ?? 0) - (a.persons_in_poverty_pct ?? 0)
    );
  const topPct = sortedByPct.slice(0, 5);

  // Aggregate: total persons in poverty across NL with a CBS row
  const totalPoverty = data.gemeenten.reduce(
    (sum, g) => sum + (g.persons_in_poverty ?? 0),
    0
  );

  // Demo cohort banks
  const demoBanks = data.banks.filter((b) => b.in_demo_cohort);

  return (
    <div className="bg-stone-50">
      <Hero />

      <section className="mx-auto max-w-6xl px-6 py-10">
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_280px] gap-6">
          <div className="rounded-xl border border-stone-200 bg-white p-4">
            <CoverageMap
              width={data.svg.width}
              height={data.svg.height}
              gemeenten={data.gemeenten}
              banks={data.banks}
            />
          </div>

          <aside className="space-y-6">
            <Legend />
            <Stats demoBanks={demoBanks} totalPoverty={totalPoverty} />
            <SourceBlock scale={data.scale} />
          </aside>
        </div>

        <div className="mt-12 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Insight title="Highest poverty by share">
            <ol className="space-y-2 text-sm">
              {topPct.map((g, i) => (
                <li key={g.code} className="flex justify-between gap-3">
                  <span className="text-stone-700">
                    <span className="text-stone-400 tabular-nums mr-2">{i + 1}</span>
                    {g.name}
                  </span>
                  <span className="font-medium tabular-nums text-stone-900">
                    {g.persons_in_poverty_pct?.toFixed(1)}%
                  </span>
                </li>
              ))}
            </ol>
          </Insight>

          <Insight title="Highest poverty by count">
            <ol className="space-y-2 text-sm">
              {topAbs.map((g, i) => (
                <li key={g.code} className="flex justify-between gap-3">
                  <span className="text-stone-700">
                    <span className="text-stone-400 tabular-nums mr-2">{i + 1}</span>
                    {g.name}
                  </span>
                  <span className="font-medium tabular-nums text-stone-900">
                    {fmtInt(g.persons_in_poverty ?? 0)}
                  </span>
                </li>
              ))}
            </ol>
          </Insight>

          <Insight title="Demo cohort coverage">
            <ul className="space-y-2 text-sm">
              {demoBanks.map((b) => (
                <li key={b.id} className="flex justify-between gap-3">
                  <span className="text-stone-700">
                    <Link
                      href={`/banks/${b.id}`}
                      className="hover:text-stone-900 hover:underline"
                    >
                      {b.name}
                    </Link>
                    {b.is_rdc && b.rdc_satellite_count && (
                      <span className="text-xs text-stone-500 ml-1">
                        +{b.rdc_satellite_count} satellites
                      </span>
                    )}
                  </span>
                  <span className="font-medium tabular-nums text-stone-900 whitespace-nowrap">
                    {b.annual_tco2e ? fmtInt(b.annual_tco2e) : "—"} tCO₂e
                  </span>
                </li>
              ))}
            </ul>
            <p className="mt-3 text-xs text-stone-500">
              The 6 demo banks cluster in the Randstad and major regional centres,
              where poverty counts are highest. The other 174 NL foodbanks (small
              dots) extend the network into smaller gemeenten.
            </p>
          </Insight>
        </div>

        <div className="mt-12 max-w-3xl space-y-4 text-stone-700 leading-relaxed">
          <p>
            The 6 demo banks already cover the <strong>top 3 NL gemeenten on both
            poverty measures</strong> — Amsterdam, Rotterdam, and &apos;s-Gravenhage
            lead by absolute count <em>and</em> by share. Groningen and Eindhoven
            extend coverage into the north and Brabant. Breda anchors the south-west.
          </p>
          <p>
            The clearest expansion target visible in the map is <strong>Heerlen</strong>{" "}
            in Limburg (4.6% poverty rate, 5th-highest in NL by share), where{" "}
            <a
              href="https://www.voedselbanklimburg-zuid.nl/"
              target="_blank"
              rel="noreferrer"
              className="underline hover:text-stone-900"
            >
              Voedselbank Limburg Zuid
            </a>{" "}
            already operates a distribution point but is not yet in the demo
            cohort. Onboarding it brings the platform&apos;s reach to the top 4
            high-share gemeenten plus the top 5 by absolute count.
          </p>
          <p>
            The choropleth uses CBS&apos;s &quot;at least one year on low income&quot;
            measure rather than a single-year snapshot — this surfaces structural
            poverty rather than transient income shocks, and matches the
            audience VBN&apos;s Onder de Radar project is trying to reach.
          </p>
        </div>
      </section>
    </div>
  );
}

// --- Components ---

function Hero() {
  return (
    <section className="border-b border-stone-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-12 lg:py-16">
        <p className="text-xs uppercase tracking-widest text-emerald-800 font-semibold mb-3">
          Coverage map
        </p>
        <h1 className="text-3xl lg:text-4xl font-semibold tracking-tight text-stone-900 max-w-3xl leading-tight">
          Where the need is, where the platform reaches, and where the gap is.
        </h1>
        <p className="mt-4 max-w-2xl text-stone-600 leading-relaxed">
          NL gemeenten shaded by share of population living on a low income for
          at least one year. Demo cohort foodbanks overlaid as emerald circles,
          sized by annual avoided emissions.
        </p>
      </div>
    </section>
  );
}


function Legend() {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-4">
      <p className="text-xs font-semibold uppercase tracking-wider text-stone-500 mb-3">
        Persons in poverty (share)
      </p>
      <div className="space-y-1.5">
        {LEGEND_BUCKETS.map((b) => (
          <div key={b.label} className="flex items-center gap-2 text-sm">
            <span
              className="inline-block w-5 h-3 rounded-sm border border-stone-200"
              style={{ backgroundColor: b.color }}
            />
            <span className="text-stone-700 tabular-nums">{b.label}</span>
          </div>
        ))}
      </div>
      <div className="mt-4 pt-3 border-t border-stone-100 space-y-2 text-sm">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-5 h-5">
            <span className="block w-3.5 h-3.5 rounded-full bg-emerald-700 border-2 border-white" />
          </span>
          <span className="text-stone-700">Demo bank · sized by annual tCO₂e</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center justify-center w-5 h-5">
            <span className="block w-2 h-2 rounded-full bg-stone-50 border border-stone-700" />
          </span>
          <span className="text-stone-700">Other NL foodbank</span>
        </div>
      </div>
    </div>
  );
}

function Stats({
  demoBanks,
  totalPoverty,
}: {
  demoBanks: Bank[];
  totalPoverty: number;
}) {
  const totalTco2e = demoBanks.reduce((s, b) => s + (b.annual_tco2e ?? 0), 0);
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-4 space-y-3 text-sm">
      <div className="flex justify-between gap-3">
        <span className="text-stone-600">Demo banks</span>
        <span className="font-medium tabular-nums text-stone-900">
          {demoBanks.length} of 180
        </span>
      </div>
      <div className="flex justify-between gap-3">
        <span className="text-stone-600">Combined annual avoided emissions</span>
        <span className="font-medium tabular-nums text-stone-900">
          {fmtInt(totalTco2e)} tCO₂e
        </span>
      </div>
      <div className="flex justify-between gap-3">
        <span className="text-stone-600">NL persons in poverty (≥ 1 yr)</span>
        <span className="font-medium tabular-nums text-stone-900">
          {fmtInt(totalPoverty)}
        </span>
      </div>
    </div>
  );
}

function SourceBlock({ scale }: { scale: CoverageData["scale"] }) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-4 text-xs text-stone-500 space-y-1.5 leading-relaxed">
      <p className="text-stone-600">
        <span className="font-semibold text-stone-700">Poverty data:</span>{" "}
        <a
          href={scale.source_url}
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-stone-700"
        >
          {scale.source_label}
        </a>
      </p>
      <p>
        <span className="font-semibold text-stone-700">Boundaries:</span>{" "}
        <a
          href="https://github.com/cartomap/nl"
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-stone-700"
        >
          cartomap/nl
        </a>
        {" "}gemeente_2024 (CBS gegeneraliseerd, public domain).
      </p>
      <p>
        <span className="font-semibold text-stone-700">Bank coordinates:</span>{" "}
        hand-curated for the 6 demo banks (HQ / regional DC). Other 174 NL
        banks not yet plotted.
      </p>
    </div>
  );
}

function Insight({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-5">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-500 mb-3">
        {title}
      </h2>
      {children}
    </div>
  );
}
