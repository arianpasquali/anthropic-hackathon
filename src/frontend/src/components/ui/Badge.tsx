import { cva, type VariantProps } from "class-variance-authority"
import * as React from "react"
import { cn } from "@/lib/cn"

const badge = cva(
  "inline-flex items-center gap-1.5 px-2 py-0.5 text-[11px] font-medium tracking-wider uppercase rounded-[2px]",
  {
    variants: {
      variant: {
        default: "bg-surface-3 text-text-muted border border-line",
        emerald: "bg-emerald-soft text-emerald-deep",
        outline: "bg-transparent text-text-muted border border-line",
        warning: "bg-warning-soft text-warning-deep",
      },
    },
    defaultVariants: { variant: "default" },
  },
)

export type BadgeProps = React.HTMLAttributes<HTMLSpanElement> & VariantProps<typeof badge>

export function Badge({ className, variant, ...props }: BadgeProps) {
  return <span className={cn(badge({ variant }), className)} {...props} />
}
