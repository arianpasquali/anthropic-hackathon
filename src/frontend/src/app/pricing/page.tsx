import Link from "next/link"

export const metadata = { title: "Pricing — Klimaatkracht" }

const TIERS = [
  {
    name: "Starter",
    price: "€10k",
    period: "/ year",
    co2e: "~333 tCO₂e / yr",
    pricePerTonne: "€30 / tCO₂e",
    features: [
      "ESRS E1 + S3 annual disclosure",
      "Allocation to 3–5 foodbanks",
      "FRAME provenance report",
      "Invoiced via Solvimon",
    ],
    cta: "Buy →",
    href: "/marketplace",
    popular: false,
  },
  {
    name: "Partner",
    price: "€100k",
    period: "/ year",
    co2e: "~3,330 tCO₂e / yr",
    pricePerTonne: "€30 / tCO₂e",
    features: [
      "Everything in Starter",
      "Allocation to 10–15 foodbanks",
      "Quarterly SSE-streamed CSRD report",
      "Priority extraction queue",
      "Named on partner page",
    ],
    cta: "Buy →",
    href: "/marketplace",
    popular: true,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "/ year",
    co2e: "Custom tCO₂e",
    pricePerTonne: "Negotiated",
    features: [
      "Everything in Partner",
      "Dedicated account manager",
      "Custom allocation logic",
      "White-label reporting",
      "SLA + audit support",
    ],
    cta: "Schedule a call →",
    href: "mailto:hello@klimaatkracht.nl",
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
          Every tier includes ESRS E1 + S3 disclosure. Pay for verified impact,
          not platform seats.
        </p>
      </div>

      <div className="grid md:grid-cols-3 gap-6 items-stretch">
        {TIERS.map((tier) => (
          <div
            key={tier.name}
            className={`relative flex flex-col rounded-2xl border p-8 ${
              tier.popular
                ? "border-[#388e3c] bg-[#f0fdf4] shadow-lg shadow-green-100"
                : "border-line bg-surface"
            }`}
          >
            {tier.popular && (
              <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                <span className="bg-[#388e3c] text-white text-[11px] font-bold uppercase tracking-wide px-3 py-1 rounded-full">
                  Most popular
                </span>
              </div>
            )}

            <div className="mb-6">
              <p className="text-[13px] font-semibold text-text-muted uppercase tracking-wide">
                {tier.name}
              </p>
              <div className="mt-2 flex items-baseline gap-1">
                <span className="display text-4xl tracking-tight">{tier.price}</span>
                <span className="text-text-muted text-[13px]">{tier.period}</span>
              </div>
              <p className="text-[13px] text-[#059669] font-medium mt-1">{tier.co2e}</p>
              <p className="text-[11px] text-text-muted mt-0.5">{tier.pricePerTonne}</p>
            </div>

            <ul className="flex flex-col gap-2.5 flex-1 mb-8">
              {tier.features.map((f) => (
                <li key={f} className="flex items-start gap-2.5 text-[13.5px]">
                  <span className="mt-0.5 shrink-0 text-[#388e3c] font-bold">✓</span>
                  {f}
                </li>
              ))}
            </ul>

            <Link
              href={tier.href}
              className={`block text-center py-3 rounded-lg text-[14px] font-bold transition-colors ${
                tier.popular
                  ? "bg-[#388e3c] text-white hover:bg-[#2e7d32]"
                  : "bg-surface-2 text-text border border-line hover:bg-[#f0fdf4] hover:border-[#388e3c]"
              }`}
            >
              {tier.cta}
            </Link>
          </div>
        ))}
      </div>

      <p className="text-center text-[12px] text-text-muted mt-10">
        All prices excl. VAT · No lock-in · Cancel anytime · Annual ESRS disclosure included in every tier
      </p>
    </main>
  )
}
