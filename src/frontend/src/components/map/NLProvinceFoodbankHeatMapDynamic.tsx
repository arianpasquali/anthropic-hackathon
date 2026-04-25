"use client"
import dynamic from "next/dynamic"

export const NLProvinceFoodbankHeatMapDynamic = dynamic(
  () =>
    import("./NLProvinceFoodbankHeatMap").then(
      (m) => m.NLProvinceFoodbankHeatMap,
    ),
  {
    ssr: false,
    loading: () => (
      <div
        className="border border-line bg-surface-2 rounded-[var(--radius-lg)] animate-pulse"
        style={{ height: "clamp(360px, 56vh, 560px)" }}
      />
    ),
  },
)
