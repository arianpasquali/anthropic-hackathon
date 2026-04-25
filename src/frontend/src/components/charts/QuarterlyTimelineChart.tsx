"use client"

import {
  Area,
  ComposedChart,
  CartesianGrid,
  Legend,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { formatNumber } from "@/lib/format"

export interface QuarterPoint {
  label: string
  year: number
  quarter: number
  co2e_kg: number
  realised: boolean
  cumulative_co2e_kg: number
}

export function QuarterlyTimelineChart({
  data,
  height = 320,
}: {
  data: QuarterPoint[]
  height?: number
}) {
  // Build two parallel series so realised vs forecast can render in different
  // colours/strokes on the same axis.
  const rows = data.map((p) => ({
    label: p.label,
    realised_t: p.realised ? p.co2e_kg / 1000 : null,
    forecast_t: !p.realised ? p.co2e_kg / 1000 : null,
    cumulative_t: p.cumulative_co2e_kg / 1000,
    realised: p.realised,
  }))

  const splitIdx = data.findIndex((p) => !p.realised)
  const splitLabel = splitIdx > 0 ? data[splitIdx - 1].label : null

  return (
    <div style={{ height, width: "100%", minWidth: 0 }}>
      <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
        <ComposedChart data={rows} margin={{ top: 10, right: 16, left: 0, bottom: 8 }}>
          <defs>
            <linearGradient id="cum-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="var(--emerald)" stopOpacity={0.18} />
              <stop offset="100%" stopColor="var(--emerald)" stopOpacity={0.02} />
            </linearGradient>
          </defs>
          <CartesianGrid stroke="var(--line)" strokeDasharray="2 4" vertical={false} />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            tickLine={false}
            axisLine={{ stroke: "var(--line)" }}
            interval="preserveStartEnd"
          />
          <YAxis
            yAxisId="left"
            tick={{ fontSize: 11, fill: "var(--text-muted)" }}
            tickLine={false}
            axisLine={false}
            width={56}
            tickFormatter={(v) => `${formatNumber(Number(v), { maximumFractionDigits: 0 })}t`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 11, fill: "var(--text-faint)" }}
            tickLine={false}
            axisLine={false}
            width={56}
            tickFormatter={(v) => `${formatNumber(Number(v), { maximumFractionDigits: 0 })}t`}
          />
          <Tooltip
            contentStyle={{ background: "var(--surface)", border: "1px solid var(--line)", borderRadius: 4, fontSize: 12 }}
            formatter={(v, name) => {
              const num = Number(v) || 0
              const label =
                name === "realised_t"
                  ? "Realised"
                  : name === "forecast_t"
                    ? "Forecast"
                    : "Cumulative"
              return [`${formatNumber(num, { maximumFractionDigits: 0 })} tCO₂e`, label]
            }}
            cursor={{ stroke: "var(--line-strong)" }}
          />
          {splitLabel ? (
            <ReferenceLine
              x={splitLabel}
              yAxisId="left"
              stroke="var(--line-strong)"
              strokeDasharray="3 3"
              label={{
                value: "now",
                position: "top",
                fontSize: 10,
                fill: "var(--text-faint)",
              }}
            />
          ) : null}
          <Area
            yAxisId="right"
            type="monotone"
            dataKey="cumulative_t"
            stroke="var(--emerald-deep)"
            strokeWidth={1}
            fill="url(#cum-fill)"
            isAnimationActive
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="realised_t"
            stroke="var(--emerald-deep)"
            strokeWidth={2.5}
            dot={{ r: 3, stroke: "var(--emerald-deep)", strokeWidth: 1.5, fill: "var(--surface)" }}
            activeDot={{ r: 5 }}
            connectNulls={false}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="forecast_t"
            stroke="var(--emerald)"
            strokeWidth={2}
            strokeDasharray="5 4"
            dot={{ r: 2.5, stroke: "var(--emerald)", strokeWidth: 1.5, fill: "var(--surface)" }}
            connectNulls={false}
          />
          <Legend wrapperStyle={{ fontSize: 11, color: "var(--text-muted)" }} iconType="plainline" />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  )
}
