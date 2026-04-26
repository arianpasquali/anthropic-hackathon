# Climate Harvest — Wireframe Spec

**Date:** 2026-04-25 (updated)
**File:** `docs/wireframes/index.html`
**Format:** Single-page HTML, tab-switched, browser-chrome wrapper per screen
**Brand:** stone/emerald (`#388e3c` green, `#064e3b` dark emerald, `#37474f` dark slate)

---

## Navigation

Top sticky bar (`#1a1a1a`), 7 tabs:

| # | Label | Screen ID | Route |
|---|---|---|---|
| 1 | Landing | `screen-landing` | `/` |
| 2 | Funds | `screen-marketplace` | `/funds` |
| 3 | Fund Profile | `screen-pkgdetail` | `/funds/{id}` |
| 4 | Corporate Dashboard | `screen-corporate` | `/dashboard/corporate` |
| 5 | Food Bank Dashboard | `screen-foodbank` | `/dashboard/foodbank` |
| 6 | Methodology | `screen-methodology` | `/methodology` |
| 7 | Pricing | `screen-pricing` | `/pricing` |

---

## Screen 1 — Landing (`/`)

**Audience:** Corporate (primary) · Food banks (ghost link)

### Sections (top → bottom)

1. **Navbar** — KK logo · "Climate Harvest" · links: Investment funds / Methodology / For Food Banks (muted)

2. **Hero** — full-width emerald gradient (`#064e3b → #065f46 → #047857`), decorative circle overlays
   - Eyebrow: `CSRD-READY · ESRS E1 + S3 · FRAME ALIGNED · 180 FOODBANKS`
   - H1: "Turn Dutch food rescue into audit-ready climate impact"
   - Sub: invest in verified Dutch foodbank funds, FRAME-weighted CO₂e, quarterly ESRS reports
   - Single primary CTA: **"View investment opportunities →"** (emerald `#10b981`)
   - Ghost link: "For food banks →" (muted, `opacity:0.55`)

3. **Stats bar** — `bg-green-50`, 3-column
   - `18,015 tCO₂e / yr` · `9.2M kg food rescued / yr` · `7,582 hh / wk`
   - Sub-label: "6 regions · 180 foodbanks · FRAME verified"

4. **HowItWorks** — white bg, 3-step grid
   1. Select a fund profile (Carbon Certified / Community First / CSRD Complete / Impact Balanced)
   2. Capital flows to 180 foodbanks weighted by FRAME CO₂e scores
   3. Receive quarterly CSRD-ready ESRS E1 + S3 report

5. **Map teaser** — `wf-map` Leaflet placeholder, 6 green dot pins (NL geographic positions), "Explore all food banks →" link

6. **Footer** — FRAME attribution · methodology link

---

## Screen 2 — Funds (`/funds`)

**Audience:** Corporates browsing fund profiles

### Sections

1. **Navbar** — "Investment funds" active

2. **Page header** — eyebrow "Verified Avoided Emissions · CSRD-Ready"

3. **Filter row** (two groups):
   - Profile: `All | 🌍 Carbon Certified | 👥 Community First | ⚖️ CSRD Complete | 🎯 Impact Balanced`
   - Region: `All NL | West/Randstad | Zuid | Noord`

4. **Fund carousel** — full-width, `scroll-snap-type: x mandatory`, 4 cards:

   | Fund | Profile | Accent color | Top region |
   |---|---|---|---|
   | NL Climate Fund | 🌍 Carbon Certified | emerald | West/Randstad 69% |
   | NL Social Fund | 👥 Community First | purple | West/Randstad 57% |
   | NL Balanced Fund | ⚖️ CSRD Complete | blue | West/Randstad 63% |
   | NL Impact Fund | 🎯 Impact Balanced | amber | West/Randstad 65% |

   Each card: fund name · "6 regions · 180 foodbanks" chip · top-2 region mini progress bars · tCO₂e/kg/hh stats · price pills (€10k · €100k · Custom) · **"View fund →"** CTA

   Scroll indicator: 4 dots below carousel

5. **NL Map** — full-width below carousel, `height: 280px`, Leaflet placeholder (`react-leaflet`), 6 green pin dots at approximate NL geographic positions:
   - Rotterdam (left:36%, top:62%) · Amsterdam (40%, 52%) · Haaglanden (33%, 58%)
   - Eindhoven (46%, 71%) · Groningen (58%, 28%) · Breda (38%, 68%)
   - Tooltip on hover: bank name · allocation % · tCO₂e · kg
   - Legend below: "Active RDC (6)" · "Explore all food banks →"

