"use client"

import "leaflet/dist/leaflet.css"
import { useEffect, useMemo, useState } from "react"
import { GeoJSON, MapContainer, TileLayer } from "react-leaflet"
import type { Feature, FeatureCollection } from "geojson"
import type { CoverageRegion } from "@/lib/types"
import { formatPercent } from "@/lib/format"

const NL_CENTRE: [number, number] = [52.15, 5.4]

// Map every NL province (CBS naam) to one of our KK region keys.
// Used to color provinces by the buyer's allocation weight.
const PROVINCE_TO_REGION: Record<string, string> = {
  Groningen: "noord",
  Friesland: "noord",
  Fryslân: "noord",
  Drenthe: "noord",
  Overijssel: "oost",
  Gelderland: "oost",
  Flevoland: "oost",
  "Noord-Brabant": "zuidoost",
  Limburg: "zuidoost",
  Zeeland: "zuid",
  "Zuid-Holland": "west",
  "Noord-Holland": "randstad",
  Utrecht: "randstad",
}

const PROVINCE_GEOJSON_URL =
  "https://cartomap.github.io/nl/wgs84/provincie_2023.geojson"

export function NLProvinceHeatMap({
  regions,
  height = 380,
}: {
  regions: CoverageRegion[]
  height?: number
}) {
  const [geojson, setGeojson] = useState<FeatureCollection | null>(null)

  useEffect(() => {
    fetch(PROVINCE_GEOJSON_URL)
      .then((r) => (r.ok ? r.json() : Promise.reject(r.status)))
      .then(setGeojson)
      .catch(() => setGeojson(null))
  }, [])

  const weightByRegion = useMemo(() => {
    const m: Record<string, number> = {}
    for (const r of regions) m[r.region] = r.weight_pct
    return m
  }, [regions])

  // Force remount of GeoJSON layer when data changes (leaflet caches styling).
  const geoKey = useMemo(
    () => JSON.stringify(weightByRegion),
    [weightByRegion],
  )

  function styleFor(feature?: Feature) {
    const name = (feature?.properties?.statnaam ?? feature?.properties?.name) as
      | string
      | undefined
    const regionKey = name ? PROVINCE_TO_REGION[name] : undefined
    const weight = (regionKey ? weightByRegion[regionKey] : 0) ?? 0
    // Map [0..max] → opacity [0.05..0.85] for visibility
    const max = Math.max(0.0001, ...regions.map((r) => r.weight_pct))
    const opacity = weight === 0 ? 0.05 : 0.18 + (weight / max) * 0.62
    return {
      fillColor: "var(--emerald)",
      fillOpacity: opacity,
      color: "var(--emerald-deep)",
      weight: 0.7,
      opacity: 0.6,
    }
  }

  function onEach(feature: Feature, layer: import("leaflet").Layer) {
    const name = (feature?.properties?.statnaam ?? feature?.properties?.name) as
      | string
      | undefined
    if (!name) return
    const regionKey = PROVINCE_TO_REGION[name]
    const weight = regionKey ? weightByRegion[regionKey] ?? 0 : 0
    layer.bindTooltip(
      `<div style="font-family: var(--font-sans); font-size: 12px;">
        <strong>${name}</strong><br/>
        <span style="color: var(--text-muted)">region: ${regionKey ?? "—"}</span><br/>
        <span style="color: var(--text-muted)">weight: ${formatPercent(weight, 1)}</span>
      </div>`,
      { sticky: true, opacity: 0.95 },
    )
  }

  return (
    <div
      className="relative w-full overflow-hidden border border-line bg-surface-2"
      style={{ height }}
    >
      <MapContainer
        center={NL_CENTRE}
        zoom={7}
        minZoom={6}
        maxZoom={11}
        scrollWheelZoom={true}
        zoomControl={true}
        doubleClickZoom={true}
        style={{ height: "100%", width: "100%", background: "var(--surface-2)" }}
        attributionControl={false}
      >
        <TileLayer
          url="https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/grijs/EPSG:3857/{z}/{x}/{y}.png"
          attribution='Kaartgegevens © <a href="https://kadaster.nl">Kadaster</a>'
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
    </div>
  )
}
