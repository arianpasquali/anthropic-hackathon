"use client";

import { useEffect, useState } from "react";

type ReportSummary = {
  report_id: string;
  commitment_id: string;
  period_start: string;
  period_end: string;
  methodology_version: string;
  markdown: string;
  json_data: { totals: { total_food_rescued_kg: number; total_net_avoided_tco2e: number; total_households_supported: number } };
};

export default function PortfolioPage() {
  const [report, setReport] = useState<ReportSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [commitmentId, setCommitmentId] = useState("");

  useEffect(() => {
    if (!commitmentId) return;
    setError(null);
    fetch(`/api/reports/${commitmentId}`)
      .then(async (response) => {
        if (!response.ok) throw new Error(`status ${response.status}`);
        return response.json();
      })
      .then((body) => setReport(body))
      .catch((e) => setError(String(e.message)));
  }, [commitmentId]);

  return (
    <div className="mx-auto max-w-4xl px-6 py-12">
      <h1 className="text-3xl font-semibold tracking-tight">Portfolio</h1>
      <p className="mt-2 text-ink/70">
        Look up a generated quarterly report by commitment id.
      </p>

      <div className="mt-6 flex gap-2">
        <input
          value={commitmentId}
          onChange={(e) => setCommitmentId(e.target.value)}
          placeholder="commitment id"
          className="flex-1 rounded-md border border-ink/15 bg-white px-3 py-2 text-sm focus:border-ink focus:outline-none"
        />
      </div>

      {error ? (
        <p className="mt-4 text-sm text-red-700">{error}</p>
      ) : null}

      {report ? (
        <article className="mt-10 rounded-md border border-ink/10 bg-white p-6">
          <header className="mb-6 border-b border-ink/10 pb-4">
            <h2 className="text-xl font-semibold">
              Q{periodToQuarter(report.period_start)} report
            </h2>
            <p className="mt-1 text-sm text-ink/60">
              {report.period_start} → {report.period_end} ·
              methodology {report.methodology_version}
            </p>
          </header>
          <pre className="whitespace-pre-wrap text-sm leading-relaxed text-ink/90">
            {report.markdown}
          </pre>
        </article>
      ) : null}
    </div>
  );
}

function periodToQuarter(periodStart: string): string {
  const month = Number(periodStart.split("-")[1] ?? "1");
  return String(Math.ceil(month / 3));
}
