"use client"

export function PrintButton() {
  return (
    <button
      onClick={() => window.print()}
      className="text-[12.5px] font-medium text-text-muted hover:text-text transition-colors"
    >
      Print / PDF →
    </button>
  )
}
