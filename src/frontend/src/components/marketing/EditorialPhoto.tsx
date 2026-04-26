import Image from "next/image"

type Treatment = "operations" | "civic" | "ambient" | "hero"

type Props = {
  src: string
  alt: string
  /** Operations: high-impact hero. Civic: contextual Dutch architecture.
   *  Ambient: ultra-faint background tile. Each maps to a different duotone
   *  intensity defined in globals.css. */
  treatment?: Treatment
  /** Set true to render a small "stock placeholder" caption beneath the figure.
   *  Drop when the imagery is replaced with commissioned work. */
  stock?: boolean
  /** Pass-through for hero-priority loading. */
  priority?: boolean
  /** Sizes hint for next/image responsive loading. */
  sizes?: string
  /** Wrapper aspect-ratio class (e.g. "aspect-[4/5]"). */
  aspect?: string
  className?: string
}

const TREATMENT_CLASS: Record<Treatment, string> = {
  operations: "kk-photo-operations",
  civic: "kk-photo-civic",
  ambient: "kk-photo-ambient",
  hero: "kk-photo-hero",
}

export function EditorialPhoto({
  src,
  alt,
  treatment = "operations",
  stock,
  priority,
  sizes = "(min-width: 1024px) 50vw, 100vw",
  aspect = "aspect-[4/5]",
  className = "",
}: Props) {
  return (
    <figure className={className}>
      <div
        className={`relative w-full overflow-hidden ${aspect} ${TREATMENT_CLASS[treatment]}`}
      >
        <Image
          src={src}
          alt={alt}
          fill
          sizes={sizes}
          priority={priority}
          className="object-cover"
        />
      </div>
      {stock ? (
        <figcaption className="mt-2 text-[11px] text-text-faint italic leading-relaxed">
          Stock placeholder · final imagery to be commissioned
        </figcaption>
      ) : null}
    </figure>
  )
}
