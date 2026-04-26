import Image from "next/image"
import Link from "next/link"
import { api } from "@/lib/api"
import { Badge } from "@/components/ui/Badge"
import { formatNumber } from "@/lib/format"
import { AdoptionSlider } from "@/components/marketing/AdoptionSlider"
import { loadImpact } from "@/lib/impact"

export const metadata = {
  title: "For food banks · Climate Harvest",
  description:
    "Upload your annual report. Claude extracts food volumes, categories, and households served — FRAME does the climate math. Once your data is in, corporates can fund your operations through verified climate-contribution packages.",
}

const PIPELINE = [
  {
    kicker: "01",
    title: "Upload your annual report",
    body: "PDF in Dutch is fine. We accept any format the report was originally published in. The bigger and messier, the better — Claude handles long-form unstructured documents better than spreadsheet templates.",
  },
  {
    kicker: "02",
    title: "Claude extracts your data",
    body: "Five parallel section-specific prompts pull food volumes, categories, household reach, demographics, and operations into typed measurements. Every field is tagged with its source: extracted, inferred from a Dutch national average, or computed.",
  },
  {
    kicker: "03",
    title: "FRAME computes your CO₂e",
    body: "kg per category × emission factor × NL counterfactual (RIVM Afvalmonitor 0.93). Aligns with the Global FoodBanking Network FRAME methodology — soon to be Gold Certified.",
  },
  {
    kicker: "04",
    title: "Corporates fund your operations",
    body: "Once you appear in the marketplace, corporates buying a Climate Harvest package allocate a verified climate contribution share to your operation. Quarterly. Auditable. Disclosed under ESRS E5 + S3, never offset.",
  },
] as const

const RECEIVES = [
  "Public transparency profile auto-generated from your report",
  "Provenance ledger — every number traceable to its source",
  "Quarterly disbursement when funds allocate to your operation",
  "Year-over-year delta tracking once you upload report #2",
  "Sponsor activity feed listing committed corporates",
] as const

const KEEPS_PRIVATE = [
  "Beneficiary records, names, household identifiers",
  "Unpublished internal financials",
  "Anything not already in your published annual report",
] as const

