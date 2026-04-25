import Link from "next/link"
import type { ProjectedAllocation } from "@/lib/types"
import { formatEur, formatKg, formatPercent, formatTCO2e } from "@/lib/format"

export function AllocationTable({ allocations }: { allocations: ProjectedAllocation[] }) {
  return (
    <div className="border border-line rounded-[var(--radius-lg)] overflow-hidden">
      <table className="w-full text-[13.5px] tabular">
        <thead className="bg-surface-2 text-text-muted text-left">
          <tr>
            <Th>Food bank</Th>
            <Th>Region</Th>
            <Th align="right">Share</Th>
            <Th align="right">kg rescued</Th>
            <Th align="right">tCO₂e</Th>
            <Th align="right">€</Th>
          </tr>
        </thead>
        <tbody>
          {allocations.map((a) => (
            <tr key={a.foodbank.id} className="border-t border-line/60 hover:bg-surface-2/60">
              <Td>
                <Link href={`/foodbanks/${a.foodbank.slug}`} className="hover:text-emerald">
                  {a.foodbank.name}
                </Link>
              </Td>
              <Td className="text-text-muted">{a.foodbank.region}</Td>
              <Td align="right">{formatPercent(a.weight_pct, 1)}</Td>
              <Td align="right">{formatKg(a.attributed_kg)}</Td>
              <Td align="right">{formatTCO2e(a.attributed_tco2e)}</Td>
              <Td align="right">{formatEur(a.attributed_eur)}</Td>
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
      scope="col"
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
    <td
      className={`px-4 py-3 ${align === "right" ? "text-right" : ""} ${className ?? ""}`}
    >
      {children}
    </td>
  )
}
