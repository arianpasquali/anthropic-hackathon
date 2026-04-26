import Image from "next/image"
import { Badge } from "@/components/ui/Badge"
import { CF_NL, EMISSION_FACTORS, EMISSION_FACTOR_SOURCES, CATEGORY_LABELS } from "@/lib/methodology"

export const metadata = {
  title: "Methodology · Klimaatkracht",
  description:
    "How Klimaatkracht computes climate-contribution CO₂e from Dutch food rescue. FRAME methodology, NL counterfactual, emission factors, and provenance ledger. Contribution claim, not offsetting.",
}

const PIPELINE = [
  { kicker: "01", title: "Annual report", body: "Foodbank submits its annual report PDF (Dutch)." },
  { kicker: "02", title: "Claude extraction", body: "Five parallel section-specific prompts extract typed measurements with provenance." },
  { kicker: "03", title: "Provenance ledger", body: "Every field is tagged: extracted, inferred (national avg / category split / calculation), or manual." },
  { kicker: "04", title: "FRAME compute", body: "kg × emission factor × NL counterfactual (0.93). Per-category and total CO₂e baseline persisted." },
  { kicker: "05", title: "Contribution disclosure", body: "On corporate purchase, allocation engine ranks banks; Claude composes ESRS E5 + S3 climate-contribution disclosure, streamed back via SSE." },
] as const

const FACTOR_KEYS = ["produce", "bakery", "dry_goods", "prepared", "dairy", "eggs", "meat"] as const
const MAX_FACTOR = Math.max(...Object.values(EMISSION_FACTORS))

