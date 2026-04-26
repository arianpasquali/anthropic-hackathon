import Link from "next/link"
import { BuyTierButton } from "@/components/marketing/BuyTierButton"
import type { ImpactProfile } from "@/lib/types"

export const metadata = { title: "Pricing — Kavel" }

type TierLike = {
  name: string
  price: string
  period: string
  co2e: string
  pricePerTonne: string
  blurb: string
  features: string[]
  marginNote?: string
}

type BuyTier = TierLike & {
  kind: "buy"
  profile: ImpactProfile
  cta: string
}

type CustomTier = TierLike & {
  kind: "custom"
  cta: string
  href: string
}

type Tier = BuyTier | CustomTier

const STARTER: BuyTier = {
  kind: "buy",
  name: "Starter",
  price: "€10k",
  period: "/ year",
  co2e: "~240 tCO₂e / yr",
  pricePerTonne: "€41.67 / tCO₂e",
  blurb:
    "Entry tier for first-time disclosers. Funds the social-reach allocation track — top households-served foodbanks across the Netherlands.",
  features: [
    "ESRS E5 + S3 annual disclosure (markdown + PDF)",
    "Allocation across top households-served food banks",
    "FRAME provenance ledger per allocation",
    "Cancel any time, no lock-in",
  ],
  cta: "Buy Social Reach Fund →",
  profile: "social_focus",
  marginNote:
    "Recommended for first-time disclosers — covers ESRS E5 obligations end-to-end.",
}

const PARTNER: BuyTier = {
  kind: "buy",
  name: "Partner",
  price: "€100k",
  period: "/ year",
  co2e: "~2,400 tCO₂e / yr",
  pricePerTonne: "€41.67 / tCO₂e",
  blurb:
    "The disclosure-grade tier for CSRD-mandated reporters. Allocation is weighted by FRAME-computed CO₂e baseline across the top operators in the network.",
  features: [
    "Everything in Starter",
    "CO₂e-weighted allocation (FRAME-baseline ranking)",
    "Quarterly SSE-streamed ESRS-aligned disclosure",
    "Priority extraction queue + named on partner page",
    "Per-tonne attribution registry — no double counting",
    "Procurement-grade invoice (NL VAT, Solvimon)",
  ],
  cta: "Buy CO₂ Impact Fund →",
  profile: "co2_focus",
}

const CUSTOM: CustomTier = {
  kind: "custom",
  name: "Custom",
  price: "Talk to us",
  period: "",
  co2e: "From 5,000 tCO₂e / yr",
  pricePerTonne: "Volume-priced",
  blurb:
    "For groups disclosing across multiple subsidiaries, multi-country operations, or with auditor-specific framing requirements. We co-design the allocation track and the disclosure structure with your sustainability lead.",
  features: [
    "Everything in Partner",
    "Multi-entity / multi-region allocation rollups",
    "White-label disclosure scaffolding for your auditor",
    "Dedicated FRAME methodology lead",
    "SLA + audit-defence support",
    "Co-marketing on the partner registry",
  ],
  cta: "Contact us →",
  href: "mailto:hello@klimaatkracht.nl?subject=Custom%20pricing%20enquiry",
}

const TIERS: Tier[] = [STARTER, PARTNER, CUSTOM]

