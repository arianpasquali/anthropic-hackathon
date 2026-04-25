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
  height?: number
}

export function NLProvinceFoodbankHeatMap({ banks, height = 480 }: Props) {
  const [geojson, setGeojson] = useState<FeatureCollection | null>(null)

  useEffect(() => {
    fetch(PROVINCE_GEOJSON_URL)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setGeojson)
      .catch(() => setGeojson(null))
  }, [])

  const countsByProvince = useMemo(() => {
    if (!geojson) return {} as Record<string, number>
    const counts: Record<string, number> = {}
    const banksWithCoords = banks.filter((b) => b.lat != null && b.lng != null)
    for (const b of banksWithCoords) {
      for (const f of geojson.features) {
        const name = (f.properties?.statnaam ?? f.properties?.name) as string | undefined
        if (!name) continue
        if (pointInFeature(b.lng!, b.lat!, f)) {
          counts[name] = (counts[name] ?? 0) + 1
          break
        }
      }
    }
    return counts
  }, [geojson, banks])

  const maxCount = Math.max(1, ...Object.values(countsByProvince))
  const geoKey = useMemo(() => JSON.stringify(countsByProvince), [countsByProvince])

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
    const count = name ? countsByProvince[name] ?? 0 : 0
    const opacity = count === 0 ? 0.05 : 0.15 + (count / maxCount) * 0.55
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
    const count = countsByProvince[name] ?? 0
    layer.bindTooltip(
      `<div class="kk-province-tip">
        <strong>${name}</strong>
        <span>${count} foodbank${count === 1 ? "" : "s"}</span>
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
