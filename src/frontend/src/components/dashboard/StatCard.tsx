export function StatCard({
  label,
  value,
  hint,
  delta,
  emphasis = false,
}: {
  label: string
  value: React.ReactNode
  hint?: React.ReactNode
  delta?: number | null
  emphasis?: boolean
}) {
  return (
    <div
      className={
        "flex flex-col gap-1.5 p-6 border border-line rounded-[var(--radius-lg)] " +
        (emphasis ? "bg-emerald-soft" : "bg-surface")
      }
    >
      <span className="eyebrow">{label}</span>
      <span className="display tabular text-3xl md:text-4xl">{value}</span>
      <div className="flex items-center gap-2 text-[12.5px] text-text-muted">
        {hint ? <span>{hint}</span> : null}
        {delta != null && Number.isFinite(delta) ? (
          <span
            className={
              "tabular font-medium " +
              (delta >= 0 ? "text-emerald-deep" : "text-warning")
            }
          >
            {delta >= 0 ? "↑" : "↓"} {(Math.abs(delta) * 100).toFixed(1)}%{" "}
            <span className="text-text-faint font-normal">YoY</span>
          </span>
        ) : null}
      </div>
    </div>
  )
}
