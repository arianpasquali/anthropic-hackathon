import Link from "next/link"

export function Footer() {
  return (
    <footer className="mt-32 border-t border-line bg-surface-2">
      <div className="mx-auto max-w-[1280px] px-6 py-16 grid grid-cols-1 md:grid-cols-[2fr_1fr_1fr_1fr] gap-12">
        <div>
          <div className="flex items-baseline gap-2 mb-4">
            <span aria-hidden className="block w-2.5 h-2.5 bg-emerald rounded-[1px] translate-y-[1px]" />
            <span className="text-[17px] font-semibold tracking-[-0.02em]">
              Climate Harvest
            </span>
          </div>
          <p className="text-[13px] text-text-muted leading-relaxed max-w-[36ch]">
            Verified climate contribution from Dutch food rescue. Built on FRAME with
            ESRS&nbsp;E5+S3 contribution disclosures. Climate contribution, not offsetting.
          </p>
        </div>

        <FooterCol
          title="Product"
          links={[
            { href: "/marketplace", label: "Funds" },
            { href: "/methodology", label: "How · methodology" },
            { href: "/why", label: "Why · public data" },
            { href: "/coverage", label: "Coverage map" },
            { href: "/faq", label: "FAQ" },
            { href: "/dashboard/corporate", label: "Corporate dashboard" },
          ]}
        />
        <FooterCol
          title="For food banks"
          links={[
            { href: "/for-foodbanks", label: "How it works for operators" },
            { href: "/dashboard/foodbank", label: "Operator dashboard" },
            { href: "/register", label: "Onboard your bank" },
          ]}
        />
        <FooterCol
          title="Sources"
          links={[
            { href: "/methodology#frame", label: "FRAME methodology" },
            { href: "/methodology#counterfactual", label: "NL counterfactual" },
            { href: "/methodology#provenance", label: "Provenance ledger" },
          ]}
        />
      </div>
      <div className="border-t border-line/60">
        <div className="mx-auto max-w-[1280px] px-6 py-6 flex flex-col gap-3">
          <p className="text-[11.5px] text-text-faint leading-relaxed max-w-[88ch]">
            <span className="text-text-muted">Disclaimer.</span> Climate Harvest packages
            fund a verified climate contribution and are disclosed under ESRS&nbsp;E5
            (resource use &amp; circular economy) and S3 (affected communities).
            They are not carbon offsets, do not reduce the buyer&apos;s
            Scope&nbsp;1/2/3 footprint under ESRS&nbsp;E1, and do not constitute
            a compliance product. Avoided emissions are reported separately per
            EFRAG&nbsp;E1-4 §AR-58. Aligned with VCMI and Oxford Net Zero contribution-claim
            guidance and the EU Green Claims Directive.
          </p>
          <div className="flex flex-col md:flex-row items-center justify-between gap-2 text-[12px] text-text-faint tabular">
            <span>Built on FRAME · Aligned with Global FoodBanking Network</span>
            <span>
              © {new Date().getFullYear()} Climate Harvest · Sources: FAO · WRAP · RIVM · CBS
            </span>
          </div>
        </div>
      </div>
    </footer>
  )
}

function FooterCol({
  title,
  links,
}: {
  title: string
  links: { href: string; label: string }[]
}) {
  return (
    <div>
      <p className="eyebrow mb-3">{title}</p>
      <ul className="flex flex-col gap-2">
        {links.map((l) => (
          <li key={l.href}>
            <Link href={l.href} className="text-[13px] text-text hover:text-emerald transition-colors">
              {l.label}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  )
}
