import type { DashboardAllocationDetail } from "@/lib/types"
import { formatEur, formatPercent, formatTCO2e } from "@/lib/format"

export function DashboardAllocationsTable({
  allocations,
}: {
  allocations: DashboardAllocationDetail[]
}) {
  return (
    <div className="border border-line rounded-[var(--radius-lg)] overflow-hidden">
      <table className="w-full text-[13.5px] tabular">
        <thead className="bg-surface-2 text-text-muted text-left">
          <tr>
            <Th>Food bank</Th>
            <Th>City</Th>
            <Th align="right">Share</Th>
            <Th align="right">Funded</Th>
            <Th align="right">tCO₂e</Th>
          </tr>
        </thead>
        <tbody>
          {allocations.map((a) => (
            <tr key={a.foodbank_id} className="border-t border-line/60">
              <Td>{a.foodbank_name}</Td>
              <Td className="text-text-muted">{a.foodbank_city}</Td>
              <Td align="right">{formatPercent(a.weight_pct, 1)}</Td>
              <Td align="right">{formatEur(a.amount_eur)}</Td>
              <Td align="right">{formatTCO2e(a.co2e_attributed_kg / 1000)}</Td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Th({ children, align = "left" }: { children: React.ReactNode; align?: "left" | "right" }) {
  return (
    <th
      className={`px-4 py-3 font-medium text-[11px] tracking-[0.08em] uppercase ${
        align === "right" ? "text-right" : "text-left"
      }`}
    >
      {children}
    </th>
  )
}

function Td({
  children,
  align = "left",
  className,
}: {
  children: React.ReactNode
  align?: "left" | "right"
  className?: string
}) {
  return (
    <td className={`px-4 py-3 ${align === "right" ? "text-right" : ""} ${className ?? ""}`}>
      {children}
    </td>
  )
}
