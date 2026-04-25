import Link from "next/link";

export default function Landing() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-24">
      <h1 className="text-5xl font-semibold tracking-tight">
        Climate-and-social impact, attributed and audit-ready.
      </h1>
      <p className="mt-6 max-w-2xl text-lg text-ink/70">
        Klimaatkracht turns food bank operations data into ESRS-aligned
        impact reports. Every euro you commit is traced through allocation,
        attribution, and audit appendix — no double-counting, no estimated
        proxies.
      </p>
      <div className="mt-10 flex gap-3">
        <Link
          href="/fund"
          className="rounded-md bg-ink px-5 py-3 text-sm font-medium text-white hover:bg-ink/90"
        >
          Try the allocation engine
        </Link>
        <Link
          href="/methodology"
          className="rounded-md border border-ink/20 px-5 py-3 text-sm font-medium hover:bg-white"
        >
          Read the methodology
        </Link>
      </div>

      <section className="mt-24 grid gap-10 sm:grid-cols-3">
        <div>
          <div className="text-3xl font-semibold">959 tCO2e</div>
          <p className="mt-1 text-sm text-ink/60">
            Net avoided emissions across the demo network in Q1 2026.
          </p>
        </div>
        <div>
          <div className="text-3xl font-semibold">€199 k</div>
          <p className="mt-1 text-sm text-ink/60">
            Total quarterly operational cost across five food banks.
          </p>
        </div>
        <div>
          <div className="text-3xl font-semibold">18,460</div>
          <p className="mt-1 text-sm text-ink/60">
            Households served in the period.
          </p>
        </div>
      </section>

      <section className="mt-24">
        <h2 className="text-2xl font-semibold">How it works</h2>
        <ol className="mt-6 space-y-4 text-ink/70">
          <li>
            <strong className="text-ink">1. Chapters submit operations data</strong> —
            kg by category, households served, transport km, refrigeration kWh.
            CSV or spreadsheet upload, not new tooling at the loading dock.
          </li>
          <li>
            <strong className="text-ink">2. The engine computes per-chapter impact</strong> —
            avoided emissions via Poore &amp; Nemecek coefficients, minus
            operational footprint via DEFRA &amp; Klimaatmonitor factors.
          </li>
          <li>
            <strong className="text-ink">3. Buyers commit with allocation preferences</strong> —
            blend climate impact, social need, and balanced distribution
            sliders. Live preview before committing.
          </li>
          <li>
            <strong className="text-ink">4. Attribution links EUR to verified impact</strong> —
            funding-share factor capped at 1.0 prevents double-counting.
          </li>
          <li>
            <strong className="text-ink">5. Reports stitch the audit appendix and methodology</strong> —
            every claim backed by a row in the operations data.
          </li>
        </ol>
      </section>
    </div>
  );
}
