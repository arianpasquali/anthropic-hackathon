import type {
  Bank,
  DashboardMetrics,
  DashboardSubscriptionSummary,
  ImpactProfile,
  Package,
  PackageDetail,
  QuarterlyPoint,
  ReportData,
  Subscription,
  SubscriptionDetail,
  SubscriptionPacing,
  TimelinePoint,
  User,
} from "./types"

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api"

// Server components cannot use the Next rewrite proxy; hit the backend directly.
const SERVER_BASE = process.env.BACKEND_URL ?? "http://localhost:8000"

function absoluteUrl(path: string): string {
  if (typeof window === "undefined") return `${SERVER_BASE}${path}`
  return `${BASE}${path}`
}

export class ApiError extends Error {
  status: number
  body: string
  constructor(status: number, body: string) {
    super(`api ${status}: ${body}`)
    this.status = status
    this.body = body
  }
}

async function serverHeaders(): Promise<Record<string, string>> {
  // On the server, manually forward the incoming request's cookies to the
  // backend so authenticated routes (/dashboard, /report, etc.) keep working.
  if (typeof window !== "undefined") return {}
  try {
    const { cookies } = await import("next/headers")
    const jar = await cookies()
    const all = jar.getAll()
    if (!all.length) return {}
    return { cookie: all.map((c) => `${c.name}=${c.value}`).join("; ") }
  } catch {
    return {}
  }
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const fwd = await serverHeaders()
  const res = await fetch(absoluteUrl(path), {
    credentials: "include",
    cache: "no-store",
    redirect: "manual",
    ...init,
    headers: {
      "content-type": "application/json",
      ...fwd,
      ...(init?.headers ?? {}),
    },
  })
  // Treat backend redirects (303 to /login when unauthenticated) as 401.
  if (res.status >= 300 && res.status < 400) {
    throw new ApiError(401, "unauthenticated")
  }
  const text = await res.text()
  if (!res.ok) throw new ApiError(res.status, text)
  return text ? (JSON.parse(text) as T) : (undefined as T)
}

export const api = {
  // public
  listFoodbanks: () => req<Bank[]>("/foodbanks"),
  getFoodbank: (slug: string) => req<Bank>(`/foodbanks/${slug}`),
  listPackages: (profile?: ImpactProfile) =>
    req<Package[]>(`/packages${profile ? `?profile=${profile}` : ""}`),
  getPackage: (id: string) => req<PackageDetail>(`/packages/${id}`),
  getFoodbankTimeline: (slug: string) => req<TimelinePoint[]>(`/foodbanks/${slug}/timeline`),
  getPackageTimeline: (id: string) => req<TimelinePoint[]>(`/packages/${id}/timeline`),
  getDashboardTimeline: (subId: string, forecastQuarters = 8) =>
    req<QuarterlyPoint[]>(`/dashboard/${subId}/timeline?forecast_quarters=${forecastQuarters}`),
  getDashboardMetrics: (subId: string) =>
    req<DashboardMetrics>(`/dashboard/${subId}/metrics`),
  getDashboardPacing: (subId: string) =>
    req<SubscriptionPacing>(`/dashboard/${subId}/pacing`),

  // auth
  login: (email: string, password: string) =>
    req<User>("/auth/login", { method: "POST", body: JSON.stringify({ email, password }) }),
  register: (email: string, password: string, role: string, org_name?: string) =>
    req<User>("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, role, org_name }),
    }),
  me: () => req<User>("/auth/me"),
  logout: () => req<{ ok: true }>("/auth/logout", { method: "POST" }),

  // checkout
  checkout: (packageId: string) =>
    req<Subscription>(`/packages/${packageId}/checkout`, { method: "POST" }),
  pay: (subId: string) => req<Subscription>(`/checkout/${subId}/pay`, { method: "POST" }),
  confirm: (subId: string) => req<SubscriptionDetail>(`/checkout/${subId}/confirm`),

  // dashboard
  listSubscriptions: () => req<DashboardSubscriptionSummary[]>("/dashboard"),
  getSubscriptionDetail: (subId: string) =>
    req<SubscriptionDetail>(`/dashboard/${subId}`),

  // report
  generateReport: (subId: string) =>
    req<{ sub_id: string; stream_url: string }>(`/report/${subId}/generate`, {
      method: "POST",
    }),
  getReportData: (subId: string, lang: "nl" | "en" = "nl") =>
    req<ReportData>(`/report/${subId}/data?lang=${lang}`),
  reportStreamUrl: (subId: string) => `${BASE}/report/${subId}/stream`,
  reportDownloadUrl: (subId: string) => `${BASE}/report/${subId}/download`,
}
