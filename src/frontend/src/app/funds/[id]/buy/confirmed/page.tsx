"use client"

import { Suspense, use, useEffect, useState } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Button } from "@/components/ui/Button"
import { Badge } from "@/components/ui/Badge"
import { api } from "@/lib/api"
import { formatEur, formatNumber, formatTCO2e } from "@/lib/format"
import type { SubscriptionDetail } from "@/lib/types"

type Params = { id: string }

export default function ConfirmedPage({ params }: { params: Promise<Params> }) {
  const { id } = use(params)
  return (
    <Suspense>
      <ConfirmedView fundId={id} />
    </Suspense>
  )
}

function ConfirmedView({ fundId }: { fundId: string }) {
  const search = useSearchParams()
  const subId = search.get("subId")
  const [detail, setDetail] = useState<SubscriptionDetail | null>(null)

  useEffect(() => {
    if (!subId) return
    api.getSubscriptionDetail(subId).then(setDetail).catch(() => setDetail(null))
  }, [subId])

  return (
    <div className="mx-auto max-w-[1100px] px-6 pt-12 pb-24">
      <Badge variant="emerald" className="mb-5">Subscription confirmed</Badge>
      <h1 className="display text-5xl md:text-6xl tracking-[-0.025em] max-w-[18ch]">
        Welcome aboard.{" "}
        <span className="display-italic text-emerald-deep">The allocation is live.</span>
      </h1>
      <p className="mt-6 text-text-muted text-[15px] max-w-[58ch] leading-relaxed">
        Your subscription has been recorded. The allocation engine has distributed your
        purchase across the top food banks per your fund profile, and your CSR report is
        ready to be generated on demand.
      </p>

      {detail ? (
        <div className="grid sm:grid-cols-3 gap-6 mt-12 border-y border-line py-8">
          <Stat label="Avoided" value={formatTCO2e(detail.total_co2e_kg / 1000)} />
          <Stat label="Banks funded" value={formatNumber(detail.allocations.length)} />
          <Stat label="Invested" value={formatEur(detail.amount_eur)} />
        </div>
      ) : null}

      <div className="mt-10 flex gap-4 flex-wrap">
        <Button asChild={false}>
          <Link href="/dashboard/corporate">Open dashboard →</Link>
        </Button>
        <Link
          href={`/funds/${fundId}`}
          className="border border-line h-10 px-4 inline-flex items-center hover:bg-surface-2 text-[14px]"
        >
          Back to fund
        </Link>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="eyebrow">{label}</span>
      <span className="display tabular text-3xl md:text-4xl">{value}</span>
    </div>
  )
}
