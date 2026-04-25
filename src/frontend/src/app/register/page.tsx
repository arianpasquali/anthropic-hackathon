"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { Button } from "@/components/ui/Button"
import { Input, Label } from "@/components/ui/Input"
import { api, ApiError } from "@/lib/api"

export default function RegisterPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [orgName, setOrgName] = useState("")
  const [role, setRole] = useState<"corporate" | "foodbank">("corporate")
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      await api.register(email, password, role, orgName)
      await api.login(email, password)
      router.push(role === "corporate" ? "/dashboard/corporate" : "/dashboard/foodbank")
    } catch (e) {
      setError(e instanceof ApiError && e.status === 409 ? "Email already registered." : "Registration failed.")
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-[1100px] px-6 pt-16 pb-24 grid lg:grid-cols-[1fr_1fr] gap-x-16 gap-y-10 items-start">
      <div>
        <p className="eyebrow">Create account</p>
        <h1 className="display text-5xl mt-3 tracking-[-0.025em] max-w-[18ch]">
          Onboard your team.{" "}
          <span className="display-italic text-emerald-deep">Pick a role to begin.</span>
        </h1>
        <p className="mt-5 text-text-muted text-[14.5px] max-w-[44ch] leading-relaxed">
          Corporate buyers purchase funds and view CSR reports. Food bank operators
          upload annual reports and track sponsorship.
        </p>
        <p className="mt-8 text-[13.5px] text-text">
          Already have an account?{" "}
          <Link href="/login" className="text-emerald hover:underline">
            Sign in →
          </Link>
        </p>
      </div>

      <form
        onSubmit={onSubmit}
        className="border border-line rounded-[var(--radius-lg)] p-8 bg-surface flex flex-col gap-5"
      >
        <div className="flex gap-2">
          <RoleButton active={role === "corporate"} onClick={() => setRole("corporate")}>
            Corporate buyer
          </RoleButton>
          <RoleButton active={role === "foodbank"} onClick={() => setRole("foodbank")}>
            Food bank operator
          </RoleButton>
        </div>

        <div className="flex flex-col gap-2">
          <Label htmlFor="org">Organisation name</Label>
          <Input id="org" value={orgName} onChange={(e) => setOrgName(e.target.value)} required />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">Password</Label>
          <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={8} />
        </div>
        {error ? <p className="text-[13px] text-warning">{error}</p> : null}
        <Button type="submit" disabled={busy} size="lg">
          {busy ? "Creating account…" : "Create account"}
        </Button>
      </form>
    </div>
  )
}

function RoleButton({
  active,
  children,
  onClick,
}: {
  active: boolean
  children: React.ReactNode
  onClick: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex-1 px-4 py-3 text-[13.5px] font-medium border rounded-[var(--radius)] transition-colors ${
        active
          ? "border-emerald bg-emerald-soft text-emerald-deep"
          : "border-line bg-surface-2 text-text-muted hover:text-text"
      }`}
    >
      {children}
    </button>
  )
}
