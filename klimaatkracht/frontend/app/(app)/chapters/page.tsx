"use client";

import { useState } from "react";

type PreviewRecord = {
  chapter_id: string;
  period_start: string;
  period_end: string;
  total_kg: number;
  households_served: number;
  category_breakdown: Record<string, number>;
};

type PreviewResponse = { count: number; records: PreviewRecord[] };

export default function ChaptersUploadPage() {
  const [busy, setBusy] = useState(false);
  const [response, setResponse] = useState<PreviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onFileSelected(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;
    setBusy(true);
    setError(null);
    setResponse(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch("/api/operations/preview", {
        method: "POST",
        body: form,
      });
      if (!res.ok) {
        const detail = await res.json().catch(() => ({}));
        setError(detail.detail?.error ?? `Upload failed (status ${res.status})`);
        return;
      }
      setResponse(await res.json());
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-3xl font-semibold tracking-tight">
        Upload operations data
      </h1>
      <p className="mt-2 max-w-2xl text-ink/70">
        Drop a CSV or .xlsx export of your chapter's monthly intake. We'll
        parse it, validate against the canonical food categories and chapter
        registry, and tell you precisely which row needs fixing if anything's
        off.
      </p>

      <label
        htmlFor="file"
        className="mt-8 flex cursor-pointer items-center justify-center rounded-md border border-dashed border-ink/30 bg-white px-8 py-12 text-sm text-ink/70 hover:bg-white"
      >
        {busy ? "Parsing…" : "Click or drop a CSV / XLSX here"}
      </label>
      <input
        id="file"
        type="file"
        accept=".csv,.xlsx"
        onChange={onFileSelected}
        className="hidden"
      />

      {error ? (
        <div className="mt-6 rounded-md border border-red-700/30 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}
        </div>
      ) : null}

      {response ? (
        <div className="mt-8 rounded-md border border-ink/10 bg-white p-6">
          <h2 className="text-lg font-semibold">
            {response.count} record{response.count === 1 ? "" : "s"} parsed
          </h2>
          <ul className="mt-4 space-y-3 text-sm">
            {response.records.map((r, i) => (
              <li
                key={i}
                className="rounded-md border border-ink/10 px-4 py-3"
              >
                <div className="flex items-baseline justify-between">
                  <span className="font-mono text-xs">{r.chapter_id}</span>
                  <span className="text-xs text-ink/50">
                    {r.period_start} → {r.period_end}
                  </span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-ink/60">Total: </span>
                    <span className="font-medium tabular-nums">
                      {Intl.NumberFormat("en-NL").format(Math.round(r.total_kg))} kg
                    </span>
                  </div>
                  <div>
                    <span className="text-ink/60">Households: </span>
                    <span className="font-medium tabular-nums">
                      {Intl.NumberFormat("en-NL").format(r.households_served)}
                    </span>
                  </div>
                </div>
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
