import type { NextConfig } from "next"

const BACKEND_URL = process.env.BACKEND_URL ?? "http://localhost:8000"

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      // Proxy all /api/* requests to the FastAPI backend so the browser sees
      // same-origin and the session cookie just works.
      { source: "/api/:path*", destination: `${BACKEND_URL}/:path*` },
    ]
  },
}

export default nextConfig
