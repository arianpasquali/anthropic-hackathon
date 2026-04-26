import type { Metadata } from "next"
import "./globals.css"
import { Header } from "@/components/nav/Header"
import { Footer } from "@/components/nav/Footer"
import { AssistantSidebar } from "@/components/chat/AssistantSidebar"

export const metadata: Metadata = {
  title: "Kavel — verified climate contribution, disclosure-ready",
  description:
    "Kavel turns Dutch food rescue into ESRS-aligned climate contribution disclosures. Fund a verified climate-contribution package and receive an ESRS E5+S3 disclosure draft — built on extracted annual reports, computed with the FRAME methodology. Climate contribution, not offsetting.",
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en-NL">
      <head>
        <link rel="icon" href="/icon.svg" type="image/svg+xml" />
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
          href="https://api.fontshare.com/v2/css?f[]=boska@400,400i,500,500i,600&f[]=switzer@400,500,600,700&f[]=jetbrains-mono@400,500&display=swap"
        />
      </head>
      <body className="min-h-screen flex flex-col bg-surface text-text">
        <Header />
        <main className="flex-1">{children}</main>
        <Footer />
        <AssistantSidebar />
      </body>
    </html>
  )
}
