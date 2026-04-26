"use client"

export type CarouselLogo = {
  name: string
  src: string
  /** Optional explicit container width (px). When set, logo is object-contained
   *  within a fixed w×itemHeight box, normalising visual weight across logos
   *  with very different aspect ratios. */
  w?: number
}

type Props = {
  logos: CarouselLogo[]
  /** CSS height class applied to each logo container, e.g. "h-8" or "h-12" */
  itemHeight?: string
  /** Animation duration in seconds (lower = faster) */
  speed?: number
  /**
   * Number of copies to repeat. Must be even so -50% lands on an exact copy
   * boundary. Increase for small logos that don't overflow the viewport at 2x.
   */
  copies?: number
}

export function LogoCarousel({ logos, itemHeight = "h-8", speed = 28, copies = 4 }: Props) {
  const count = copies % 2 === 0 ? copies : copies + 1
  const track = Array.from({ length: count }, () => logos).flat()

  return (
    <div className="relative w-full overflow-hidden">
      <div className="pointer-events-none absolute inset-y-0 left-0 w-10 z-10 bg-gradient-to-r from-[var(--surface)] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-10 z-10 bg-gradient-to-l from-[var(--surface)] to-transparent" />

      <div
        className="flex w-max animate-logo-scroll items-center py-1"
        style={{ animationDuration: `${speed}s` }}
      >
        {track.map(({ name, src, w }, i) => (
          <div
            key={`${name}-${i}`}
            className={`flex-shrink-0 ${itemHeight} mr-10 flex items-center opacity-35 grayscale hover:opacity-65 hover:grayscale-0 transition-all duration-300`}
            style={w ? { width: w } : undefined}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={src}
              alt={name}
              className={w ? "h-full w-full object-contain" : "h-full w-auto object-contain"}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
