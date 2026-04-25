import Link from "next/link";
import { notFound } from "next/navigation";
import {
  loadBanks,
  formatNumber,
  formatEuros,
  formatPercent,
} from "@/lib/banks";

export default async function BankDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const data = await loadBanks();
  const bank = data.banks.find((b) => b.id === id);
  if (!bank) notFound();

  const sp = bank.standard_package;
  const isSolo = sp.is_solo_capable;

  return (
    <div className="mx-auto max-w-5xl px-6 py-10">
      <Link
        href="/"
        className="text-sm text-stone-500 hover:text-stone-900 inline-flex items-center gap-1"
      >
        ← Back to marketplace
      </Link>

      <header className="mt-4 mb-10">
        <div className="flex items-start justify-between gap-6">
          <div>
            <h1 className="text-3xl lg:text-4xl font-semibold tracking-tight text-stone-900">
              {bank.name}
            </h1>
            <p className="mt-1 text-stone-500">{bank.region} · Netherlands</p>
          </div>
          <span
            className={
              "shrink-0 inline-flex items-center rounded-md px-2.5 py-1 text-xs font-medium uppercase tracking-wide " +
              (isSolo
                ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
                : "bg-amber-50 text-amber-800 border border-amber-200")
            }
          >
            {isSolo ? "Solo sponsorship eligible" : "Regional cluster sponsorship"}
          </span>
        </div>
      </header>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <Card title="Annual operations (verified)">
            <dl className="grid grid-cols-2 sm:grid-cols-3 gap-6">
              <Stat
                label="Avoided emissions"
                value={formatNumber(bank.annual_tco2e)}
                unit="tCO2e/yr"
              />
              <Stat
                label="Food rescued"
                value={formatNumber(bank.annual_kg_rescued / 1000)}
                unit="tonnes/yr"
              />
              <Stat
                label="Households served"
                value={
                  bank.households_weekly ? formatNumber(bank.households_weekly) : "—"
                }
                unit={bank.households_weekly ? "weekly" : ""}
              />
              <Stat
                label="Weighted EF"
                value={bank.weighted_emission_factor.toFixed(3)}
                unit="kg CO2e/kg"
              />
              {bank.is_rdc && bank.rdc_satellite_count && (
                <Stat
                  label="RDC satellites"
                  value={String(bank.rdc_satellite_count)}
                  unit="banks served"
                />
              )}
              {bank.cluster_banks.length > 0 && (
                <Stat
                  label="Alliance banks"
                  value={String(bank.cluster_banks.length)}
                  unit="cluster members"
                />
              )}
            </dl>
          </Card>

          <Card title="Category mix">
            <div className="space-y-2">
              {Object.entries(bank.category_mix)
                .sort(([, a], [, b]) => b - a)
                .map(([cat, share]) => (
                  <div key={cat} className="flex items-center gap-3">
                    <div className="w-24 text-sm text-stone-600 capitalize">
                      {cat.replace("_", " ")}
                    </div>
                    <div className="flex-1 h-2 bg-stone-100 rounded">
                      <div
                        className="h-2 bg-emerald-700 rounded"
                        style={{ width: `${share * 100}%` }}
                      />
                    </div>
                    <div className="w-12 text-right text-sm text-stone-700 tabular-nums">
                      {formatPercent(share)}
                    </div>
                  </div>
                ))}
            </div>
          </Card>

          <Card title="Methodology and provenance">
            <p className="text-sm text-stone-600 leading-relaxed">{bank.provenance}</p>
            <p className="mt-3 text-xs text-stone-500">
              Source: {" "}
              <a
                href={bank.source_url}
                target="_blank"
                rel="noreferrer"
                className="underline hover:text-stone-700"
              >
                {bank.source_url}
              </a>
            </p>
          </Card>
        </div>

        <aside className="lg:col-span-1">
          <div className="sticky top-6 rounded-xl border border-stone-200 bg-white p-6">
            <p className="text-xs uppercase tracking-widest text-emerald-800 font-semibold">
              Climate-Action Package
            </p>
            <p className="mt-2 text-3xl font-semibold tabular-nums text-stone-900">
              {formatEuros(sp.amount_eur)}
            </p>
            <p className="text-sm text-stone-500">per quarter, billed via Solvimon</p>

            <div className="mt-6 space-y-3 text-sm">
              <Row
                label="Attributed avoided emissions"
                value={`${formatNumber(sp.attributed_tco2e)} tCO2e`}
              />
              <Row
                label="Attributed food rescued"
                value={`${formatNumber(sp.attributed_kg_food)} kg`}
              />
              <Row
                label="Share of bank annual"
                value={formatPercent(sp.attribution_share)}
              />
              <Row
                label="Price per tCO2e"
                value={`€${data.package.price_per_tco2e}`}
              />
            </div>

            {!isSolo && (
              <p className="mt-4 text-xs text-amber-800 bg-amber-50 border border-amber-200 rounded p-3 leading-relaxed">
                A single package consumes more than half this foodbank&apos;s annual
                avoided emissions. Recommended as part of a regional cluster
                sponsorship rather than a solo allocation.
              </p>
            )}

            <Link
              href={`/banks/${bank.id}/buy`}
              className="mt-6 block w-full text-center rounded-lg bg-emerald-900 hover:bg-emerald-800 text-white font-medium py-3 transition-colors"
            >
              Sponsor this foodbank
            </Link>
            <p className="mt-3 text-xs text-stone-500 text-center">
              Includes quarterly audit-ready CSR report (ESRS E1 + S3)
            </p>
          </div>
        </aside>
      </section>
    </div>
  );
}

function Card({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-stone-200 bg-white p-6">
      <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-500 mb-4">
        {title}
      </h2>
      {children}
    </div>
  );
}

function Stat({
  label,
  value,
  unit,
}: {
  label: string;
  value: string;
  unit: string;
}) {
  return (
    <div>
      <dt className="text-xs text-stone-500">{label}</dt>
      <dd className="mt-0.5">
        <span className="text-xl font-semibold tabular-nums text-stone-900">
          {value}
        </span>
        {unit && <span className="text-sm text-stone-500 ml-1">{unit}</span>}
      </dd>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3 border-b border-stone-100 pb-2 last:border-0">
      <span className="text-stone-600">{label}</span>
      <span className="font-medium tabular-nums text-stone-900">{value}</span>
    </div>
  );
}
