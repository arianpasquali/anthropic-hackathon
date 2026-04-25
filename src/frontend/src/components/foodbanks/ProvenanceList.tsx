import { Badge } from "@/components/ui/Badge"
import type { ProvenanceRecord, Source } from "@/lib/types"

const SOURCE_LABEL: Record<Source, string> = {
  extracted: "Extracted",
  inferred_national_avg: "National avg",
  inferred_category_split: "Category split",
  inferred_calculation: "Calculated",
  manual: "Manual",
}

const SOURCE_VARIANT: Record<Source, "emerald" | "default" | "outline" | "warning"> = {
  extracted: "emerald",
  inferred_national_avg: "default",
  inferred_category_split: "default",
  inferred_calculation: "default",
  manual: "outline",
}

const FIELD_LABEL: Record<string, string> = {
  kg_produce: "Produce kg",
  kg_meat_fish: "Meat & fish kg",
  kg_dairy_eggs: "Dairy & eggs kg",
  kg_dry_goods: "Dry goods kg",
  kg_bread_bakery: "Bakery kg",
  kg_prepared: "Prepared kg",
  households_weekly: "Households / wk",
  individuals_total: "Individuals served",
  children_count: "Children served",
}

export function ProvenanceList({ records }: { records: ProvenanceRecord[] }) {
  if (!records.length) {
    return (
      <p className="text-text-muted text-[13.5px]">
        No provenance ledger available — annual report not yet ingested.
      </p>
    )
  }
  return (
    <ul className="flex flex-col divide-y divide-line/60">
      {records.map((r, i) => (
        <li key={`${r.field}-${i}`} className="py-3 flex items-center justify-between gap-4">
          <div className="flex flex-col">
            <span className="text-[13.5px] text-text">
              {FIELD_LABEL[r.field] ?? r.field}
            </span>
            {r.method ? (
              <span className="text-[12px] text-text-muted">{r.method}</span>
            ) : null}
          </div>
          <Badge variant={SOURCE_VARIANT[r.source] ?? "default"}>
            {SOURCE_LABEL[r.source] ?? r.source}
          </Badge>
        </li>
      ))}
    </ul>
  )
}
