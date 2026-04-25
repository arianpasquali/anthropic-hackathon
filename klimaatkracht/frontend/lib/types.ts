export type Chapter = {
  id: string;
  name: string;
  type: string;
  households_served_per_week: number;
  needs_score: number;
  regional_bonus: number;
  operational_footprint_kgco2e_per_tonne: number;
  cost_per_household_per_week_eur: number;
};

export type ChapterSnapshot = {
  id: string;
  net_avoided_tco2e: number;
  households_served_quarter: number;
  needs_score: number;
  regional_bonus: number;
  total_tonnes: number;
};

export type AllocationPreferences = {
  max_climate_impact: number;
  max_social_need: number;
  balanced_distribution: number;
};

export type AllocationResult = {
  chapter_id: string;
  weight: number;
  amount_eur: number;
  axis_weights: { climate: number; social: number; balanced: number };
};
