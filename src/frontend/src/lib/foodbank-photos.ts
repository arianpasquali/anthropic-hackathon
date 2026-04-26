/**
 * Slug-to-photo map for foodbank profile heroes. Verified Unsplash CDN URLs
 * (free for commercial use, no attribution required per Unsplash License).
 *
 * Strategy:
 *   - Cities with a verified location-specific photo render that.
 *   - Anything else falls back to a generic Dutch operations / civic shot
 *     so the layout never breaks when a new bank is ingested.
 *
 * To extend: paste a fresh `https://images.unsplash.com/photo-...` URL keyed
 * to the bank slug. Treatment + scrim is applied page-side via `kk-photo-hero`.
 */
const CITY_PHOTOS: Record<string, string> = {
  amsterdam: "https://images.unsplash.com/photo-1753810809240-a28f725d3328",
  rotterdam: "https://images.unsplash.com/photo-1597224646250-fadbb825dcf8",
  utrecht: "https://images.unsplash.com/photo-1744233291331-60d717f651f0",
  "den-haag": "https://images.unsplash.com/photo-1665302478277-8a7f22f80853",
}

const FALLBACK_PHOTO =
  "https://images.unsplash.com/photo-1754835143820-bcf20e2e1a35"

export function foodbankHeroPhoto(slug: string): string {
  const base = CITY_PHOTOS[slug] ?? FALLBACK_PHOTO
  // Append responsive params if not already present so each photo loads at
  // hero resolution without being huge.
  return base.includes("?")
    ? base
    : `${base}?auto=format&fit=crop&w=2400&q=80`
}
