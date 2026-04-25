import { Badge } from "@/components/ui/Badge"
import type { ProvenanceMix } from "@/lib/types"
import { formatPercent } from "@/lib/format"

const SEGMENTS: { key: keyof ProvenanceMix; label: string; tone: string }[] = [
  { key: "extracted_pct", label: "Extracted", tone: "var(--emerald-deep)" },
  { key: "inferred_national_avg_pct", label: "National avg", tone: "var(--emerald)" },
  { key: "inferred_category_split_pct", label: "Category split", tone: "oklch(72% 0.06 155)" },
  { key: "inferred_calculation_pct", label: "Calculated", tone: "oklch(82% 0.04 155)" },
  { key: "manual_pct", label: "Manual", tone: "oklch(72% 0.15 75)" },
]

const BAND_LABEL = {
  high: "High audit confidence",
  medium: "Medium audit confidence",
  low: "Low audit confidence",
} as const

export function ProvenanceScorecard({ provenance }: { provenance: ProvenanceMix }) {
  const segments = SEGMENTS.map((s) => ({
    ...s,
    pct: provenance[s.key] as number,
  })).filter((s) => s.pct > 0)

  return (
    <div className="border border-line rounded-[var(--radius-lg)] bg-surface p-6">
      <div className="flex items-baseline justify-between gap-3 flex-wrap">
        <p className="eyebrow">Provenance scorecard</p>
        <Badge
          variant={
            provenance.confidence_band === "high"
              ? "emerald"
              : provenance.confidence_band === "medium"
                ? "default"
                : "warning"
          }
        >
          {BAND_LABEL[provenance.confidence_band]}
        </Badge>
      </div>

      <p className="display tabular text-3xl mt-2">
        {formatPercent(provenance.extracted_pct, 0)}
      </p>
      <p className="text-[12.5px] text-text-muted mt-1">
        of measurements pulled directly from source documents
      </p>

      <div className="mt-5 h-2 w-full flex overflow-hidden rounded-full bg-surface-3">
        {segments.map((s) => (
          <div
            key={s.key as string}
            style={{ width: `${s.pct * 100}%`, background: s.tone }}
            title={`${s.label}: ${formatPercent(s.pct, 0)}`}
          />
        ))}
      </div>

      <ul className="mt-4 grid grid-cols-2 gap-x-4 gap-y-2 text-[12.5px]">
        {segments.map((s) => (
          <li key={s.key as string} className="flex items-center gap-2">
            <span aria-hidden className="block w-2 h-2 rounded-sm" style={{ background: s.tone }} />
            <span className="text-text-muted flex-1">{s.label}</span>
            <span className="tabular text-text">{formatPercent(s.pct, 0)}</span>
          </li>
        ))}
      </ul>

      <p className="mt-5 text-[12px] text-text-faint leading-relaxed">
        Auditor signal: every measurement carries a source tag. Confidence band
        is derived from the share read directly from each food bank&apos;s annual
        report.
      </p>
    </div>
  )
}
