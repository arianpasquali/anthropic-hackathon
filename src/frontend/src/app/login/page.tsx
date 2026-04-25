"use client"

import { Suspense, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/Button"
import { Input, Label } from "@/components/ui/Input"
import { api, ApiError } from "@/lib/api"

function LoginForm() {
  const router = useRouter()
  const search = useSearchParams()
  const next = search.get("next") ?? "/dashboard/corporate"
  const [email, setEmail] = useState("demo@acme.nl")
  const [password, setPassword] = useState("demo1234")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await api.login(email, password)
      router.push(next)
    } catch (e) {
      setError(e instanceof ApiError && e.status === 401 ? "Invalid email or password." : "Login failed.")
      setBusy(false)
    }
  }

  return (
    <form onSubmit={onSubmit} className="flex flex-col gap-5">
      <div className="flex flex-col gap-2">
        <Label htmlFor="email">Email</Label>
        <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="password">Password</Label>
        <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
      </div>
      {error ? <p className="text-[13px] text-warning">{error}</p> : null}
      <Button type="submit" disabled={busy} size="lg">
        {busy ? "Signing in…" : "Sign in"}
      </Button>
      <p className="text-[12.5px] text-text-faint">
        Demo: <span className="tabular">demo@acme.nl</span> / <span className="tabular">demo1234</span>
      </p>
    </form>
  )
}

export default function LoginPage() {
  return (
    <div className="mx-auto max-w-[1100px] px-6 pt-16 pb-24 grid lg:grid-cols-[1fr_1fr] gap-x-16 gap-y-10 items-start">
      <div>
        <p className="eyebrow">Sign in</p>
        <h1 className="display text-5xl mt-3 tracking-[-0.025em] max-w-[16ch]">
          Welcome back.{" "}
          <span className="display-italic text-emerald-deep">Pick up where you left off.</span>
        </h1>
        <p className="mt-5 text-text-muted text-[14.5px] max-w-[44ch] leading-relaxed">
          Klimaatkracht uses a single account for both corporate buyers and food bank
          operators. Your role determines which dashboard you land on.
        </p>
        <p className="mt-8 text-[13.5px] text-text">
          New here?{" "}
          <Link href="/register" className="text-emerald hover:underline">
            Create an account →
          </Link>
        </p>
      </div>
      <div className="border border-line rounded-[var(--radius-lg)] p-8 bg-surface">
        <Suspense>
          <LoginForm />
        </Suspense>
      </div>
    </div>
  )
}
