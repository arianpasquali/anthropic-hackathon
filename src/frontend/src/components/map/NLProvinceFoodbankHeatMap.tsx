"use client"

import "leaflet/dist/leaflet.css"
import { useEffect, useMemo, useState } from "react"
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet"
import type { Feature, FeatureCollection, Polygon, MultiPolygon } from "geojson"
import type { Bank } from "@/lib/types"

const NL_CENTRE: [number, number] = [52.15, 5.4]

const PROVINCE_GEOJSON_URL =
  "https://cartomap.github.io/nl/wgs84/provincie_2023.geojson"

// Ray-casting point-in-polygon. ring is [[lng,lat], ...]
function pointInRing(lng: number, lat: number, ring: number[][]): boolean {
  let inside = false
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const xi = ring[i][0],
      yi = ring[i][1]
    const xj = ring[j][0],
      yj = ring[j][1]
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

export function NLProvinceFoodbankHeatMap({ banks, height = 600 }: Props) {
  const [geojson, setGeojson] = useState<FeatureCollection | null>(null)

  useEffect(() => {
    fetch(PROVINCE_GEOJSON_URL)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setGeojson)
      .catch(() => setGeojson(null))
  }, [])

  // Count banks per province (statnaam)
  const countsByProvince = useMemo(() => {
    if (!geojson) return {} as Record<string, number>
    const counts: Record<string, number> = {}
    const features = geojson.features
    const banksWithCoords = banks.filter((b) => b.lat != null && b.lng != null)
    for (const b of banksWithCoords) {
      for (const f of features) {
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
  const totalCounted = Object.values(countsByProvince).reduce((s, n) => s + n, 0)

  const geoKey = useMemo(() => JSON.stringify(countsByProvince), [countsByProvince])

  function styleFor(feature?: Feature) {
    const name = (feature?.properties?.statnaam ?? feature?.properties?.name) as string | undefined
    const count = name ? countsByProvince[name] ?? 0 : 0
    const opacity = count === 0 ? 0.06 : 0.2 + (count / maxCount) * 0.7
    return {
      fillColor: "#10b981",
      fillOpacity: opacity,
      color: "#1a3a52",
      weight: 0.8,
      opacity: 0.7,
    }
  }

  function onEach(feature: Feature, layer: import("leaflet").Layer) {
    const name = (feature?.properties?.statnaam ?? feature?.properties?.name) as string | undefined
    if (!name) return
    const count = countsByProvince[name] ?? 0
    layer.bindTooltip(
      `<div style="font-family: var(--font-sans); font-size: 12px; padding: 2px 4px;">
        <strong style="color: #fff;">${name}</strong><br/>
        <span style="color: #10b981; font-weight: 600;">${count}</span>
        <span style="color: #94a3b8;"> foodbank${count === 1 ? "" : "s"}</span>
      </div>`,
      { sticky: true, opacity: 0.96, className: "kk-dark-tip" },
    )
  }

  return (
    <div
      className="relative w-full overflow-hidden rounded-[14px]"
      style={{
        height,
        background: "#0c1929",
        boxShadow: "0 8px 32px rgba(0,0,0,0.4)",
      }}
    >
      <MapContainer
        center={NL_CENTRE}
        zoom={7}
        minZoom={6}
        maxZoom={12}
        scrollWheelZoom={true}
        zoomControl={true}
        doubleClickZoom={true}
        style={{ height: "100%", width: "100%", background: "#0c1929" }}
        attributionControl={false}
      >
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_nolabels/{z}/{x}/{y}.png"
          subdomains={["a", "b", "c", "d"]}
          attribution='&copy; <a href="https://carto.com/attributions">CARTO</a>'
        />
        {geojson ? (
          <GeoJSON
            key={geoKey}
            data={geojson}
            style={styleFor as never}
            onEachFeature={onEach}
          />
        ) : null}
      </MapContainer>

      {/* Stats overlay */}
      <div
        style={{
          position: "absolute",
          top: 16,
          left: 16,
          background: "rgba(12,25,41,0.85)",
          backdropFilter: "blur(10px)",
          border: "1px solid rgba(255,255,255,0.1)",
          borderRadius: 10,
          padding: "12px 18px",
          display: "flex",
          gap: 22,
          zIndex: 500,
        }}
      >
        <Stat label="Provinces covered" value={String(Object.values(countsByProvince).filter((n) => n > 0).length)} />
        <Stat label="Foodbanks mapped" value={String(totalCounted)} accent />
      </div>

      {/* Legend */}
      <div
        style={{
          position: "absolute",
          bottom: 16,
          right: 16,
          background: "rgba(12,25,41,0.82)",
          backdropFilter: "blur(8px)",
          border: "1px solid rgba(255,255,255,0.08)",
          borderRadius: 8,
          padding: "10px 14px",
          zIndex: 500,
          display: "flex",
          alignItems: "center",
          gap: 10,
        }}
      >
        <span style={{ fontSize: 10, color: "#94a3b8", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em" }}>
          Banks / province
        </span>
        <div style={{ display: "flex", height: 10, width: 90, borderRadius: 3, overflow: "hidden" }}>
          {[0.2, 0.35, 0.5, 0.65, 0.8, 0.92].map((o, i) => (
            <div key={i} style={{ flex: 1, background: `rgba(16,185,129,${o})` }} />
          ))}
        </div>
        <span style={{ fontSize: 10, color: "#94a3b8", fontVariantNumeric: "tabular-nums" }}>
          0 → {maxCount}
        </span>
      </div>
    </div>
  )
}

function Stat({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div>
      <div style={{ fontSize: 9, color: "#6b8fa8", textTransform: "uppercase", letterSpacing: "0.06em", fontWeight: 700, marginBottom: 2 }}>
        {label}
      </div>
      <div style={{ fontSize: 20, fontWeight: 700, color: accent ? "#10b981" : "#fff", fontVariantNumeric: "tabular-nums", lineHeight: 1.1 }}>
        {value}
      </div>
    </div>
  )
}
