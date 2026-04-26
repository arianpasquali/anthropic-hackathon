# Kavel — Frontend Design Spec

**Date:** 2026-04-25  
**Project:** Anthropic x Whale Hackathon  
**Scope:** Landing page + full frontend for the Kavel sponsored-impact marketplace

---

## What We're Building

Two-sided marketplace connecting Dutch corporates to food banks via verified CO2e reporting. Frontend is a 4-page Vite + React SPA with mock data mirroring the existing Python/SQLModel backend schema.

---

## Decisions

| Decision | Choice | Reason |
|---|---|---|
| Framework | Vite + React 18 + TypeScript | No SSR needed, fastest scaffold |
| UI components | shadcn/ui + Tailwind | Already specified by user |
| Routing | React Router v6 | Client-side, no backend required for demo |
| Map | Leaflet (react-leaflet) | No API key, works offline, fast |
| Charts | Recharts | Lightweight, works with shadcn styling |
| Data | Mock TypeScript data | Mirrors Python schema, no live DB risk in demo |
| Brand | Emerald green | Sustainability signal, `emerald-700` primary |

---

## Architecture

Frontend lives at `src/frontend/` (currently `src/frontend/.gitkeep`).

```
src/frontend/
├── package.json
├── vite.config.ts
├── index.html
├── src/
│   ├── main.tsx
│   ├── App.tsx                        # Router root
│   ├── pages/
│   │   ├── Landing.tsx                # /
│   │   ├── Marketplace.tsx            # /marketplace
│   │   ├── CorporateDashboard.tsx     # /dashboard/corporate
│   │   └── FoodbankDashboard.tsx      # /dashboard/foodbank
│   ├── components/
│   │   ├── ui/                        # shadcn auto-generated
│   │   ├── layout/
│   │   │   ├── Navbar.tsx
│   │   │   └── Footer.tsx
│   │   ├── landing/
│   │   │   ├── HeroSplit.tsx          # split CTA: corporate | foodbank
│   │   │   ├── ImpactStats.tsx        # 155k clients, ~100k tCO2e, 172 banks
│   │   │   └── HowItWorks.tsx         # 3-step flow
│   │   ├── marketplace/
│   │   │   ├── NLMap.tsx              # Leaflet, pins by RegionEnum
│   │   │   ├── PackageCard.tsx        # Package: name, region, €25k, 600 tCO2e
│   │   │   └── PackageModal.tsx       # PackageFoodbank breakdown + mock checkout
│   │   ├── corporate/
│   │   │   ├── ImpactChart.tsx        # FrameResult CO2e by category (Recharts BarChart)
│   │   │   └── ReportPreview.tsx      # CsrReport, TemplateEnum selector
│   │   └── foodbank/
│   │       ├── UploadWidget.tsx       # AnnualReport upload + mock ingestion states
│   │       └── FundingTracker.tsx     # FundSubscription table + status badges
│   └── data/
│       └── mock.ts                    # typed mock data matching Python models
```

---

## Data Types (TypeScript mirrors from Python schema)

```typescript
// From enums.py
type RegionEnum = 'noord' | 'oost' | 'zuid' | 'west' | 'randstad'
type StatusEnum = 'pending' | 'paid' | 'failed' | 'refunded'
type TemplateEnum = 'gri' | 'csrd' | 'esrs_e1' | 'generic'
type SourceEnum = 'extracted' | 'inferred_national_avg' | 'inferred_category_split' | 'inferred_calculation' | 'manual'

// From foodbank.py
interface Foodbank { id: string; name: string; city: string; region: RegionEnum; is_regional_dc: boolean; vbn_member_id?: string }
interface AnnualReport { id: string; foodbank_id: string; year: number; period_start: string; period_end: string; raw_file_path: string; ingested_at: string; ingestion_model: string }

// From marketplace.py
interface Package { id: string; name: string; description?: string; region: RegionEnum; price_eur: number; co2e_claim_kg: number; is_active: boolean }
interface PackageFoodbank { package_id: string; foodbank_id: string; weight_pct?: number }
interface FundSubscription { id: string; user_id: string; package_id: string; amount_eur: number; status: StatusEnum; solvimon_id?: string; purchased_at: string; csr_report_id?: string }
interface CsrReport { id: string; subscription_id: string; frame_result_id: string; generated_at: string; file_path: string; template: TemplateEnum }

// From frame.py
interface FrameResult { id: string; report_id: string; co2e_total_kg: number; co2e_produce_kg: number; co2e_meat_fish_kg: number; co2e_dairy_eggs_kg: number; co2e_dry_goods_kg: number; co2e_bread_kg: number; emission_factor_source: string; methodology_version: string; computed_at: string }
```

