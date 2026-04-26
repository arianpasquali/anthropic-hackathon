"use client"

const LOGOS = [
  { name: "Heineken",      src: "/SVGBrand.com_heineken_nv.svg"  },
  { name: "Philips",       src: "/philips.svg"                   },
  { name: "ASML",          src: "/ASML_Holding_N.V._logo.svg"    },
  { name: "Albert Heijn",  src: "/Albert_Heijn_Logo.svg"         },
  { name: "DSM-Firmenich", src: "/DSM-Firmenich_Logo_2023.svg"   },
]

// Duplicate for seamless loop
const TRACK = [...LOGOS, ...LOGOS]

export function LogoCarousel() {
  return (
    <div className="relative w-full overflow-hidden">
      {/* fade edges */}
      <div className="pointer-events-none absolute inset-y-0 left-0 w-10 z-10 bg-gradient-to-r from-[var(--surface)] to-transparent" />
      <div className="pointer-events-none absolute inset-y-0 right-0 w-10 z-10 bg-gradient-to-l from-[var(--surface)] to-transparent" />

      <div className="flex w-max animate-logo-scroll gap-10 items-center py-1">
        {TRACK.map(({ name, src }, i) => (
          <div
            key={`${name}-${i}`}
            className="flex-shrink-0 h-8 flex items-center opacity-35 grayscale hover:opacity-65 hover:grayscale-0 transition-all duration-300"
          >
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img
              src={src}
              alt={name}
              className="h-full w-auto object-contain"
            />
          </div>
        ))}
      </div>
    </div>
  )
}