---

## Screen 3 — Fund Profile (`/funds/{id}`)

**Mock state:** NL Climate Fund · Carbon Certified profile
**Audience:** Corporate pre-investment

### Sections

1. **Navbar** — "Investment funds" active

2. **Fund header** (2-col: info | CTA)
   - Left: profile label ("🌍 Carbon Certified") · H1 "NL Climate Fund" · description · badges (ESRS E1 · ESRS S3 · CSRD-ready · FRAME Aligned · 6 regions · 180 foodbanks)
   - Right: invest CTA card (green-tinted, `bg-green-50`):
     - "From €10k / year"
     - **"Invest in this fund →"** button (emerald, `onclick → show('pricing')`)
     - "No lock-in · ESRS E1+S3 report included · Solvimon invoice"

3. **Aggregate stats pills** (3-col): `18,015 tCO₂e/yr` · `9.2M kg` · `7,582 hh/wk`

4. **Two-col main body** (content | right sidebar)

   **Left col:**
   - Regional allocation table (6 RDCs):
     | RDC | Region | Share | Banks | tCO₂e |
     |---|---|---|---|---|
     | Rotterdam RDC | West/Randstad | 43% | ~50 | 7,746 |
     | Haaglanden RDC | West/Randstad | 26% | ~46 | 4,684 |
     | Amsterdam RDC | West/Randstad | 16% | ~32 | 2,928 |
     | Breda RDC | Zuid | 6% | ~27 | 1,034 |
     | Eindhoven RDC | Zuid | 4% | ~26 | 652 |
     | Groningen RDC | Noord | 5% | ~37 | 986 |
   - Footer: "Weights recomputed quarterly as foodbanks upload new annual data."
   - **Fund mix tabs** — `[By Category | By Region]` toggle
     - By Category: 7-bar Recharts BarChart (produce · dry_goods · dairy · meat · bakery · prepared · eggs)

   **Right col:**
   - Mini SVG choropleth — 4 schematic regions, opacity ∝ allocation (Noord 5%/0.20 · West/Randstad 69%/0.78 · Zuid 15%/0.42 · Oost 11%/0.30)
   - CSR Report profile card (green-tinted):
     - Quarterly · 48h delivery · generated by Claude
     - Badges: ESRS E1 · ESRS S3 · CSRD-ready
     - Contents: E1-1 · E1-4 · E1-6 · S3-1 · S3-4 · FRAME workings · Sources
     - "generated by claude-sonnet-4-6"

---

## Screen 4 — Corporate Dashboard (`/dashboard/corporate`)

**Mock state:** Heineken N.V., Rotterdam package, Q2 2026

### Sections

1. **Header row** — "Heineken N.V." blue badge · "Corporate sponsor" green badge · "Q2 2026" · "View CSR report →" CTA

2. **Stat cards** (4-col):
   | Stat | Value |
   |---|---|
   | tCO₂e avoided | 600 |
   | kg rescued | 323,389 |
   | People reached | 8,400 individuals |
   | Amount invested | €25,000 |

3. **Impact timeline + projection scenarios** — Recharts AreaChart + dashed projections
   - X axis: Q1'25 → Q4'26 (8 points)
   - Solid emerald area/line: historical actuals Q1'25 → Q2'26 (current)
   - "NOW · Q2 2026" vertical marker
   - Three dashed projection lines from Q2'26 → Q4'26:
     - 🚀 Optimistic: 3,200 tCO₂e (emerald dashed)
     - 📊 Base: 2,800 tCO₂e (gray dashed)
     - 🛡 Conservative: 2,100 tCO₂e (light gray dashed)
   - Scenario summary row (3 cards): Optimistic/Base/Conservative with value + rationale

4. **Attribution panel** — "7.77% of Rotterdam's annual baseline" · `shadcn Progress` bar (emerald)

5. **Allocation panels** (2-col row)
   - Left: top-3 bank allocation table — bank name / region / share% / kg / tCO₂e
   - Right: NL Region heatmap SVG — 4 schematic rectangles (Noord · West/Randstad · Zuid · Oost), emerald opacity ∝ allocation weight; legend

