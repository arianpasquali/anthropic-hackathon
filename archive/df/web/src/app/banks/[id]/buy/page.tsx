import Link from "next/link";
import { notFound } from "next/navigation";
import {
  loadBanks,
  formatEuros,
  formatNumber,
  formatPercent,
} from "@/lib/banks";

export default async function BuyPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const data = await loadBanks();
  const bank = data.banks.find((b) => b.id === id);
  if (!bank) notFound();

  const sp = bank.standard_package;

  return (
    <div className="mx-auto max-w-3xl px-6 py-12">
      <Link
        href={`/banks/${bank.id}`}
        className="text-sm text-stone-500 hover:text-stone-900 inline-flex items-center gap-1"
      >
        ← Back to {bank.name}
      </Link>

      <div className="mt-6 rounded-xl border border-stone-200 bg-white">
        <div className="border-b border-stone-100 p-6">
          <p className="text-xs uppercase tracking-widest text-emerald-800 font-semibold">
            Solvimon checkout · sandbox
          </p>
          <h1 className="mt-2 text-2xl font-semibold tracking-tight text-stone-900">
            Sponsor {bank.name}
          </h1>
          <p className="mt-1 text-sm text-stone-500">
            Climate-Action Package · {bank.region}
          </p>
        </div>

        <div className="p-6 space-y-6">
          <section>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-500 mb-3">
              Order summary
            </h2>
            <dl className="space-y-2 text-sm">
              <Row label="Package" value="Climate-Action Package — Q2 2026" />
              <Row label="Foodbank" value={bank.name} />
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
              <Row label="Quarterly CSR report" value="Included (ESRS E1 + S3)" />
              <Row label="Methodology" value="FRAME-aligned" />
            </dl>
          </section>

          <section className="border-t border-stone-100 pt-6">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-500 mb-3">
              Billing
            </h2>
            <div className="rounded-lg border border-stone-200 bg-stone-50 p-4 space-y-2 text-sm">
              <Row label="Subtotal" value={formatEuros(sp.amount_eur)} />
              <Row label="VAT (0% — ANBI)" value={formatEuros(0)} />
              <div className="flex justify-between gap-3 pt-2 border-t border-stone-200">
                <span className="font-semibold text-stone-900">Total per quarter</span>
                <span className="font-semibold tabular-nums text-stone-900">
                  {formatEuros(sp.amount_eur)}
                </span>
              </div>
            </div>
            <p className="mt-3 text-xs text-stone-500">
              Recurring quarterly billing via Solvimon. Cancel anytime — last quarter&apos;s
              report is delivered before billing stops.
            </p>
          </section>

          <section className="border-t border-stone-100 pt-6">
            <Link
              href={`/banks/${bank.id}/buy/confirmed`}
              className="block w-full text-center rounded-lg bg-emerald-900 hover:bg-emerald-800 text-white font-medium py-3 transition-colors"
            >
              Confirm and pay {formatEuros(sp.amount_eur)}
            </Link>
            <p className="mt-3 text-xs text-stone-500 text-center">
              Demo build · no real payment is taken. In production, this routes
              through Solvimon checkout.
            </p>
          </section>
        </div>
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-3">
      <span className="text-stone-600">{label}</span>
      <span className="font-medium tabular-nums text-stone-900">{value}</span>
    </div>
  );
}
