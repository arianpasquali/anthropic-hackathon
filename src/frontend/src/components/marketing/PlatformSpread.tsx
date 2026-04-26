/**
 * Two-document spread: foodbank operational truth on the left, corporate
 * ESRS disclosure draft on the right, attribution-ID connector between.
 * Reuses the Heineken-mock document idiom — same numbers tie both sides.
 *
 * Pitches the "two-sided platform" story without using the consultant phrase.
 * Pre-empts the double-counting objection (visible attribution ID) and the
 * greenwashing objection (explicit "not counted against Scope 1/2/3" line).
 */

type Row = [label: string, value: string]

const FOODBANK_ROWS: Row[] = [
  ["Food rescued", "1,240 t / yr"],
  ["Households served", "3,200 / wk"],
  ["FRAME categories", "produce · bakery · dairy · …"],
  ["FRAME CO₂e baseline", "1,451 tCO₂e / yr"],
  ["Counterfactual (NL)", "0.93 — incineration w/ energy"],
  ["Provenance", "extracted · vbr-2024.pdf §3.1"],
]

const CORPORATE_ROWS: Row[] = [
  ["Climate contribution", "600 tCO₂e / quarter"],
  ["Allocation share", "31.4%"],
  ["Foodbanks funded", "8 of 10 ingested"],
  ["Disclosure track", "ESRS E5 + S3"],
  ["Not counted against", "Scope 1/2/3 footprint"],
  ["Attribution ID", "01HXR9K… retired 2026-04-15"],
]

export function PlatformSpread() {
  return (
    <section className="border-y border-line bg-surface-2">
      <div className="mx-auto max-w-[1280px] px-6 py-20">
        <p className="eyebrow">Two-sided ledger</p>
        <h2 className="display text-4xl md:text-5xl mt-3 tracking-[-0.025em] max-w-[28ch]">
          Operational truth on one side.{" "}
          <span className="display-italic text-emerald-deep">
            Auditable disclosure on the other.
          </span>
        </h2>
        <p className="mt-5 text-text-muted text-[15px] max-w-[66ch] leading-relaxed">
          Foodbanks publish operational data — kg, categories, households —
          which the FRAME methodology turns into a verified CO₂e baseline.
          Corporates funding a Klimaatkracht package receive a portion of that
          impact, attributed once and disclosed under ESRS&nbsp;E5 + S3 — never
          recounted, never offset against own footprint.
        </p>

        <div className="mt-14 grid lg:grid-cols-[1fr_auto_1fr] gap-x-6 gap-y-10 items-stretch">
          <DocumentPanel
            kicker="Foodbank · annual report"
            title="Voedselbank Rotterdam"
            subtitle="2024 annual report — extracted by Claude"
            rows={FOODBANK_ROWS}
            footer="Page 14 of 22 · FRAME (soon Gold-Certified)"
            corner="A"
          />

          <Connector />

          <DocumentPanel
            kicker="Corporate · ESRS disclosure draft"
            title="Heineken N.V."
            subtitle="Q1 2026 — composed by Klimaatkracht"
            rows={CORPORATE_ROWS}
            footer="ESRS E5-5 · S3 · contribution claim, not offset"
            corner="B"
            tone="emerald"
          />
        </div>

        <p className="mt-10 text-[12.5px] text-text-faint italic max-w-[68ch] leading-relaxed">
          Klimaatkracht sits between: FRAME compute · NL counterfactual ·
          attribution registry · ESRS draft generation. Same number, two sides
          of one ledger.
        </p>
      </div>
    </section>
  )
}

function DocumentPanel({
  kicker,
  title,
  subtitle,
  rows,
  footer,
  corner,
  tone = "default",
}: {
  kicker: string
  title: string
  subtitle: string
  rows: Row[]
  footer: string
  corner: string
  tone?: "default" | "emerald"
}) {
  const accent =
    tone === "emerald"
      ? "border-emerald/40 bg-surface"
      : "border-line bg-surface"
  return (
    <article
      className={`kk-rise-on-view relative flex flex-col border ${accent} rounded-[var(--radius-lg)] overflow-hidden`}
    >
      {/* Page corner mark */}
      <span
        aria-hidden
        className="absolute right-5 top-5 text-[10px] tracking-[0.18em] uppercase text-text-faint tabular"
      >
        {corner}
      </span>

      <header className="px-7 pt-7 pb-5 border-b border-line/70">
        <p className="eyebrow">{kicker}</p>
        <h3 className="display text-2xl md:text-[26px] mt-2 tracking-[-0.015em]">
          {title}
        </h3>
        <p className="display-italic text-[14px] text-text-muted mt-1">
          {subtitle}
        </p>
      </header>

      <dl className="px-7 py-6 flex flex-col">
        {rows.map(([label, value], i) => (
          <div
            key={label}
            className={`flex items-baseline justify-between gap-6 py-2.5 ${i > 0 ? "border-t border-line/50" : ""}`}
          >
            <dt className="text-[12.5px] text-text-muted tracking-wide">
              {label}
            </dt>
            <dd className="text-[13.5px] text-text tabular text-right max-w-[60%]">
              {value}
            </dd>
          </div>
        ))}
      </dl>

      <footer className="mt-auto px-7 py-4 border-t border-line/60 bg-surface-2/60 flex items-center justify-between text-[11px] text-text-faint tabular">
        <span>{footer}</span>
        <span>kk-ledger / v1</span>
      </footer>
    </article>
  )
}

function Connector() {
  return (
    <div className="flex lg:flex-col items-center justify-center gap-3 py-2 lg:py-6 lg:px-2">
      {/* Top hairline (vertical on desktop, horizontal on mobile) */}
      <span
        aria-hidden
        className="block w-12 h-px lg:w-px lg:h-12 bg-line"
      />
      <div className="flex flex-col items-center gap-1.5">
        <span
          aria-hidden
          className="text-[18px] text-emerald-deep leading-none"
        >
          →
        </span>
        <span className="text-[10px] tracking-[0.12em] uppercase text-text-faint tabular leading-none">
          Attribution
        </span>
        <span className="text-[10.5px] text-text-muted tabular leading-none">
          01HXR9K…
        </span>
      </div>
      <span
        aria-hidden
        className="block w-12 h-px lg:w-px lg:h-12 bg-line"
      />
    </div>
  )
}
