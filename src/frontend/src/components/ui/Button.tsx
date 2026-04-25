import { cva, type VariantProps } from "class-variance-authority"
import * as React from "react"
import { cn } from "@/lib/cn"

const button = cva(
  "inline-flex items-center justify-center gap-2 font-medium transition-[background,color,border] duration-150 disabled:opacity-50 disabled:pointer-events-none whitespace-nowrap",
  {
    variants: {
      variant: {
        primary:
          "bg-emerald text-text-on-emerald hover:bg-emerald-deep border border-emerald-deep/0",
        secondary:
          "bg-surface-2 text-text border border-line hover:bg-surface-3 hover:border-line-strong",
        ghost: "bg-transparent text-text hover:bg-surface-2",
        link: "bg-transparent text-emerald underline-offset-4 hover:underline px-0 py-0 h-auto",
      },
      size: {
        sm: "h-8 px-3 text-[13px] rounded-[var(--radius)]",
        md: "h-10 px-4 text-sm rounded-[var(--radius)]",
        lg: "h-12 px-5 text-[15px] rounded-[var(--radius)]",
      },
    },
    defaultVariants: { variant: "primary", size: "md" },
  }
)

export type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof button> & { asChild?: boolean }

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(button({ variant, size }), className)} {...props} />
  )
)
Button.displayName = "Button"
