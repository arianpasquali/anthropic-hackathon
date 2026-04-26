import type { Stat } from "@/lib/impact-types"

/**
 * Two-bar comparison: NL annual food waste vs. foodbank rescue volume.
 * Reads as "this is how big the wedge is" — used on /methodology and /why.
 */
export function PovertyBars({
  waste,
  rescued,
}: {
  waste: Stat
  rescued: Stat
}) {
  const max = waste.value
  const ratio = (rescued.value / max) * 100

  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-6 lg:p-8">
      <Bar
        label="NL food waste / year"
        valueLabel={`${(waste.value / 1_000_000_000).toFixed(1)} billion kg`}
        widthPct={100}
        tone="muted"
        sourceLabel={waste.source_label}
        sourceUrl={waste.source_url}
      />
      <div className="h-6" />
      <Bar
        label="Rescued by foodbanks"
        valueLabel={`${(rescued.value / 1_000_000).toFixed(0)} million kg`}
        widthPct={Math.max(ratio, 1.5)}
        tone="emerald"
        sourceLabel={rescued.source_label}
        sourceUrl={rescued.source_url}
      />
    </div>
  )
}

function Bar({
  label,
  valueLabel,
  widthPct,
  tone,
  sourceLabel,
  sourceUrl,
}: {
  label: string
  valueLabel: string
  widthPct: number
  tone: "muted" | "emerald"
  sourceLabel: string
  sourceUrl: string
}) {
  return (
    <div>
      <div className="flex justify-between items-baseline mb-1.5">
        <span className="text-[13px] text-text-muted">{label}</span>
        <span className="text-[13px] tabular font-medium text-text">
          {valueLabel}
        </span>
      </div>
      <div className="h-7 bg-surface-2 border border-line rounded-[var(--radius)] overflow-hidden">
        <div
          className={`h-full rounded-[var(--radius)] ${tone === "emerald" ? "bg-emerald-deep" : "bg-line-strong"}`}
          style={{ width: `${widthPct}%` }}
        />
      </div>
      <p className="mt-2 text-[11.5px] text-text-faint">
        Source:{" "}
        <a
          href={sourceUrl}
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-2 hover:text-text-muted"
        >
          {sourceLabel}
        </a>
      </p>
    </div>
  )
}
