"use client"
import * as React from "react"
import { cn } from "@/lib/cn"

export interface TabItem {
  value: string
  label: string
}

export function TabBar({
  items,
  value,
  onChange,
  className,
}: {
  items: TabItem[]
  value: string
  onChange: (value: string) => void
  className?: string
}) {
  return (
    <div
      role="tablist"
      className={cn(
        "inline-flex border-b border-line gap-6",
        className,
      )}
    >
      {items.map((item) => {
        const active = item.value === value
        return (
          <button
            key={item.value}
            type="button"
            role="tab"
            aria-selected={active}
            onClick={() => onChange(item.value)}
            className={cn(
              "py-3 text-[13px] tracking-wide transition-colors",
              "border-b-2 -mb-[1px]",
              active
                ? "border-emerald text-text font-medium"
                : "border-transparent text-text-muted hover:text-text",
            )}
          >
            {item.label}
          </button>
        )
      })}
    </div>
  )
}
