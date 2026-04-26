import type { SubscriptionPacing } from "@/lib/types"
import { formatPercent } from "@/lib/format"

export function PacingBar({ pacing }: { pacing: SubscriptionPacing }) {
  return (
    <div className="h-full flex flex-col border border-line rounded-[var(--radius-lg)] bg-surface p-6">
      <div className="flex items-baseline justify-between gap-3 flex-wrap">
        <p className="eyebrow">Subscription pacing</p>
        <span className="text-[12.5px] text-text-faint tabular">
          next disclosure · {pacing.next_disclosure_quarter}
        </span>
      </div>
      <p className="mt-2 text-[14px] text-text">
        <span className="display tabular text-3xl">
          {pacing.quarters_realised}
        </span>{" "}
        <span className="text-text-muted">of</span>{" "}
        <span className="tabular text-text">{pacing.quarters_contracted}</span>{" "}
        <span className="text-text-muted">quarters realised</span>
      </p>
      <p className="text-[12.5px] text-text-muted mt-1">
        Annual cycle: {formatPercent(pacing.cycle_pct, 0)} complete
      </p>

      <div className="mt-auto pt-5 grid grid-cols-4 gap-2">
        {Array.from({ length: pacing.quarters_contracted }, (_, i) => {
          const realised = i < pacing.quarters_realised
          return (
            <div
              key={i}
              className={
                "h-1.5 rounded-full " +
                (realised ? "bg-emerald" : "bg-surface-3")
              }
              aria-label={`Quarter ${i + 1}: ${realised ? "realised" : "future"}`}
            />
          )
        })}
      </div>
    </div>
  )
}
