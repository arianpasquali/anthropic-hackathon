import Image from "next/image"
import Link from "next/link"
import { Badge } from "@/components/ui/Badge"

export const metadata = {
  title: "FAQ · Kavel",
  description:
    "Hard questions about Kavel — positioning, methodology, marketplace mechanics, partnerships, and business model. Climate contribution, not offsetting.",
}

type Q = { q: string; a: React.ReactNode }
type Section = { kicker: string; title: string; intro?: string; items: Q[] }

const SECTIONS: Section[] = [
  {
    kicker: "01",
    title: "Positioning",
    intro:
      "The first question every auditor and every skeptic asks. Answered cleanly so the rest of the page can move faster.",
    items: [
      {
        q: "Is Kavel a carbon credit?",
        a: (
          <>
            <p>
              <strong>No.</strong> Not Verra-certified, not Gold Standard, not a
              voluntary offset retirement. Kavel does not issue, retire,
              or trade credits.
            </p>
            <p className="text-text-muted">
              It is an{" "}
              <em className="display-italic text-text">
                attributed climate-contribution disclosure
              </em>{" "}
              — aligned with the EU Code of Conduct on Climate Contribution Claims
              (May 2025), defensible to a Big-4 auditor under ESRS E5. Cleaner
              positioning, faster to market, no double-counting risk.
            </p>
          </>
        ),
      },
      {
        q: "Isn't this double-counting? The foodbank reports the same avoided emissions in their own report.",
        a: (
          <>
            <p>
              <strong>No.</strong> Foodbanks publish operational data — kilograms,
              households, demographics. None of the operators in our network
              currently quantify avoided emissions in their own reports.
            </p>
            <p className="text-text-muted">
              Sponsors receive the only formal climate-contribution disclosure
              derived from those operations. The foodbank does not issue a
              competing claim. We log the attribution per package; the same
              tonne is never disclosed twice.
            </p>
          </>
        ),
      },
      {
        q: "How is this different from offsetting?",
        a: (
          <>
            <p>
              Offsetting compensates a corporate's own residual emissions with
              an equal-and-opposite reduction elsewhere. Contribution funds an
              external project without counting it against the corporate's own
              footprint.
            </p>
            <p className="text-text-muted">
              Kavel sits in the contribution lane. The corporate still
              has to reduce its own scope 1/2/3 emissions. ESRS E5 disclosures
              describe resource flows — not net-zero math.
            </p>
          </>
        ),
      },
    ],
  },
  {
    kicker: "02",
    title: "Methodology",
    intro: "Why FRAME, why now, and how defensible the math is.",
    items: [
      {
        q: "Why FRAME-aligned and not FRAME-certified?",
        a: (
          <>
            <p>
              Certification is a multi-month audit. Alignment ships now and is
              fully defensible — every factor cited, every assumption surfaced,
              deterministic math, no model in the loop on the numerical path.
            </p>
            <p className="text-text-muted">
              Certification is our 2027 milestone, after the first audit cycle
              with corporate sponsors confirms the methodology survives Big-4
              review. See{" "}
              <Link href="/methodology" className="text-emerald hover:underline">
                Methodology
              </Link>{" "}
              for the full ledger.
            </p>
          </>
        ),
      },
      {
        q: "What if FRAME revises its emission factors next year?",
        a: (
          <>
            <p>
              We re-version. Disclosures carry a methodology version stamp; old
              disclosures retain the factors that were valid at the time of
              issue. New subscriptions adopt the revised factors automatically.
            </p>
            <p className="text-text-muted">
              The provenance ledger means re-computation is mechanical — every
              field traces to a source and a formula.
            </p>
          </>
        ),
      },
      {
        q: "Why is the Dutch counterfactual 0.93 and not 1.0?",
        a: (
          <>
            <p>
              The Netherlands incinerates most municipal waste with energy
              recovery — not landfill. Methane avoidance is therefore lower than
              in landfill-dominant countries. We discount by 7% per RIVM
              Afvalmonitor 2024 + CBS waste statistics.
            </p>
            <p className="text-text-muted">
              This makes Kavel more conservative than naïve FRAME
              applications and more defensible to auditors familiar with NL
              waste infrastructure.
            </p>
          </>
        ),
      },
    ],
  },
  {
    kicker: "03",
    title: "Fund mechanics",
    intro: "How packages are priced, capped, and routed.",
    items: [
      {
        q: "How is €41.67 per tCO₂e set?",
        a: (
          <>
            <p>
              Calibrated against the EU ETS 2024 average (~€73/t) and voluntary
              contribution prices (~€20–60/t). €41.67 sits where corporate
              willingness-to-pay meets foodbank operational cost recovery.
            </p>
            <p className="text-text-muted">
              The price is locked per package at purchase time. We don't run a
              spot market — predictability matters more than discovery for
              compliance buyers.
            </p>
          </>
        ),
      },
      {
        q: "What stops you over-selling a foodbank's annual capacity?",
        a: (
          <>
            <p>
              Hard cap per bank. The marketplace shows real-time remaining
              capacity. When a bank's annual baseline is sold through, packages
              route to other food banks or to a regional cluster.
            </p>
            <p className="text-text-muted">
              The locked unit price prevents a race to the bottom; the cap
              prevents over-attribution. Two corporates cannot disclose the
              same tonne.
            </p>
          </>
        ),
      },
      {
        q: "What happens if a foodbank's actuals fall short of the FRAME estimate?",
        a: (
          <>
            <p>
              Disclosures are generated against actuals, not estimates. The
              annual report is the source of truth — if Q4 numbers shrink, the
              full-year disclosure shrinks with them and a true-up is issued.
            </p>
            <p className="text-text-muted">
              Sponsors see this exposure upfront. The contract framing is
              contribution to actual operations, not a guaranteed tonne.
            </p>
          </>
        ),
      },
    ],
  },
  {
    kicker: "04",
    title: "Partnerships & ethics",
    intro: "Foodbank dignity, regulatory posture, data handling.",
    items: [
      {
        q: "Is Voedselbanken Nederland on board?",
        a: (
          <>
            <p>
              In conversation. The partnership is critical and we treat it as a
              launch gate. The platform respects every kernwaarde — no
              operations change, all-volunteer model preserved, transparent
              reporting, no exploitative branding.
            </p>
          </>
        ),
      },
      {
        q: "Doesn't this commodify foodbanks or compromise their dignity?",
        a: (
          <>
            <p>
              Foodbanks already publish their operations. We don't change what
              they do; we attribute a climate disclosure to work they already
              perform. They keep 100% of the package amount.
            </p>
            <p className="text-text-muted">
              The corporate does not place a logo on a soup kitchen. The
              disclosure is a back-office document — ESRS E5 in a CSRD
              statement, not a marketing asset.
            </p>
          </>
        ),
      },
      {
        q: "How is recipient (household) data handled?",
        a: (
          <>
            <p>
              We never receive personally identifiable data. Foodbanks share
              aggregated counts and demographic bands at municipality level.
              Disclosures cite cohorts, not individuals.
            </p>
            <p className="text-text-muted">
              GDPR posture: Kavel is the data controller for corporate
              sponsor data only. Foodbank operational data flows through a
              data-processing agreement with Voedselbanken Nederland.
            </p>
          </>
        ),
      },
    ],
  },
  {
    kicker: "05",
    title: "Business",
    intro: "Take rate, market size, and competitive moat.",
    items: [
      {
        q: "How do you make money?",
        a: (
          <>
            <p>
              <strong>5% platform fee</strong> on the corporate side, on top of
              the package price. Foodbanks receive 100% of the sponsor amount.
            </p>
            <p className="text-text-muted">
              NL TAM: ~7,000 corporates with CSRD obligations from 2026. If 1%
              buy a single package, that is €1.75M ARR at 5% take. Up-market
              packages and multi-year contracts compound from there.
            </p>
          </>
        ),
      },
      {
        q: "Why won't Heineken just do this directly with one foodbank?",
        a: (
          <>
            <p>
              Same reason they don't run their own payments rail. Methodology,
              audit trail, multi-bank aggregation, and capacity routing are
              platform work.
            </p>
            <p className="text-text-muted">
              A direct corporate↔foodbank contract concentrates exposure on one
              bank's annual baseline and exposes the corporate to
              methodological risk. We aggregate the supply side and give the
              auditor one clean disclosure asset.
            </p>
          </>
        ),
      },
      {
        q: "Why Netherlands first, not all of Europe?",
        a: (
          <>
            <p>
              CSRD applies EU-wide, but ESRS E5 disclosure quality and FRAME
              applicability vary by country waste infrastructure. NL is a
              tractable wedge: ~181 foodbanks, one umbrella organisation
              (Voedselbanken Nederland), homogeneous waste system, English-
              and Dutch-fluent corporates.
            </p>
            <p className="text-text-muted">
              Belgium and Germany follow once the NL playbook is audited.
            </p>
          </>
        ),
      },
    ],
  },
  {
    kicker: "06",
    title: "Risk & founders",
    intro: "What could break this and who is committed.",
    items: [
      {
        q: "What if the EU revises the Code of Conduct on Climate Contribution Claims?",
        a: (
          <>
            <p>
              Disclosures are versioned against the Code edition active at
              issue. A revision triggers a re-disclosure cycle for active
              subscriptions, not retroactive invalidation of prior years.
            </p>
            <p className="text-text-muted">
              We track the EU Joint Research Centre guidance quarterly and
              maintain a methodology changelog public to corporates.
            </p>
          </>
        ),
      },
      {
        q: "Founder commitment — full-time?",
        a: (
          <>
            <p>
              Yes. Confirmed before walking on stage.
            </p>
          </>
        ),
      },
      {
        q: "Is anyone else doing this?",
        a: (
          <>
            <p>
              Voluntary carbon platforms (Klima, Patch) do not touch food rescue.
              Food-rescue operators (Too Good To Go, OLIO) do not generate
              auditor-defensible ESRS disclosures. The intersection — FRAME-aligned
              contribution disclosures sold as a CSRD-grade artifact — is open.
            </p>
            <p className="text-text-muted">
              The moat is methodology rigor + foodbank network density, not
              software.
            </p>
          </>
        ),
      },
    ],
  },
]

