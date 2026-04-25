"use client"

import "leaflet/dist/leaflet.css"
import { useEffect } from "react"
import { MapContainer, TileLayer, CircleMarker, Tooltip, Popup } from "react-leaflet"
import type { Bank } from "@/lib/types"
import { formatNumber, formatTCO2e } from "@/lib/format"
import Link from "next/link"

// Centre of the Netherlands
const NL_CENTRE: [number, number] = [52.15, 5.4]

export interface NLMapProps {
  banks: Bank[]
  height?: number
  highlightSlug?: string | null
  showLinks?: boolean
}

export function NLMap({ banks, height = 320, highlightSlug = null, showLinks = true }: NLMapProps) {
  // Disable scroll wheel zoom by default — feels less aggressive on long pages.
  useEffect(() => {
    // ensures leaflet recalculates size after CSS load
    const id = setTimeout(() => window.dispatchEvent(new Event("resize")), 80)
    return () => clearTimeout(id)
  }, [])

  return (
    <div
      className="relative w-full overflow-hidden border border-line bg-surface-2"
      style={{ height }}
    >
      <MapContainer
        center={NL_CENTRE}
        zoom={7}
        scrollWheelZoom={false}
        zoomControl={false}
        style={{ height: "100%", width: "100%", background: "var(--surface-2)" }}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png"
          subdomains={["a", "b", "c", "d"]}
        />
        {banks
          .filter((b) => b.lat != null && b.lng != null)
          .map((b) => {
            const isHi = highlightSlug === b.slug
            const radius = isHi ? 11 : Math.max(6, Math.min(14, Math.sqrt((b.annual_tco2e ?? 100) / 60)))
            return (
              <CircleMarker
                key={b.id}
                center={[b.lat as number, b.lng as number]}
                radius={radius}
                pathOptions={{
                  color: isHi ? "var(--emerald-deep)" : "var(--emerald)",
                  fillColor: "var(--emerald)",
                  fillOpacity: isHi ? 0.85 : 0.55,
                  weight: 2,
                }}
              >
                <Tooltip direction="top" offset={[0, -6]} opacity={0.95} permanent={false}>
                  <span className="text-[12px] font-medium">{b.name}</span>
                </Tooltip>
                <Popup>
                  <div className="font-sans text-[13px] min-w-[160px]">
                    <div className="font-medium text-text">{b.name}</div>
                    <div className="text-text-muted text-[12px]">{b.region}</div>
                    {b.annual_tco2e ? (
                      <div className="mt-1.5 tabular text-[12px]">
                        {formatTCO2e(b.annual_tco2e)} · {formatNumber(b.annual_kg_rescued ?? 0 / 1000)}t rescued
                      </div>
                    ) : null}
                    {showLinks ? (
                      <Link
                        href={`/foodbanks/${b.slug}`}
                        className="text-emerald text-[12px] mt-2 inline-block hover:underline"
                      >
                        View profile →
                      </Link>
                    ) : null}
                  </div>
                </Popup>
              </CircleMarker>
            )
          })}
      </MapContainer>
    </div>
  )
}
