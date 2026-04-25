import * as React from "react"
import { cn } from "@/lib/cn"

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className, ...props }, ref) => (
    <input
      ref={ref}
      className={cn(
        "h-11 w-full px-3 bg-surface-2 border border-line rounded-[var(--radius)] text-text placeholder:text-text-faint",
        "focus:outline-none focus:border-emerald focus:ring-2 focus:ring-emerald/20",
        "disabled:opacity-50 disabled:bg-surface-3",
        className,
      )}
      {...props}
    />
  ),
)
Input.displayName = "Input"

export const Label = React.forwardRef<HTMLLabelElement, React.LabelHTMLAttributes<HTMLLabelElement>>(
  ({ className, ...props }, ref) => (
    <label
      ref={ref}
      className={cn("text-[13px] font-medium text-text-muted tracking-wide", className)}
      {...props}
    />
  ),
)
Label.displayName = "Label"
