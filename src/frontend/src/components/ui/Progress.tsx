import { cn } from "@/lib/cn"

export function Progress({ value, className }: { value: number; className?: string }) {
  const pct = Math.max(0, Math.min(1, value))
  return (
    <div
      className={cn("h-1.5 w-full bg-surface-3 overflow-hidden rounded-full", className)}
      role="progressbar"
      aria-valuenow={Math.round(pct * 100)}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="h-full bg-emerald transition-[width] duration-500"
        style={{ width: `${pct * 100}%` }}
      />
    </div>
  )
}