---

## Pages

### 1. Landing (`/`)

Top → bottom:
1. **Navbar** — "Kavel" + leaf icon, links: Marketplace | For Food Banks | For Corporates
2. **HeroSplit** — dark `emerald-800` gradient bg, white text, two columns:
   - Left: "Turn climate action into CSR proof" → "Browse packages →"
   - Right: "Unlock funding for your food rescue" → "Join as food bank →"
3. **ImpactStats bar** — `155,600 clients` · `~100,000 tCO2e/yr` · `172 food banks`
4. **HowItWorks** — 3 horizontal cards: Upload data → FRAME computes CO2e → Corporate buys + gets report
5. **Map preview** — small Leaflet map, 5 NL pins, "See all →" to `/marketplace`
6. **Footer** — methodology note, FRAME / Global Foodbanking Network attribution

### 2. Marketplace (`/marketplace`)

1. **Filter bar** — region chips (`RegionEnum` values) + "Available only" toggle
2. **Split layout** — 60% Leaflet map / 40% card list
3. **NL Map** — pin per `Foodbank`, color by region, `is_regional_dc` pins larger, click → scroll to card
4. **PackageCard** — name, region badge, city, `€25,000`, `600 tCO2e`, availability progress bar, "Buy package →"
5. **PackageModal** — `PackageFoodbank` weight breakdown, CO2e preview, mock Solvimon checkout → redirects to `/dashboard/corporate`

### 3. Corporate Dashboard (`/dashboard/corporate`)

1. **Header** — company name, role badge, download report link
2. **Summary cards** (4): `600 tCO2e avoided` · `240t food rescued` · `€25,000 invested` · `Q2 2025 report ready`
3. **ImpactChart** — Recharts `BarChart`, all 5 `FrameResult` CO2e category fields, emerald palette
4. **Linked food banks** — cards from `PackageFoodbank`, shows `weight_pct` attribution %
5. **ReportPreview** — `TemplateEnum` selector (GRI / CSRD / ESRS E1 / Generic), "Generate Report" → mock PDF panel
6. **Subscription row** — `FundSubscription`: amount, status badge (paid=green, pending=amber)

### 4. Food Bank Dashboard (`/dashboard/foodbank`)

1. **Header** — food bank name, region badge, `vbn_member_id`
2. **Funding cards** (3): `€25,000 received` · `2 active sponsors` · `Next report due: Q3 2025`
3. **UploadWidget** — drag-and-drop PDF/Excel/CSV, year + period selectors, mock progress: Uploading → Parsing → FRAME computing → Done, shows `ingestion_model`
4. **Impact metrics** — `kg_received_total`, category donut chart (Recharts) from `FoodCategories`
5. **People served** — stat grid from `PeopleServed`: households, individuals, % children
6. **Sponsorship tracker** — table of `FundSubscription` rows: corporate · package · amount · status · report generated?
7. **Source legend** — `SourceEnum` values explained: extracted | inferred | manual

---

## Brand Tokens

```css
--color-primary:   #047857  /* emerald-700 */
--color-surface:   #ecfdf5  /* emerald-50  */
--color-accent:    #34d399  /* emerald-400 */
--color-text:      #0f172a  /* slate-900   */
--color-muted:     #475569  /* slate-600   */
```

---

## Mock Data Plan (`src/data/mock.ts`)

- 8–10 `Foodbank` records across all 5 regions, 2–3 marked `is_regional_dc: true`
- 5 `Package` records (one per region), all `is_active: true`
- `PackageFoodbank` linking packages to 2–3 banks each with `weight_pct`
- 1 `FundSubscription` with `status: paid` (for corporate dashboard demo)
- 1 `FrameResult` with realistic CO2e values (produce ~40%, dairy ~25%, dry goods ~20%, bread ~10%, meat ~5%)
- 1 `CsrReport` with `template: csrd`
- NL geo coordinates per food bank city (for Leaflet pins)

---

## Out of Scope

- Auth / login flows
- Real Solvimon payment integration
- Live backend API calls
- PDF generation
- Mobile responsiveness (nice-to-have, not required for demo)
