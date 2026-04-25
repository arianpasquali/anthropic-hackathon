import type {
  Bank,
  DashboardSubscriptionSummary,
  ImpactProfile,
  Package,
  PackageDetail,
  Subscription,
  SubscriptionDetail,
  User,
} from "./types"

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api"

// On the server we hit the backend directly (server components cannot use the
// Next rewrite proxy). On the browser we use the proxy so the session cookie
// is treated as same-origin.
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

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(absoluteUrl(path), {
    credentials: "include",
    cache: "no-store",
    ...init,
    headers: {
      "content-type": "application/json",
      ...(init?.headers ?? {}),
    },
  })
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
  reportStreamUrl: (subId: string) => `${BASE}/report/${subId}/stream`,
  reportDownloadUrl: (subId: string) => `${BASE}/report/${subId}/download`,
}
