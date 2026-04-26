"use client"

import { useEffect, useRef, useState, type FormEvent } from "react"
import Link from "next/link"
import ReactMarkdown, { type Components } from "react-markdown"
import remarkGfm from "remark-gfm"
import { cn } from "@/lib/cn"

// CTA labels for Kavel internal paths — used by the link renderer
// to upgrade bare links into call-to-action buttons.
const CTA_LABELS: Record<string, string> = {
  "/marketplace": "Browse the marketplace",
  "/reports/sample": "View a sample disclosure",
  "/methodology": "Read the methodology",
  "/faq": "Read the FAQ",
  "/foodbanks": "See the foodbank network",
  "/for-foodbanks": "Onboard a foodbank",
  "/pricing": "See pricing",
}

function isInternalKavel(href: string): { path: string; label: string } | null {
  if (!href) return null
  // Match relative `/...` or any kavel.tech URL
  const rel = href.startsWith("/")
    ? href
    : href.match(/^https?:\/\/(?:www\.)?kavel\.tech(\/[^\s]*)?$/i)?.[1] ?? null
  if (!rel) return null
  const path = rel.replace(/[).,;:!?]+$/, "") // strip trailing punctuation
  const cleanPath = path.split("?")[0].split("#")[0] || "/"
  const label = CTA_LABELS[cleanPath] ?? `Open ${cleanPath}`
  return { path: cleanPath, label }
}

// Linkify bare kavel.tech/... URLs and bare /<path> references the
// model emits as **bold** so they become real anchors that the markdown
// renderer can upgrade to CTAs.
function linkifyAssistantText(input: string): string {
  let out = input

  // 1. Bare URLs (with or without protocol)
  out = out.replace(
    /(https?:\/\/)?(?:www\.)?kavel\.tech(\/[a-z0-9/_-]*)?/gi,
    (match) => {
      const url = match.startsWith("http") ? match : `https://${match.replace(/^www\./, "")}`
      return `[${match}](${url})`
    },
  )

  // 2. Unwrap bold-wrapped links: **[text](url)** → [text](url)
  out = out.replace(/\*\*(\[[^\]]+\]\([^)]+\))\*\*/g, "$1")

  return out
}

type Role = "user" | "assistant"

type Message = {
  id: string
  role: Role
  content: string
  pending?: boolean
}

type ChatResponse = {
  reply: string
  task_id: string
  response_id: string
  usage?: unknown
  error?: string
}

const STORAGE_KEY = "ch-chat-state-v1"
const SUGGESTIONS = [
  "Are we eligible to buy?",
  "Is this a carbon offset?",
  "How is CO₂e calculated?",
  "What does a disclosure look like?",
] as const

const GREETING: Message = {
  id: "greet",
  role: "assistant",
  content:
    "Hi — I'm the Kavel assistant. I can answer questions about the methodology, marketplace, and ESRS E5 disclosures, and check whether your company is eligible to buy a contribution package. Where would you like to start?",
}

function uid() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36)
}

