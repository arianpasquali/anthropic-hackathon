import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Climate-Action Packages — Verified Avoided Emissions",
  description:
    "Audit-ready CSR climate impact through Dutch foodbanks. FRAME-aligned methodology, ESRS E1 disclosure-ready, locked at €41.67 per tCO2e.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${inter.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-stone-50 text-stone-900 font-sans">
        <header className="border-b border-stone-200 bg-white">
          <div className="mx-auto max-w-6xl px-6 py-4 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-2 group">
              <span className="inline-block h-8 w-8 rounded-md bg-emerald-900 flex items-center justify-center text-white font-semibold text-sm">
                CA
              </span>
              <span className="font-semibold tracking-tight text-stone-900">
                Climate-Action Packages
              </span>
            </Link>
            <nav className="hidden sm:flex gap-6 text-sm text-stone-600">
              <Link href="/" className="hover:text-stone-900">Marketplace</Link>
              <Link href="/methodology" className="hover:text-stone-900">Methodology</Link>
              <a
                href="https://voedselbankennederland.nl/"
                target="_blank"
                rel="noreferrer"
                className="hover:text-stone-900"
              >
                Foodbanks
              </a>
            </nav>
          </div>
        </header>
        <main className="flex-1">{children}</main>
        <footer className="border-t border-stone-200 bg-white">
          <div className="mx-auto max-w-6xl px-6 py-8 text-xs text-stone-500 flex flex-col sm:flex-row gap-2 sm:justify-between">
            <span>© 2026 Climate-Action Packages — Demo build, not for production use.</span>
            <span>Methodology aligned with the Global Foodbanking Network FRAME framework.</span>
          </div>
        </footer>
      </body>
    </html>
  );
}
