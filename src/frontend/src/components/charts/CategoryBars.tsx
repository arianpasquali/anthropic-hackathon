"use client"

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { CATEGORY_LABELS, EMISSION_FACTORS } from "@/lib/methodology"

const ORDER = ["produce", "dry_goods", "dairy", "bakery", "meat", "prepared", "eggs"] as const

export interface CategoryBarsProps {
  /** map of category key → tCO2e value */
  data: Record<string, number>
  height?: number
  yLabel?: string
}

export function CategoryBars({ data, height = 280, yLabel = "tCO₂e" }: CategoryBarsProps) {
  const rows = ORDER.map((k) => ({
    key: k,
    label: CATEGORY_LABELS[k as keyof typeof EMISSION_FACTORS],
    value: data[k] ?? 0,
  }))

  return (
    <div style={{ height, width: "100%", minWidth: 0 }}>
      <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
        <BarChart data={rows} margin={{ top: 10, right: 8, left: 0, bottom: 8 }}>
          <CartesianGrid stroke="var(--line)" strokeDasharray="2 4" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            tickLine={false}
            axisLine={{ stroke: "var(--line)" }}
          />
          <YAxis
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            tickLine={false}
            axisLine={false}
            label={{ value: yLabel, angle: -90, position: "insideLeft", fontSize: 11, fill: "var(--text-faint)" }}
          />
          <Tooltip
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--line)",
              borderRadius: 4,
              fontSize: 12,
            }}
            cursor={{ fill: "var(--surface-2)" }}
          />
          <Bar dataKey="value" fill="var(--emerald)" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