export function AssistantSidebar() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [input, setInput] = useState("")
  const [sending, setSending] = useState(false)
  const [taskId, setTaskId] = useState<string | undefined>()
  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Restore from sessionStorage so the conversation survives navigation
  useEffect(() => {
    if (typeof window === "undefined") return
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY)
      if (!raw) return
      const parsed = JSON.parse(raw) as {
        messages: Message[]
        taskId?: string
      }
      if (parsed.messages?.length) setMessages(parsed.messages)
      if (parsed.taskId) setTaskId(parsed.taskId)
    } catch {
      // ignore corrupt state
    }
  }, [])

  useEffect(() => {
    if (typeof window === "undefined") return
    try {
      sessionStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ messages, taskId }),
      )
    } catch {
      // quota / private mode — non-fatal
    }
  }, [messages, taskId])

  // Autoscroll to latest message
  useEffect(() => {
    if (!open) return
    scrollRef.current?.scrollTo({
      top: scrollRef.current.scrollHeight,
      behavior: "smooth",
    })
  }, [messages, open])

  // Focus input when opened
  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  // Esc to close
  useEffect(() => {
    if (!open) return
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false)
    }
    window.addEventListener("keydown", onKey)
    return () => window.removeEventListener("keydown", onKey)
  }, [open])

  async function send(text: string) {
    const trimmed = text.trim()
    if (!trimmed || sending) return

    const userMsg: Message = { id: uid(), role: "user", content: trimmed }
    const pendingId = uid()
    setMessages((prev) => [
      ...prev,
      userMsg,
      { id: pendingId, role: "assistant", content: "", pending: true },
    ])
    setInput("")
    setSending(true)

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: trimmed,
          task_id: taskId,
        }),
      })

      const data = (await res.json()) as ChatResponse

      if (!res.ok || data.error) {
        throw new Error(data.error ?? `HTTP ${res.status}`)
      }

      setTaskId(data.task_id)
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? { ...m, content: data.reply || "(no reply)", pending: false }
            : m,
        ),
      )
    } catch (err) {
      const message = err instanceof Error ? err.message : "Something went wrong."
      setMessages((prev) =>
        prev.map((m) =>
          m.id === pendingId
            ? { ...m, content: `⚠️ ${message}`, pending: false }
            : m,
        ),
      )
    } finally {
      setSending(false)
    }
  }

  function onSubmit(e: FormEvent) {
    e.preventDefault()
    void send(input)
  }

  function reset() {
    setMessages([GREETING])
    setTaskId(undefined)
    setInput("")
    if (typeof window !== "undefined") {
      sessionStorage.removeItem(STORAGE_KEY)
    }
  }

  return (
    <>
      {/* Floating launcher */}
      <button
        type="button"
        onClick={() => setOpen(true)}
        aria-label="Open Kavel assistant"
        className={cn(
          "fixed bottom-6 right-6 z-[1100] group",
          "h-12 pl-4 pr-5 inline-flex items-center gap-2.5",
          "bg-emerald text-text-on-emerald shadow-lg shadow-emerald/20",
          "border border-emerald-deep/20 rounded-full",
          "text-[13px] font-medium tracking-wide",
          "hover:bg-emerald-deep transition-colors",
          "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald",
          open && "pointer-events-none opacity-0 translate-y-2",
        )}
      >
        <span
          aria-hidden
          className="block w-2 h-2 rounded-[1px] bg-text-on-emerald"
        />
        Ask the assistant
      </button>

      {/* Backdrop */}
      <div
        aria-hidden
        onClick={() => setOpen(false)}
        className={cn(
          "fixed inset-0 z-[1100] transition-opacity duration-200",
          "bg-[color-mix(in_oklch,var(--text)_14%,transparent)]",
          open ? "opacity-100" : "pointer-events-none opacity-0",
        )}
      />

      {/* Slide-over panel */}
      <aside
        role="dialog"
        aria-label="Kavel assistant"
        aria-modal="true"
        className={cn(
          "fixed top-0 right-0 z-[1200] h-dvh w-full sm:w-[420px] flex flex-col",
          "bg-surface border-l border-line shadow-2xl shadow-black/10",
          "transition-transform duration-300 ease-out",
          open ? "translate-x-0" : "translate-x-full",
        )}
      >
        {/* Header */}
        <header className="flex items-center justify-between px-5 h-14 border-b border-line bg-surface-2">
          <div className="flex items-center gap-2.5">
            <span aria-hidden className="block w-2.5 h-2.5 bg-emerald rounded-[1px]" />
            <div className="leading-tight">
              <p className="text-[13.5px] font-semibold tracking-[-0.01em]">
                Kavel assistant
              </p>
              <p className="text-[11px] text-text-faint">
                FAQ · eligibility · marketplace
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              type="button"
              onClick={reset}
              className="text-[11.5px] text-text-muted hover:text-text px-2 py-1 transition-colors"
              title="Start a new conversation"
            >
              Reset
            </button>
            <button
              type="button"
              onClick={() => setOpen(false)}
              aria-label="Close assistant"
              className="text-text-muted hover:text-text p-1.5 transition-colors"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <path d="M18 6 6 18M6 6l12 12" />
              </svg>
            </button>
          </div>
        </header>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-5 flex flex-col gap-4">
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} />
          ))}

          {messages.length === 1 && (
            <div className="mt-2">
              <p className="eyebrow text-[10.5px] mb-2.5">Try asking</p>
              <div className="flex flex-col gap-1.5">
                {SUGGESTIONS.map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => void send(s)}
                    disabled={sending}
                    className="text-left text-[13px] text-text-muted hover:text-text border border-line hover:border-line-strong bg-surface-2/40 hover:bg-surface-2 px-3 py-2 rounded-[var(--radius)] transition-colors disabled:opacity-50"
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Composer */}
        <form
          onSubmit={onSubmit}
          className="border-t border-line bg-surface-2 px-3 py-3"
        >
          <div className="flex items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault()
                  void send(input)
                }
              }}
              placeholder="Ask about eligibility, methodology, packages…"
              rows={1}
              disabled={sending}
              className={cn(
                "flex-1 resize-none bg-surface border border-line",
                "text-[14px] leading-snug text-text placeholder:text-text-faint",
                "px-3 py-2.5 max-h-32 min-h-[40px]",
                "focus:outline-none focus:border-emerald focus:ring-1 focus:ring-emerald/20",
                "disabled:opacity-60",
              )}
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className={cn(
                "h-10 px-3.5 inline-flex items-center text-[13px] font-medium",
                "bg-emerald text-text-on-emerald hover:bg-emerald-deep",
                "disabled:bg-surface-3 disabled:text-text-faint disabled:cursor-not-allowed",
                "transition-colors",
              )}
            >
              {sending ? "…" : "Send"}
            </button>
          </div>
          <p className="mt-2 text-[10.5px] text-text-faint leading-snug">
            Powered by Claude via orq.ai. Answers are guidance only — confirm
            eligibility with your auditor.
          </p>
        </form>
      </aside>
    </>
  )
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user"
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[85%] text-[13.5px] leading-[1.55]",
          isUser
            ? "bg-emerald text-text-on-emerald px-3.5 py-2.5 rounded-[var(--radius-lg)] rounded-br-[2px]"
            : "text-text",
        )}
      >
        {!isUser && (
          <p className="eyebrow text-[10px] text-text-faint mb-1.5">
            Assistant
          </p>
        )}
        {message.pending ? (
          <PendingDots />
        ) : isUser ? (
          message.content
        ) : (
          <div className="prose-chat">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={MARKDOWN_COMPONENTS}
            >
              {linkifyAssistantText(message.content)}
            </ReactMarkdown>
          </div>
        )}
      </div>
    </div>
  )
}

// Renderer overrides — promote internal Kavel links to CTA buttons
const MARKDOWN_COMPONENTS: Components = {
  a({ href, children }) {
    const internal = href ? isInternalKavel(href) : null
    if (internal) {
      return <CTALink href={internal.path} label={internal.label} />
    }
    return (
      <a href={href} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    )
  },
}

function CTALink({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className={cn(
        "not-prose mt-2 mb-1 inline-flex items-center gap-2",
        "bg-emerald text-text-on-emerald hover:bg-emerald-deep",
        "px-3.5 py-2 text-[13px] font-medium tracking-wide",
        "rounded-[var(--radius)] no-underline",
        "transition-colors",
        "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-emerald",
      )}
    >
      {label}
      <span aria-hidden>→</span>
    </Link>
  )
}

function PendingDots() {
  return (
    <span className="inline-flex items-center gap-1 py-1" aria-label="thinking">
      <span className="w-1.5 h-1.5 rounded-full bg-text-faint animate-pulse [animation-delay:-200ms]" />
      <span className="w-1.5 h-1.5 rounded-full bg-text-faint animate-pulse [animation-delay:-100ms]" />
      <span className="w-1.5 h-1.5 rounded-full bg-text-faint animate-pulse" />
    </span>
  )
}