export default async function ForFoodbanksPage() {
  const [banks, impact] = await Promise.all([
    api.listFoodbanks().catch(() => []),
    loadImpact(),
  ])
  const totalKg = banks.reduce((s, b) => s + (b.annual_kg_rescued ?? 0), 0)
  const adoption = impact.adoption_scenarios

  return (
    <div>
      <section className="relative isolate border-b border-line">
        <div aria-hidden className="kk-photo-hero absolute inset-0 -z-10">
          <Image
            src="https://images.unsplash.com/photo-1593113598332-cd288d649433?auto=format&fit=crop&w=2400&q=80"
            alt=""
            fill
            sizes="100vw"
            priority
            className="object-cover"
          />
        </div>
        <header className="mx-auto max-w-[1280px] px-6 pt-12 md:pt-20 pb-16 md:pb-20 grid md:grid-cols-[1.4fr_1fr] gap-12 items-end">
          <div>
            <p className="eyebrow">For food bank operators · FRAME-aligned</p>
            <h1 className="display text-5xl md:text-7xl mt-4 tracking-[-0.025em] leading-[1.02] max-w-[18ch]">
              Upload your annual report.{" "}
              <span className="display-italic text-emerald-deep">
                Unlock corporate funding.
              </span>
            </h1>
            <p className="mt-6 text-text-muted text-[15.5px] leading-relaxed max-w-[58ch]">
              Climate Harvest turns the operational data already in your annual
              report into a verified CO₂e baseline that Dutch corporates can
              fund. No new templates to fill out. No new spreadsheets. No new
              auditors knocking on the door.
            </p>
            <div className="mt-9 flex flex-wrap gap-3">
              <Link
                href="/register?role=foodbank"
                className="bg-emerald text-text-on-emerald h-12 px-6 inline-flex items-center text-[14.5px] font-medium hover:bg-emerald-deep transition-colors"
              >
                Onboard your bank →
              </Link>
              <Link
                href="/methodology"
                className="border border-line h-12 px-6 inline-flex items-center text-[14.5px] hover:bg-surface-2 transition-colors"
              >
                Read the FRAME methodology
              </Link>
            </div>
          </div>
          <dl className="grid grid-cols-2 gap-x-8 gap-y-6 lg:pl-8 lg:border-l lg:border-line">
            <Stat label="Operators ingested" value={formatNumber(banks.length)} />
            <Stat label="NL network total" value="~170" />
            <Stat
              label="Annual rescue (network)"
              value={`${formatNumber(totalKg / 1_000_000, { maximumFractionDigits: 1 })}M kg`}
            />
            <Stat label="Cost to onboard" value="€0" />
          </dl>
        </header>
      </section>

      <section className="border-b border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-20">
          <p className="eyebrow">How it works</p>
          <h2 className="display text-4xl md:text-5xl mt-3 tracking-[-0.025em] max-w-[20ch]">
            One upload.{" "}
            <span className="display-italic text-emerald-deep">
              Audit-grade output.
            </span>
          </h2>
          <ol className="mt-14 grid md:grid-cols-2 lg:grid-cols-4 gap-x-8 gap-y-12">
            {PIPELINE.map((step) => (
              <li
                key={step.kicker}
                className="flex flex-col gap-3 border-t border-line pt-5"
              >
                <span className="eyebrow tabular">{step.kicker}</span>
                <h3 className="display text-[22px] tracking-[-0.015em] leading-snug">
                  {step.title}
                </h3>
                <p className="text-[13.5px] text-text-muted leading-relaxed">
                  {step.body}
                </p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section className="border-b border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-20">
          <div className="grid md:grid-cols-[1fr_1.4fr] gap-x-12 gap-y-8 items-end mb-12">
            <div>
              <p className="eyebrow">Capacity &amp; growth path</p>
              <h2 className="display text-4xl md:text-5xl mt-3 tracking-[-0.025em] leading-[1.05] max-w-[20ch]">
                Demand is bounded by your{" "}
                <span className="display-italic text-emerald-deep">
                  network capacity.
                </span>
              </h2>
            </div>
            <p className="text-text-muted text-[14.5px] leading-relaxed max-w-[58ch]">
              Climate Harvest is supply-constrained, not demand-constrained.
              Even modest CSRD-mandated corporate adoption fully books the NL
              foodbank network. The platform locks unit price and caps
              attribution per bank — your operation will not be over-sold.
            </p>
          </div>
          <AdoptionSlider
            supplyCap={adoption.supply_cap}
            packageEur={adoption.package_eur}
            packageTco2e={adoption.package_tco2e}
            totalCorporates={adoption.total_csrd_corporates_nl}
            vbnBudget={adoption.vbn_annual_budget_eur}
            vbnBudgetSourceLabel={adoption.vbn_budget_source_label}
            vbnBudgetSourceUrl={adoption.vbn_budget_source_url}
          />
        </div>
      </section>

      <section className="border-b border-line bg-surface-2">
        <div className="mx-auto max-w-[1280px] px-6 py-20 grid md:grid-cols-2 gap-x-12 gap-y-10 items-start">
          <div>
            <p className="eyebrow">What you receive</p>
            <h2 className="display text-3xl md:text-4xl mt-3 tracking-[-0.02em] max-w-[20ch]">
              A public profile.{" "}
              <span className="display-italic text-emerald-deep">
                A funding line.
              </span>
            </h2>
            <ul className="mt-8 flex flex-col gap-3">
              {RECEIVES.map((item) => (
                <Item key={item}>{item}</Item>
              ))}
            </ul>
          </div>
          <div className="border border-line bg-surface rounded-[var(--radius-lg)] p-7">
            <p className="eyebrow">What stays private</p>
            <h3 className="display text-2xl mt-3 tracking-[-0.015em]">
              Only what you already publish goes in.
            </h3>
            <ul className="mt-6 flex flex-col gap-2.5">
              {KEEPS_PRIVATE.map((item) => (
                <li
                  key={item}
                  className="flex items-start gap-2.5 text-[13.5px] text-text-muted leading-relaxed"
                >
                  <span aria-hidden className="mt-2 block w-1.5 h-1.5 bg-text-faint rounded-full shrink-0" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
            <p className="mt-6 text-[12px] text-text-faint leading-relaxed">
              GDPR-safe by design. Only aggregate fields published in your
              annual report are extracted; individual beneficiary data never
              enters the platform.
            </p>
          </div>
        </div>
      </section>

      <section className="border-b border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-20 grid md:grid-cols-[1fr_1.4fr] gap-x-12 gap-y-10 items-start">
          <div>
            <p className="eyebrow">Trust</p>
            <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[18ch]">
              We&apos;re the auditor for{" "}
              <span className="display-italic text-emerald-deep">
                your numbers.
              </span>
            </h2>
          </div>
          <div className="text-text-muted text-[14.5px] leading-relaxed max-w-[60ch] flex flex-col gap-4">
            <p>
              Every measurement we ingest carries provenance: extracted directly
              from a page of your annual report, inferred from a Dutch national
              average (CBS, RIVM), or computed from other extracted values. You
              can audit the ledger before your profile goes live.
            </p>
            <p>
              FRAME is the Global FoodBanking Network methodology used by 1,400+
              foodbanks worldwide. Our NL-specific counterfactual is RIVM
              Afvalmonitor 2024 + CBS Waste Statistics — conservative versus
              international defaults, by design.
            </p>
            <div className="mt-2 flex items-center gap-2 flex-wrap">
              <Badge variant="outline">FRAME aligned</Badge>
              <Badge variant="outline">ESRS-aligned</Badge>
              <Badge variant="outline">Contribution claim</Badge>
              <Badge variant="outline">NL-specific</Badge>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-line bg-emerald-soft/40">
        <div className="mx-auto max-w-[1280px] px-6 py-20 flex flex-col items-start gap-6">
          <p className="eyebrow">Onboard</p>
          <h2 className="display text-4xl md:text-5xl tracking-[-0.025em] max-w-[20ch] leading-[1.05]">
            Five minutes to a public transparency profile.{" "}
            <span className="display-italic text-emerald-deep">
              No spreadsheets.
            </span>
          </h2>
          <p className="text-text-muted text-[15px] max-w-[60ch] leading-relaxed">
            Create an operator account, upload your most recent annual report
            PDF, and the extraction pipeline kicks off automatically. We&apos;ll
            email you when your profile is live in the marketplace.
          </p>
          <div className="mt-2 flex flex-wrap gap-3">
            <Link
              href="/register?role=foodbank"
              className="bg-emerald text-text-on-emerald h-12 px-6 inline-flex items-center text-[14.5px] font-medium hover:bg-emerald-deep transition-colors"
            >
              Create operator account →
            </Link>
            <Link
              href="/login"
              className="border border-line h-12 px-6 inline-flex items-center text-[14.5px] hover:bg-surface transition-colors"
            >
              I already have an account
            </Link>
          </div>
          <p className="mt-2 text-[12px] text-text-faint italic">
            Free. No credit card. No lock-in. Climate Harvest earns from the
            corporate side, never from operators.
          </p>
        </div>
      </section>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <span className="eyebrow">{label}</span>
      <span className="display tabular text-[28px] md:text-[32px]">{value}</span>
    </div>
  )
}

function Item({ children }: { children: React.ReactNode }) {
  return (
    <li className="flex items-start gap-2.5 text-[14px] text-text leading-relaxed">
      <span aria-hidden className="mt-2 block w-1.5 h-1.5 bg-emerald rounded-full shrink-0" />
      <span>{children}</span>
    </li>
  )
}
