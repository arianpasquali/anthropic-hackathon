// Client-safe: types + formatters only. No `fs`. Used from both server and client components.

export interface Stat {
  value: number;
  unit: string;
  label: string;
  source_label: string;
  source_url: string;
}

export interface HistoryPoint {
  year: number;
  people: number;
  note: string;
}

export interface CsrdMilestone {
  year: number;
  label: string;
  companies_nl: number;
  is_current: boolean;
}

export interface AdoptionScenario {
  adoption_pct: number;
  companies: number;
  funds_eur: number;
  tco2e: number;
}

export interface ImpactData {
  generated_at: string;
  poverty: {
    people_under_poverty_line_nl: Stat;
    people_helped_2024: Stat;
    reach_rate_pct: Stat;
  };
  food_paradox: {
    nl_food_waste_kg: Stat;
    foodbanks_rescued_kg: Stat;
    rescue_share_pct: Stat;
  };
  history: {
    series: HistoryPoint[];
    source_label: string;
    source_url: string;
    annotation_2024: string;
  };
  csrd_wave: {
    milestones: CsrdMilestone[];
    source_label: string;
    source_url: string;
  };
  avoided_emissions_gap: {
    rescued_kg: number;
    rescued_tco2e: number;
    nl_food_waste_tco2e: number;
    currently_disclosed_tco2e: number;
    current_mitigation_share_pct: number;
    source_label: string;
    source_url: string;
  };
  adoption_scenarios: {
    package_eur: number;
    package_tco2e: number;
    total_csrd_corporates_nl: number;
    vbn_annual_budget_eur: number;
    supply_cap: {
      max_packages_nl: number;
      max_funds_eur: number;
      max_tco2e: number;
      max_adoption_pct: number;
      explanation: string;
    };
    scenarios: AdoptionScenario[];
    vbn_budget_source_label: string;
    vbn_budget_source_url: string;
  };
}

export function fmtInt(n: number): string {
  return new Intl.NumberFormat("en-NL").format(Math.round(n));
}

export function fmtEur(n: number, opts: { compact?: boolean } = {}): string {
  return new Intl.NumberFormat("en-NL", {
    style: "currency",
    currency: "EUR",
    notation: opts.compact ? "compact" : "standard",
    maximumFractionDigits: opts.compact ? 1 : 0,
  }).format(n);
}
