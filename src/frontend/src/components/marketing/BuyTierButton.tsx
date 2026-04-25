"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { api, ApiError } from "@/lib/api"
import type { ImpactProfile, Package } from "@/lib/types"

export function BuyTierButton({
  profile,
  label,
  popular = false,
}: {
  profile: ImpactProfile
  label: string
  popular?: boolean
}) {
  const router = useRouter()
  const [pkg, setPkg] = useState<Package | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    api
      .listPackages(profile)
      .then((list) => setPkg(list[0] ?? null))
      .catch(() => setPkg(null))
  }, [profile])

  async function onBuy() {
    if (!pkg) {
      router.push("/marketplace")
      return
    }
    setBusy(true)
    setError(null)
    try {
      const sub = await api.checkout(pkg.id)
      router.push(`/funds/${pkg.id}/buy?subId=${sub.id}`)
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        router.push(`/login?next=/funds/${pkg.id}/buy`)
        return
      }
      setError("Could not start checkout.")
      setBusy(false)
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={onBuy}
        disabled={busy}
        className={`block w-full text-center py-3 rounded-[var(--radius)] text-[14px] font-medium transition-colors disabled:opacity-60 ${
          popular
            ? "bg-emerald text-text-on-emerald hover:bg-emerald-deep"
            : "bg-surface-2 text-text border border-line hover:bg-emerald-soft hover:border-emerald"
        }`}
      >
        {busy ? "Starting checkout…" : label}
      </button>
      {error ? (
        <p className="mt-2 text-[12px] text-warning text-center">{error}</p>
      ) : null}
    </>
  )
}
