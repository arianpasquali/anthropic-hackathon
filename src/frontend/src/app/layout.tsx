import type { Metadata } from "next"
import "./globals.css"
import { Header } from "@/components/nav/Header"
import { Footer } from "@/components/nav/Footer"

export const metadata: Metadata = {
  title: "Klimaatkracht — verified avoided emissions, audit-ready",
  description:
    "Klimaatkracht turns Dutch food rescue into CSRD-compliant climate impact. Buy a verified avoided-emissions package and receive an ESRS E1+S3 report — built on extracted annual reports, computed with the FRAME methodology.",
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <head>
        <link
          rel="preconnect"
          href="https://api.fontshare.com"
          crossOrigin="anonymous"
        />
        <link
          rel="preconnect"
          href="https://cdn.fontshare.com"
          crossOrigin="anonymous"
        />
        <link
          rel="stylesheet"
          href="https://api.fontshare.com/v2/css?f[]=gambarino@400,400i&f[]=switzer@400,500,600,700&f[]=jetbrains-mono@400,500&display=swap"
        />
      </head>
      <body className="min-h-screen flex flex-col bg-surface text-text">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
