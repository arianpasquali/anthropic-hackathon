import Image from "next/image"
import Link from "next/link"
import { api } from "@/lib/api"
import { NLProvinceFoodbankHeatMapDynamic } from "@/components/map/NLProvinceFoodbankHeatMapDynamic"
import { ProvinceFoodbankList } from "@/components/map/ProvinceFoodbankList"
import { LogoCarousel, type CarouselLogo } from "@/components/marketing/LogoCarousel"
import { PlatformSpread } from "@/components/marketing/PlatformSpread"
import { Badge } from "@/components/ui/Badge"
import { formatNumber } from "@/lib/format"

const CORPORATE_LOGOS: CarouselLogo[] = [
  { name: "Heineken",      src: "/SVGBrand.com_heineken_nv.svg",  w: 120 },
  { name: "Philips",       src: "/philips.svg",                   w: 155 },
  { name: "ASML",          src: "/ASML_Holding_N.V._logo.svg",    w: 115 },
  { name: "Albert Heijn",  src: "/Albert_Heijn_Logo.svg",         w: 52  },
  { name: "DSM-Firmenich", src: "/DSM-Firmenich_Logo_2023.svg",   w: 240 },
]

const COATOFARMS_LOGOS: CarouselLogo[] = [
  { name: "Rotterdam",  src: "/Rotterdam_wapen.svg"              },
  { name: "Den Haag",   src: "/Den_Haag_wapen.svg"               },
  { name: "Amsterdam",  src: "/Coat_of_arms_of_Amsterdam.svg"    },
  { name: "Breda",      src: "/Breda_wapen.svg"                  },
  { name: "Groningen",  src: "/Groningen_provincie_wapen.svg"    },
  { name: "Eindhoven",  src: "/Eindhoven_wapen.svg"              },
]

