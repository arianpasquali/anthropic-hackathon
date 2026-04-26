"use client"

import { useState } from "react"
import { Badge } from "@/components/ui/Badge"

const STAGES = [
  { label: "Uploading PDF", duration: 1000 },
  { label: "Parsing report", duration: 2200 },
  { label: "Computing FRAME", duration: 1100 },
  { label: "Persisting provenance", duration: 700 },
] as const

export function UploadWidget({ onComplete }: { onComplete: () => void }) {
  const [stage, setStage] = useState<number>(-1)
  const [year, setYear] = useState("2024")
  const [filename, setFilename] = useState<string | null>(null)

  function start(name: string) {
    setFilename(name)
    setStage(0)
    let acc = 0
    STAGES.forEach((s, i) => {
      acc += s.duration
      setTimeout(() => {
        if (i === STAGES.length - 1) {
          setStage(STAGES.length)
          onComplete()
        } else {
          setStage(i + 1)
        }
      }, acc)
    })
  }

  function onDrop(e: React.DragEvent<HTMLLabelElement>) {
    e.preventDefault()
    const f = e.dataTransfer.files?.[0]
    if (f) start(f.name)
  }

  function onPick(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0]
    if (f) start(f.name)
  }

  const running = stage >= 0 && stage < STAGES.length
  const done = stage === STAGES.length

  return (
    <div className="border border-line rounded-[var(--radius-lg)] bg-surface p-7">
      <div className="flex items-center justify-between flex-wrap gap-3 mb-4">
        <div>
          <p className="eyebrow">Upload annual report</p>
          <h2 className="display text-2xl mt-2 tracking-[-0.02em]">
            Drop a PDF, we handle the rest.
          </h2>
        </div>
        <label className="inline-flex items-center gap-2 text-[13px] text-text-muted">
          Year
          <select
            value={year}
            onChange={(e) => setYear(e.target.value)}
            className="border border-line bg-surface-2 h-8 px-2 rounded-[var(--radius)]"
          >
            <option>2023</option>
            <option>2024</option>
            <option>2025</option>
          </select>
        </label>
      </div>

      <label
        onDrop={onDrop}
        onDragOver={(e) => e.preventDefault()}
        className="block border border-dashed border-line-strong bg-surface-2 rounded-[var(--radius-lg)] p-8 text-center cursor-pointer hover:bg-surface-3 transition-colors"
      >
        <input type="file" accept="application/pdf" hidden onChange={onPick} />
        <p className="text-[14px] text-text">Drop a PDF or click to choose</p>
        <p className="text-[12px] text-text-muted mt-1">
          Demo: any PDF triggers a mocked extraction pipeline.
        </p>
        {filename ? (
          <p className="text-[12px] text-text-faint mt-2 tabular">{filename}</p>
        ) : null}
      </label>

      {(running || done) && (
        <ol className="mt-6 flex flex-col gap-3">
          {STAGES.map((s, i) => {
            const state = stage > i ? "done" : stage === i ? "active" : "pending"
            return (
              <li key={s.label} className="flex items-center gap-3 text-[13.5px]">
                <span
                  aria-hidden
                  className={`w-1.5 h-1.5 rounded-full ${
                    state === "done"
                      ? "bg-emerald-deep"
                      : state === "active"
                        ? "bg-emerald animate-pulse"
                        : "bg-line"
                  }`}
                />
                <span className={state === "pending" ? "text-text-faint" : "text-text"}>
                  {s.label}
                </span>
                {state === "done" ? <Badge variant="emerald">ok</Badge> : null}
              </li>
            )
          })}
        </ol>
      )}

      <p className="mt-6 text-[12px] text-text-faint tabular">
        ingestion model: claude-sonnet-4-6 · provenance recorded per measurement
      </p>
    </div>
  )
}
