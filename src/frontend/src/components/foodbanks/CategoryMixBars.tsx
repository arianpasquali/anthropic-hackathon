"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { CATEGORY_LABELS } from "@/lib/methodology"
import type { CategoryMix } from "@/lib/types"

const ORDER: (keyof CategoryMix)[] = [
  "produce", "dry_goods", "dairy", "bakery", "meat", "prepared", "eggs",
]

export function CategoryMixBars({ mix, totalKg }: { mix: CategoryMix; totalKg: number }) {
  const rows = ORDER.map((k) => ({
    label: CATEGORY_LABELS[k as keyof typeof CATEGORY_LABELS],
    kg: (mix[k] ?? 0) * totalKg,
    pct: (mix[k] ?? 0) * 100,
  }))
  return (
    <div style={{ height: 280, width: "100%", minWidth: 0 }}>
      <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
        <BarChart data={rows} layout="vertical" margin={{ top: 10, right: 16, left: 12, bottom: 8 }}>
          <CartesianGrid stroke="var(--line)" strokeDasharray="2 4" horizontal={false} />
          <XAxis
            type="number"
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            type="category"
            dataKey="label"
            tick={{ fontSize: 12, fill: "var(--text)" }}
            axisLine={false}
            tickLine={false}
            width={86}
          />
          <Tooltip
            contentStyle={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 4, fontSize: 12 }}
            formatter={(v) => [`${Math.round(Number(v) ?? 0).toLocaleString()} kg`, "Rescued"]}
            cursor={{ fill: "var(--surface-2)" }}
          />
          <Bar dataKey="kg" fill="var(--emerald)" radius={[0, 2, 2, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
