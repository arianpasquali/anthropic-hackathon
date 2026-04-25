"use client";

import { useMemo, useState } from "react";
import type { AdoptionScenario } from "@/lib/impact-types";
import { fmtInt, fmtEur } from "@/lib/impact-types";

interface SupplyCap {
  max_packages_nl: number;
  max_funds_eur: number;
  max_tco2e: number;
  max_adoption_pct: number;
  explanation: string;
}

interface Props {
  scenarios: AdoptionScenario[];
  supplyCap: SupplyCap;
  packageEur: number;
  packageTco2e: number;
  totalCorporates: number;
  vbnBudget: number;
  vbnBudgetSourceLabel: string;
  vbnBudgetSourceUrl: string;
}

// Compute demand at a given adoption % using package economics
function demandAt(pct: number, totalCorporates: number, packageEur: number, packageTco2e: number) {
  const companies = Math.round((pct / 100) * totalCorporates);
  return {
    adoption_pct: pct,
    companies,
    funds_eur: companies * packageEur,
    tco2e: companies * packageTco2e,
  };
}

export default function AdoptionSlider({
  supplyCap,
  packageEur,
  packageTco2e,
  totalCorporates,
  vbnBudget,
  vbnBudgetSourceLabel,
  vbnBudgetSourceUrl,
}: Props) {
  const SLIDER_MAX = 5; // %, beyond supply cap to show the constraint
  const [pct, setPct] = useState(1);
  const demand = useMemo(
    () => demandAt(pct, totalCorporates, packageEur, packageTco2e),
    [pct, totalCorporates, packageEur, packageTco2e]
  );
  const supplyConstrained = demand.tco2e > supplyCap.max_tco2e;
  const delivered = supplyConstrained
    ? {
        funds_eur: supplyCap.max_funds_eur,
        tco2e: supplyCap.max_tco2e,
        companies: supplyCap.max_packages_nl,
      }
    : {
        funds_eur: demand.funds_eur,
        tco2e: demand.tco2e,
        companies: demand.companies,
      };

  const supplyMarkPct = (supplyCap.max_adoption_pct / SLIDER_MAX) * 100;
  const presets = [0.5, 1, 1.79, 5];

  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6 lg:p-8">
      <div className="flex items-baseline justify-between gap-4 mb-2">
        <label htmlFor="adoption" className="text-sm text-stone-600">
          Demand at{" "}
          <span className="font-semibold text-stone-900 tabular-nums">{pct.toFixed(2)}%</span>{" "}
          of {fmtInt(totalCorporates)} CSRD-obligated NL mid-caps
        </label>
        <span className="text-xs text-stone-500 tabular-nums hidden sm:inline">
          {fmtInt(demand.companies)} companies
        </span>
      </div>

      {/* Slider with supply-cap mark */}
      <div className="relative">
        <input
          id="adoption"
          type="range"
          min={0.5}
          max={SLIDER_MAX}
          step={0.01}
          value={pct}
          onChange={(e) => setPct(Number(e.target.value))}
          className="w-full h-2 bg-stone-100 rounded-lg appearance-none cursor-pointer accent-emerald-800"
        />
        <div
          className="absolute pointer-events-none"
          style={{ left: `${supplyMarkPct}%`, top: -4, height: 14 }}
        >
          <div className="w-px h-full bg-amber-600" />
        </div>
        <div className="relative h-5 mt-1 text-[10px] text-stone-500">
          <span className="absolute left-0">0.5%</span>
          <span
            className="absolute -translate-x-1/2 text-amber-700 font-medium whitespace-nowrap"
            style={{ left: `${supplyMarkPct}%` }}
          >
            ↑ NL supply cap (1.79%)
          </span>
          <span className="absolute right-0">5%</span>
        </div>
      </div>

      <div className="mt-4 flex gap-2 flex-wrap">
        {presets.map((p) => (
          <button
            key={p}
            type="button"
            onClick={() => setPct(p)}
            className={
              "text-xs rounded-md border px-2.5 py-1 transition-colors " +
              (Math.abs(pct - p) < 0.01
                ? "bg-emerald-900 border-emerald-900 text-white"
                : "bg-white border-stone-200 text-stone-700 hover:border-stone-300")
            }
          >
            {p}%
          </button>
        ))}
      </div>

      <dl className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-6 border-t border-stone-100 pt-6">
        <div>
          <dt className="text-xs text-stone-500 uppercase tracking-wide font-medium">
            Funds to foodbanks
          </dt>
          <dd className="mt-1 text-3xl font-semibold tabular-nums text-stone-900">
            {fmtEur(delivered.funds_eur, { compact: delivered.funds_eur >= 10_000_000 })}
          </dd>
          <dd className="text-sm text-stone-500">per year</dd>
        </div>
        <div>
          <dt className="text-xs text-stone-500 uppercase tracking-wide font-medium">
            Avoided emissions claimed
          </dt>
          <dd className="mt-1 text-3xl font-semibold tabular-nums text-stone-900">
            {fmtInt(delivered.tco2e)}
            <span className="text-base font-normal text-stone-500 ml-1">tCO₂e</span>
          </dd>
          <dd className="text-sm text-stone-500">per year, audit-ready</dd>
        </div>
        <div>
          <dt className="text-xs text-stone-500 uppercase tracking-wide font-medium">
            NL supply utilisation
          </dt>
          <dd className="mt-1 text-3xl font-semibold tabular-nums text-stone-900">
            {Math.min(100, Math.round((delivered.tco2e / supplyCap.max_tco2e) * 100))}%
          </dd>
          <dd className="text-sm text-stone-500">
            of {fmtInt(supplyCap.max_packages_nl)} max NL packages
          </dd>
        </div>
      </dl>

      <div className="mt-6">
        {supplyConstrained ? (
          <div className="rounded-lg border border-amber-200 bg-amber-50 p-4">
            <p className="text-sm text-amber-900 leading-relaxed">
              <strong>Demand exceeds NL supply.</strong> At {pct.toFixed(1)}% adoption,
              corporate demand is {fmtInt(demand.companies)} packages
              ({fmtEur(demand.funds_eur, { compact: true })}), but the Dutch
              foodbank network can only support {fmtInt(supplyCap.max_packages_nl)}{" "}
              packages of avoided emissions per year.
            </p>
            <p className="mt-2 text-sm text-amber-900 leading-relaxed">
              Growth from here requires expansion: onboarding additional banks
              from VBN&apos;s 180-bank network, regional cluster sponsorships,
              or extending the platform to other EU countries with FRAME-aligned
              foodbanking infrastructure.
            </p>
          </div>
        ) : pct < 1 ? (
          <p className="text-sm text-stone-700 leading-relaxed">
            <strong className="text-stone-900">For context:</strong> a 1% adoption
            rate brings €1.75M to Dutch foodbanks each year — comparable to{" "}
            <a
              href={vbnBudgetSourceUrl}
              target="_blank"
              rel="noreferrer"
              className="underline decoration-stone-300 hover:decoration-stone-700"
            >
              VBN&apos;s entire 2024 umbrella budget
            </a>{" "}
            of {fmtEur(vbnBudget, { compact: true })}.
          </p>
        ) : (
          <p className="text-sm text-stone-700 leading-relaxed">
            <strong className="text-stone-900">{fmtEur(delivered.funds_eur, { compact: true })}</strong>{" "}
            flows to foodbanks at this adoption level —{" "}
            {(delivered.funds_eur / vbnBudget).toFixed(1)}× the VBN umbrella&apos;s
            2024 operating budget of{" "}
            <a
              href={vbnBudgetSourceUrl}
              target="_blank"
              rel="noreferrer"
              className="underline decoration-stone-300 hover:decoration-stone-700"
            >
              {fmtEur(vbnBudget, { compact: true })}
            </a>
            .
          </p>
        )}
      </div>

      <p className="mt-4 text-xs text-stone-500">
        Supply cap derivation: {supplyCap.explanation} VBN budget source:{" "}
        <a
          href={vbnBudgetSourceUrl}
          target="_blank"
          rel="noreferrer"
          className="underline hover:text-stone-700"
        >
          {vbnBudgetSourceLabel}
        </a>
      </p>
    </div>
  );
}
