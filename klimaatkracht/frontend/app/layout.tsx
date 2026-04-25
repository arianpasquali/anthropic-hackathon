import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "Klimaatkracht",
  description:
    "Verifiable climate-and-social impact attribution for corporate buyers funding food banks.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen antialiased">
        <header className="border-b border-ink/10 bg-white/60 backdrop-blur">
          <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
            <Link href="/" className="font-semibold tracking-tight">
              Klimaatkracht
            </Link>
            <nav className="flex gap-6 text-sm text-ink/70">
              <Link href="/methodology" className="hover:text-ink">
                Methodology
              </Link>
              <Link href="/fund" className="hover:text-ink">
                Fund
              </Link>
              <Link href="/portfolio" className="hover:text-ink">
                Portfolio
              </Link>
              <Link href="/chapters" className="hover:text-ink">
                Chapters
              </Link>
            </nav>
          </div>
        </header>
        <main>{children}</main>
        <footer className="mt-24 border-t border-ink/10 py-10 text-center text-sm text-ink/50">
          Methodology version <span className="font-mono">KKM-2026.1</span> ·
          Sources: Poore &amp; Nemecek 2018, EPA WARM v15, DEFRA 2024,
          Klimaatmonitor 2025
        </footer>
      </body>
    </html>
  );
}
