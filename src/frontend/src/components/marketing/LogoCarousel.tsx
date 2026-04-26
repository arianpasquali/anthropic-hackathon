"use client"

export type CarouselLogo = { name: string; src: string }

type Props = {
  logos: CarouselLogo[]
  /** CSS height class applied to each logo container, e.g. "h-8" or "h-12" */
  itemHeight?: string
  /** Animation duration in seconds (lower = faster) */
  speed?: number
}

export function LogoCarousel({ logos, itemHeight = "h-8", speed = 28 }: Props) {
  const track = [...logos, ...logos]

  return (
    <div className="relative w-full overflow-hidden">
      <div className="pointer-events-none absolute inset-y-0 left-0 w-10 z-10 bg-gradient-to-r from-[var(--surface)] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-10 z-10 bg-gradient-to-l from-[var(--surface)] to-transparent" />

      <div
        className="flex w-max animate-logo-scroll gap-10 items-center py-1"
        style={{ animationDuration: `${speed}s` }}
      >
        {track.map(({ name, src }, i) => (
          <div
            key={`${name}-${i}`}
            className={`flex-shrink-0 ${itemHeight} flex items-center opacity-35 grayscale hover:opacity-65 hover:grayscale-0 transition-all duration-300`}
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={src} alt={name} className="h-full w-auto object-contain" />
          </div>
        ))}
      </div>
    </div>
  )
}
