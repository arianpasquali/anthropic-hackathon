import Link from "next/link"
import { api } from "@/lib/api"
import { LangToggle } from "@/components/report/LangToggle"
import { PrintButton } from "@/components/report/PrintButton"
import { formatEur, formatNumber, formatTCO2e } from "@/lib/format"
import type { ReportData } from "@/lib/types"

type Lang = "nl" | "en"

export default async function ReportPage({
  params,
  searchParams,
}: {
  params: Promise<{ subId: string }>
  searchParams: Promise<{ lang?: string }>
}) {
  const { subId } = await params
  const { lang: rawLang } = await searchParams
  const lang: Lang = rawLang === "en" ? "en" : "nl"

  const d: ReportData = await api.getReportData(subId, lang)
  const t = d.texts as Record<string, string>

  return (
    <div className="report-root bg-surface-2 min-h-screen pb-24">
      <div className="mx-auto max-w-[920px] px-6 pt-8">

        {/* nav bar — hidden on print, sits on the desk above the sheet */}
        <div className="no-print flex items-center justify-between mb-6">
          <Link href="/dashboard/corporate" className="text-[13px] text-text-muted hover:text-text">
            ← Back to dashboard
          </Link>
          <div className="flex items-center gap-4">
            <LangToggle lang={lang} subId={subId} />
            <PrintButton />
          </div>
        </div>

        {/* Paper sheet — printed-document treatment, civic register. */}
        <article className="kk-paper-sheet">

      {/* header */}
      <header className="pb-8 border-b border-line">
        <p className="eyebrow">ESRS E5 + S3 · climate contribution disclosure</p>
        <h1 className="display text-[3rem] mt-3 max-w-[24ch]">{d.meta.org}</h1>
        <p className="text-text-muted text-[14px] mt-2 tabular">
          {d.meta.package_name} · {d.meta.period} · {d.meta.generated}
        </p>
      </header>

      {/* KPI strip */}
      <section className="grid grid-cols-2 md:grid-cols-4 border-b border-line">
        {[
          { label: t.kpi_co2e,      value: formatTCO2e(d.kpis.total_co2e_t),       hint: "attributed" },
          { label: t.kpi_investment, value: formatEur(d.kpis.investment_eur),         hint: "annual" },
          { label: t.kpi_economics,  value: `€${d.kpis.eur_per_tco2e.toFixed(2)}`,   hint: "per tCO₂e" },
          { label: t.kpi_households, value: formatNumber(d.kpis.households_per_week), hint: "per week" },
        ].map((k, i) => (
          <div key={i} className="py-6 pr-8 border-r border-line last:border-r-0 pl-0 md:[&:not(:first-child)]:pl-6">
            <p className="eyebrow text-[10px]">{k.label}</p>
            <p className="display tabular text-[1.75rem] mt-1">{k.value}</p>
            <p className="text-[11px] text-text-faint mt-0.5">{k.hint}</p>
          </div>
        ))}
      </section>

      {/* executive summary */}
      <section className="mt-10 max-w-[66ch]">
        <p className="eyebrow">Executive summary</p>
        <div
          className="mt-4 text-[14.5px] leading-relaxed [&_strong]:font-semibold [&_em]:italic"
          dangerouslySetInnerHTML={{ __html: d.summary.body_html }}
        />
        <div
          className="mt-5 text-[12.5px] text-text-muted leading-relaxed border-t border-line pt-4 [&_strong]:font-semibold"
          dangerouslySetInnerHTML={{ __html: d.summary.disclaimer_html }}
        />
      </section>

      {/* methodology */}
      <section className="mt-12 pt-10 border-t border-line">
        <p className="eyebrow">Methodology</p>
        <h2 className="display text-2xl mt-3">FRAME-NL v2.0</h2>
        <div className="mt-4 grid md:grid-cols-2 gap-8 max-w-[72ch]">
          <div
            className="text-[13.5px] leading-relaxed text-text-muted [&_strong]:text-text [&_strong]:font-semibold"
            dangerouslySetInnerHTML={{ __html: d.methodology.body1_html }}
          />
          <div
            className="text-[13.5px] leading-relaxed text-text-muted [&_strong]:text-text [&_strong]:font-semibold"
            dangerouslySetInnerHTML={{ __html: d.methodology.body2_html }}
          />
        </div>
        <ul className="mt-6 flex flex-col gap-1">
          {(d.texts.sources as unknown as string[]).map((s, i) => (
            <li key={i} className="text-[12px] text-text-faint">[{i + 1}] {s}</li>
          ))}
        </ul>
      </section>

      {/* allocation table */}
      <section className="mt-12 pt-10 border-t border-line">
        <p className="eyebrow">{t.alloc_h2}</p>
        <h2 className="display text-2xl mt-3 max-w-[30ch]">{t.alloc_sub}</h2>
        <div className="mt-6 overflow-x-auto">
          <table className="w-full text-[13px] tabular">
            <thead>
              <tr className="border-b border-line">
                {[t.col_bank, t.col_alloc, t.col_amount, t.col_bank_co2e, t.col_attr_co2e, t.col_households, t.col_kg].map((h) => (
                  <th key={h} className="pb-2 pr-4 text-left text-[10.5px] font-semibold tracking-widest uppercase text-text-muted">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {d.allocations.map((r) => (
                <tr key={r.slug} className="border-b border-line/50 hover:bg-surface-2/50 transition-colors">
                  <td className="py-3 pr-4 font-medium">
                    <Link href={`/foodbanks/${r.slug}`} className="hover:text-emerald-deep hover:underline">
                      {r.name}
                    </Link>
                    <span className="block text-[11px] text-text-faint">{r.city} · {r.year}</span>
                  </td>
                  <td className="py-3 pr-4">{r.weight_pct.toFixed(1)}%</td>
                  <td className="py-3 pr-4">{formatEur(r.amount_eur)}</td>
                  <td className="py-3 pr-4">{formatTCO2e(r.bank_co2e_t)}</td>
                  <td className="py-3 pr-4 font-semibold text-emerald-deep">{r.attributed_co2e_t.toFixed(3)} t</td>
                  <td className="py-3 pr-4">{r.households ? formatNumber(r.households) : "—"}</td>
                  <td className="py-3">{r.kg_rescued_attr ? `${formatNumber(Math.round(r.kg_rescued_attr / 1000))} t` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {d.data_gaps.length > 0 && (
          <div className="mt-4 p-4 bg-surface-2 rounded-[var(--radius)]">
            <p className="text-[12px] text-text-muted">{d.data_gaps.join(" · ")}</p>
          </div>
        )}
      </section>

      {/* category breakdown */}
      {d.allocations.some((r) => r.cat_rows.length > 0) && (
        <section className="mt-12 pt-10 border-t border-line">
          <p className="eyebrow">{t.cat_h2}</p>
          <h2 className="display text-2xl mt-3">{t.cat_sub}</h2>
          {d.allocations.filter((r) => r.cat_rows.length > 0).map((r) => (
            <div key={r.slug} className="mt-8">
              <p className="text-[13px] font-semibold">{r.name}</p>
              <table className="mt-3 w-full text-[12.5px] tabular">
                <thead>
                  <tr className="border-b border-line">
                    {[t.col_cat, t.col_kg_attr, t.col_tco2e_attr, t.col_ef, t.col_source].map((h) => (
                      <th key={h} className="pb-2 pr-4 text-left text-[10px] font-semibold tracking-widest uppercase text-text-muted">
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {r.cat_rows.map((c) => (
                    <tr key={c.category} className="border-b border-line/40">
                      <td className="py-2 pr-4 capitalize">{c.category}</td>
                      <td className="py-2 pr-4">{formatNumber(Math.round(c.kg_attr))} kg</td>
                      <td className="py-2 pr-4">{c.tco2e_attr.toFixed(3)} t</td>
                      <td className="py-2 pr-4">{c.ef} kg CO₂e/kg</td>
                      <td className="py-2 text-text-muted text-[11.5px]">{c.source}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}
        </section>
      )}

      {/* disclaimers */}
      {d.disclaimers.length > 0 && (
        <section className="mt-12 pt-10 border-t border-line">
          <p className="eyebrow">{t.disc_h2}</p>
          <div className="mt-6 flex flex-col gap-6 max-w-[66ch]">
            {d.disclaimers.map((disc, i) => (
              <div key={i}>
                <p className="text-[13px] font-semibold">{disc.title}</p>
                <p className="mt-1 text-[13px] text-text-muted leading-relaxed">{disc.body}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* recommendations */}
      {d.recommendations.length > 0 && (
        <section className="mt-12 pt-10 border-t border-line">
          <p className="eyebrow">{t.rec_h2}</p>
          <h2 className="display text-2xl mt-3">{t.rec_sub}</h2>
          <div className="mt-6 grid md:grid-cols-2 gap-6">
            {d.recommendations.map((rec, i) => (
              <div key={i} className="bg-surface-2 rounded-[var(--radius)] p-5">
                <p className="text-[13px] font-semibold">{rec.title}</p>
                <p className="mt-2 text-[13px] text-text-muted leading-relaxed">{rec.body}</p>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* appendix */}
      <section className="mt-12 pt-10 border-t border-line">
        <p className="eyebrow">{t.appendix_h2}</p>
        <h2 className="display text-2xl mt-3">{t.trail_h3}</h2>
        <pre className="mt-4 text-[11.5px] text-text-muted font-mono leading-relaxed whitespace-pre-wrap break-words bg-surface-2 p-5 rounded-[var(--radius)]">
          {d.calc_trail}
        </pre>
        <div className="mt-8 grid md:grid-cols-2 gap-8">
          <div>
            <p className="text-[12px] font-semibold tracking-widest uppercase text-text-muted mb-3">{t.ef_h3}</p>
            <table className="w-full text-[12px] tabular">
              <tbody>
                {d.emission_factors.map((ef) => (
                  <tr key={ef.category} className="border-b border-line/40">
                    <td className="py-1.5 pr-4 capitalize">{ef.category}</td>
                    <td className="py-1.5 pr-4 text-right">{ef.ef}</td>
                    <td className="py-1.5 text-text-faint text-[11px]">{ef.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div>
            <p className="text-[12px] font-semibold tracking-widest uppercase text-text-muted mb-3">{t.cf_h3}</p>
            <p className="text-[13px] text-text-muted leading-relaxed">{t.cf_body}</p>
          </div>
        </div>
      </section>

      {/* footer */}
      <footer className="mt-16 pt-6 border-t border-line">
        <p className="text-[11.5px] text-text-faint">{t.footer}</p>
      </footer>
        </article>
      </div>
    </div>
  )
}
