"use client"
import dynamic from "next/dynamic"

export const NLMapDynamic = dynamic(() => import("./NLMap").then((m) => m.NLMap), {
  ssr: false,
  loading: () => (
    <div className="border border-line bg-surface-2 animate-pulse" style={{ height: 320 }} />
  ),
})
