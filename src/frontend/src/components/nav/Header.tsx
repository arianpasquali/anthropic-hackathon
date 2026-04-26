import Link from "next/link"

export function Header() {
  return (
    <header className="sticky top-0 z-30 backdrop-blur-md bg-surface/85 border-b border-line">
      <div className="mx-auto max-w-[1280px] px-6 h-14 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-baseline gap-2 group"
          aria-label="Climate Harvest — home"
        >
          <span
            aria-hidden
            className="block w-2.5 h-2.5 bg-emerald rounded-[1px] translate-y-[1px] group-hover:bg-emerald-deep transition-colors"
          />
          <span className="text-[17px] font-semibold tracking-[-0.02em]">
            Climate Harvest
          </span>
        </Link>

        <nav className="flex items-center gap-7 text-[13px] tracking-wide">
          <Link href="/" className="text-text-muted hover:text-text transition-colors">
            Start here
          </Link>
          <Link href="/marketplace" className="text-text-muted hover:text-text transition-colors">
            Marketplace
          </Link>
          <Link href="/methodology" className="text-text-muted hover:text-text transition-colors">
            Methodology
          </Link>
          <Link href="/for-foodbanks" className="text-text-muted hover:text-text transition-colors">
            For food banks
          </Link>
          <Link href="/why" className="text-text-muted hover:text-text transition-colors">
            Why
          </Link>
          <Link
            href="/login"
            className="text-text border border-line px-3 py-1.5 hover:bg-surface-2 transition-colors"
          >
            Sign in
          </Link>
        </nav>
      </div>
    </header>
  )
}
