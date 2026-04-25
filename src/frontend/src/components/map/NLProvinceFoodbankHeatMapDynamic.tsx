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
        style={{
          height: 460,
          background: "#0c1929",
          borderRadius: 14,
          opacity: 0.6,
        }}
      />
    ),
  },
)
