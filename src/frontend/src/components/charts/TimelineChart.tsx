"use client"

import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { formatNumber } from "@/lib/format"

export interface TimelinePoint {
  year: number
  co2e_kg: number
  annual_kg_rescued?: number | null
  households_weekly?: number | null
}

export function TimelineChart({
  data,
  height = 260,
  metric = "co2e",
}: {
  data: TimelinePoint[]
  height?: number
  metric?: "co2e" | "kg"
}) {
  const series = data.map((p) => ({
    label: String(p.year),
    co2e_t: (p.co2e_kg ?? 0) / 1000,
    kg_m: (p.annual_kg_rescued ?? 0) / 1_000_000,
  }))

  return (
    <div style={{ height, width: "100%", minWidth: 0 }}>
      <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
        <AreaChart data={series} margin={{ top: 10, right: 16, left: 0, bottom: 8 }}>
          <defs>
            <linearGradient id="emerald-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--emerald)" stopOpacity={0.32} />
              <stop offset="100%" stopColor="var(--emerald)" stopOpacity={0.04} />
            </linearGradient>
          </defs>
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
            width={56}
            tickFormatter={(v) =>
              metric === "co2e"
                ? `${formatNumber(Number(v), { maximumFractionDigits: 0 })}t`
                : `${Number(v).toFixed(1)}M`
            }
          />
          <Tooltip
            contentStyle={{
              background: "var(--surface)",
              border: "1px solid var(--line)",
              borderRadius: 4,
              fontSize: 12,
            }}
            formatter={(v, name) => {
              const num = Number(v) || 0
              if (name === "co2e_t") return [`${formatNumber(num, { maximumFractionDigits: 0 })} tCO₂e`, "Avoided"]
              return [`${num.toFixed(2)}M kg`, "Rescued"]
            }}
            labelFormatter={(l) => `Year ${l}`}
            cursor={{ stroke: "var(--line-strong)" }}
          />
          {metric === "co2e" ? (
            <Area
              type="monotone"
              dataKey="co2e_t"
              stroke="var(--emerald-deep)"
              strokeWidth={2}
              fill="url(#emerald-fill)"
              activeDot={{ r: 4, stroke: "var(--emerald-deep)", strokeWidth: 2, fill: "var(--surface)" }}
            />
          ) : (
            <Area
              type="monotone"
              dataKey="kg_m"
              stroke="var(--emerald-deep)"
              strokeWidth={2}
              fill="url(#emerald-fill)"
            />
          )}
          <Legend wrapperStyle={{ display: "none" }} />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
