import { cn } from "@/lib/cn"

export function StatBlock({
  label,
  value,
  hint,
  className,
}: {
  label: string
  value: React.ReactNode
  hint?: React.ReactNode
  className?: string
}) {
  return (
    <div className={cn("flex flex-col gap-1.5", className)}>
      <span className="eyebrow">{label}</span>
      <span className="display tabular text-4xl md:text-5xl">{value}</span>
      {hint ? (
        <span className="text-[13px] text-text-muted tabular">{hint}</span>
      ) : null}
    </div>
  )
}
