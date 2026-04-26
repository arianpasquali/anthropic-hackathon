"use client"

import { useMemo, useState } from "react"
import Link from "next/link"
import { TabBar } from "@/components/ui/Tabs"
import { formatNumber, formatTCO2e } from "@/lib/format"
import type { Bank } from "@/lib/types"

type Sort = "tco2e_desc" | "kg_desc" | "households_desc" | "name_asc"

const SORTS: { value: Sort; label: string }[] = [
  { value: "tco2e_desc", label: "CO₂e baseline" },
  { value: "kg_desc", label: "Food rescued" },
  { value: "households_desc", label: "Households served" },
  { value: "name_asc", label: "Name (A–Z)" },
]

export function FoodbankFilters({ banks }: { banks: Bank[] }) {
  const regions = useMemo(() => {
    const set = new Set<string>()
    for (const b of banks) if (b.region) set.add(b.region)
    return Array.from(set).sort()
  }, [banks])

  const tabs = useMemo(
    () => [
      { value: "all", label: "All regions" },
      ...regions.map((r) => ({ value: r, label: r })),
    ],
    [regions],
  )

  const [region, setRegion] = useState<string>("all")
  const [sort, setSort] = useState<Sort>("tco2e_desc")

  const filtered = useMemo(() => {
    const base = region === "all" ? banks : banks.filter((b) => b.region === region)
    const sorted = [...base]
    switch (sort) {
      case "tco2e_desc":
        sorted.sort((a, b) => (b.annual_tco2e ?? 0) - (a.annual_tco2e ?? 0))
        break
      case "kg_desc":
        sorted.sort((a, b) => (b.annual_kg_rescued ?? 0) - (a.annual_kg_rescued ?? 0))
        break
      case "households_desc":
        sorted.sort((a, b) => (b.households_weekly ?? 0) - (a.households_weekly ?? 0))
        break
      case "name_asc":
        sorted.sort((a, b) => a.name.localeCompare(b.name))
        break
    }
    return sorted
  }, [banks, region, sort])

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-4 pb-4 mb-2 border-b border-line/60">
        <div className="flex items-center gap-2.5 text-[12.5px] text-text-muted">
          <span className="kk-live-dot" aria-hidden />
          <span className="tabular">
            {banks.length} foodbanks ingested
          </span>
          <span aria-hidden className="text-text-faint">·</span>
          <span className="tabular text-text-faint">181-bank network on roadmap</span>
        </div>
        <label className="flex items-center gap-2 text-[12.5px] text-text-muted">
          <span>Sort</span>
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value as Sort)}
            className="bg-transparent border border-line h-8 px-2 text-[13px] text-text rounded-[var(--radius)] focus:outline-none focus:border-emerald-deep transition-colors"
          >
            {SORTS.map((s) => (
              <option key={s.value} value={s.value}>{s.label}</option>
            ))}
          </select>
        </label>
      </div>

      {regions.length > 1 ? (
        <TabBar items={tabs} value={region} onChange={(v) => setRegion(v)} />
      ) : null}

      <div className="mt-8 border border-line rounded-[var(--radius-lg)] overflow-hidden bg-surface">
        <table className="w-full text-[13.5px]">
          <thead className="bg-surface-2 text-text-muted">
            <tr>
              <Th>Foodbank</Th>
              <Th>Region</Th>
              <Th align="right">CO₂e baseline</Th>
              <Th align="right">Food rescued</Th>
              <Th align="right">Households / wk</Th>
              <Th align="right" />
            </tr>
          </thead>
          <tbody>
            {filtered.map((b) => (
              <tr key={b.id} className="border-t border-line/60 hover:bg-surface-2/60 transition-colors">
                <Td>
                  <span className="text-text font-medium">{b.name}</span>
                  <span className="block text-[12px] text-text-faint">{b.city}</span>
                </Td>
                <Td className="text-text-muted">{b.region || "—"}</Td>
                <Td align="right" className="tabular">
                  {b.annual_tco2e != null ? formatTCO2e(b.annual_tco2e) : "—"}
                </Td>
                <Td align="right" className="tabular">
                  {b.annual_kg_rescued != null
                    ? `${formatNumber(b.annual_kg_rescued / 1000, { maximumFractionDigits: 0 })} t`
                    : "—"}
                </Td>
                <Td align="right" className="tabular">
                  {b.households_weekly != null ? formatNumber(b.households_weekly) : "—"}
                </Td>
                <Td align="right">
                  <Link
                    href={`/foodbanks/${b.slug}`}
                    className="text-emerald hover:underline text-[13px]"
                  >
                    View profile →
                  </Link>
                </Td>
              </tr>
            ))}
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center text-text-muted text-[13px]">
                  No foodbanks match this filter.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function Th({
  children,
  align = "left",
}: {
  children?: React.ReactNode
  align?: "left" | "right"
}) {
  return (
    <th
      className={`px-4 py-3 text-${align} font-medium text-[11px] tracking-[0.08em] uppercase`}
    >
      {children}
    </th>
  )
}

function Td({
  children,
  align = "left",
  className = "",
}: {
  children?: React.ReactNode
  align?: "left" | "right"
  className?: string
}) {
  return (
    <td className={`px-4 py-3 text-${align} align-middle ${className}`}>{children}</td>
  )
}
