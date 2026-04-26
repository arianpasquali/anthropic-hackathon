"use client"

import { useRouter } from "next/navigation"

type Lang = "nl" | "en"

export function LangToggle({ lang, subId }: { lang: Lang; subId: string }) {
  const router = useRouter()
  return (
    <div className="flex items-center border border-line rounded-[var(--radius)] overflow-hidden text-[12px] font-medium">
      {(["nl", "en"] as Lang[]).map((l) => (
        <button
          key={l}
          onClick={() => router.push(`/reports/${subId}?lang=${l}`)}
          className={[
            "px-3 py-1 transition-colors",
            lang === l
              ? "bg-emerald text-text-on-emerald"
              : "text-text-muted hover:text-text hover:bg-surface-2",
          ].join(" ")}
        >
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  )
}
