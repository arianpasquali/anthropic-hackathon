"use client"

import { useCallback, useRef, useState } from "react"

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
  x: number
  y: number
  annual_tco2e?: number
  households_weekly?: number | null
  is_rdc?: boolean
  rdc_satellite_count?: number | null
  in_demo_cohort: boolean
}

interface Props {
  width: number
  height: number
  gemeenten: Gemeente[]
  banks: Bank[]
}

type Hovered =
  | { kind: "gemeente"; data: Gemeente }
  | { kind: "bank"; data: Bank }
  | null

// Five-bucket choropleth in the design-system register: warm-grey base scaling
// up to deepening warning oranges for the highest-share gemeenten. Tokens
// resolved at runtime via getComputedStyle would be heavier than this static
// scale; values handpicked to match --line, --warning, --warning-deep.
function bucketColor(pct: number | null): string {
  if (pct === null) return "oklch(94% 0.005 155)"
  if (pct < 2) return "oklch(96.5% 0.008 155)"
  if (pct < 3) return "oklch(91% 0.013 155)"
  if (pct < 4) return "oklch(88% 0.07 75)"
  if (pct < 5.5) return "oklch(72% 0.15 75)"
  return "oklch(48% 0.13 55)"
}

function bankRadius(tco2e?: number): number {
  if (!tco2e) return 5
  return Math.max(5, Math.min(14, 5 + Math.sqrt(tco2e / 100)))
}

function fmtInt(n: number): string {
  return new Intl.NumberFormat("en-NL").format(Math.round(n))
}

export function CoverageMap({ width, height, gemeenten, banks }: Props) {
  const [hovered, setHovered] = useState<Hovered>(null)
  const [pointer, setPointer] = useState<{ x: number; y: number } | null>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)

  const onMove = useCallback((e: React.MouseEvent) => {
    const rect = wrapperRef.current?.getBoundingClientRect()
    if (!rect) return
    setPointer({ x: e.clientX - rect.left, y: e.clientY - rect.top })
  }, [])

  const clear = useCallback(() => {
    setHovered(null)
    setPointer(null)
  }, [])

  const nonDemo = banks.filter((b) => !b.in_demo_cohort)
  const demo = banks.filter((b) => b.in_demo_cohort)

  return (
    <div
      ref={wrapperRef}
      className="relative"
      onMouseMove={onMove}
      onMouseLeave={clear}
    >
      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="w-full h-auto"
        role="img"
        aria-label="Map of the Netherlands shaded by poverty share, with foodbank locations overlaid."
      >
        <g>
          {gemeenten.map((g) => {
            const isHov =
              hovered?.kind === "gemeente" && hovered.data.code === g.code
            return (
              <path
                key={g.code}
                d={g.path}
                fill={bucketColor(g.persons_in_poverty_pct)}
                stroke={isHov ? "var(--text)" : "var(--surface)"}
                strokeWidth={isHov ? 1.5 : 0.4}
                onMouseEnter={() => setHovered({ kind: "gemeente", data: g })}
                style={{ cursor: "pointer" }}
              />
            )
          })}
        </g>

        <g>
          {nonDemo.map((b) => {
            const isHov = hovered?.kind === "bank" && hovered.data.id === b.id
            return (
              <circle
                key={b.id}
                cx={b.x}
                cy={b.y}
                r={isHov ? 6 : 4}
                fill={isHov ? "var(--text)" : "var(--surface)"}
                stroke={isHov ? "var(--text)" : "var(--text-muted)"}
                strokeWidth={1}
                opacity={0.95}
                onMouseEnter={() => setHovered({ kind: "bank", data: b })}
                style={{ cursor: "pointer" }}
              />
            )
          })}
        </g>

        <g>
          {demo.map((b) => {
            const isHov = hovered?.kind === "bank" && hovered.data.id === b.id
            const r = bankRadius(b.annual_tco2e)
            return (
              <g key={b.id}>
                <circle
                  cx={b.x}
                  cy={b.y}
                  r={r + 2}
                  fill="var(--surface)"
                  stroke="var(--emerald-deep)"
                  strokeWidth={1}
                />
                <circle
                  cx={b.x}
                  cy={b.y}
                  r={isHov ? r + 1 : r}
                  fill={isHov ? "var(--text)" : "var(--emerald-deep)"}
                  stroke="var(--surface)"
                  strokeWidth={1.5}
                  onMouseEnter={() => setHovered({ kind: "bank", data: b })}
                  style={{ cursor: "pointer" }}
                />
              </g>
            )
          })}
        </g>
      </svg>

      {hovered && pointer ? (
        <Tooltip pointer={pointer} hovered={hovered} />
      ) : null}
    </div>
  )
}

function Tooltip({
  pointer,
  hovered,
}: {
  pointer: { x: number; y: number }
  hovered: Hovered
}) {
  if (!hovered) return null
  const TOOLTIP_W = 240
  const left = pointer.x + 12
  const top = pointer.y + 12
  return (
    <div
      role="tooltip"
      className="absolute z-10 pointer-events-none border border-line bg-surface shadow-md p-3.5 text-[13px] rounded-[var(--radius)]"
      style={{ left, top, width: TOOLTIP_W }}
    >
      {hovered.kind === "gemeente" ? (
        <GemeenteTip g={hovered.data} />
      ) : (
        <BankTip b={hovered.data} />
      )}
    </div>
  )
}

function GemeenteTip({ g }: { g: Gemeente }) {
  return (
    <div>
      <p className="font-semibold text-text">{g.name}</p>
      <p className="text-[11.5px] text-text-faint mt-0.5">
        Gemeente · poverty 2023
      </p>
      <dl className="mt-2.5 flex flex-col gap-1 text-[11.5px]">
        <Row
          label="Persons (≥ 1 yr low income)"
          value={
            g.persons_in_poverty !== null
              ? fmtInt(g.persons_in_poverty)
              : "—"
          }
        />
        <Row
          label="Share of population"
          value={
            g.persons_in_poverty_pct !== null
              ? `${g.persons_in_poverty_pct.toFixed(1)}%`
              : "—"
          }
        />
        <Row
          label="Households"
          value={
            g.households_in_poverty !== null
              ? fmtInt(g.households_in_poverty)
              : "—"
          }
        />
      </dl>
    </div>
  )
}

function BankTip({ b }: { b: Bank }) {
  return (
    <div>
      <p className="font-semibold text-text">{b.name}</p>
      <p className="text-[11.5px] text-text-faint mt-0.5">
        {b.region ?? "Nederland"} ·{" "}
        {b.in_demo_cohort ? "Demo cohort" : "NL network"}
      </p>
      {b.in_demo_cohort ? (
        <dl className="mt-2.5 flex flex-col gap-1 text-[11.5px]">
          {b.annual_tco2e !== undefined ? (
            <Row
              label="Annual climate contribution"
              value={`${fmtInt(b.annual_tco2e)} tCO₂e`}
            />
          ) : null}
          {b.households_weekly ? (
            <Row
              label="Households / week"
              value={fmtInt(b.households_weekly)}
            />
          ) : null}
          {b.is_rdc && b.rdc_satellite_count ? (
            <Row
              label="RDC satellites"
              value={`${b.rdc_satellite_count} food banks`}
            />
          ) : null}
        </dl>
      ) : (
        <p className="mt-2.5 text-[11.5px] text-text-muted leading-snug">
          Member of Voedselbanken Nederland; not yet in the platform&apos;s
          demo cohort.
        </p>
      )}
    </div>
  )
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3">
      <dt className="text-text-faint">{label}</dt>
      <dd className="tabular font-medium text-text">{value}</dd>
    </div>
  )
}
