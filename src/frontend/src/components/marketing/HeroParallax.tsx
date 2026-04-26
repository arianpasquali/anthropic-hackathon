"use client"

import { useEffect, useRef } from "react"

/**
 * Hero photo parallax. JS-driven via rAF for reliable cross-browser
 * behavior. Reads scrollY, computes a 0-1 progress over the configured
 * range, and updates a CSS custom property on the inner image. Disables
 * itself entirely under prefers-reduced-motion.
 */
type Props = {
  children: React.ReactNode
  /** Scroll distance (px) over which the parallax interpolates. */
  range?: number
  /** Maximum vertical drift in px applied to the image. */
  maxTranslateY?: number
  /** Maximum scale boost applied at end of range. */
  maxScaleBoost?: number
  className?: string
}

export function HeroParallax({
  children,
  range = 720,
  maxTranslateY = 160,
  maxScaleBoost = 0.08,
  className = "",
}: Props) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const root = ref.current
    if (!root) return
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)")
    if (reduced.matches) return

    const target = root.querySelector<HTMLImageElement>("img")
    if (!target) return

    let raf = 0
    let pending = false

    const update = () => {
      pending = false
      const progress = Math.max(0, Math.min(1, window.scrollY / range))
      const translate = progress * maxTranslateY
      const scale = 1.05 + progress * maxScaleBoost
      target.style.transform = `translate3d(0, ${translate}px, 0) scale(${scale})`
    }

    const onScroll = () => {
      if (pending) return
      pending = true
      raf = requestAnimationFrame(update)
    }

    update()
    window.addEventListener("scroll", onScroll, { passive: true })
    return () => {
      window.removeEventListener("scroll", onScroll)
      cancelAnimationFrame(raf)
    }
  }, [range, maxTranslateY, maxScaleBoost])

  return (
    <div ref={ref} className={className}>
      {children}
    </div>
  )
}
