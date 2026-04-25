"use client"

import { useMemo, useState } from "react"
import { TabBar } from "@/components/ui/Tabs"
import { FundCard } from "./FundCard"
import type { ImpactProfile, Package } from "@/lib/types"

type Filter = "all" | ImpactProfile

const TABS = [
  { value: "all", label: "All funds" },
  { value: "co2_focus", label: "CO₂ focus" },
  { value: "social_focus", label: "Social focus" },
  { value: "balanced", label: "Balanced" },
]

export function MarketplaceFilters({ packages }: { packages: Package[] }) {
  const [filter, setFilter] = useState<Filter>("all")
  const filtered = useMemo(
    () => (filter === "all" ? packages : packages.filter((p) => p.impact_profile === filter)),
    [packages, filter],
  )

  return (
    <div>
      <TabBar items={TABS} value={filter} onChange={(v) => setFilter(v as Filter)} />
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-8">
        {filtered.map((pkg, i) => (
          <FundCard key={pkg.id} pkg={pkg} featured={i === 0 && filter === "all"} />
        ))}
      </div>
      {filtered.length === 0 ? (
        <p className="text-text-muted text-sm py-8">No funds in this profile yet.</p>
      ) : null}
    </div>
  )
}
