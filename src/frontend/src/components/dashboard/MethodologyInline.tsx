import Link from "next/link"
import { CF_NL } from "@/lib/methodology"

export function MethodologyInline() {
  return (
    <div className="border border-line rounded-[var(--radius-lg)] bg-surface-2 p-5 flex flex-col md:flex-row md:items-center gap-4 justify-between">
      <div className="flex flex-col gap-1">
        <p className="eyebrow">Methodology disclosure</p>
        <p className="text-[13.5px] text-text leading-relaxed max-w-[64ch]">
          <span className="text-text-muted">FRAME-NL v1.0 ·</span>{" "}
          counterfactual <span className="tabular">CF<sub>NL</sub> = {CF_NL}</span>{" "}
          (incineration with energy recovery, RIVM Afvalmonitor 2024 + CBS Waste
          Statistics) · emission factors per FAO FWF 2013 + Poore &amp; Nemecek 2018 +
          WRAP Courtauld 2030.
        </p>
      </div>
      <Link
        href="/methodology"
        className="inline-flex items-center gap-2 text-[13px] font-medium text-emerald hover:underline whitespace-nowrap"
      >
        Full methodology →
      </Link>
    </div>
  )
}
