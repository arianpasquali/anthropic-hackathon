"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { api, ApiError } from "@/lib/api"
import { formatEur, formatTCO2e } from "@/lib/format"
import type { PackageDetail } from "@/lib/types"

export function BuyPanel({ pkg }: { pkg: PackageDetail }) {
  const router = useRouter()
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onPurchase() {
    setBusy(true)
    setError(null)
    try {
      const sub = await api.checkout(pkg.id)
      router.push(`/funds/${pkg.id}/buy?subId=${sub.id}`)
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        router.push(`/login?next=/funds/${pkg.id}`)
      } else {
        setError(e instanceof Error ? e.message : "Something went wrong")
        setBusy(false)
      }
    }
  }

  return (
    <aside className="lg:sticky lg:top-20 self-start border border-line rounded-[var(--radius-lg)] bg-surface overflow-hidden">
      <div className="p-6 border-b border-line/60">
        <Badge variant="emerald" className="mb-4">
          Annual subscription
        </Badge>
        <div className="flex items-baseline gap-2">
          <span className="display tabular tracking-[-0.03em] leading-[0.95] text-[44px]">
            {formatEur(pkg.price_eur * 4)}
          </span>
          <span className="text-text-muted text-[13px]">/ year</span>
        </div>
        <p className="text-[12.5px] text-text-faint mt-1.5 tabular">
          {formatEur(pkg.price_eur)} per quarter · invoiced via Solvimon
        </p>
      </div>

      <dl className="p-6 grid grid-cols-2 gap-y-3 gap-x-6 border-b border-line/60 text-[13.5px]">
        <dt className="text-text-muted">Climate contribution</dt>
        <dd className="tabular text-right">{formatTCO2e(pkg.co2e_claim_kg / 1000)} / yr</dd>
        <dt className="text-text-muted">Top foodbanks</dt>
        <dd className="tabular text-right">{pkg.top_n}</dd>
        <dt className="text-text-muted">Profile</dt>
        <dd className="text-right capitalize">{pkg.impact_profile.replace("_", " ")}</dd>
      </dl>

      <div className="p-6 flex flex-col gap-3">
        <Button onClick={onPurchase} disabled={busy} size="lg">
          {busy ? "Preparing checkout…" : "Purchase →"}
        </Button>
        <p className="text-[12px] text-text-faint leading-relaxed">
          You will receive an annual ESRS E5 + S3 contribution disclosure with full
          FRAME workings and source citations. Climate contribution, not offsetting.
        </p>
        {error ? (
          <p className="text-[12px] text-warning">{error}</p>
        ) : null}
      </div>
    </aside>
  )
}
