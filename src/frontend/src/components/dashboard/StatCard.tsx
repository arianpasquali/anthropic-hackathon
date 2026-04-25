export function StatCard({
  label,
  value,
  hint,
  emphasis = false,
}: {
  label: string
  value: React.ReactNode
  hint?: React.ReactNode
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
      {hint ? <span className="text-[12.5px] text-text-muted">{hint}</span> : null}
    </div>
  )
}
