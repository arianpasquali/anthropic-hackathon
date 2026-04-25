import Link from "next/link"
import { BuyTierButton } from "@/components/marketing/BuyTierButton"
import type { ImpactProfile } from "@/lib/types"

export const metadata = { title: "Pricing — Klimaatkracht" }

type Tier = {
  name: string
  price: string
  period: string
  co2e: string
  pricePerTonne: string
  features: string[]
  cta: string
  profile?: ImpactProfile
  href?: string
  popular: boolean
}

const TIERS: Tier[] = [
  {
    name: "Starter",
    price: "€15k",
    period: "/ quarter",
    co2e: "~400 tCO₂e / yr",
    pricePerTonne: "€38 / tCO₂e",
    features: [
      "ESRS E1 + S3 quarterly disclosure",
      "Allocation across top households-served banks",
      "FRAME provenance report",
      "Invoiced via Solvimon",
    ],
    cta: "Buy Social Reach Fund →",
    profile: "social_focus",
    popular: false,
  },
  {
    name: "Partner",
    price: "€25k",
    period: "/ quarter",
    co2e: "~800 tCO₂e / yr",
    pricePerTonne: "€31 / tCO₂e",
    features: [
      "Everything in Starter",
      "Allocation across top CO₂e-baseline banks",
      "Quarterly SSE-streamed CSRD report",
      "Priority extraction queue",
      "Named on partner page",
    ],
    cta: "Buy CO₂ Impact Fund →",
    profile: "co2_focus",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "€50k",
    period: "/ quarter",
    co2e: "~1,500 tCO₂e / yr",
    pricePerTonne: "€33 / tCO₂e",
    features: [
      "Everything in Partner",
      "Balanced CO₂e + social allocation",
      "Dedicated account manager",
      "White-label reporting",
      "SLA + audit support",
    ],
    cta: "Buy Balanced Impact Fund →",
    profile: "balanced",
    popular: false,
  },
]

export default function PricingPage() {
  return (
    <main className="max-w-screen-lg mx-auto px-6 py-24">
      <div className="text-center mb-16">
        <p className="eyebrow">Pricing</p>
        <h1 className="display text-5xl mt-4 tracking-[-0.03em]">
          Simple, impact-linked pricing.
        </h1>
        <p className="text-text-muted text-[15px] mt-5 max-w-[48ch] mx-auto leading-relaxed">
          Every tier maps to a Fund in our marketplace. Pay for verified impact,
          not platform seats. ESRS E1 + S3 disclosure included.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 items-stretch">
        {TIERS.map((tier) => (
          <div
            key={tier.name}
            className={`relative flex flex-col rounded-[var(--radius-lg)] border p-8 ${
              tier.popular
                ? "border-emerald bg-emerald-soft/40"
                : "border-line bg-surface"
            }`}
          >
            {tier.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-emerald text-text-on-emerald text-[11px] font-medium uppercase tracking-wider px-3 py-1 rounded-full">
                  Most popular
                </span>
              </div>
            )}

            <div className="mb-6">
              <p className="eyebrow">{tier.name}</p>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="display tabular text-4xl tracking-tight">{tier.price}</span>
                <span className="text-text-muted text-[13px]">{tier.period}</span>
              </div>
              <p className="text-[13px] text-emerald-deep font-medium mt-1 tabular">{tier.co2e}</p>
              <p className="text-[11px] text-text-faint mt-0.5 tabular">{tier.pricePerTonne}</p>
            </div>

            <ul className="flex flex-col gap-2.5 flex-1 mb-8">
              {tier.features.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-[13.5px]">
                  <span className="mt-0.5 shrink-0 text-emerald-deep font-bold">✓</span>
                  {f}
                </li>
              ))}
            </ul>

            {tier.profile ? (
              <BuyTierButton profile={tier.profile} label={tier.cta} popular={tier.popular} />
            ) : (
              <Link
                href={tier.href ?? "/marketplace"}
                className="block text-center py-3 rounded-[var(--radius)] text-[14px] font-medium bg-surface-2 text-text border border-line hover:bg-emerald-soft hover:border-emerald transition-colors"
              >
                {tier.cta}
              </Link>
            )}
          </div>
        ))}
      </div>

      <p className="text-center text-[12px] text-text-faint mt-10 tabular">
        All prices excl. VAT · No lock-in · Cancel anytime · Annual ESRS disclosure included in every tier
      </p>
    </main>
  )
}
