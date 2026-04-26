import { formatEur } from "@/lib/format"
import type { ImpactProfile } from "@/lib/types"

// Reference benchmarks (EUR / tCO2e) — voluntary carbon market reference points only,
// not endorsed as offsets. Climate Harvest packages are climate contributions.
const BENCHMARKS = [
  { label: "Voluntary average", value: 12, tone: "oklch(78% 0.08 75)" },
  { label: "Gold Standard", value: 35, tone: "oklch(72% 0.10 110)" },
  { label: "Verified novel approaches", value: 250, tone: "var(--emerald)" },
  { label: "Direct air capture", value: 600, tone: "oklch(45% 0.10 220)" },
]

export function CostEffectivenessGauge({
  eurPerTco2e,
  profile,
}: {
  eurPerTco2e: number | null
  profile?: ImpactProfile
}) {
  if (eurPerTco2e == null) {
    return null
  }
  const xMax = 700
  const pct = Math.min(100, (eurPerTco2e / xMax) * 100)

  // Where does this land?
  const band =
    eurPerTco2e <= 30
      ? { label: "Below voluntary avg", tone: "oklch(50% 0.10 110)" }
      : eurPerTco2e <= 80
        ? { label: "Around Gold Standard", tone: "var(--emerald-deep)" }
        : eurPerTco2e <= 350
          ? { label: "Premium for verified social co-benefits", tone: "var(--emerald-deep)" }
          : { label: "DAC-territory premium", tone: "oklch(45% 0.10 220)" }

  return (
    <div className="border border-line rounded-[var(--radius-lg)] bg-surface p-6">
      <div className="flex items-baseline justify-between gap-3 flex-wrap">
        <p className="eyebrow">Cost effectiveness</p>
        <span
          className="text-[11.5px] tracking-wider uppercase font-medium"
          style={{ color: band.tone }}
        >
          {band.label}
        </span>
      </div>
      <p className="display tabular text-3xl mt-2">
        {formatEur(eurPerTco2e)} <span className="text-text-faint text-lg">/ tCO₂e</span>
      </p>
      <p className="text-[12.5px] text-text-muted mt-1">
        Your fund&apos;s blended price per tonne of climate contribution
        {profile ? ` · ${profile.replace("_", " ")} profile` : ""}
      </p>

      <div className="mt-6 relative h-8">
        <div className="absolute inset-x-0 top-3 h-1.5 bg-surface-3 rounded-full overflow-hidden">
          {BENCHMARKS.map((b, i) => {
            const left = (b.value / xMax) * 100
            return (
              <div
                key={b.label}
                className="absolute top-0 h-full"
                style={{ left: `${left}%`, width: 1, background: b.tone, opacity: 0.5 }}
              />
            )
          })}
        </div>
        <div
          className="absolute top-1.5 w-3 h-4 rounded-sm"
          style={{
            left: `calc(${pct}% - 6px)`,
            background: "var(--emerald-deep)",
            boxShadow: "0 0 0 3px var(--surface)",
          }}
          title={`${formatEur(eurPerTco2e)} / tCO₂e`}
        />
      </div>

      <ul className="mt-3 flex justify-between text-[10.5px] text-text-faint tabular">
        {BENCHMARKS.map((b) => (
          <li key={b.label} className="flex flex-col items-center gap-0.5">
            <span>{formatEur(b.value)}</span>
            <span className="text-[9.5px]">{b.label}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
