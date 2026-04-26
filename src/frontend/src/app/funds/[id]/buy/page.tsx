"use client"

import { Suspense, useState, use } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/Button"
import { Input, Label } from "@/components/ui/Input"
import { Badge } from "@/components/ui/Badge"
import { api, ApiError } from "@/lib/api"

type Params = { id: string }

export default function BuyPage({ params }: { params: Promise<Params> }) {
  const { id } = use(params)
  return (
    <Suspense>
      <BuyForm fundId={id} />
    </Suspense>
  )
}

function BuyForm({ fundId }: { fundId: string }) {
  const router = useRouter()
  const search = useSearchParams()
  const subId = search.get("subId")

  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!subId) {
      setError("Missing subscription id — restart from the fund page.")
      return
    }
    setBusy(true)
    setError(null)
    try {
      const sub = await api.pay(subId)
      router.push(`/funds/${fundId}/buy/confirmed?subId=${sub.id}`)
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        router.push(`/login?next=/funds/${fundId}`)
        return
      }
      setError("Payment failed. Try again.")
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-[820px] px-6 pt-12 pb-24">
      <Link href={`/funds/${fundId}`} className="text-[13px] text-text-muted hover:text-text">
        ← Back to fund
      </Link>
      <p className="eyebrow mt-6">Mock checkout · Solvimon sandbox</p>
      <h1 className="display text-5xl mt-4 tracking-[-0.025em] max-w-[16ch]">
        Confirm your annual subscription.
      </h1>
      <p className="text-text-muted text-[14.5px] mt-5 max-w-[52ch] leading-relaxed">
        This is a sandbox checkout. No card is charged; submitting the form marks the
        subscription as paid and triggers the allocation engine on the backend.
      </p>

      <form onSubmit={onSubmit} className="mt-12 grid md:grid-cols-[1.4fr_1fr] gap-x-10 gap-y-6 items-start">
        <div className="flex flex-col gap-5 border border-line rounded-[var(--radius-lg)] bg-surface p-7">
          <div className="flex items-center justify-between">
            <p className="eyebrow">Billing details</p>
            <Badge variant="default">Solvimon</Badge>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <Field label="Card holder" defaultValue="Demo Acme N.V." />
            <Field label="VAT ID" defaultValue="NL12345678B01" />
            <Field label="Card number" defaultValue="4242 4242 4242 4242" />
            <Field label="Expiry" defaultValue="12 / 28" />
            <Field label="CVC" defaultValue="123" />
            <Field label="Country" defaultValue="Netherlands" />
          </div>
          {error ? <p className="text-[13px] text-warning">{error}</p> : null}
          <Button type="submit" disabled={busy} size="lg">
            {busy ? "Processing payment…" : "Pay & confirm subscription →"}
          </Button>
        </div>

        <aside className="border border-line rounded-[var(--radius-lg)] bg-surface-2 p-6">
          <p className="eyebrow">Subscription</p>
          <p className="text-[13px] text-text-muted mt-2 tabular">id: {subId ?? "—"}</p>
          <ul className="flex flex-col gap-2 mt-5 text-[13.5px]">
            <li className="flex justify-between"><span className="text-text-muted">Cadence</span><span>Quarterly</span></li>
            <li className="flex justify-between"><span className="text-text-muted">Cancel</span><span>Any quarter</span></li>
            <li className="flex justify-between"><span className="text-text-muted">Reporting</span><span>ESRS E5+S3</span></li>
            <li className="flex justify-between"><span className="text-text-muted">Provider</span><span>Solvimon</span></li>
          </ul>
        </aside>
      </form>
    </div>
  )
}

function Field({ label, defaultValue }: { label: string; defaultValue: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label>{label}</Label>
      <Input defaultValue={defaultValue} />
    </div>
  )
}
