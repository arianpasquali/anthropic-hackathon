import Image from "next/image"
import Link from "next/link"
import { notFound } from "next/navigation"
import { api, ApiError } from "@/lib/api"
import { Badge } from "@/components/ui/Badge"
import { CategoryMixBars } from "@/components/foodbanks/CategoryMixBars"
import { ProvenanceList } from "@/components/foodbanks/ProvenanceList"
import { TimelineChart } from "@/components/charts/TimelineChart"
import { formatEur, formatKg, formatNumber, formatTCO2e } from "@/lib/format"
import { foodbankHeroPhoto } from "@/lib/foodbank-photos"

export default async function FoodbankProfilePage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const bank = await api.getFoodbank(slug).catch((e) => {
    if (e instanceof ApiError && e.status === 404) return null
    throw e
  })
  if (!bank) notFound()
  const [timeline, packages] = await Promise.all([
    api.getFoodbankTimeline(slug).catch(() => []),
    api.listPackages().catch(() => []),
  ])
  const packageDetails = await Promise.all(
    packages.map((p) => api.getPackage(p.id).catch(() => null)),
  )
  const fundsWithBank = packageDetails
    .filter((p): p is NonNullable<typeof p> => p != null)
    .filter((p) => p.projected_allocations.some((a) => a.foodbank.id === bank.id))

  return (
    <div>
      <section className="relative isolate border-b border-line">
        <div aria-hidden className="kk-photo-hero absolute inset-0 -z-10">
          <Image
            src={foodbankHeroPhoto(slug)}
            alt=""
            fill
            sizes="100vw"
            priority
            className="object-cover"
          />
        </div>
        <div className="mx-auto max-w-[1100px] px-6 pt-12 md:pt-20 pb-16 md:pb-20">
          <Link
            href="/foodbanks"
            className="text-[13px] text-text-muted hover:text-text inline-flex items-center gap-1"
          >
            ← All foodbanks
          </Link>
          <p className="eyebrow mt-6">{bank.region.toUpperCase()} · transparency profile</p>
          <div className="mt-4 flex items-baseline gap-4 flex-wrap">
            <h1 className="display text-5xl md:text-6xl tracking-[-0.025em]">{bank.name}</h1>
            {bank.is_regional_dc ? <Badge variant="emerald">Regional DC</Badge> : null}
          </div>
          <p className="mt-5 max-w-[58ch] text-text-muted text-[15px] leading-relaxed">
            Operator profile derived from {bank.name}&apos;s most recent annual report, processed through
            AI and the FRAME methodology. Every metric below carries its source and method —
            cite this page directly in your audit trail.
          </p>
        </div>
      </section>

      <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24 grid lg:grid-cols-[minmax(0,1fr)_320px] gap-x-12 gap-y-10 items-start">
        <div className="min-w-0">

      <section className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-x-6 gap-y-8 border-y border-line py-8">
        <Stat
          label="CO₂e baseline"
          value={bank.annual_tco2e != null ? formatTCO2e(bank.annual_tco2e) : "—"}
          hint="Annual, FRAME-computed"
        />
        <Stat
          label="Rescued"
          value={bank.annual_kg_rescued != null ? formatKg(bank.annual_kg_rescued) : "—"}
          hint="kg / yr"
        />
        <Stat
          label="Households"
          value={bank.households_weekly != null ? formatNumber(bank.households_weekly) : "—"}
          hint="per week"
        />
        <Stat
          label="People served"
          value={bank.people_served != null ? formatNumber(bank.people_served) : "—"}
          hint="individuals / yr"
        />
      </section>

      {timeline.length > 0 ? (
        <section className="mt-16 min-w-0">
          <div className="flex items-end justify-between flex-wrap gap-3">
            <div>
              <p className="eyebrow">Historical performance</p>
              <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[24ch]">
                Annual CO₂e baseline since {timeline[0].year}.
              </h2>
            </div>
            <p className="text-[12.5px] text-text-faint tabular">
              {timeline.length} reports · FRAME-computed
            </p>
          </div>
          <div className="mt-6">
            <TimelineChart data={timeline} height={280} />
          </div>
        </section>
      ) : null}

      <section className="mt-16 grid lg:grid-cols-[1.4fr_1fr] gap-x-12 gap-y-10 items-start">
        <div className="min-w-0">
          <p className="eyebrow">Category mix</p>
          <h2 className="display text-3xl mt-3 tracking-[-0.02em]">
            What this bank rescues, by mass.
          </h2>
          <p className="text-text-muted text-[14px] mt-4 max-w-[52ch]">
            Distribution of rescued food across FRAME categories. Category emission factors
            and the NL counterfactual produce the {bank.annual_tco2e != null ? formatTCO2e(bank.annual_tco2e) : "—"} baseline above.
          </p>
          <div className="mt-6">
            {bank.category_mix && bank.annual_kg_rescued ? (
              <CategoryMixBars mix={bank.category_mix} totalKg={bank.annual_kg_rescued} />
            ) : (
              <p className="text-text-muted text-[13.5px] py-8">
                Category breakdown not yet available for this bank.
              </p>
            )}
          </div>
          {bank.weighted_emission_factor != null ? (
            <p className="mt-4 text-[12.5px] text-text-faint tabular">
              Weighted EF: {bank.weighted_emission_factor.toFixed(2)} kg CO₂e per kg food (cf NL: 0.93)
            </p>
          ) : null}
        </div>

        <div>
          <p className="eyebrow">Provenance ledger</p>
          <h2 className="display text-2xl mt-3 tracking-[-0.02em]">
            Where each number comes from.
          </h2>
          <p className="text-text-muted text-[13.5px] mt-3 max-w-[40ch]">
            Every measurement we ingest is tagged with its source: extracted directly from
            the annual report, inferred from a Dutch national average, or computed.
          </p>
          <div className="mt-6 border-t border-line pt-2">
            <ProvenanceList records={bank.provenance} />
          </div>
        </div>
      </section>

      {bank.source_url ? (
        <section className="mt-16 pt-10 border-t border-line">
          <p className="eyebrow">Source document</p>
          {/^https?:\/\//.test(bank.source_url) ? (
            <a
              href={bank.source_url}
              target="_blank"
              rel="noreferrer"
              className="display-italic text-2xl text-emerald-deep hover:underline mt-2 inline-block"
            >
              {bank.source_url} →
            </a>
          ) : (
            <p className="display-italic text-2xl text-emerald-deep mt-2 break-all">
              {bank.source_url}
            </p>
          )}
          <p className="text-text-faint text-[12.5px] mt-2 tabular">
            The original annual report this profile was derived from.
          </p>
        </section>
      ) : null}
        </div>

        <aside className="lg:sticky lg:top-24 flex flex-col gap-4">
          <div className="border border-emerald/30 bg-emerald-soft/60 rounded-[var(--radius-lg)] p-6">
            <p className="eyebrow text-emerald-deep">Fund this bank</p>
            <p className="display text-2xl mt-3 tracking-[-0.015em] leading-[1.2]">
              {fundsWithBank.length > 0 ? (
                <>
                  Included in{" "}
                  <span className="display-italic text-emerald-deep tabular">
                    {fundsWithBank.length} of {packageDetails.length}
                  </span>{" "}
                  active funds.
                </>
              ) : (
                <>
                  Not yet ranked into an{" "}
                  <span className="display-italic text-emerald-deep">active fund.</span>
                </>
              )}
            </p>

            {fundsWithBank.length > 0 ? (
              <ul className="mt-5 flex flex-col gap-3">
                {fundsWithBank.map((p) => {
                  const alloc = p.projected_allocations.find(
                    (a) => a.foodbank.id === bank.id,
                  )
                  return (
                    <li key={p.id}>
                      <Link
                        href={`/funds/${p.id}`}
                        className="block border border-line/80 bg-surface rounded-[var(--radius)] p-4 hover:border-emerald-deep transition-colors"
                      >
                        <div className="flex items-baseline justify-between gap-3">
                          <span className="text-[13.5px] font-medium text-text">{p.name}</span>
                          <span className="text-[12px] text-text-faint tabular">
                            {alloc ? `${(alloc.weight_pct * 100).toFixed(1)}%` : ""}
                          </span>
                        </div>
                        <div className="mt-1 flex items-baseline justify-between gap-3 text-[12px] text-text-muted tabular">
                          <span>{p.impact_profile.replace("_", " ")}</span>
                          <span>{formatEur(p.price_eur)} / quarter</span>
                        </div>
                      </Link>
                    </li>
                  )
                })}
              </ul>
            ) : null}

            <Link
              href="/marketplace"
              className="mt-6 inline-flex items-center justify-center w-full h-11 px-5 bg-emerald text-text-on-emerald text-[14px] font-medium hover:bg-emerald-deep transition-colors rounded-[var(--radius)]"
            >
              Browse all funds →
            </Link>
            <p className="mt-3 text-[11.5px] text-text-faint italic leading-relaxed">
              Climate contribution claim — disclosed under ESRS&nbsp;E5 + S3.
              Not a Scope 1/2/3 offset.
            </p>
          </div>
        </aside>
      </div>
    </div>
  )
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="eyebrow">{label}</span>
      <span className="display tabular text-3xl md:text-4xl">{value}</span>
      {hint ? <span className="text-[12px] text-text-muted">{hint}</span> : null}
    </div>
  )
}
