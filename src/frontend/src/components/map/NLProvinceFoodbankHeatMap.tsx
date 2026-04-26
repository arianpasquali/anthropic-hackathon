"use client"

import "leaflet/dist/leaflet.css"
import { useEffect, useMemo, useState } from "react"
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet"
import type { Feature, FeatureCollection, Polygon, MultiPolygon } from "geojson"
import type { Bank } from "@/lib/types"

const NL_CENTRE: [number, number] = [52.15, 5.4]
const PROVINCE_GEOJSON_URL = "/geo/nl-provinces.json"

// Ray-casting point-in-polygon. ring is [[lng,lat], ...]
function pointInRing(lng: number, lat: number, ring: number[][]): boolean {
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0], yi = ring[i][1]
    const xj = ring[j][0], yj = ring[j][1]
    const intersect =
      yi > lat !== yj > lat &&
      lng < ((xj - xi) * (lat - yi)) / (yj - yi || 1e-12) + xi
    if (intersect) inside = !inside
  }
  return inside
}

function pointInFeature(lng: number, lat: number, feature: Feature): boolean {
  const geom = feature.geometry
  if (!geom) return false
  if (geom.type === "Polygon") {
    const poly = geom as Polygon
    const [outer, ...holes] = poly.coordinates
    if (!pointInRing(lng, lat, outer)) return false
    for (const h of holes) if (pointInRing(lng, lat, h)) return false
    return true
  }
  if (geom.type === "MultiPolygon") {
    const mp = geom as MultiPolygon
    for (const poly of mp.coordinates) {
      const [outer, ...holes] = poly
      if (pointInRing(lng, lat, outer)) {
        let inHole = false
        for (const h of holes) if (pointInRing(lng, lat, h)) { inHole = true; break }
        if (!inHole) return true
      }
    }
  }
  return false
}

interface Props {
  banks: Bank[]
  height?: number | string
  /** Bank-count (default, used on landing) or CO₂e baseline (used on marketplace
   *  to differentiate the two maps and emphasise fund-eligible capacity). */
  colorBy?: "count" | "co2e"
  /** Total fund count in the catalogue. When provided, the tooltip surfaces
   *  "X of N funds reach this province" — every province with ≥1 bank reaches
   *  every fund (top_n caps allocation, not eligibility), so the count equals
   *  N when banks > 0. */
  totalFunds?: number
}

export function NLProvinceFoodbankHeatMap({
  banks,
  height = "clamp(360px, 56vh, 560px)",
  colorBy = "count",
  totalFunds,
}: Props) {
  const [geojson, setGeojson] = useState<FeatureCollection | null>(null)

  useEffect(() => {
    fetch(PROVINCE_GEOJSON_URL)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setGeojson)
      .catch(() => setGeojson(null))
  }, [])

  const statsByProvince = useMemo(() => {
    if (!geojson) return {} as Record<string, { count: number; tco2e: number }>
    const stats: Record<string, { count: number; tco2e: number }> = {}
    const banksWithCoords = banks.filter((b) => b.lat != null && b.lng != null)
    for (const b of banksWithCoords) {
      for (const f of geojson.features) {
        const name = (f.properties?.statnaam ?? f.properties?.name) as string | undefined
        if (!name) continue
        if (pointInFeature(b.lng!, b.lat!, f)) {
          const cur = stats[name] ?? { count: 0, tco2e: 0 }
          cur.count += 1
          cur.tco2e += b.annual_tco2e ?? 0
          stats[name] = cur
          break
        }
      }
    }
    return stats
  }, [geojson, banks])

  const maxValue = useMemo(() => {
    const values = Object.values(statsByProvince).map((s) =>
      colorBy === "co2e" ? s.tco2e : s.count,
    )
    return Math.max(1, ...values)
  }, [statsByProvince, colorBy])
  const geoKey = useMemo(
    () => `${colorBy}:${JSON.stringify(statsByProvince)}`,
    [statsByProvince, colorBy],
  )

  // Resolve OKLCH brand emerald to a static rgb() at mount, since Leaflet/Canvas
  // ignore CSS custom properties in the GeoJSON style fn.
  const [emeraldRGB, setEmeraldRGB] = useState<string>("rgb(72,140,99)")
  useEffect(() => {
    const probe = document.createElement("span")
    probe.style.color = "var(--emerald)"
    document.body.appendChild(probe)
    const c = getComputedStyle(probe).color
    document.body.removeChild(probe)
    if (c) setEmeraldRGB(c)
  }, [])

  function styleFor(feature?: Feature) {
    const name = (feature?.properties?.statnaam ?? feature?.properties?.name) as string | undefined
    const stat = name ? statsByProvince[name] : undefined
    const value = stat ? (colorBy === "co2e" ? stat.tco2e : stat.count) : 0
    const opacity = value === 0 ? 0.05 : 0.15 + (value / maxValue) * 0.55
    return {
      fillColor: emeraldRGB,
      fillOpacity: opacity,
      color: emeraldRGB,
      weight: 0.6,
      opacity: 0.5,
    }
  }

  function onEach(feature: Feature, layer: import("leaflet").Layer) {
    const name = (feature?.properties?.statnaam ?? feature?.properties?.name) as string | undefined
    if (!name) return
    const stat = statsByProvince[name] ?? { count: 0, tco2e: 0 }
    const tco2eFmt = stat.tco2e >= 1000
      ? `${(stat.tco2e / 1000).toFixed(1)}k tCO₂e/yr`
      : `${stat.tco2e.toFixed(0)} tCO₂e/yr`
    const fundsLine =
      typeof totalFunds === "number"
        ? stat.count > 0
          ? `<span>${totalFunds} of ${totalFunds} funds reach here</span>`
          : `<span>No funds reach here yet</span>`
        : ""
    layer.bindTooltip(
      `<div class="kk-province-tip">
        <strong>${name}</strong>
        <span>${stat.count} foodbank${stat.count === 1 ? "" : "s"} · ${tco2eFmt}</span>
        ${fundsLine}
      </div>`,
      { sticky: true, opacity: 1, className: "kk-leaflet-tip" },
    )
  }

  return (
    <div
      className="relative w-full overflow-hidden border border-line bg-surface-2 rounded-[var(--radius-lg)]"
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
          url="https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/grijs/EPSG:3857/{z}/{x}/{y}.png"
          attribution='Kaartgegevens &copy; <a href="https://kadaster.nl">Kadaster</a>'
        />
        {geojson ? (
          <GeoJSON
            key={geoKey + emeraldRGB}
            data={geojson}
            style={styleFor as never}
            onEachFeature={onEach}
          />
        ) : null}
      </MapContainer>
    </div>
  )
}
