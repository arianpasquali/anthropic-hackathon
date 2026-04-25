import type { DashboardMetrics } from "@/lib/types"
import { formatNumber } from "@/lib/format"

export function Equivalents({ metrics }: { metrics: DashboardMetrics }) {
  const items = [
    {
      value: metrics.cars_equivalent,
      unit: "cars / yr",
      label: "Average NL passenger car (4.6 tCO₂e/yr · CBS 2023)",
    },
    {
      value: metrics.nl_households_equivalent,
      unit: "NL households",
      label: "Annual electricity (6.5 tCO₂e/yr · RIVM)",
    },
    {
      value: metrics.flights_equivalent,
      unit: "flights",
      label: "Economy AMS-JFK round-trip (0.255 tCO₂e · ICAO)",
    },
  ]

  return (
    <div className="border border-line rounded-[var(--radius-lg)] bg-surface-2 p-6">
      <p className="eyebrow">In context</p>
      <p className="text-[13px] text-text-muted mt-2 max-w-[44ch]">
        Annual claim translated to lay equivalents. For board copy, not for
        formal disclosure.
      </p>
      <ul className="grid grid-cols-3 gap-x-4 mt-6">
        {items.map((it) => (
          <li key={it.unit} className="flex flex-col gap-1">
            <span className="display tabular text-3xl">
              {formatNumber(it.value)}
            </span>
            <span className="text-[12px] text-text font-medium">{it.unit}</span>
            <span className="text-[11px] text-text-faint leading-snug">
              {it.label}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}