6. **CSR Report panel** — green-tinted card
   - "CSR Report — Q2 2026" · "ready" badge · ESRS E1 + ESRS S3 + CSRD-ready badges
   - Contents: E1-1 · E1-4 · E1-6 · S3-1 · S3-4 · FRAME workings · Sources
   - Footer: `generated: claude-sonnet-4-6 · 2026-04-25` · "View full report →"

7. **Subscription row** — `€25,000` · "paid" green badge · Q2 2026

---

## Screen 5 — Food Bank Dashboard (`/dashboard/foodbank`)

**Mock state:** Voedselbank Amsterdam, no sponsor yet

### Sections

1. **Header row** — "Voedselbank Amsterdam" blue badge · "Food bank operator" amber badge · "Noord-Holland" region

2. **Stat cards** (3-col): Funding received €0 · Active sponsors 0 · Annual data "Not uploaded" (amber)

3. **Upload widget** — dashed drag-and-drop zone
   - "Drop PDF / Excel / CSV here"
   - Year selector (2024 / 2025)
   - Mock progress bar 4-stage: Uploading → Parsing with Claude → Computing FRAME → Done ✓

4. **Pre-upload locked state** — right sidebar card (grayed, `opacity:0.5`, `pointer-events:none`): marketplace preview placeholder

5. **Post-upload metrics** (revealed after upload)
   - Stat row: tCO₂e/yr · kg rescued · hh/wk
   - People reached: 1,960 individuals (blue card)
   - CO₂e bar chart (7-category, green bars) — Recharts BarChart

6. **Sponsorship tracker** — empty: "Your bank will appear in the marketplace once data is uploaded and reviewed"

7. **Source legend** — `extracted` (green) vs `inferred` (amber) — locked until upload complete

---

## Screen 6 — Methodology (`/methodology`)

**Scroll behavior:** IntersectionObserver reveals sections on scroll

### Hero strip

Dark emerald gradient (`#064e3b → #047857`) · decorative circle
- Eyebrow: "METHODOLOGY" `#6ee7b7`
- H1: "How we calculate avoided CO₂e"
- Sub: "deterministic, source-cited, auditor-grade"
- Badges: FRAME Aligned · CSRD-Ready · ESRS E1 + S3 · NL-specific
- Animated pulse dot

### Section 1 — Ingestion pipeline

5-step `@keyframes flow` animated arrows:
```
📄 Annual Report → 🤖 Claude Extraction → ✅ Provenance Tagging → 🧮 FRAME Calculation → 📊 CSR Report
```
"FRAME Calculation" step highlighted (emerald bg). Reveals on scroll.

### Section 2 — Core formula

Dark code panel (`bg-slate-900`), `@keyframes shimmer`:
```
CO₂e = Σ(kg_i × EF_i) × CF_NL
       ─────────────────────────
       where CF_NL = 0.93
```

### Section 3 — Emission factors table

7 rows, scroll-triggered bar animation (`cubic-bezier(0.4,0,0.2,1)` 1.2s):

| Category | EF (kg CO₂e/kg) | Source |
|---|---|---|
| Produce | 1.0 | FAO FWF (2013) |
| Bakery | 1.5 | WRAP Courtauld 2030 |
| Dry goods | 2.0 | FAO FWF + Poore & Nemecek (2018) |
| Prepared | 3.0 | Poore & Nemecek (2018) |
| Dairy | 3.2 | FAO FWF + RIVM Dutch dairy LCA |
| Eggs | 4.5 | FAO FWF + Dutch egg sector data |
| Meat | 8.5 | FAO FWF (2013) weighted Dutch meat mix |

### Section 4 — NL counterfactual

`0.93` (NL incineration with energy recovery) vs `1.0` (US landfill baseline, not used). Source: RIVM Afvalmonitor 2024 + CBS.

### Section 5 — Provenance system

| Badge | Color | Meaning |
|---|---|---|
| `extracted` | Green | Parsed from PDF/annual report |
| `inferred_national_avg` | Amber | National average applied |
| `inferred_calculation` | Blue | Derived via formula |
| `manual` | Pink | Operator-entered, flagged |

### Section 6 — Audit trail (6-step numbered list)

### Section 7 — Trust pillars (3-col grid)

🧮 Deterministic formula · 📚 Source citations · 🇳🇱 Conservative NL baseline

---

