import type { Bank } from "@/lib/types"
import { formatTCO2e } from "@/lib/format"

// SVG canvas
const VW = 500
const VH = 440
const LON_MIN = 3.2, LON_MAX = 7.3
const LAT_MAX = 53.6, LAT_MIN = 50.7

function project(lat: number, lng: number): [number, number] {
  const x = ((lng - LON_MIN) / (LON_MAX - LON_MIN)) * VW
  const y = ((LAT_MAX - lat) / (LAT_MAX - LAT_MIN)) * VH
  return [parseFloat(x.toFixed(1)), parseFloat(y.toFixed(1))]
}

// Approximate NL mainland outline (18-point polygon, SVG space)
const NL_PATH =
  "M190,80 L215,118 L200,150 L175,190 L152,218 L120,252 L106,278 L88,306 L64,320 L38,334 L55,418 L368,418 L443,268 L488,184 L462,48 L438,16 L328,38 L218,46 Z"

const PULSE_DURS = ["2s", "2.4s", "2.8s", "3.2s", "3.6s", "4s"]

interface NLMapDarkProps {
  banks: Bank[]
  height?: number
}

export function NLMapDark({ banks, height = 440 }: NLMapDarkProps) {
  const withCoords = banks.filter((b) => b.lat != null && b.lng != null)
  const totalCo2 = banks.reduce((s, b) => s + (b.annual_tco2e ?? 0), 0)

  const sorted = [...withCoords].sort((a, b) => (b.annual_tco2e ?? 0) - (a.annual_tco2e ?? 0))
  const topSlugs = new Set(sorted.slice(0, 6).map((b) => b.slug))
  const maxCo2 = sorted[0]?.annual_tco2e ?? 1

  function dotRadius(tco2: number | null): number {
    if (!tco2) return 4
    return Math.max(3, Math.min(20, Math.sqrt(tco2 / maxCo2) * 20))
  }

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height,
        background: "#0c1929",
        borderRadius: 14,
        overflow: "hidden",
        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
      }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${VW} ${VH}`}
        preserveAspectRatio="xMidYMid meet"
        aria-hidden="true"
      >
        <defs>
          <pattern id="nlgrid" width="32" height="32" patternUnits="userSpaceOnUse">
            <path d="M 32 0 L 0 0 0 32" fill="none" stroke="#1a2d45" strokeWidth="0.4" />
          </pattern>
          <filter id="nlglow" x="-60%" y="-60%" width="220%" height="220%">
            <feGaussianBlur stdDeviation="3.5" result="blur" />
            <feMerge>
              <feMergeNode in="blur" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <radialGradient id="heatgrad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="#10b981" stopOpacity="0.18" />
            <stop offset="100%" stopColor="#10b981" stopOpacity="0" />
          </radialGradient>
        </defs>

        {/* Background grid */}
        <rect width={VW} height={VH} fill="url(#nlgrid)" />

        {/* NL mainland */}
        <path d={NL_PATH} fill="#152030" stroke="#2a4060" strokeWidth="1.5" opacity="0.97" />

        {/* IJsselmeer cutout */}
        <ellipse cx="248" cy="138" rx="32" ry="26" fill="#0c1929" opacity="0.85" />

        {/* Soft heat aura around top bank */}
        {sorted[0]?.lat != null && sorted[0]?.lng != null && (() => {
          const [x, y] = project(sorted[0].lat!, sorted[0].lng!)
          return <ellipse cx={x} cy={y} rx="60" ry="50" fill="url(#heatgrad)" />
        })()}

        {/* Bank dots */}
        {withCoords.map((b) => {
          const [x, y] = project(b.lat!, b.lng!)
          const r = dotRadius(b.annual_tco2e)
          const isTop = topSlugs.has(b.slug)
          const pulseIdx = sorted.findIndex((s) => s.slug === b.slug)
          const dur = PULSE_DURS[pulseIdx] ?? "3s"
          const isDominant = sorted[0]?.slug === b.slug

          return (
            <g key={b.id}>
              {isTop && (
                <circle cx={x} cy={y} r={r} fill="none" stroke="#10b981" strokeWidth="1.5" opacity="0">
                  <animate
                    attributeName="r"
                    values={`${r};${r + 20}`}
                    dur={dur}
                    repeatCount="indefinite"
                  />
                  <animate attributeName="opacity" values="0.55;0" dur={dur} repeatCount="indefinite" />
                </circle>
              )}
              <circle
                cx={x}
                cy={y}
                r={r}
                fill="#10b981"
                stroke="#ffffff"
                strokeWidth={isDominant ? 2 : 1}
                opacity={isDominant ? 1 : 0.72}
                filter={isDominant ? "url(#nlglow)" : undefined}
              />
            </g>
          )
        })}
      </svg>

      {/* Stats glass overlay */}
      <div
        style={{
          position: "absolute",
          top: 16,
          left: 16,
          background: "rgba(12,25,41,0.82)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255,255,255,0.09)",
          borderRadius: 10,
          padding: "14px 20px",
          display: "flex",
          gap: 24,
        }}
      >
        <StatCell label="Foodbanks" value={String(banks.length)} />
        <StatCell label="CO₂e / yr" value={formatTCO2e(totalCo2)} accent />
        <StatCell label="Kg rescued" value={`${(banks.reduce((s, b) => s + (b.annual_kg_rescued ?? 0), 0) / 1e6).toFixed(1)}M`} />
      </div>

      {/* Legend */}
      <div
        style={{
          position: "absolute",
          bottom: 16,
          right: 16,
          background: "rgba(12,25,41,0.78)",
          backdropFilter: "blur(8px)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 8,
          padding: "8px 14px",
          display: "flex",
          alignItems: "center",
          gap: 14,
        }}
      >
        <LegendItem size={12} label="High CO₂e" />
        <LegendItem size={7} label="Mid" />
        <LegendItem size={4} label="Low" pulse />
      </div>
    </div>
  )
}

function StatCell({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div>
      <div
        style={{
          fontSize: 9,
          color: "#6b8fa8",
          textTransform: "uppercase",
          letterSpacing: "0.06em",
          fontWeight: 700,
          marginBottom: 2,
        }}
      >
        {label}
      </div>
      <div
        style={{
          fontSize: 20,
          fontWeight: 700,
          color: accent ? "#10b981" : "#fff",
          fontVariantNumeric: "tabular-nums",
          lineHeight: 1.1,
        }}
      >
        {value}
      </div>
    </div>
  )
}

function LegendItem({ size, label, pulse }: { size: number; label: string; pulse?: boolean }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 5 }}>
      <svg width={size + 2} height={size + 2} style={{ overflow: "visible" }}>
        <circle cx={(size + 2) / 2} cy={(size + 2) / 2} r={size / 2} fill="#10b981" opacity="0.8" />
        {pulse && (
          <circle cx={(size + 2) / 2} cy={(size + 2) / 2} r={size / 2} fill="none" stroke="#10b981" strokeWidth="1" opacity="0">
            <animate attributeName="r" values={`${size / 2};${size / 2 + 6}`} dur="2s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="0.6;0" dur="2s" repeatCount="indefinite" />
          </circle>
        )}
      </svg>
      <span style={{ fontSize: 10, color: "#6b8fa8", fontWeight: 500 }}>{label}</span>
    </div>
  )
}
