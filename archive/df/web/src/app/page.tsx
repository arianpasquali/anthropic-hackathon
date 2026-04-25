import Link from "next/link";
import {
  loadBanks,
  formatNumber,
  formatEuros,
  formatPercent,
  type Bank,
} from "@/lib/banks";

export default async function MarketplacePage() {
  const data = await loadBanks();

  return (
    <div>
      <Hero packagePrice={data.package.price_eur} packageTCO2e={data.package.tco2e} />
      <section className="mx-auto max-w-6xl px-6 py-12">
        <div className="flex items-end justify-between mb-6">
          <h2 className="text-2xl font-semibold tracking-tight text-stone-900">
            Available Climate-Action Packages
          </h2>
          <p className="text-sm text-stone-500">
            {data.banks.length} Dutch foodbanks · methodology aligned with FRAME
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {data.banks.map((bank) => (
            <BankCard key={bank.id} bank={bank} />
          ))}
        </div>
      </section>
    </div>
  );
}

function Hero({
  packagePrice,
  packageTCO2e,
}: {
  packagePrice: number;
  packageTCO2e: number;
}) {
  return (
    <section className="border-b border-stone-200 bg-white">
      <div className="mx-auto max-w-6xl px-6 py-16 lg:py-20">
        <p className="text-xs uppercase tracking-widest text-emerald-800 font-semibold mb-3">
          Verified Avoided Emissions · CSRD-Ready
        </p>
        <h1 className="text-4xl lg:text-5xl font-semibold tracking-tight text-stone-900 max-w-3xl leading-[1.05]">
          Audit-ready climate impact through Dutch foodbanks.
        </h1>
        <p className="mt-5 max-w-2xl text-lg text-stone-600 leading-relaxed">
          Sponsor a verified Climate-Action Package for {formatEuros(packagePrice)}.
          Receive {formatNumber(packageTCO2e)} tCO<sub>2</sub>e of avoided emissions
          attributed under FRAME-aligned methodology, with quarterly audit-ready
          reports formatted for direct inclusion in your ESRS E1 disclosure.
        </p>
        <div className="mt-8 flex flex-wrap gap-3 text-sm">
          <span className="inline-flex items-center gap-2 rounded-full border border-stone-200 px-3 py-1 bg-stone-50">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-700"></span>
            FRAME-aligned methodology
          </span>
          <span className="inline-flex items-center gap-2 rounded-full border border-stone-200 px-3 py-1 bg-stone-50">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-700"></span>
            CSRD ESRS E1 + S3 sections
          </span>
          <span className="inline-flex items-center gap-2 rounded-full border border-stone-200 px-3 py-1 bg-stone-50">
            <span className="h-1.5 w-1.5 rounded-full bg-emerald-700"></span>
            Locked at €41.67 / tCO<sub>2</sub>e
          </span>
        </div>
      </div>
    </section>
  );
}

function BankCard({ bank }: { bank: Bank }) {
  const sp = bank.standard_package;
  const isSolo = sp.is_solo_capable;

  return (
    <Link
      href={`/banks/${bank.id}`}
      className="group flex flex-col rounded-xl border border-stone-200 bg-white p-5 hover:border-stone-300 hover:shadow-sm transition-all"
    >
      <div className="flex items-start justify-between mb-4">
        <div>
          <h3 className="font-semibold text-stone-900 leading-tight">{bank.name}</h3>
          <p className="text-xs text-stone-500 mt-0.5">{bank.region}</p>
        </div>
        <span
          className={
            "shrink-0 ml-2 inline-flex items-center rounded-md px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide " +
            (isSolo
              ? "bg-emerald-50 text-emerald-800 border border-emerald-200"
              : "bg-amber-50 text-amber-800 border border-amber-200")
          }
        >
          {isSolo ? "Solo eligible" : "Cluster"}
        </span>
      </div>

      <div className="border-t border-stone-100 pt-4">
        <p className="text-xs text-stone-500 uppercase tracking-wide font-medium">
          Annual avoided emissions
        </p>
        <p className="text-3xl font-semibold tabular-nums text-stone-900 mt-0.5">
          {formatNumber(bank.annual_tco2e)}
          <span className="text-base font-normal text-stone-500 ml-1">
            tCO<sub>2</sub>e
          </span>
        </p>
      </div>

      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <div>
          <dt className="text-xs text-stone-500">Food rescued / yr</dt>
          <dd className="font-medium tabular-nums text-stone-800">
            {formatNumber(bank.annual_kg_rescued / 1000)} t
          </dd>
        </div>
        <div>
          <dt className="text-xs text-stone-500">Households / wk</dt>
          <dd className="font-medium tabular-nums text-stone-800">
            {bank.households_weekly
              ? formatNumber(bank.households_weekly)
              : "—"}
          </dd>
        </div>
      </dl>

      <div className="mt-5 pt-4 border-t border-stone-100 flex items-center justify-between text-sm">
        <span className="text-stone-600">
          €25k buys{" "}
          <span className="font-medium text-stone-900 tabular-nums">
            {formatPercent(sp.attribution_share)}
          </span>{" "}
          share
        </span>
        <span className="text-emerald-800 font-medium group-hover:translate-x-0.5 transition-transform">
          View →
        </span>
      </div>

      {bank.is_rdc && bank.rdc_satellite_count && (
        <p className="mt-3 text-xs text-stone-500">
          Regional Distribution Centre · {bank.rdc_satellite_count} satellite banks
        </p>
      )}
      {bank.cluster_banks.length > 0 && (
        <p className="mt-3 text-xs text-stone-500">
          Cluster lead · {bank.cluster_banks.length} alliance banks
        </p>
      )}
    </Link>
  );
}
