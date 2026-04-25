"use client"
import dynamic from "next/dynamic"

export const NLProvinceHeatMapDynamic = dynamic(
  () => import("./NLProvinceHeatMap").then((m) => m.NLProvinceHeatMap),
  {
    ssr: false,
    loading: () => (
      <div className="border border-line bg-surface-2 animate-pulse" style={{ height: 380 }} />
    ),
  },
)