export default function PricingPage() {
  return (
    <main className="overflow-hidden">
      <section className="border-b border-line">
        <div className="mx-auto max-w-[1280px] px-6 pt-16 md:pt-24 pb-14 grid lg:grid-cols-[1.4fr_1fr] gap-x-12 gap-y-8 items-end">
          <div>
            <p className="eyebrow">Pricing</p>
            <h1 className="display text-5xl md:text-7xl mt-4 tracking-[-0.03em] leading-[1.02] max-w-[20ch]">
              Three tiers.{" "}
              <span className="display-italic text-emerald-deep">
                One audit trail per euro.
              </span>
            </h1>
          </div>
          <p className="text-text-muted text-[15px] leading-relaxed max-w-[52ch]">
            Annual climate-contribution packages, allocated across the top Dutch
            foodbanks and disclosed under ESRS&nbsp;E5&nbsp;+&nbsp;S3. Pay for
            verified contribution, never platform seats. Same FRAME methodology,
            same provenance ledger, same auditor-defensible output at every tier.
          </p>
        </div>
      </section>

      <section className="border-b border-line bg-surface-2">
        <div className="mx-auto max-w-[1280px] px-6 py-20">
          <div className="grid lg:grid-cols-3 gap-px bg-line border border-line rounded-[var(--radius-lg)] overflow-hidden">
            <TierColumn tier={STARTER} emphasis={false} />
            <TierColumn tier={PARTNER} emphasis />
            <TierColumn tier={CUSTOM} emphasis={false} />
          </div>
        </div>
      </section>

      <section className="border-b border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-12 flex flex-wrap items-center justify-between gap-x-10 gap-y-3 text-[12.5px] text-text-faint tabular">
          <span>Invoiced via Solvimon · NL VAT 21%</span>
          <span aria-hidden>·</span>
          <span>Cancel any time</span>
          <span aria-hidden>·</span>
          <span>Annual ESRS disclosure included</span>
          <span aria-hidden>·</span>
          <span>Audit-grade provenance ledger</span>
          <span aria-hidden>·</span>
          <span>Contribution claim, not offsetting</span>
        </div>
      </section>
    </main>
  )
}

function TierColumn({ tier, emphasis }: { tier: Tier; emphasis: boolean }) {
  const bg = emphasis ? "bg-emerald-soft/40" : "bg-surface"
  return (
    <article className={`flex flex-col p-8 md:p-10 ${bg}`}>
      <header className="flex flex-col gap-4">
        <p className="eyebrow tabular">{tier.name}</p>
        <div className="flex items-baseline gap-2">
          <span
            className={`display tabular tracking-[-0.03em] leading-[0.95] ${emphasis ? "text-[64px] md:text-[80px]" : "text-[48px] md:text-[60px]"}`}
          >
            {tier.price}
          </span>
          {tier.period ? (
            <span className="text-text-muted text-[14px]">{tier.period}</span>
          ) : null}
        </div>
        <div className="flex flex-col gap-0.5">
          <p
            className={`tabular font-medium ${emphasis ? "text-[14.5px] text-emerald-deep" : "text-[13px] text-emerald-deep"}`}
          >
            {tier.co2e}
          </p>
          <p className="text-[12px] text-text-faint tabular">
            {tier.pricePerTonne}
          </p>
        </div>
        {emphasis ? (
          <p className="display-italic text-[13.5px] text-text-muted leading-snug mt-1">
            Recommended for CSRD-mandated reporters — covers ESRS&nbsp;E5 + S3
            obligations end-to-end.
          </p>
        ) : null}
      </header>

      <p
        className={`mt-6 leading-relaxed ${emphasis ? "text-[14.5px] text-text" : "text-[13.5px] text-text-muted"}`}
      >
        {tier.blurb}
      </p>

      <ul className="mt-7 flex flex-col gap-2.5">
        {tier.features.map((f) => (
          <li
            key={f}
            className="flex items-start gap-2.5 text-[13px] leading-relaxed"
          >
            <span
              aria-hidden
              className="mt-2 block w-1.5 h-1.5 bg-emerald rounded-full shrink-0"
            />
            <span>{f}</span>
          </li>
        ))}
      </ul>

      <div className="mt-auto pt-8">
        {tier.kind === "buy" ? (
          <BuyTierButton
            profile={tier.profile}
            label={tier.cta}
            popular={emphasis}
          />
        ) : (
          <Link
            href={tier.href}
            className={`block text-center py-3 rounded-[var(--radius)] text-[14px] font-medium transition-colors ${
              emphasis
                ? "bg-emerald text-text-on-emerald hover:bg-emerald-deep"
                : "bg-surface-2 text-text border border-line hover:bg-emerald-soft hover:border-emerald"
            }`}
          >
            {tier.cta}
          </Link>
        )}
      </div>
    </article>
  )
}