export default function MethodologyPage() {
  return (
    <div className="overflow-hidden">
      <section className="relative isolate">
        <div aria-hidden className="kk-photo-hero absolute inset-0 -z-10">
          <Image
            src="https://images.unsplash.com/photo-1757627550652-30788bfce978?auto=format&fit=crop&w=2400&q=80"
            alt=""
            fill
            sizes="100vw"
            priority
            className="object-cover"
          />
        </div>
        <div className="mx-auto max-w-[1100px] px-6 pt-12 md:pt-20 pb-16 md:pb-20">
        <p className="eyebrow">Methodology</p>
        <h1 className="display text-5xl md:text-7xl mt-4 tracking-[-0.03em] max-w-[18ch]">
          How we compute{" "}
          <span className="display-italic text-emerald-deep">climate contribution.</span>
        </h1>
        <p className="mt-7 text-text-muted text-[16px] max-w-[64ch] leading-relaxed">
          Klimaatkracht aligns with FRAME — the Food Recovery Avoided Methane Emissions
          methodology used by Global FoodBanking Network — and applies a Dutch-specific
          counterfactual based on RIVM Afvalmonitor 2024 + CBS Waste Statistics. Every
          number on this site can be traced back to the field it was extracted from,
          and the source it was extracted from.
        </p>
        <div className="mt-7 flex items-center gap-2 flex-wrap">
          <Badge variant="outline">FRAME aligned</Badge>
          <Badge variant="outline">ESRS-aligned</Badge>
          <Badge variant="outline">ESRS E5 + S3</Badge>
          <Badge variant="outline">Contribution claim</Badge>
          <Badge variant="outline">NL-specific</Badge>
        </div>
        </div>
      </section>

      <section id="pipeline" className="bg-surface-2 border-y border-line">
        <div className="mx-auto max-w-[1100px] px-6 py-20">
          <p className="eyebrow">Ingestion pipeline</p>
          <h2 className="display text-4xl mt-3 tracking-[-0.02em] max-w-[24ch]">
            From an annual report PDF to a contribution disclosure.
          </h2>
          <ol className="mt-12 grid md:grid-cols-5 gap-x-6 gap-y-8">
            {PIPELINE.map((step) => (
              <li key={step.kicker} className="flex flex-col gap-2 border-t border-line pt-4">
                <span className="eyebrow tabular">{step.kicker}</span>
                <h3 className="display text-xl tracking-[-0.015em]">{step.title}</h3>
                <p className="text-[13px] text-text-muted leading-relaxed">{step.body}</p>
              </li>
            ))}
          </ol>
        </div>
      </section>

      <section id="frame" className="mx-auto max-w-[1100px] px-6 py-24">
        <p className="eyebrow">Core formula</p>
        <h2 className="display text-4xl mt-3 tracking-[-0.02em]">
          The arithmetic, in one line.
        </h2>
        <pre className="mt-8 bg-surface border border-line rounded-[var(--radius-lg)] p-7 font-mono text-[14px] text-text overflow-x-auto">
          <code>
            <span className="text-emerald-deep">CO₂e</span> ={" "}
            <span className="text-text">Σ</span>(
            <span className="text-text-muted">kg<sub>i</sub></span> ×{" "}
            <span className="text-text-muted">EF<sub>i</sub></span>) ×{" "}
            <span className="text-text-muted">CF<sub>NL</sub></span>
            {"\n"}
            <span className="text-text-faint">where</span> CF<sub>NL</sub> = {CF_NL}
            {"  "}
            <span className="text-text-faint">(NL incineration with energy recovery)</span>
          </code>
        </pre>
        <p className="mt-5 text-[13.5px] text-text-muted max-w-[60ch] leading-relaxed">
          Each food category contributes its mass times its emission factor (kg CO₂e per
          kg food). The sum is multiplied by the Dutch counterfactual — the emissions
          that would have occurred if the food were sent to the dominant Dutch waste
          route instead of being rescued.
        </p>
      </section>

      <section id="factors" className="border-y border-line bg-surface-2">
        <div className="mx-auto max-w-[1100px] px-6 py-20">
          <p className="eyebrow">Emission factors</p>
          <h2 className="display text-4xl mt-3 tracking-[-0.02em] max-w-[22ch]">
            Per category, with sources.
          </h2>
          <div className="mt-10 border border-line rounded-[var(--radius-lg)] overflow-hidden bg-surface">
            <table className="w-full text-[13.5px]">
              <thead className="bg-surface-2 text-text-muted text-left">
                <tr>
                  <Th>Category</Th>
                  <Th>EF (kg CO₂e / kg)</Th>
                  <Th>Visual</Th>
                  <Th>Source</Th>
                </tr>
              </thead>
              <tbody>
                {FACTOR_KEYS.map((k) => (
                  <tr key={k} className="border-t border-line/60">
                    <Td>{CATEGORY_LABELS[k]}</Td>
                    <Td className="tabular">{EMISSION_FACTORS[k].toFixed(1)}</Td>
                    <Td>
                      <div className="bg-surface-3 h-1.5 w-full max-w-[260px] overflow-hidden rounded-full">
                        <div
                          className="h-full bg-emerald"
                          style={{ width: `${(EMISSION_FACTORS[k] / MAX_FACTOR) * 100}%` }}
                        />
                      </div>
                    </Td>
                    <Td className="text-text-muted">{EMISSION_FACTOR_SOURCES[k]}</Td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </section>

      <section id="counterfactual" className="mx-auto max-w-[1100px] px-6 py-24 grid md:grid-cols-2 gap-x-12 gap-y-8">
        <div>
          <p className="eyebrow">NL counterfactual</p>
          <h2 className="display text-4xl mt-3 tracking-[-0.025em] max-w-[16ch]">
            0.93 — not 1.0.{" "}
            <span className="display-italic text-emerald-deep">Why it matters.</span>
          </h2>
        </div>
        <div className="text-text-muted text-[14.5px] leading-relaxed max-w-[60ch]">
          <p>
            Most international food rescue calculators apply a counterfactual of 1.0,
            assuming food would otherwise rot in landfill — generating significant methane.
            The Netherlands incinerates virtually all unrecycled waste with energy
            recovery, which produces less methane than landfill.
          </p>
          <p className="mt-4">
            We apply <span className="text-text tabular">CF<sub>NL</sub> = 0.93</span> per RIVM Afvalmonitor 2024
            and CBS Waste Statistics. This makes Klimaatkracht conservative compared to
            FRAME defaults — by design.
          </p>
        </div>
      </section>

      <section id="provenance" className="border-y border-line bg-surface-2">
        <div className="mx-auto max-w-[1100px] px-6 py-20">
          <p className="eyebrow">Provenance ledger</p>
          <h2 className="display text-4xl mt-3 tracking-[-0.025em] max-w-[22ch]">
            Every measurement carries its source.
          </h2>
          <div className="mt-10 grid md:grid-cols-2 gap-x-10 gap-y-6 max-w-[68ch]">
            <ProvenanceCard
              tag="extracted"
              variant="emerald"
              body="Read directly from the annual report. Pinpointed to a page or table cell in the source document."
            />
            <ProvenanceCard
              tag="inferred · national avg"
              body="Filled from a Dutch national average when missing — e.g. CBS household size for individuals served."
            />
            <ProvenanceCard
              tag="inferred · category split"
              body="Distributed across categories using a national typical mix when only a total is reported."
            />
            <ProvenanceCard
              tag="inferred · calculation"
              body="Derived from other extracted fields (e.g. residual = total − sum of categories)."
            />
            <ProvenanceCard
              tag="manual"
              variant="outline"
              body="Manually corrected after audit — used sparingly, always with a reviewer note."
            />
          </div>
        </div>
      </section>

      <section id="claim-type" className="mx-auto max-w-[1100px] px-6 py-20">
        <p className="eyebrow">Claim type</p>
        <h2 className="display text-4xl mt-3 tracking-[-0.025em] max-w-[22ch]">
          Climate contribution.{" "}
          <span className="display-italic text-emerald-deep">Not offsetting.</span>
        </h2>
        <div className="mt-8 grid md:grid-cols-2 gap-x-10 gap-y-4 text-text-muted text-[14px] leading-relaxed max-w-[80ch]">
          <p>
            Klimaatkracht packages fund verified climate impact at Dutch foodbanks.
            Corporates disclose this as a <span className="text-text">climate contribution</span>{" "}
            under ESRS&nbsp;E5 (resource use &amp; circular economy) and ESRS&nbsp;S3
            (affected communities) — not as Scope&nbsp;1/2/3 reduction or offset under
            ESRS&nbsp;E1.
          </p>
          <p>
            Avoided emissions are reported separately per EFRAG&nbsp;E1-4 §AR-58.
            We align with VCMI &amp; Oxford Net Zero contribution-claim guidance and the
            EU Green Claims Directive — no offset, neutrality, or compliance-substitute
            claims are made or supported.
          </p>
        </div>
      </section>

      <section className="mx-auto max-w-[1100px] px-6 py-24 border-t border-line">
        <p className="eyebrow">Trust pillars</p>
        <h2 className="display text-4xl mt-3 tracking-[-0.025em] max-w-[20ch]">
          What this approach buys you.
        </h2>
        <div className="grid md:grid-cols-3 gap-6 mt-12">
          <Pillar
            title="Deterministic compute"
            body="Same input → same output. The FRAME formula is a multiplication, not a model. Auditors can reproduce every number."
          />
          <Pillar
            title="Source citations"
            body="Each emission factor carries its source. Each measurement carries its provenance. Every figure is one click from its receipt."
          />
          <Pillar
            title="Conservative baseline"
            body="NL counterfactual of 0.93 (incineration with energy recovery), not the global default of 1.0. Less generous on purpose."
          />
        </div>
      </section>
    </div>
  )
}

function Th({ children }: { children: React.ReactNode }) {
  return (
    <th className="px-4 py-3 text-left font-medium text-[11px] tracking-[0.08em] uppercase">
      {children}
    </th>
  )
}

function Td({ children, className }: { children: React.ReactNode; className?: string }) {
  return <td className={`px-4 py-3 align-middle ${className ?? ""}`}>{children}</td>
}

function ProvenanceCard({
  tag,
  body,
  variant = "default",
}: {
  tag: string
  body: string
  variant?: "default" | "emerald" | "outline"
}) {
  return (
    <div className="border border-line rounded-[var(--radius-lg)] bg-surface p-6">
      <Badge variant={variant}>{tag}</Badge>
      <p className="text-[13.5px] text-text-muted leading-relaxed mt-3">{body}</p>
    </div>
  )
}

function Pillar({ title, body }: { title: string; body: string }) {
  return (
    <div className="border-t border-line pt-6">
      <h3 className="display text-2xl tracking-[-0.02em]">{title}</h3>
      <p className="text-text-muted text-[14px] mt-3 leading-relaxed">{body}</p>
    </div>
  )
}
