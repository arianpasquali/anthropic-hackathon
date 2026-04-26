import type { MetadataRoute } from "next"
import { api } from "@/lib/api"

const BASE_URL =
  process.env.NEXT_PUBLIC_SITE_URL?.replace(/\/$/, "") ??
  "https://klimaatkracht.nl"

type Entry = MetadataRoute.Sitemap[number]

const STATIC_ENTRIES: Array<Pick<Entry, "url" | "changeFrequency" | "priority">> = [
  { url: "/", changeFrequency: "weekly", priority: 1.0 },
  { url: "/marketplace", changeFrequency: "daily", priority: 0.9 },
  { url: "/methodology", changeFrequency: "monthly", priority: 0.8 },
  { url: "/pricing", changeFrequency: "monthly", priority: 0.8 },
  { url: "/foodbanks", changeFrequency: "weekly", priority: 0.7 },
  { url: "/for-foodbanks", changeFrequency: "monthly", priority: 0.7 },
  { url: "/login", changeFrequency: "yearly", priority: 0.3 },
  { url: "/register", changeFrequency: "yearly", priority: 0.3 },
]

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date()

  const [banks, packages] = await Promise.all([
    api.listFoodbanks().catch(() => []),
    api.listPackages().catch(() => []),
  ])

  const staticUrls: MetadataRoute.Sitemap = STATIC_ENTRIES.map((e) => ({
    url: `${BASE_URL}${e.url}`,
    lastModified: now,
    changeFrequency: e.changeFrequency,
    priority: e.priority,
  }))

  const foodbankUrls: MetadataRoute.Sitemap = banks.map((b) => ({
    url: `${BASE_URL}/foodbanks/${b.slug}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: 0.7,
  }))

  const fundUrls: MetadataRoute.Sitemap = packages.map((p) => ({
    url: `${BASE_URL}/funds/${p.id}`,
    lastModified: now,
    changeFrequency: "weekly",
    priority: 0.8,
  }))

  return [...staticUrls, ...foodbankUrls, ...fundUrls]
}