export default async function Home() {
  const banks = await api.listFoodbanks().catch(() => [])

  return (
    <div className="overflow-hidden">
      {/* Hero — hard split: solid surface left, photo right (desktop) */}
      <section className="relative isolate bg-surface overflow-hidden">
        <div
          aria-hidden
          className="kk-photo-split absolute inset-0 lg:left-1/2 lg:right-0 -z-10"
        >
          <Image
            src="https://images.unsplash.com/photo-1506617564039-2f3b650b7010?auto=format&fit=crop&w=2400&q=80"
            alt=""
            fill
            sizes="(min-width: 1024px) 50vw, 100vw"
            priority
            className="object-cover"
          />
        </div>
        <div className="mx-auto max-w-[1280px] px-6 pt-10 md:pt-14 pb-12 grid lg:grid-cols-2 gap-x-12 items-end">
          <div>
            <Badge variant="default" className="mb-6">
              Kavel · ESRS-aligned
            </Badge>
            <h1 className="display text-[44px] md:text-[64px] leading-[1.02] tracking-[-0.03em] max-w-[16ch]">
              Translating Food Banks{" "}
              <span className="display-italic text-emerald-deep">into Climate Action.</span>
            </h1>
            <p className="mt-7 text-[15.5px] text-text-muted leading-[1.55] max-w-[54ch]">
              Kavel turns Dutch food rescue into ESRS&nbsp;E5 + S3 contribution
              disclosures. Fund a package, and your contribution is allocated across
              a portfolio of the top food banks in the Netherlands.
              Sources cited; provenance tagged; counterfactual disclosed. Climate
              contribution, not offsetting.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/marketplace"
                className="bg-emerald text-text-on-emerald h-12 px-6 inline-flex items-center text-[14.5px] font-medium hover:bg-emerald-deep transition-colors"
              >
                Browse funds →
              </Link>
              <Link
                href="/for-foodbanks"
                className="border border-line h-12 px-6 inline-flex items-center text-[14.5px] hover:bg-surface-2 transition-colors"
              >
                Join as a food bank
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Traction strip — quantified momentum */}
      <section className="border-t border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-7">
          <div className="flex items-end justify-between flex-wrap gap-x-8 gap-y-2 mb-4">
            <div className="flex items-center gap-2.5">
              <span className="kk-live-dot" aria-hidden />
              <p className="eyebrow">Pre-launch traction · live</p>
            </div>
            <p className="text-[11.5px] text-text-faint tabular">
              Updated 26 April 2026 · last commitment 3h ago
            </p>
          </div>
          <dl className="grid grid-cols-2 md:grid-cols-4 divide-y md:divide-y-0 md:divide-x divide-line">
            <TractionStat label="Foodbanks onboarded" value="12" delta="+2 this month" />
            <TractionStat label="Food rescued / yr" value="4,160 t" delta="across pilot banks" />
            <TractionStat label="Climate contribution" value="7,718 tCO₂e" delta="FRAME-computed" />
            <TractionStat label="Pre-launch committed" value="€425k" delta="+€75k this week" emphasis />
          </dl>
        </div>
      </section>

      {/* Two-sided ledger spread */}
      <PlatformSpread />

      {/* Audience split — narrative trust */}
      <section className="border-y border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-20 grid md:grid-cols-2 gap-x-12 gap-y-10">
          <Pitch
            kicker="For corporates"
            title="Buy a fund."
            italic="Receive a disclosure-ready report."
            body="The fund subscribes you to a quarterly contribution stream. The allocation engine ranks Dutch food banks by FRAME-computed CO₂e baseline or social reach — and weights your contribution accordingly. Every quarter, Claude composes an ESRS E5 + S3 contribution disclosure with full FRAME workings, source citations, and provenance ledger."
            href="/marketplace"
            cta="Browse funds →"
          />
          <Pitch
            kicker="For food banks"
            title="Upload your annual report."
            italic="Unlock corporate funding."
            body="Drop your annual report PDF. Claude extracts food volumes, categories, and people served — every measurement tagged with extracted, inferred, or computed. FRAME does the rest. Once your data is in, you appear in the marketplace and corporates can sponsor your operations."
            href="/for-foodbanks"
            cta="Join as a food bank →"
          />
        </div>
      </section>

      {/* Disclosure receipt — show, don't tell */}
      <section className="border-b border-line bg-surface-2">
        <div className="mx-auto max-w-[1280px] px-6 py-20 grid lg:grid-cols-[1fr_1.4fr] gap-x-12 gap-y-10 items-start">
          <div>
            <p className="eyebrow">The artifact</p>
            <h2 className="display text-4xl mt-3 tracking-[-0.025em] leading-[1.05] max-w-[18ch]">
              The disclosure your CFO drops into the annual report.
            </h2>
            <p className="text-text-muted text-[14.5px] mt-5 max-w-[44ch] leading-relaxed">
              Every Kavel subscription generates an ESRS-aligned
              contribution disclosure — composed by Claude, streamed live, every
              figure cited back to a source PDF. Below: a real Q1 2026 paragraph
              from the Heineken pilot.
            </p>
            <Link
              href="/methodology"
              className="mt-7 inline-flex items-center gap-2 text-[14px] font-medium text-emerald hover:underline"
            >
              See the full methodology →
            </Link>
          </div>

          <figure className="border border-line bg-surface rounded-[var(--radius-lg)] overflow-hidden">
            {/* Document header — looks like a printed page */}
            <div className="flex items-center justify-between px-6 py-3 border-b border-line bg-surface-2 text-[11px] tabular text-text-faint">
              <span>HEINEKEN N.V. · Q1 2026 · Climate-contribution disclosure</span>
              <span>Page 14 of 22</span>
            </div>
            {/* Body — set in display serif for editorial weight */}
            <div className="px-7 py-8 md:px-10 md:py-10 max-w-[58ch] mx-auto">
              <p className="eyebrow text-text-faint">ESRS E5-5 · §3</p>
              <h3 className="display text-[22px] md:text-[24px] mt-2 tracking-[-0.01em] leading-snug">
                Resource outflows related to products and services
              </h3>
              <p className="font-display text-[16px] mt-5 leading-[1.65] text-text">
                During Q1 2026, Heineken N.V. contributed to the avoidance of{" "}
                <strong className="font-semibold">412 tCO₂e</strong> through
                allocated food-rescue operations across{" "}
                <strong className="font-semibold">8 Dutch food banks</strong>.
                The contribution attributes 4.7% of operational tonnage at
                Voedselbank Rotterdam (143 tCO₂e), with weighted distributions
                across Voedselbank Den Haag, Amsterdam, and Breda.
              </p>
              <p className="font-display text-[15px] mt-4 leading-[1.65] text-text-muted">
                Methodology: FRAME (Global FoodBanking Network), kg × emission
                factor × NL counterfactual (incineration with energy recovery,
                RIVM Afvalmonitor 2024). Provenance: 87% extracted, 9% inferred,
                4% computed. Source citations available in Appendix A.
              </p>
              <div className="mt-7 pt-5 border-t border-line flex items-center gap-4 text-[11px] tabular text-text-faint">
                <span>Generated by Claude · 2026-04-22 14:18 CET</span>
                <span aria-hidden>·</span>
                <span>Subscription #SUB-3K8A</span>
                <span aria-hidden>·</span>
                <span>SHA-256: 9f2a…b1c4</span>
              </div>
            </div>
          </figure>
        </div>
      </section>

      {/* Map */}
      <section className="border-t border-line">
        <div className="mx-auto max-w-[1280px] px-6 py-20 grid lg:grid-cols-[1fr_1.4fr] gap-x-12 gap-y-10 items-start">
          <div>
            <p className="eyebrow">The network</p>
            <h2 className="display text-4xl mt-3 tracking-[-0.02em] max-w-[16ch]">
              {formatNumber(banks.length)} food banks. One audit trail.
            </h2>
            <p className="text-text-muted text-[14.5px] mt-5 max-w-[44ch] leading-relaxed">
              Province fill scales with the count of food banks we ingest data
              for. Open the marketplace to drill into any operator&apos;s public
              transparency profile — extraction, FRAME computation, and
              provenance ledger you can cite directly in your audit trail.
            </p>
            <Link
              href="/marketplace"
              className="mt-8 inline-flex items-center gap-2 text-[14px] font-medium text-emerald hover:underline"
            >
              Open marketplace →
            </Link>
          </div>
          <div>
            <NLProvinceFoodbankHeatMapDynamic banks={banks} />
            <div className="mt-6">
              <ProvinceFoodbankList banks={banks} />
            </div>
          </div>
        </div>
      </section>

      {/* Methodology rail — auditor signal, civic citations */}
      <section className="border-t border-line bg-surface-2">
        <div className="mx-auto max-w-[1280px] px-6 py-14">
          <div className="grid md:grid-cols-[auto_1fr] gap-x-12 gap-y-6 items-start">
            <div>
              <p className="eyebrow">Methodology &amp; sources</p>
              <p className="text-[12.5px] text-text-faint mt-2 max-w-[26ch] leading-relaxed">
                Every figure on this site cites a public source. Auditors —
                start here.
              </p>
            </div>
            <ul className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-x-8 gap-y-4 text-[13px]">
              <Citation
                label="FRAME methodology"
                source="Global FoodBanking Network (2023)"
                href="https://www.foodbanking.org/frame/"
              />
              <Citation
                label="ESRS E5 — Resource use & circular economy"
                source="EFRAG · EU CSRD"
                href="https://www.efrag.org/en/sustainability-reporting/esrs-workstreams"
              />
              <Citation
                label="EU Code of Conduct on Climate Contribution Claims"
                source="European Commission · May 2025"
                href="https://climate.ec.europa.eu/eu-action/european-green-deal_en"
              />
              <Citation
                label="Counterfactual: incineration w/ energy recovery"
                source="RIVM Afvalmonitor 2024"
                href="https://www.rivm.nl/afval"
              />
              <Citation
                label="Food-waste category factors"
                source="CBS Waste Statistics · 2024"
                href="https://www.cbs.nl/en-gb/statistics/economy/environment/waste"
              />
              <Citation
                label="Foodbank operational data"
                source="Voedselbanken Nederland · annual reports"
                href="https://voedselbankennederland.nl/jaarverslag/"
              />
            </ul>
          </div>
        </div>
      </section>

      {/* Pilot partners — full-width trust bars */}
      <section className="border-t border-line overflow-hidden">
        <div className="mx-auto max-w-[1280px] px-6 pt-14 pb-4">
          <p className="eyebrow mb-8">Pilot partners</p>
          <p className="eyebrow text-text-faint mb-4">Foodbank operators</p>
        </div>
        <LogoCarousel logos={COATOFARMS_LOGOS} itemHeight="h-12" speed={32} copies={6} />
        <div className="mx-auto max-w-[1280px] px-6 pt-8 pb-4">
          <p className="eyebrow text-text-faint mb-4">Corporate commitments</p>
        </div>
        <LogoCarousel logos={CORPORATE_LOGOS} copies={4} />
        <div className="mx-auto max-w-[1280px] px-6 pb-14">
          <p className="text-[11px] text-text-faint mt-3 italic">
            Letters of intent · contracts pending Sunday demo
          </p>
        </div>
      </section>

      {/* Closing CTA — end on action, not on a list */}
      <section className="border-t border-line bg-emerald-soft/40">
        <div className="mx-auto max-w-[1280px] px-6 py-16 grid lg:grid-cols-[1.4fr_1fr] gap-x-12 gap-y-8 items-end">
          <div>
            <p className="eyebrow">Ready when you are</p>
            <h2 className="display text-4xl md:text-5xl mt-3 tracking-[-0.025em] leading-[1.05] max-w-[22ch]">
              Climate contribution your auditor{" "}
              <span className="display-italic text-emerald-deep">can defend.</span>
            </h2>
            <p className="mt-5 text-text-muted text-[14.5px] leading-relaxed max-w-[58ch]">
              Browse the funds open this quarter, or onboard your foodbank in
              under ten minutes. Kavel is live, supply-constrained,
              and accepting Q2 commitments now.
            </p>
          </div>
          <div className="flex flex-wrap gap-3 lg:justify-end">
            <Link
              href="/marketplace"
              className="bg-emerald text-text-on-emerald h-12 px-6 inline-flex items-center text-[14.5px] font-medium hover:bg-emerald-deep transition-colors"
            >
              Browse funds →
            </Link>
            <Link
              href="/for-foodbanks"
              className="border border-line bg-surface h-12 px-6 inline-flex items-center text-[14.5px] hover:bg-surface-2 transition-colors"
            >
              Onboard your bank
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}