export default function FaqPage() {
  return (
    <div className="overflow-hidden">
      <section className="relative isolate">
        <div aria-hidden className="kk-photo-hero absolute inset-0 -z-10">
          <Image
            src="https://images.unsplash.com/photo-1755599629285-91cc09a185c7?auto=format&fit=crop&w=2400&q=80"
            alt=""
            fill
            sizes="100vw"
            priority
            className="object-cover"
          />
        </div>
        <div className="mx-auto max-w-[1100px] px-6 pt-12 md:pt-20 pb-16 md:pb-20">
          <p className="eyebrow">FAQ</p>
          <h1 className="display text-5xl md:text-7xl mt-4 tracking-[-0.03em] max-w-[20ch]">
            The questions an auditor asks first.{" "}
            <span className="display-italic text-emerald-deep">Answered cleanly.</span>
          </h1>
          <p className="mt-7 text-text-muted text-[16px] max-w-[64ch] leading-relaxed">
            Kavel is a contribution claim, not an offset. ESRS E5-aligned,
            FRAME-grounded, NL-specific. Below: positioning, methodology rigor,
            marketplace mechanics, partnerships, business model, and risk —
            every answer first-sentence-is-the-answer.
          </p>
          <div className="mt-7 flex items-center gap-2 flex-wrap">
            <Badge variant="outline">Contribution claim</Badge>
            <Badge variant="outline">Not offsetting</Badge>
            <Badge variant="outline">ESRS E5</Badge>
            <Badge variant="outline">FRAME aligned</Badge>
            <Badge variant="outline">EU Code of Conduct, May 2025</Badge>
          </div>
        </div>
      </section>

      {SECTIONS.map((section, idx) => (
        <section
          key={section.kicker}
          className={
            idx % 2 === 0
              ? "bg-surface-2 border-y border-line"
              : "border-b border-line"
          }
        >
          <div className="mx-auto max-w-[1100px] px-6 py-20 grid lg:grid-cols-[1fr_2fr] gap-x-12 gap-y-10 items-start">
            <div className="lg:sticky lg:top-20">
              <span className="eyebrow tabular">{section.kicker}</span>
              <h2 className="display text-4xl mt-3 tracking-[-0.02em] leading-[1.05] max-w-[18ch]">
                {section.title}
              </h2>
              {section.intro && (
                <p className="mt-5 text-[14px] text-text-muted max-w-[44ch] leading-relaxed">
                  {section.intro}
                </p>
              )}
            </div>
            <ol className="flex flex-col">
              {section.items.map((item, i) => (
                <li
                  key={i}
                  className="border-t border-line first:border-t-0 py-8 first:pt-0"
                >
                  <h3 className="display text-[22px] md:text-[24px] tracking-[-0.01em] leading-snug max-w-[58ch]">
                    {item.q}
                  </h3>
                  <div className="mt-4 text-[14.5px] leading-relaxed flex flex-col gap-3 max-w-[62ch]">
                    {item.a}
                  </div>
                </li>
              ))}
            </ol>
          </div>
        </section>
      ))}

      <section className="border-t border-line bg-emerald-soft/30">
        <div className="mx-auto max-w-[1100px] px-6 py-16 flex flex-col md:flex-row items-start md:items-end justify-between gap-6">
          <div>
            <p className="eyebrow">Still have a question?</p>
            <h2 className="display text-3xl mt-3 tracking-[-0.02em] max-w-[20ch]">
              Read the methodology, or talk to us.
            </h2>
          </div>
          <div className="flex items-center gap-4 text-[14px]">
            <Link href="/methodology" className="text-emerald hover:underline font-medium">
              Methodology →
            </Link>
            <Link href="/marketplace" className="text-emerald hover:underline font-medium">
              Marketplace →
            </Link>
          </div>
        </div>
      </section>
    </div>
  )
}
