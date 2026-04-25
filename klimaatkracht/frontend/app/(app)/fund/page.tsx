"use client";

import { useEffect, useMemo, useState } from "react";

import { AllocationSliders } from "@/components/allocation/AllocationSliders";
import { ChapterAllocationTable } from "@/components/allocation/ChapterAllocationTable";
import { computeAllocation } from "@/lib/allocation-preview";
import type {
  AllocationPreferences,
  AllocationResult,
  ChapterSnapshot,
} from "@/lib/types";

const DEMO_CHAPTERS: ChapterSnapshot[] = [
  {
    id: "VB-AMS-OOST",
    net_avoided_tco2e: 274.0,
    households_served_quarter: 4940,
    needs_score: 0.78,
    regional_bonus: 1.0,
    total_tonnes: 162.5,
  },
  {
    id: "VB-RDM-ZUID",
    net_avoided_tco2e: 247.0,
    households_served_quarter: 5460,
    needs_score: 0.92,
    regional_bonus: 1.0,
    total_tonnes: 145.6,
  },
  {
    id: "VB-LEI-CTR",
    net_avoided_tco2e: 174.5,
    households_served_quarter: 3120,
    needs_score: 0.61,
    regional_bonus: 1.0,
    total_tonnes: 101.4,
  },
  {
    id: "VB-FRL-NRD",
    net_avoided_tco2e: 64.8,
    households_served_quarter: 1235,
    needs_score: 0.71,
    regional_bonus: 1.15,
    total_tonnes: 44.2,
  },
  {
    id: "VB-EHV-CTR",
    net_avoided_tco2e: 199.2,
    households_served_quarter: 3705,
    needs_score: 0.68,
    regional_bonus: 1.0,
    total_tonnes: 118.3,
  },
];

const DEFAULT_PREFS: AllocationPreferences = {
  max_climate_impact: 0.4,
  max_social_need: 0.4,
  balanced_distribution: 0.2,
};

const eurFormatter = new Intl.NumberFormat("en-NL", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

export default function FundPage() {
  const [amount, setAmount] = useState(100_000);
  const [prefs, setPrefs] = useState<AllocationPreferences>(DEFAULT_PREFS);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{
    netAvoidedTco2e: number;
    foodKg: number;
    households: number;
  } | null>(null);

  const allocations = useMemo<Record<string, AllocationResult>>(() => {
    try {
      return computeAllocation(DEMO_CHAPTERS, prefs, amount);
    } catch {
      return {};
    }
  }, [amount, prefs]);

  useEffect(() => {
    setResult(null);
  }, [amount, prefs]);

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <div className="mb-10">
        <h1 className="text-3xl font-semibold tracking-tight">
          Set your allocation preferences
        </h1>
        <p className="mt-2 max-w-2xl text-ink/70">
          Move the sliders to weight your contribution. The preview updates
          live, in-browser, with the same algorithm the backend uses to
          compute the persisted attribution.
        </p>
      </div>

      <div className="grid gap-10 lg:grid-cols-[20rem_1fr]">
        <aside className="space-y-8">
          <div>
            <label
              htmlFor="amount"
              className="block text-sm font-medium text-ink/80"
            >
              Commitment amount
            </label>
            <div className="mt-1 flex items-center gap-2">
              <span className="text-ink/50">€</span>
              <input
                id="amount"
                type="number"
                min={1000}
                step={1000}
                value={amount}
                onChange={(e) => setAmount(Number(e.target.value))}
                className="w-full rounded-md border border-ink/15 bg-white px-3 py-2 text-lg font-medium tabular-nums focus:border-ink focus:outline-none"
              />
            </div>
          </div>

          <AllocationSliders value={prefs} onChange={setPrefs} />

          <button
            onClick={async () => {
              setSubmitting(true);
              try {
                const response = await fetch("/api/fund/commit", {
                  method: "POST",
                  headers: { "content-type": "application/json" },
                  body: JSON.stringify({
                    buyer_id: "buyer-test",
                    fund_id: "demo-fund-q1-2026",
                    amount_eur: amount,
                    preferences: prefs,
                    rationale: "Live demo commitment from buyer dashboard",
                    period_start: "2026-01-06",
                    period_end: "2026-03-30",
                  }),
                });
                if (!response.ok) {
                  const err = await response.json().catch(() => ({}));
                  alert(`Commit failed: ${err.detail ?? response.status}`);
                  return;
                }
                const body = await response.json();
                setResult({
                  netAvoidedTco2e: body.total_net_avoided_tco2e,
                  foodKg: body.total_food_rescued_kg,
                  households: body.total_households_supported,
                });
              } finally {
                setSubmitting(false);
              }
            }}
            disabled={submitting}
            className="w-full rounded-md bg-ink px-4 py-3 text-sm font-medium text-white hover:bg-ink/90 disabled:opacity-50"
          >
            {submitting ? "Committing…" : `Commit ${eurFormatter.format(amount)}`}
          </button>
        </aside>

        <section className="space-y-6">
          <ChapterAllocationTable
            chapters={DEMO_CHAPTERS}
            allocations={allocations}
          />

          {result ? (
            <div className="rounded-md border border-emerald-700/30 bg-emerald-50 px-5 py-4">
              <div className="text-sm font-semibold text-emerald-900">
                Commitment created
              </div>
              <dl className="mt-2 grid grid-cols-3 gap-4 text-sm text-emerald-900">
                <div>
                  <dt className="text-emerald-700/70 text-xs">Net avoided</dt>
                  <dd className="font-semibold">
                    {result.netAvoidedTco2e.toFixed(1)} tCO₂e
                  </dd>
                </div>
                <div>
                  <dt className="text-emerald-700/70 text-xs">Food rescued</dt>
                  <dd className="font-semibold">
                    {Intl.NumberFormat("en-NL").format(
                      Math.round(result.foodKg),
                    )}{" "}
                    kg
                  </dd>
                </div>
                <div>
                  <dt className="text-emerald-700/70 text-xs">Households</dt>
                  <dd className="font-semibold">
                    {Intl.NumberFormat("en-NL").format(
                      Math.round(result.households),
                    )}
                  </dd>
                </div>
              </dl>
            </div>
          ) : null}
        </section>
      </div>
    </div>
  );
}
