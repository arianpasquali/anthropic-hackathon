import Link from "next/link"
import { Badge } from "@/components/ui/Badge"
import type { Package } from "@/lib/types"
import { formatEur, formatNumber, formatTCO2e } from "@/lib/format"

const PROFILE_LABELS: Record<string, string> = {
  co2_focus: "CO₂ focus",
  social_focus: "Social focus",
  balanced: "Balanced",
}

export function FundCard({ pkg, featured = false }: { pkg: Package; featured?: boolean }) {
  return (
    <Link
      href={`/funds/${pkg.id}`}
      className={`group flex flex-col bg-surface border border-line hover:border-line-strong rounded-[var(--radius-lg)] overflow-hidden transition-colors ${
        featured ? "ring-1 ring-emerald" : ""
      }`}
    >
      <div className="p-7 flex-1 flex flex-col gap-5">
        <div className="flex items-center justify-between">
          <Badge variant="default">{PROFILE_LABELS[pkg.impact_profile] ?? pkg.impact_profile}</Badge>
          {featured ? <Badge variant="emerald">Featured</Badge> : null}
        </div>

        <h3 className="display text-3xl tracking-[-0.02em]">{pkg.name}</h3>
        {pkg.description ? (
          <p className="text-[13.5px] text-text-muted leading-relaxed max-w-[42ch]">
            {pkg.description}
          </p>
        ) : null}

        <div className="grid grid-cols-2 gap-y-3 gap-x-6 mt-2 pt-5 border-t border-line/60">
          <Stat label="Price" value={formatEur(pkg.price_eur)} />
          <Stat label="Avoided" value={formatTCO2e(pkg.co2e_claim_kg / 1000)} />
          <Stat label="Top banks" value={`${formatNumber(pkg.top_n)}`} />
          <Stat label="Region" value={pkg.region.toUpperCase()} />
        </div>
      </div>

      <div className="px-7 py-4 bg-surface-2 border-t border-line/60 flex items-center justify-between">
        <span className="text-[13px] text-text-muted">FRAME · ESRS E5+S3 · contribution</span>
        <span className="text-[13px] font-medium text-emerald group-hover:translate-x-0.5 transition-transform">
          View fund →
        </span>
      </div>
    </Link>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="eyebrow text-[10px]">{label}</span>
      <span className="text-[15px] font-medium tabular text-text">{value}</span>
    </div>
  )
}
