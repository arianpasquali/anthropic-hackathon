"use client"

import { useMemo, useState } from "react"
import { fmtInt, fmtEur } from "@/lib/impact-types"

interface SupplyCap {
  max_packages_nl: number
  max_funds_eur: number
  max_tco2e: number
  max_adoption_pct: number
  explanation: string
}

interface Props {
  supplyCap: SupplyCap
  packageEur: number
  packageTco2e: number
  totalCorporates: number
  vbnBudget: number
  vbnBudgetSourceLabel: string
  vbnBudgetSourceUrl: string
}

function demandAt(
  pct: number,
  totalCorporates: number,
  packageEur: number,
  packageTco2e: number,
) {
  const companies = Math.round((pct / 100) * totalCorporates)
  return {
    companies,
    funds_eur: companies * packageEur,
    tco2e: companies * packageTco2e,
  }
}

export function AdoptionSlider({
  supplyCap,
  packageEur,
  packageTco2e,
  totalCorporates,
  vbnBudget,
  vbnBudgetSourceLabel,
  vbnBudgetSourceUrl,
}: Props) {
  const SLIDER_MAX = 5
  const [pct, setPct] = useState(1)
  const demand = useMemo(
    () => demandAt(pct, totalCorporates, packageEur, packageTco2e),
    [pct, totalCorporates, packageEur, packageTco2e],
  )
  const supplyConstrained = demand.tco2e > supplyCap.max_tco2e
  const delivered = supplyConstrained
    ? {
        funds_eur: supplyCap.max_funds_eur,
        tco2e: supplyCap.max_tco2e,
        companies: supplyCap.max_packages_nl,
      }
    : demand

  const supplyMarkPct = (supplyCap.max_adoption_pct / SLIDER_MAX) * 100
  const presets = [0.5, 1, 1.79, 5]

  return (
    <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-6 lg:p-8">
      <div className="flex items-baseline justify-between gap-4 mb-3">
        <label htmlFor="adoption" className="text-[13.5px] text-text-muted">
          Demand at{" "}
          <span className="font-semibold text-text tabular">
            {pct.toFixed(2)}%
          </span>{" "}
          of {fmtInt(totalCorporates)} CSRD-obligated NL mid-caps
        </label>
        <span className="text-[12px] text-text-faint tabular hidden sm:inline">
          {fmtInt(demand.companies)} companies
        </span>
      </div>

      <div className="relative">
        <input
          id="adoption"
          type="range"
          min={0.5}
          max={SLIDER_MAX}
          step={0.01}
          value={pct}
          onChange={(e) => setPct(Number(e.target.value))}
          className="w-full h-2 bg-surface-2 border border-line rounded-full appearance-none cursor-pointer accent-emerald-deep"
        />
        <div
          className="absolute pointer-events-none"
          style={{ left: `${supplyMarkPct}%`, top: -4, height: 14 }}
        >
          <div className="w-px h-full bg-warning-deep" />
        </div>
        <div className="relative h-5 mt-1.5 text-[10.5px] text-text-faint tabular">
          <span className="absolute left-0">0.5%</span>
          <span
            className="absolute -translate-x-1/2 text-warning-deep font-semibold whitespace-nowrap"
            style={{ left: `${supplyMarkPct}%` }}
          >
            ↑ NL supply cap (1.79%)
          </span>
          <span className="absolute right-0">5%</span>
        </div>
      </div>

      <div className="mt-5 flex gap-2 flex-wrap">
        {presets.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPct(p)}
            className={`text-[12px] px-3 py-1 rounded-[var(--radius)] border tabular transition-colors ${
              Math.abs(pct - p) < 0.01
                ? "bg-emerald-deep border-emerald-deep text-text-on-emerald"
                : "bg-surface border-line text-text-muted hover:border-line-strong"
            }`}
          >
            {p}%
          </button>
        ))}
      </div>

      <dl className="mt-9 grid grid-cols-1 sm:grid-cols-3 gap-x-8 gap-y-6 border-t border-line pt-7">
        <div>
          <dt className="eyebrow">Funds to foodbanks</dt>
          <dd className="display tabular tracking-[-0.025em] text-3xl mt-2">
            {fmtEur(delivered.funds_eur, {
              compact: delivered.funds_eur >= 10_000_000,
            })}
          </dd>
          <dd className="text-[12px] text-text-faint mt-0.5">per year</dd>
        </div>
        <div>
          <dt className="eyebrow">Climate contribution</dt>
          <dd className="display tabular tracking-[-0.025em] text-3xl mt-2">
            {fmtInt(delivered.tco2e)}
            <span className="text-[14px] text-text-faint ml-1.5">tCO₂e</span>
          </dd>
          <dd className="text-[12px] text-text-faint mt-0.5">
            attributable per year
          </dd>
        </div>
        <div>
          <dt className="eyebrow">NL supply utilisation</dt>
          <dd className="display tabular tracking-[-0.025em] text-3xl mt-2">
            {Math.min(
              100,
              Math.round((delivered.tco2e / supplyCap.max_tco2e) * 100),
            )}
            <span className="text-[14px] text-text-faint ml-1.5">%</span>
          </dd>
          <dd className="text-[12px] text-text-faint mt-0.5">
            of {fmtInt(supplyCap.max_packages_nl)} max NL packages
          </dd>
        </div>
      </dl>

      <div className="mt-7">
        {supplyConstrained ? (
          <div className="border border-warning/40 bg-warning-soft rounded-[var(--radius)] p-5">
            <p className="text-[13.5px] text-warning-deep leading-relaxed">
              <strong>Demand exceeds NL supply.</strong> At {pct.toFixed(1)}%
              adoption, corporate demand is {fmtInt(demand.companies)} packages
              ({fmtEur(demand.funds_eur, { compact: true })}), but the Dutch
              foodbank network can only support{" "}
              {fmtInt(supplyCap.max_packages_nl)} packages of attributable
              climate contribution per year.
            </p>
            <p className="mt-2.5 text-[13.5px] text-warning-deep leading-relaxed">
              Growth requires expansion: onboarding additional banks from
              VBN&apos;s 181-bank network, regional cluster sponsorships, or
              extending the platform to other EU countries with FRAME-aligned
              foodbanking infrastructure.
            </p>
          </div>
        ) : pct < 1 ? (
          <p className="text-[13.5px] text-text-muted leading-relaxed">
            <strong className="text-text">For context:</strong> a 1% adoption
            rate brings €1.75M to Dutch foodbanks each year — approaching half of{" "}
            <a
              href={vbnBudgetSourceUrl}
              target="_blank"
              rel="noreferrer"
              className="underline underline-offset-2 hover:text-text"
            >
              VBN&apos;s entire 2024 umbrella budget
            </a>{" "}
            of {fmtEur(vbnBudget, { compact: true })}.
          </p>
        ) : (
          <p className="text-[13.5px] text-text-muted leading-relaxed">
            <strong className="text-text">
              {fmtEur(delivered.funds_eur, { compact: true })}
            </strong>{" "}
            flows to foodbanks at this adoption level —{" "}
            {(delivered.funds_eur / vbnBudget).toFixed(1)}× the VBN
            umbrella&apos;s 2024 operating budget of{" "}
            <a
              href={vbnBudgetSourceUrl}
              target="_blank"
              rel="noreferrer"
              className="underline underline-offset-2 hover:text-text"
            >
              {fmtEur(vbnBudget, { compact: true })}
            </a>
            .
          </p>
        )}
      </div>

      <p className="mt-5 text-[11.5px] text-text-faint leading-relaxed">
        Supply cap derivation: {supplyCap.explanation} VBN budget source:{" "}
        <a
          href={vbnBudgetSourceUrl}
          target="_blank"
          rel="noreferrer"
          className="underline underline-offset-2 hover:text-text-muted"
        >
          {vbnBudgetSourceLabel}
        </a>
      </p>
    </div>
  )
}
