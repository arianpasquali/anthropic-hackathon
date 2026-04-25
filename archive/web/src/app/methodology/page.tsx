import { loadBanks } from "@/lib/banks";

export default async function MethodologyPage() {
  const data = await loadBanks();
  const m = data.methodology;
  const pkg = data.package;

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <header className="mb-12">
        <p className="text-xs uppercase tracking-widest text-emerald-800 font-semibold mb-3">
          Public methodology disclosure
        </p>
        <h1 className="text-3xl lg:text-4xl font-semibold tracking-tight text-stone-900">
          How we calculate avoided emissions
        </h1>
        <p className="mt-4 max-w-2xl text-lg text-stone-600 leading-relaxed">
          Every Climate-Action Package report cites the same calculation chain
          documented on this page. The methodology is deterministic, auditable,
          and reviewed quarterly.
        </p>
      </header>

      <Section title="1. Framework alignment, not certification">
        <p>
          The Climate-Action Packages platform applies a methodology aligned
          with the Global Foodbanking Network&apos;s FRAME framework
          (<em>Food Recovery to Avoid Methane Emissions</em>). FRAME is the
          standards-track measurement framework that quantifies climate impact
          from food rescue, combining avoided wasted-production emissions
          with avoided disposal-route emissions.
        </p>
        <p>
          We are not FRAME-certified. Certification requires multi-month audit
          by GFN; alignment means we apply the same calculation structure with
          publicly cited factors, surfacing every assumption transparently.
          Every quantitative claim in a sponsor report traces to a citable
          source on this page or in the foodbank&apos;s own published annual
          report.
        </p>
      </Section>

      <Section title="2. Attribution by package economics">
        <p>
          A sponsor&apos;s claim on a foodbank&apos;s avoided emissions is
          attributed pro-rata. Each Climate-Action Package is locked at a fixed
          economic ratio of <strong>€{pkg.price_per_tco2e}</strong> per tCO
          <sub>2</sub>e — a {formatPrice(pkg.price_eur)} package corresponds
          to {formatNumber(pkg.tco2e)} tCO<sub>2</sub>e.
        </p>
        <p>
          The model assumes sponsor funding is fungible across the
          foodbank&apos;s operations, rather than directed to a specific
          food-rescue activity. The sponsor&apos;s attribution share is
          reported alongside the foodbank&apos;s annual baseline, so an auditor
          can always see what fraction of the bank&apos;s overall climate
          impact has been claimed.
        </p>
      </Section>

      <Section title="3. Category emission factors">
        <p>
          Per kilogramme of food rescued, avoided emissions are calculated by
          weighting each category in the foodbank&apos;s reported food mix by
          its category-specific emission factor. Factors are sourced from
          peer-reviewed and government datasets and represent the conservative
          end of published ranges.
        </p>
        <div className="my-6 overflow-x-auto rounded-lg border border-stone-200">
          <table className="w-full text-sm">
            <thead className="bg-stone-50 border-b border-stone-200">
              <tr>
                <th className="text-left font-semibold text-stone-700 px-4 py-2.5">
                  Category
                </th>
                <th className="text-right font-semibold text-stone-700 px-4 py-2.5">
                  kg CO<sub>2</sub>e / kg food
                </th>
                <th className="text-left font-semibold text-stone-700 px-4 py-2.5">
                  Source
                </th>
              </tr>
            </thead>
            <tbody>
              {m.emission_factors.map((ef) => (
                <tr
                  key={ef.category}
                  className="border-b border-stone-100 last:border-0"
                >
                  <td className="px-4 py-2.5 capitalize font-medium text-stone-800">
                    {ef.category.replace("_", " ")}
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums text-stone-800">
                    {ef.kg_co2e_per_kg.toFixed(1)}
                  </td>
                  <td className="px-4 py-2.5 text-stone-600">{ef.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-sm text-stone-500">
          Non-food items distributed by foodbanks (hygiene products, baby
          supplies, household goods) are out of scope for FRAME and reported
          separately under social impact, not climate impact.
        </p>
      </Section>

      <Section title="4. Dutch disposal counterfactual">
        <p>
          The avoided-emissions calculation depends on what would have
          happened to the food if it had not been rescued. US-default FRAME
          calculations assume landfill (high methane). The Dutch waste
          treatment mix is dominated by incineration with energy recovery,
          with smaller fractions for composting, anaerobic digestion and
          animal feed.
        </p>
        <p>
          To reflect this, we apply a counterfactual factor of{" "}
          <strong>{m.counterfactual_factor_nl}</strong> to the weighted
          production-stage average, lowering the disposal-stage component
          relative to the US default. This makes our estimates conservative
          rather than headline-friendly.
        </p>
        <blockquote className="my-4 border-l-2 border-stone-300 pl-4 text-sm text-stone-600 italic">
          {m.counterfactual_source}
        </blockquote>
      </Section>

      <Section title="5. Foodbank operational data">
        <p>
          Bank-level operational figures (kg food rescued, household coverage,
          parcel composition) are sourced from each bank&apos;s most recently
          published annual report. Where banks report in product units rather
          than kilogrammes, a conversion factor of 0.6 kg per consumer unit
          is applied, validated cross-bank against banks that publish both
          metrics.
        </p>
        <p>
          Every bank&apos;s detail page exposes the provenance string and
          source URL for its operational figures. The platform regenerates
          the dataset at the start of each quarter so reports always reference
          the most recent published data.
        </p>
      </Section>

      <Section title="6. Independent verification">
        <p>
          Reports generated by this platform are sponsor copy and have not
          been subject to independent third-party assurance under ISAE 3000
          or equivalent. Sponsors seeking limited or reasonable assurance
          for inclusion in their CSRD assurance scope should engage a
          qualified provider; the deterministic calculation chain and full
          source citations are designed to make external verification
          straightforward.
        </p>
        <p className="text-sm text-stone-500 mt-4">
          Audit queries: audit@climate-action-packages.eu
        </p>
      </Section>

      <p className="mt-12 pt-6 border-t border-stone-200 text-xs text-stone-500">
        Methodology last reviewed: {new Date(data.generated_at).toLocaleDateString("en-NL", { year: "numeric", month: "long", day: "numeric" })}.
        Framework reference: {m.framework}.
      </p>
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section className="mb-10">
      <h2 className="text-xl font-semibold tracking-tight text-stone-900 mb-3">
        {title}
      </h2>
      <div className="space-y-3 text-stone-700 leading-relaxed">{children}</div>
    </section>
  );
}

function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-NL").format(n);
}

function formatPrice(n: number): string {
  return new Intl.NumberFormat("en-NL", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(n);
}
