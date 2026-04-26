"use client"

import { useMemo, useState } from "react"
import { TabBar } from "@/components/ui/Tabs"
import { FundCard } from "./FundCard"
import type { ImpactProfile, Package } from "@/lib/types"

type Filter = "all" | ImpactProfile
type Sort = "impact" | "price_asc" | "price_desc" | "co2e_desc"

const TABS = [
  { value: "all", label: "All funds" },
  { value: "co2_focus", label: "CO₂ focus" },
  { value: "social_focus", label: "Social focus" },
  { value: "balanced", label: "Balanced" },
]

const SORTS: { value: Sort; label: string }[] = [
  { value: "impact", label: "Recommended" },
  { value: "co2e_desc", label: "Highest CO₂e" },
  { value: "price_asc", label: "Lowest price" },
  { value: "price_desc", label: "Highest price" },
]

export function MarketplaceFilters({ packages }: { packages: Package[] }) {
  const [filter, setFilter] = useState<Filter>("all")
  const [sort, setSort] = useState<Sort>("impact")
  const filtered = useMemo(() => {
    const base = filter === "all" ? packages : packages.filter((p) => p.impact_profile === filter)
    const sorted = [...base]
    switch (sort) {
      case "price_asc":
        sorted.sort((a, b) => a.price_eur - b.price_eur)
        break
      case "price_desc":
        sorted.sort((a, b) => b.price_eur - a.price_eur)
        break
      case "co2e_desc":
        sorted.sort((a, b) => b.co2e_claim_kg - a.co2e_claim_kg)
        break
    }
    return sorted
  }, [packages, filter, sort])

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-4 pb-4 mb-2 border-b border-line/60">
        <div className="flex items-center gap-2.5 text-[12.5px] text-text-muted">
          <span className="kk-live-dot" aria-hidden />
          <span className="tabular">
            {packages.length} {packages.length === 1 ? "fund" : "funds"} available
          </span>
          <span aria-hidden className="text-text-faint">·</span>
          <span className="tabular text-text-faint">last allocation computed 6m ago</span>
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
      <TabBar items={TABS} value={filter} onChange={(v) => setFilter(v as Filter)} />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
        {filtered.map((pkg, i) => (
          <FundCard key={pkg.id} pkg={pkg} featured={i === 0 && filter === "all" && sort === "impact"} />
        ))}
      </div>
      {filtered.length === 0 ? (
        <p className="text-text-muted text-sm py-8">No funds in this profile yet.</p>
      ) : null}
    </div>
  )
}
