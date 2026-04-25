import type { Bank } from "@/lib/types"
import provinces from "@/lib/geo/nl-provinces.json"
import type { Feature, FeatureCollection, Polygon, MultiPolygon } from "geojson"

const PROV = provinces as unknown as FeatureCollection

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

function pointInFeature(lng: number, lat: number, f: Feature): boolean {
  const g = f.geometry
  if (!g) return false
  if (g.type === "Polygon") {
    const [outer, ...holes] = (g as Polygon).coordinates
    if (!pointInRing(lng, lat, outer)) return false
    for (const h of holes) if (pointInRing(lng, lat, h)) return false
    return true
  }
  if (g.type === "MultiPolygon") {
    for (const poly of (g as MultiPolygon).coordinates) {
      const [outer, ...holes] = poly
      if (pointInRing(lng, lat, outer)) {
        for (const h of holes) if (pointInRing(lng, lat, h)) return false
        return true
      }
    }
  }
  return false
}

function countsFor(banks: Bank[]): Array<{ name: string; count: number }> {
  const counts: Record<string, number> = {}
  for (const f of PROV.features) {
    const name = (f.properties?.statnaam ?? f.properties?.name) as string | undefined
    if (name) counts[name] = 0
  }
  for (const b of banks) {
    if (b.lat == null || b.lng == null) continue
    for (const f of PROV.features) {
      const name = (f.properties?.statnaam ?? f.properties?.name) as string | undefined
      if (!name) continue
      if (pointInFeature(b.lng, b.lat, f)) {
        counts[name] = (counts[name] ?? 0) + 1
        break
      }
    }
  }
  return Object.entries(counts)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count || a.name.localeCompare(b.name))
}

export function ProvinceFoodbankList({ banks }: { banks: Bank[] }) {
  const rows = countsFor(banks)
  const max = Math.max(1, ...rows.map((r) => r.count))
  return (
    <ul className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1.5 text-[12.5px]">
      {rows.map((r) => (
        <li
          key={r.name}
          className="flex items-center justify-between border-b border-line/60 pb-1.5"
        >
          <span className="text-text-muted">{r.name}</span>
          <span
            className="tabular text-text"
            style={{ opacity: r.count === 0 ? 0.45 : 0.7 + (r.count / max) * 0.3 }}
          >
            {r.count}
          </span>
        </li>
      ))}
    </ul>
  )
}
