import type { AllocationPreferences, AllocationResult, Chapter } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "/api";

export async function listChapters(): Promise<Chapter[]> {
  const response = await fetch(`${API_BASE}/chapters`);
  if (!response.ok) throw new Error(`chapters: ${response.status}`);
  const body = await response.json();
  return body.chapters;
}

export type AllocationPreviewResponse = {
  amount_eur: number;
  period_start: string;
  period_end: string;
  allocations: AllocationResult[];
};

export async function fetchAllocationPreview(input: {
  amount_eur: number;
  period_start: string;
  period_end: string;
  preferences: AllocationPreferences;
}): Promise<AllocationPreviewResponse> {
  const response = await fetch(`${API_BASE}/fund/allocation-preview`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail ?? `allocation-preview: ${response.status}`);
  }
  return response.json();
}

export type CommitInput = {
  buyer_id: string;
  fund_id: string;
  amount_eur: number;
  preferences: AllocationPreferences;
  rationale?: string;
  period_start: string;
  period_end: string;
};

export type CommitResponse = {
  commitment_id: string;
  report_id: string;
  total_food_rescued_kg: number;
  total_net_avoided_tco2e: number;
  total_households_supported: number;
};

export async function createCommitment(input: CommitInput): Promise<CommitResponse> {
  const response = await fetch(`${API_BASE}/fund/commit`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!response.ok) {
    const detail = await response.json().catch(() => ({}));
    throw new Error(detail.detail ?? `commit: ${response.status}`);
  }
  return response.json();
}

export async function fetchReport(commitmentId: string): Promise<{
  report_id: string;
  markdown: string;
  methodology_version: string;
}> {
  const response = await fetch(`${API_BASE}/reports/${commitmentId}`);
  if (!response.ok) throw new Error(`report: ${response.status}`);
  return response.json();
}
