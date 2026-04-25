"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Badge } from "@/components/ui/Badge"
import { StatCard } from "@/components/dashboard/StatCard"
import { UploadWidget } from "@/components/dashboard/UploadWidget"
import { CategoryMixBars } from "@/components/foodbanks/CategoryMixBars"
import { api } from "@/lib/api"
import { formatKg, formatNumber, formatTCO2e } from "@/lib/format"
import type { Bank, User } from "@/lib/types"

export default function FoodbankDashboardPage() {
  const [me, setMe] = useState<User | null>(null)
  const [bank, setBank] = useState<Bank | null>(null)
  const [revealed, setRevealed] = useState(false)

  useEffect(() => {
    api.me().then(setMe).catch(() => null)
    // demo: show Amsterdam profile as the operator's bank
    api.getFoodbank("amsterdam").then(setBank).catch(() => null)
  }, [])

  return (
    <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24">
      <header className="pb-10 border-b border-line">
        <p className="eyebrow">Food bank dashboard</p>
        <h1 className="display text-5xl mt-3 tracking-[-0.025em]">
          {bank?.name ?? "Voedselbank Amsterdam"}
        </h1>
        <p className="text-text-muted mt-3 text-[14.5px]">
          <Badge variant="default" className="mr-2">Food bank operator</Badge>
          <Badge variant="outline">{bank?.region ?? "Noord-Holland"}</Badge>
          {me?.email ? (
            <span className="ml-3 tabular text-[13px] text-text-faint">{me.email}</span>
          ) : null}
        </p>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-5 mt-10">
        <StatCard label="Funding received" value="€0" hint="this quarter" />
        <StatCard label="Active sponsors" value="0" hint="quarterly subscriptions" />
        <StatCard
          label="Annual data"
          value={revealed ? "Uploaded" : "Not uploaded"}
          hint={revealed ? "extracted by Claude" : "drop a PDF below"}
          emphasis={revealed}
        />
      </section>

      <section className="grid lg:grid-cols-[1.2fr_1fr] gap-x-12 gap-y-10 mt-12 items-start">
        <UploadWidget onComplete={() => setRevealed(true)} />

        <aside className="border border-line rounded-[var(--radius-lg)] bg-surface-2 p-6">
          <p className="eyebrow">How it works</p>
          <ol className="mt-3 flex flex-col gap-3 text-[13.5px]">
            {[
              "Drop your annual report PDF (one per year).",
              "Claude extracts food volumes, categories, and people served.",
              "Each field is tagged with its source — extracted, inferred, or computed.",
              "FRAME computes your CO₂e baseline and weighted emission factor.",
              "You appear in the marketplace; corporates can sponsor your operations.",
            ].map((t, i) => (
              <li key={t} className="flex items-start gap-3">
                <span className="tabular text-text-faint w-5 shrink-0">0{i + 1}</span>
                <span className="text-text">{t}</span>
              </li>
            ))}
          </ol>
        </aside>
      </section>

      {revealed && bank ? (
        <section className="mt-16 pt-10 border-t border-line">
          <p className="eyebrow">Your impact, computed</p>
          <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[24ch]">
            Annual baseline and category breakdown.
          </h2>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-5 mt-8">
            <StatCard label="CO₂e" value={bank.annual_tco2e ? formatTCO2e(bank.annual_tco2e) : "—"} hint="per year" emphasis />
            <StatCard label="Rescued" value={bank.annual_kg_rescued ? formatKg(bank.annual_kg_rescued) : "—"} hint="kg / yr" />
            <StatCard label="Households / wk" value={bank.households_weekly ? formatNumber(bank.households_weekly) : "—"} hint="weekly" />
            <StatCard label="Individuals" value={bank.people_served ? formatNumber(bank.people_served) : "—"} hint="annual" />
          </div>

          {bank.category_mix && bank.annual_kg_rescued ? (
            <div className="mt-10 grid lg:grid-cols-[1.4fr_1fr] gap-x-10 gap-y-6 items-start">
              <div className="min-w-0">
                <CategoryMixBars mix={bank.category_mix} totalKg={bank.annual_kg_rescued} />
              </div>
              <div>
                <p className="eyebrow">Source legend</p>
                <ul className="mt-3 flex flex-col gap-2 text-[13.5px]">
                  <li className="flex items-center gap-2"><Badge variant="emerald">extracted</Badge><span className="text-text-muted">directly from PDF</span></li>
                  <li className="flex items-center gap-2"><Badge variant="default">inferred</Badge><span className="text-text-muted">national or category averages</span></li>
                  <li className="flex items-center gap-2"><Badge variant="outline">computed</Badge><span className="text-text-muted">derived from other fields</span></li>
                </ul>
                <Link
                  href={`/foodbanks/${bank.slug}`}
                  className="mt-6 inline-block text-[13px] text-emerald hover:underline"
                >
                  View public profile →
                </Link>
              </div>
            </div>
          ) : null}
        </section>
      ) : null}
    </div>
  )
}