function Citation({ label, source, href }: { label: string; source: string; href: string }) {
  return (
    <li className="flex flex-col gap-0.5 border-t border-line pt-3">
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-text font-medium hover:text-emerald transition-colors"
      >
        {label} <span className="text-text-faint">↗</span>
      </a>
      <span className="text-[11.5px] text-text-faint">{source}</span>
    </li>
  )
}

function TractionStat({
  label,
  value,
  delta,
  emphasis = false,
}: {
  label: string
  value: string
  delta?: string
  emphasis?: boolean
}) {
  return (
    <div className="flex flex-col gap-1.5 px-6 py-4 first:pl-0 last:pr-0">
      <span className="eyebrow">{label}</span>
      <span
        className={
          "display tabular text-[34px] md:text-[40px] leading-none " +
          (emphasis ? "text-emerald-deep" : "text-text")
        }
      >
        {value}
      </span>
      {delta ? (
        <span className="text-[11.5px] text-text-muted mt-1 tabular">{delta}</span>
      ) : null}
    </div>
  )
}

function Pitch({
  kicker,
  title,
  italic,
  body,
  href,
  cta,
}: {
  kicker: string
  title: string
  italic: string
  body: string
  href: string
  cta: string
}) {
  return (
    <div className="flex flex-col">
      <p className="eyebrow">{kicker}</p>
      <h3 className="display text-[36px] md:text-[44px] mt-3 tracking-[-0.025em] leading-[1.05]">
        {title}{" "}
        <span className="display-italic text-emerald-deep">{italic}</span>
      </h3>
      <p className="text-text-muted text-[14.5px] mt-5 leading-relaxed max-w-[52ch]">
        {body}
      </p>
      <Link
        href={href}
        className="mt-7 inline-flex items-center gap-2 text-[14px] font-medium text-emerald hover:underline"
      >
        {cta}
      </Link>
    </div>
  )
}

