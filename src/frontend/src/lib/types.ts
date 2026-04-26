export interface ReportCatRow {
  category: string; kg_attr: number; tco2e_attr: number; ef: number; source: string
}
export interface ReportAllocation {
  name: string; city: string; slug: string; year: number | string
  weight_pct: number; amount_eur: number; bank_co2e_t: number
  attributed_co2e_t: number; attribution_share_pct: number
  households: number | null; individuals: number | null
  kg_rescued_attr: number | null; cat_rows: ReportCatRow[]; methodology: string
}
export interface ReportData {
  lang: "nl" | "en"
  meta: { org: string; package_name: string; impact_profile: string; amount_eur: number; sub_id: string; period: number; generated: string }
  kpis: { total_co2e_t: number; investment_eur: number; eur_per_tco2e: number; households_per_week: number; individuals: number }
  summary: { body_html: string; disclaimer_html: string }
  methodology: { body1_html: string; body2_html: string }
  allocations: ReportAllocation[]
  data_gaps: string[]
  calc_trail: string
  emission_factors: { category: string; ef: number; source: string }[]
  nl_cf: number
  disclaimers: { title: string; body: string }[]
  recommendations: { title: string; body: string }[]
  texts: Record<string, string | string[]>
}

export type ImpactProfile = "co2_focus" | "social_focus" | "balanced"
export type SubscriptionStatus = "pending" | "paid" | "failed" | "refunded"
export type Source =
  | "extracted"
  | "inferred_national_avg"
  | "inferred_category_split"
  | "inferred_calculation"
  | "manual"
export type UserRole = "corporate" | "foodbank" | "admin"

export interface CategoryMix {
  produce: number
  dry_goods: number
  dairy: number
  bakery: number
  meat: number
  prepared: number
  eggs: number
}

export interface ProvenanceRecord {
  field: string
  source: Source
  method: string
}

export interface Bank {
  id: string
  slug: string
  name: string
  region: string
  city: string
  lat: number | null
  lng: number | null
  is_regional_dc: boolean
  rdc_satellite_count: number | null
  annual_kg_rescued: number | null
  annual_tco2e: number | null
  weighted_emission_factor: number | null
  households_weekly: number | null
  people_served: number | null
  category_mix: CategoryMix | null
  source_url: string | null
  provenance: ProvenanceRecord[]
}

export interface Package {
  id: string
  name: string
  description: string | null
  region: string
  price_eur: number
  co2e_claim_kg: number
  impact_profile: ImpactProfile
  top_n: number
  is_active: boolean
}

export interface ProjectedAllocation {
  foodbank: Bank
  weight_pct: number
  attributed_kg: number
  attributed_tco2e: number
  attributed_eur: number
}

export interface PackageDetail extends Package {
  projected_allocations: ProjectedAllocation[]
}

export interface User {
  id: string
  email: string
  role: UserRole
  org_name: string | null
}

export interface Subscription {
  id: string
  user_id: string
  package_id: string
  amount_eur: number
  status: SubscriptionStatus
  purchased_at: string
  csr_report_id: string | null
}

// Backend dashboard shape (src/backend/routers/dashboard.py)
export interface DashboardSubscriptionSummary {
  id: string
  package_id: string
  package_name: string
  amount_eur: number
  status: SubscriptionStatus
  total_co2e_kg: number
}

export interface DashboardAllocationDetail {
  foodbank_id: string
  foodbank_name: string
  foodbank_city: string
  weight_pct: number
  amount_eur: number
  co2e_attributed_kg: number
}

export interface DashboardSubscriptionDetail {
  id: string
  package_id: string
  package_name: string
  amount_eur: number
  status: SubscriptionStatus
  total_co2e_kg: number
  allocations: DashboardAllocationDetail[]
  report_id: string | null
}

// Compatibility aliases used by some pages
export type SubscriptionDetail = DashboardSubscriptionDetail
export interface SubscriptionAllocation extends DashboardAllocationDetail {}

export interface TimelinePoint {
  year: number
  co2e_kg: number
  annual_kg_rescued: number | null
  households_weekly: number | null
}

export interface QuarterlyPoint {
  label: string
  year: number
  quarter: number
  co2e_kg: number
  realised: boolean
  cumulative_co2e_kg: number
}

export interface ProvenanceMix {
  extracted_pct: number
  inferred_national_avg_pct: number
  inferred_category_split_pct: number
  inferred_calculation_pct: number
  manual_pct: number
  confidence_band: "high" | "medium" | "low"
}

export interface CoverageRegion {
  region: string
  weight_pct: number
  foodbanks: number
}

export interface DashboardMetrics {
  period_co2e_kg: number
  period_delta_pct: number | null
  cumulative_co2e_kg: number
  eur_per_tco2e: number | null
  households_weighted: number
  individuals_weighted: number
  provenance: ProvenanceMix
  cars_equivalent: number
  nl_households_equivalent: number
  flights_equivalent: number
  regions: CoverageRegion[]
}

export interface SubscriptionPacing {
  quarters_realised: number
  quarters_contracted: number
  cycle_pct: number
  next_disclosure_quarter: string
}
