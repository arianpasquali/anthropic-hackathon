"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"

export function Header() {
  return (
    <header className="sticky top-0 z-30 bg-surface border-b border-line">
      <div className="mx-auto max-w-[1280px] px-6 h-14 flex items-center justify-between">
        <Link
          href="/"
          className="flex items-baseline gap-2 group"
          aria-label="Kavel — home"
        >
          <img src="/logo.svg" alt="Kavel" height={22} className="block" />
        </Link>

        <nav className="flex items-center gap-7 text-[13px] tracking-wide">
          <NavLink href="/marketplace" exact={false}>Funds</NavLink>
          <NavLink href="/why">Why</NavLink>
          <NavLink href="/methodology">How</NavLink>
          <NavLink href="/for-foodbanks">For food banks</NavLink>
          <Link
            href="/login"
            className="text-text border border-line h-10 px-4 inline-flex items-center hover:bg-surface-2 transition-colors"
          >
            Sign in
          </Link>
        </nav>
      </div>
    </header>
  )
}

/**
 * NavLink — applies an emerald 1px underline when the current route matches.
 * exact=true requires equality; exact=false matches by prefix (so /marketplace
 * also lights up on /marketplace/foo).
 */
function NavLink({
  href,
  children,
  exact = true,
}: {
  href: string
  children: React.ReactNode
  exact?: boolean
}) {
  const pathname = usePathname() ?? "/"
  const active = exact ? pathname === href : pathname.startsWith(href)
  return (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={`relative pb-0.5 transition-colors ${
        active
          ? "text-text"
          : "text-text-muted hover:text-text"
      }`}
    >
      {children}
      {active ? (
        <span
          aria-hidden
          className="absolute left-0 right-0 -bottom-0.5 h-px bg-emerald"
        />
      ) : null}
    </Link>
  )
}
