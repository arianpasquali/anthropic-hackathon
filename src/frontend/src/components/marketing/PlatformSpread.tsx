"use client"

import { useEffect, useRef, useState } from "react"

/**
 * Two-document spread: foodbank operational truth on the left, corporate
 * ESRS disclosure draft on the right, attribution-ID connector between.
 *
 * On first viewport entry, rows reveal top-to-bottom on the left, the
 * connector arrow + attribution ID animate in, then the right panel
 * populates row-by-row. Reads as: extract → compute → mint → disclose.
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

// Stagger budget (ms). Drives delay computation in component + CSS reads.
const ROW_DELAY = 90
const LEFT_LEAD = 120
const CONNECTOR_AT = LEFT_LEAD + FOODBANK_ROWS.length * ROW_DELAY + 80
const RIGHT_LEAD = CONNECTOR_AT + 420

export function PlatformSpread() {
  const ref = useRef<HTMLDivElement>(null)
  const [revealed, setRevealed] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return

    if (typeof IntersectionObserver === "undefined") {
      setRevealed(true)
      return
    }
    const obs = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) {
            setRevealed(true)
            obs.disconnect()
            break
          }
        }
      },
      { threshold: 0.18 },
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  return (
    <section
      ref={ref}
      data-revealed={revealed ? "true" : "false"}
      className="kk-spread border-y border-line bg-surface-2"
    >
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
          Corporates funding a Kavel package receive a portion of that
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
            sideDelayBase={LEFT_LEAD}
          />

          <Connector />

          <DocumentPanel
            kicker="Corporate · ESRS disclosure draft"
            title="Heineken N.V."
            subtitle="Q1 2026 — composed by Kavel"
            rows={CORPORATE_ROWS}
            footer="ESRS E5-5 · S3 · contribution claim, not offset"
            corner="B"
            tone="emerald"
            sideDelayBase={RIGHT_LEAD}
          />
        </div>

        <p className="mt-10 text-[12.5px] text-text-faint italic max-w-[68ch] leading-relaxed">
          Kavel sits between: FRAME compute · NL counterfactual ·
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
  sideDelayBase,
}: {
  kicker: string
  title: string
  subtitle: string
  rows: Row[]
  footer: string
  corner: string
  tone?: "default" | "emerald"
  sideDelayBase: number
}) {
  const accent =
    tone === "emerald"
      ? "border-emerald/40 bg-surface"
      : "border-line bg-surface"
  return (
    <article
      className={`kk-rise-on-view relative flex flex-col border ${accent} rounded-[var(--radius-lg)] overflow-hidden`}
    >
      <span
        aria-hidden
        className="absolute right-5 top-5 text-[10px] tracking-[0.18em] uppercase text-text-faint tabular"
      >
        {corner}
      </span>

      <header
        className="kk-row-reveal px-7 pt-7 pb-5 border-b border-line/70"
        style={{ ["--kk-delay" as string]: `${sideDelayBase}ms` }}
      >
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
            className={`kk-row-reveal flex items-baseline justify-between gap-6 py-2.5 ${i > 0 ? "border-t border-line/50" : ""}`}
            style={{
              ["--kk-delay" as string]: `${sideDelayBase + (i + 1) * ROW_DELAY}ms`,
            }}
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

      <footer
        className="kk-row-reveal mt-auto px-7 py-4 border-t border-line/60 bg-surface-2/60 flex items-center justify-between text-[11px] text-text-faint tabular"
        style={{
          ["--kk-delay" as string]: `${sideDelayBase + (rows.length + 1) * ROW_DELAY}ms`,
        }}
      >
        <span>{footer}</span>
        <span>kk-ledger / v1</span>
      </footer>
    </article>
  )
}

function Connector() {
  return (
    <div className="flex lg:flex-col items-center justify-center gap-3 py-2 lg:py-6 lg:px-2">
      <span
        aria-hidden
        className="kk-connector-line block w-12 h-px lg:w-px lg:h-12 bg-line"
        style={{ ["--kk-delay" as string]: `${CONNECTOR_AT}ms` }}
      />
      <div className="flex flex-col items-center gap-1.5">
        <span
          aria-hidden
          className="kk-connector-arrow text-[18px] text-emerald-deep leading-none"
          style={{ ["--kk-delay" as string]: `${CONNECTOR_AT + 80}ms` }}
        >
          →
        </span>
        <span
          className="kk-connector-label text-[10px] tracking-[0.12em] uppercase text-text-faint tabular leading-none"
          style={{ ["--kk-delay" as string]: `${CONNECTOR_AT + 160}ms` }}
        >
          Attribution
        </span>
        <span
          className="kk-connector-id text-[10.5px] text-text-muted tabular leading-none"
          style={{ ["--kk-delay" as string]: `${CONNECTOR_AT + 240}ms` }}
        >
          01HXR9K…
        </span>
      </div>
      <span
        aria-hidden
        className="kk-connector-line block w-12 h-px lg:w-px lg:h-12 bg-line"
        style={{ ["--kk-delay" as string]: `${CONNECTOR_AT}ms` }}
      />
    </div>
  )
}