## Screen 7 — Pricing (`/pricing`)

**Audience:** Corporates ready to invest

### Sections

1. **Navbar** — "Pricing" active (or can be reached from Fund Profile "Invest →")

2. **Hero** — dark emerald gradient
   - "For Corporates" eyebrow
   - H1: "Turn food rescue into audit-ready CO₂e proof"
   - Sub: quarterly subscription, ESRS E1+S3 included, same science three price points
   - Badges: CSRD-ready · ESRS E1 + S3 · FRAME aligned · Quarterly reports

3. **Price anchoring bar** — `€30 / tCO₂e` · same emission factor table across tiers · NL counterfactual 0.93 · prices ex-VAT, billed quarterly, cancel anytime

4. **Three-column pricing table**:

   | | Starter | Partner | Enterprise |
   |---|---|---|---|
   | Price | **€10k / yr** | **€100k / yr** | **Custom / yr** |
   | tCO₂e | ~333 / yr | ~3,330 / yr | Custom |
   | Badge | — | Most popular | — |
   | ESRS E1 | ✓ | ✓ | ✓ |
   | ESRS S3 | ✗ | ✓ | ✓ |
   | Co-branded report | ✗ | ✓ | ✓ |
   | Big-4 audit package | ✗ | ✗ | ✓ |
   | Account manager | ✗ | ✗ | ✓ |
   | CTA | **Buy →** | **Buy →** | **Schedule a call →** |

5. **Price-per-tCO₂e comparison bar** — all tiers at €30/tCO₂e (Enterprise: "Negotiated · same formula")

6. **What you receive** (3 cards) — Impact dashboard · ESRS E1+S3 report · Audit-ready workings

7. **How it works** (3-step) — Choose tier → FRAME computes impact → Receive quarterly report

8. **FAQ strip** — 4 common questions (2-col grid)

9. **CTA footer** — dark emerald · "Buy Starter €10k →" · "Buy Partner €100k →" · "Schedule a call →"

---

## CSS Animation System

| Name | Trigger | Effect |
|---|---|---|
| `@keyframes flow` | Always (methodology pipe arrows) | Green gradient sweeps left→right, 1.8s infinite |
| `@keyframes shimmer` | Always (formula panel) | Light sweep across dark bg, 3s infinite |
| `@keyframes pulse-ring` | Always (methodology hero dot) | Ring expands + fades, 1.5s infinite |
| `@keyframes spin` | On upload progress | Spinner rotation |
| `.reveal` + `.visible` | IntersectionObserver scroll | `opacity 0→1`, `translateY(28px)→0`, 0.55s ease |
| `.reveal-delay-{1-5}` | Same | Staggered 0.1s–0.5s delays |
| `.ef-bar-fill.animate` | IntersectionObserver scroll | `width: 0 → var(--w)`, 1.2s cubic-bezier |

---

## Key Data

All numbers from `archive/df/web/public/banks.json` (6 RDCs):

| Field | Value |
|---|---|
| Total tCO₂e/yr | 18,015 |
| Total kg rescued/yr | 9.2M |
| Total households/wk | 7,582 |
| Total foodbanks | 180 |
| Regions | 6 |
| Mock corporate | Heineken N.V. · 600 tCO₂e · 323,389 kg · €25,000 · 8,400 people |
| Mock foodbank | Voedselbank Amsterdam · 1,960 people reached |
| NL counterfactual | 0.93 (RIVM Afvalmonitor 2024 + CBS) |

Emission factors: produce 1.0 · bakery 1.5 · dry_goods 2.0 · prepared 3.0 · dairy 3.2 · eggs 4.5 · meat 8.5

Carbon Certified allocation (West/Randstad dominant): Rotterdam 43% · Haaglanden 26% · Amsterdam 16% · Breda 6% · Groningen 5% · Eindhoven 4%

---

## Implementation Notes

- Wireframe → implementation target: `src/frontend/` (Next.js 16 App Router)
- shadcn/ui: `card`, `badge`, `button`, `progress`, `separator`
- Map: `react-leaflet` (6 RDC pins)
- Charts: `recharts` (`AreaChart` for timeline, `BarChart` for food categories)
- NL heatmap: inline SVG (4 schematic region rectangles)
- Fund choropleth on Funds page: inline SVG (same 4-region schema)
- Pricing screen reached from Fund Profile "Invest in this fund →" CTA
