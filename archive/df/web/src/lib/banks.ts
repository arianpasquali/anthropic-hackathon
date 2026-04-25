import { promises as fs } from "fs";
import path from "path";

export interface EmissionFactor {
  category: string;
  kg_co2e_per_kg: number;
  source: string;
  notes: string;
}

export interface Bank {
  id: string;
  name: string;
  region: string;
  annual_kg_rescued: number;
  annual_tco2e: number;
  weighted_emission_factor: number;
  households_weekly: number | null;
  people_served: number | null;
  is_rdc: boolean;
  rdc_satellite_count: number | null;
  cluster_banks: string[];
  category_mix: Record<string, number>;
  source_url: string;
  provenance: string;
  standard_package: {
    amount_eur: number;
    attributed_tco2e: number;
    attributed_kg_food: number;
    attribution_share: number;
    is_solo_capable: boolean;
    category_breakdown: Record<string, { tco2e: number; kg_food: number }>;
  };
}

export interface MarketplaceData {
  generated_at: string;
  package: {
    price_eur: number;
    tco2e: number;
    price_per_tco2e: number;
  };
  methodology: {
    framework: string;
    counterfactual_factor_nl: number;
    counterfactual_source: string;
    emission_factors: EmissionFactor[];
  };
  banks: Bank[];
}

let cached: MarketplaceData | null = null;

export async function loadBanks(): Promise<MarketplaceData> {
  if (cached) return cached;
  const filePath = path.join(process.cwd(), "public", "banks.json");
  const raw = await fs.readFile(filePath, "utf-8");
  cached = JSON.parse(raw) as MarketplaceData;
  return cached;
}

export async function getBank(id: string): Promise<Bank | null> {
  const data = await loadBanks();
  return data.banks.find((b) => b.id === id) ?? null;
}

export function formatNumber(n: number): string {
  return new Intl.NumberFormat("en-NL").format(Math.round(n));
}

export function formatEuros(n: number): string {
  return new Intl.NumberFormat("en-NL", {
    style: "currency",
    currency: "EUR",
    maximumFractionDigits: 0,
  }).format(n);
}

export function formatPercent(n: number): string {
  return new Intl.NumberFormat("en-NL", {
    style: "percent",
    maximumFractionDigits: 1,
  }).format(n);
}
