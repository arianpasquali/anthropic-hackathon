import Image from "next/image"
import Link from "next/link"
import { api } from "@/lib/api"
import { FoodbankFilters } from "@/components/marketing/FoodbankFilters"
import { NLProvinceFoodbankHeatMapDynamic } from "@/components/map/NLProvinceFoodbankHeatMapDynamic"
import { ProvinceFoodbankList } from "@/components/map/ProvinceFoodbankList"
import { formatNumber, formatTCO2e } from "@/lib/format"

export const metadata = {
  title: "Foodbanks · Climate Harvest",
  description:
    "Every Dutch foodbank we have ingested. Browse FRAME-computed CO₂e baselines, food rescued, and households served — open any operator's transparency profile to cite it directly in your audit trail.",
}

export default async function FoodbanksIndexPage() {
  const banks = await api.listFoodbanks().catch(() => [])
  const totalCo2 = banks.reduce((s, b) => s + (b.annual_tco2e ?? 0), 0)
  const totalKg = banks.reduce((s, b) => s + (b.annual_kg_rescued ?? 0), 0)
  const totalHouseholds = banks.reduce((s, b) => s + (b.households_weekly ?? 0), 0)

  return (
    <div>
      <section className="relative isolate border-b border-line">
        <div aria-hidden className="kk-photo-hero absolute inset-0 -z-10">
          <Image
            src="https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?auto=format&fit=crop&w=2400&q=80"
            alt=""
            fill
            sizes="100vw"
            priority
            className="object-cover"
          />
        </div>
        <header className="mx-auto max-w-[1280px] px-6 pt-12 md:pt-20 pb-16 md:pb-20 grid md:grid-cols-[1.4fr_1fr] gap-12 items-end">
          <div>
            <p className="eyebrow">Operator network · FRAME-aligned</p>
            <h1 className="display text-5xl md:text-6xl mt-4 tracking-[-0.025em] max-w-[20ch]">
              Every foodbank.{" "}
              <span className="display-italic text-emerald-deep">One audit trail.</span>
            </h1>
          </div>
          <p className="text-text-muted text-[15px] leading-relaxed max-w-[42ch]">
            {formatNumber(banks.length)} Dutch foodbanks ingested so far. The
            Voedselbanken Nederland network counts ~170 operators in total — the
            extraction queue keeps moving each week. Open any operator&apos;s
            transparency profile to cite their FRAME workings directly.
          </p>
        </header>
      </section>

      <div className="mx-auto max-w-[1280px] px-6 pt-12 pb-24">
        <section className="mt-2">
          <FoodbankFilters banks={banks} />
        </section>

        <section className="mt-24">
          <div className="flex flex-col md:flex-row md:items-end gap-6 mb-10">
            <div className="flex-1">
              <p className="eyebrow">Bank density</p>
              <h2 className="display text-4xl mt-3 tracking-[-0.02em] max-w-[24ch]">
                {formatNumber(banks.length)} food banks across the Netherlands.
              </h2>
            </div>
            <dl className="flex flex-wrap gap-x-10 gap-y-3 pb-1 shrink-0">
              <div>
                <dt className="eyebrow">Annual baseline</dt>
                <dd className="display tabular text-3xl mt-1">{formatTCO2e(totalCo2)}</dd>
              </div>
              <div>
                <dt className="eyebrow">Rescued / yr</dt>
                <dd className="display tabular text-3xl mt-1">
                  {formatNumber(totalKg / 1_000_000, { maximumFractionDigits: 1 })}M kg
                </dd>
              </div>
              <div>
                <dt className="eyebrow">Households / wk</dt>
                <dd className="display tabular text-3xl mt-1">{formatNumber(totalHouseholds)}</dd>
              </div>
            </dl>
          </div>
          <NLProvinceFoodbankHeatMapDynamic banks={banks} />
          <div className="mt-6">
            <ProvinceFoodbankList banks={banks} />
          </div>
          <p className="mt-8 text-[13px] text-text-faint leading-relaxed max-w-[64ch]">
            Want to compare bank coverage to where Dutch poverty is actually
            concentrated?{" "}
            <Link href="/coverage" className="text-emerald hover:underline">
              See the gemeente-level coverage map →
            </Link>
          </p>
        </section>

        <section className="mt-24 grid md:grid-cols-2 gap-x-12 gap-y-8 items-start border-t border-line pt-12">
          <div>
            <p className="eyebrow">For corporate buyers</p>
            <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[20ch]">
              Fund the network through a single contribution.
            </h2>
          </div>
          <div className="text-text-muted text-[14.5px] leading-relaxed max-w-[56ch]">
            <p>
              The marketplace funds wrap top-N foodbanks per allocation profile —
              CO₂e impact, social reach, or a balance. Choose a fund and your
              quarterly contribution is split across the operators that move the
              biggest needle.
            </p>
            <Link
              href="/marketplace"
              className="mt-6 inline-flex items-center gap-2 text-emerald font-medium text-[14px] hover:underline"
            >
              Browse funds →
            </Link>
          </div>
        </section>
      </div>
    </div>
  )
}
