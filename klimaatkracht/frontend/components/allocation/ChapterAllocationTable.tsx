"use client";

import type { AllocationResult, ChapterSnapshot } from "../../lib/types";

const formatter = new Intl.NumberFormat("en-NL", { maximumFractionDigits: 0 });
const eurFormatter = new Intl.NumberFormat("en-NL", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});
const pctFormatter = new Intl.NumberFormat("en-NL", {
  style: "percent",
  maximumFractionDigits: 1,
});

export type ChapterAllocationTableProps = {
  chapters: ChapterSnapshot[];
  allocations: Record<string, AllocationResult>;
};

export function ChapterAllocationTable({
  chapters,
  allocations,
}: ChapterAllocationTableProps) {
  return (
    <div className="overflow-hidden rounded-md border border-ink/10 bg-white">
      <table className="w-full text-sm">
        <thead className="bg-ink/5 text-left text-xs uppercase tracking-wide text-ink/60">
          <tr>
            <th className="px-3 py-2">Chapter</th>
            <th className="px-3 py-2 text-right">Net avoided</th>
            <th className="px-3 py-2 text-right">Households / quarter</th>
            <th className="px-3 py-2 text-right">Tonnage</th>
            <th className="px-3 py-2 text-right">Weight</th>
            <th className="px-3 py-2 text-right">Allocation</th>
          </tr>
        </thead>
        <tbody>
          {chapters.map((c) => {
            const a = allocations[c.id];
            return (
              <tr key={c.id} className="border-t border-ink/10">
                <td className="px-3 py-2 font-mono text-xs">{c.id}</td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {c.net_avoided_tco2e.toFixed(1)} tCO₂e
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {formatter.format(c.households_served_quarter)}
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {c.total_tonnes.toFixed(1)} t
                </td>
                <td className="px-3 py-2 text-right tabular-nums">
                  {a ? pctFormatter.format(a.weight) : "—"}
                </td>
                <td className="px-3 py-2 text-right tabular-nums font-medium">
                  {a ? eurFormatter.format(a.amount_eur) : "—"}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
