# Klimaatkracht — Wireframe Spec

**Date:** 2026-04-25  
**File:** `docs/wireframes/index.html`  
**Format:** Single-page HTML, tab-switched, browser-chrome wrapper per screen  
**Brand:** stone/emerald (`#388e3c` green, `#37474f` dark slate)

---

## Navigation

Top sticky bar, dark (`#1a1a1a`), 6 tabs:

| # | Label | Screen ID | Route |
|---|---|---|---|
| 1 | Landing | `screen-landing` | `/` |
| 2 | Marketplace | `screen-marketplace` | `/marketplace` |
| 3 | Package Detail | `screen-pkgdetail` | `/packages/{id}` |
| 4 | Corporate Dashboard | `screen-corporate` | `/dashboard/corporate` |
| 5 | Food Bank Dashboard | `screen-foodbank` | `/dashboard/foodbank` |
| 6 | Methodology | `screen-methodology` | `/methodology` |

---

## Screen 1 — Landing (`/`)

**Status:** NEW  
**Audience:** Both (split hero)

### Sections (top → bottom)

1. **Navbar** — KK logo (emerald pill) · "Klimaatkracht" · links: Marketplace / Methodology / For Food Banks

2. **HeroSplit** — `bg-slate-700`, 2-column grid  
   - Left col: "For corporates" — headline placeholder lines · "Browse marketplace →" (green CTA) · "View methodology →" (ghost)  
   - Right col: "For food banks" — headline placeholder lines · "Join as food bank →" (green CTA)  
   - `wf-divider` separator column between

3. **ImpactStats bar** — `bg-green-50`, 3-column grid  
   - `4,200 tCO₂e/yr avoided` · `7.84M kg rescued/yr` · `5,800 households/wk`  
   - Values aggregated from `banks.json` (6 NL banks)

4. **HowItWorks** — white bg, 3-step grid  
   1. Food bank uploads annual data  
   2. FRAME engine computes CO₂e  
   3. Corporate buys package, receives quarterly CSR report  

5. **Map teaser** — `wf-map` placeholder (`[ NL Map — Leaflet ]`), 6 green dot pins positioned, "Explore all food banks →" link

6. **Footer** — FRAME attribution · methodology link

---

## Screen 2 — Marketplace (`/marketplace`)

**Status:** EXISTING + NL map added  
**Audience:** Corporates browsing packages

### Sections

1. **Navbar** (same as landing)

2. **Page header** — "Verified Avoided Emissions · CSRD-Ready" eyebrow · headline + sub placeholders · impact profile filter bar:  
   `All | CO₂ Focus | Social Focus | Balanced` (tab pills)

3. **NL map** — `react-leaflet` placeholder, `height: 260px`, 6 pin dots with approximate NL coordinates:  
   Rotterdam (51.92, 4.48) · Amsterdam (52.37, 4.90) · Haaglanden (52.07, 4.30) · Eindhoven (51.44, 5.47) · Groningen (53.22, 6.57) · Breda (51.57, 4.77)

4. **Bank cards grid** — 3 cards shown  
   - Card 1 (Rotterdam): highlighted green border, `€25,000 · Q package`, green "Solo eligible" badge · metric lines  
   - Cards 2–3: standard  

---

## Screen 3 — Package Detail (`/packages/{id}`)

**Status:** NEW  
**Audience:** Corporate pre-purchase

### Sections

1. **Navbar**

2. **Main layout** — 2-col (content | sticky sidebar)

   **Left — package info:**  
   - Package name · region badge · ESRS E1 + S3 badges  
   - 3 stat pills: attributed tCO₂e · kg rescued · households  
   - "Projected allocation" table — shows top 6 of 50 banks, Rotterdam row: 42.8% share (highlighted green)  
   - "What's included" card (green bg): quarterly ESRS E1+S3 report · FRAME workings · source citations  
   - "About the methodology" card → link to `/methodology`

   **Right — sticky buy sidebar (240px):**  
   - Package name · `€25,000` price · "Purchase" CTA  
   - Billing info placeholder lines

---

## Screen 4 — Corporate Dashboard (`/dashboard/corporate`)

**Status:** NEW  
**Mock state:** Heineken N.V., Rotterdam package, Q2 2026

### Sections

1. **Header row** — "Heineken N.V." blue badge · "Corporate sponsor" green badge · "Q2 2026" · "View CSR report →" CTA

2. **Stat cards** (4-col row)  
   | Stat | Value |
   |---|---|
   | tCO₂e avoided | 600 |
   | kg rescued | 323,389 |
   | People reached | 8,400 individuals |
   | Amount invested | €25,000 |

   > "Report status" card removed per design decision.

3. **CO₂e breakdown chart** — Recharts `BarChart`, 7 food categories, green bars, height proportional to emission factor × volume:  
   `produce · dry_goods · dairy · meat · bakery · prepared · eggs`

4. **Attribution panel** — "7.77% of Rotterdam's annual baseline" · shadcn `Progress` bar (emerald fill)

5. **Allocation panels** (2-col row)

   **Left — Top bank allocation table:**  
   - Top 3 of 50 banks shown  
   - Columns: bank name / region / share % / kg / tCO₂e  

   **Right — NL Region heatmap (SVG):**  
   - 4 regions (schematic rectangles): Noord · West/Randstad · Zuid · Oost  
   - Emerald opacity scaled by allocation weight:  
     West/Randstad 69% (darkest) · Zuid 15% · Noord 8% · Oost 8%  
   - Legend sidebar: opacity swatch + label + percentage

6. **CSR Report panel** — green-tinted card  
   - Header: "CSR Report — Q2 2026" · "ready" badge · ESRS E1 + ESRS S3 + CSRD-ready badges  
   - Contents list:
     - E1-1 Climate transition plan (progress bars)
     - E1-4 GHG reduction targets (metric: −600 tCO₂e)
     - E1-6 Gross Scope 3 emissions (upstream food waste)
     - S3-1 Material impacts on affected communities
     - S3-4 Channels for engagement
     - FRAME methodology workings (attribution calculation)
     - Source citations (RIVM, FAO, WRAP, CBS)
   - Footer: `generated: claude-sonnet-4-6 · 2026-04-25` · "View full report →" link

7. **Subscription row** — `€25,000` · "paid" green badge · Q2 2026

---

## Screen 5 — Food Bank Dashboard (`/dashboard/foodbank`)

**Status:** NEW  
**Mock state:** Voedselbank Amsterdam, no sponsor yet

### Sections

1. **Header row** — "Voedselbank Amsterdam" blue badge · "Food bank operator" amber badge · "Noord-Holland" region

2. **Stat cards** (3-col row)  
   | Stat | Value |
   |---|---|
   | Funding received | €0 |
   | Active sponsors | 0 |
   | Annual data | Not uploaded (amber badge) |

3. **Upload widget** — `wf-upload` dashed-border zone  
   - "Drop PDF / Excel / CSV here"  
   - Year selector (2024 / 2025)  
   - Mock progress bar (4-stage): Uploading (1s) → Parsing with Claude (2s) → Computing FRAME (1s) → Done ✓  
   - `annotation: mock ingestion`

4. **Pre-upload locked state** — right sidebar card (grayed, `opacity:0.5`, `pointer-events:none`): marketplace preview placeholder

5. **Post-upload metrics** (revealed after upload completes)  
   - Stat row: `tCO₂e/yr · kg rescued · households/wk`  
   - **People reached:** 1,960 individuals (blue card)  
   - **CO₂e bar chart** (7-category, green bars) — identical pattern to corporate dashboard  
     `produce · dry_goods · dairy · meat · bakery · prepared · eggs`  
   - `annotation: Recharts BarChart`

6. **Sponsorship tracker** — empty state: "Your bank will appear in the marketplace once data is uploaded and reviewed"

7. **Source legend** — "extracted" (green badge, from PDF) vs "inferred" (amber badge, national average)  
   - `annotation: locked until upload complete`

---

## Screen 6 — Methodology (`/methodology`)

**Status:** EXISTING — redesigned as animated infographic  
**Audience:** Auditors, compliance teams  
**Scroll behavior:** IntersectionObserver reveals sections on scroll

### Hero strip

Dark emerald gradient (`#064e3b → #047857`), decorative circle overlay.  
- Eyebrow: "METHODOLOGY" in `#6ee7b7`  
- H1: "How we calculate avoided CO₂e"  
- Sub: "deterministic, source-cited, auditor-grade" framing  
- Badges: `FRAME Aligned · CSRD-Ready · ESRS E1 + S3 · NL-specific`  
- Pulse dot (animated) — live indicator

### Section 1 — Ingestion pipeline

5-step pipeline (`pipeline` flex layout), animated arrows between steps:

```
📄 Annual Report  →  🤖 Claude Extraction  →  ✅ Provenance Tagging  →  🧮 FRAME Calculation  →  📊 CSR Report
```

- Arrows: `@keyframes flow` — green gradient sweeping left→right, 1.8s infinite  
- "FRAME Calculation" step highlighted (emerald bg)  
- Pipeline reveals on scroll (`.reveal` + IntersectionObserver)

### Section 2 — Core formula

Dark code panel (`bg-slate-900`), monospace, shimmer animation:

```
CO₂e = Σ(kg_i × EF_i) × CF_NL
       ─────────────────────────
       where CF_NL = 0.93
```

- `@keyframes shimmer` — light sweep across dark panel, 3s infinite  
- Variables colored emerald (`#6ee7b7`)  
- Operators muted slate  
- Result line: `#34d399`, 16px bold

### Section 3 — Emission factors table

7 rows, scroll-triggered bar animation:

| Category | EF (kg CO₂e/kg) | Bar width | Source |
|---|---|---|---|
| Produce | 1.0 | 12% | FAO Food Wastage Footprint (2013), Table 4.2 |
| Bakery | 1.5 | 18% | WRAP Courtauld Commitment 2030 |
| Dry goods | 2.0 | 24% | FAO FWF cereals + Poore & Nemecek (2018) |
| Prepared | 3.0 | 35% | Poore & Nemecek (2018) |
| Dairy | 3.2 | 38% | FAO FWF + RIVM Dutch dairy LCA |
| Eggs | 4.5 | 53% | FAO FWF + Dutch egg sector data |
| Meat | 8.5 | 100% | FAO FWF (2013) weighted Dutch meat mix |

Bar widths: `--w` CSS custom property, `width: var(--w)` set via JS when `.animate` class applied on scroll.  
Transition: `cubic-bezier(0.4,0,0.2,1)` 1.2s.

### Section 4 — NL counterfactual

Side-by-side comparison (`cf-compare` grid):

| NL (used) | vs | Global avg (not used) |
|---|---|---|
| `0.93` — incineration with energy recovery | ≠ | `1.0` — US landfill baseline |

- NL box: emerald border (`#6ee7b7`)  
- Global box: red border, 0.7 opacity (strikethrough intent)  
- Source: RIVM Afvalmonitor 2024 + CBS Waste Statistics

### Section 5 — Provenance system

4 badge types explained:

| Badge | Color | Meaning |
|---|---|---|
| `extracted` | Green | Parsed directly from PDF/annual report |
| `inferred_national_avg` | Amber | National average applied where missing |
| `inferred_calculation` | Blue | Derived via formula from other fields |
| `manual` | Pink | Operator-entered, flagged for review |

### Section 6 — Audit trail

6-step numbered list, each step shows badge status:

1. Food bank submits annual report (PDF/Excel/CSV)
2. Claude extracts measurements — `extracted` badge
3. Missing values filled from national averages — `inferred` badge
4. FRAME calculation applied — `calculation` badge
5. Output reviewed by FRAME-aligned algorithm
6. CSR report generated — `ESRS E1 · S3 · FRAME` badges

### Section 7 — Trust pillars

3-column grid:

| Pillar | Icon | Content |
|---|---|---|
| Deterministic formula | 🧮 | Same inputs always produce same output; no ML black box in the calculation |
| Source citations | 📚 | Every emission factor traces to FAO, WRAP, RIVM, or CBS publications |
| Conservative NL baseline | 🇳🇱 | CF 0.93 uses Dutch incineration, not higher-impact landfill assumption |

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

`initMethAnimations()` called when methodology tab activated — attaches observer to `#meth-scroll` container.

---

## Wireframe Primitive Classes

| Class | Purpose |
|---|---|
| `.wf-bar` | Generic grey placeholder bar |
| `.wf-box` / `.wf-box.dark` / `.wf-box.accent` | Content placeholders with variants |
| `.wf-navbar` | Page navigation chrome |
| `.wf-hero` | Split hero section |
| `.wf-stats` | Green-tinted stat bar |
| `.wf-steps` | 3-column how-it-works grid |
| `.wf-map` | Leaflet map placeholder |
| `.wf-card` | shadcn Card equivalent |
| `.wf-badge.green/.amber/.blue` | Status badges |
| `.wf-progress-track/.wf-progress-fill` | Progress bar |
| `.wf-chart` / `.wf-bars` / `.wf-bar-col` | Bar chart skeleton |
| `.wf-upload` | Dashed drag-and-drop zone |
| `.wf-table` / `.wf-table-header` / `.wf-table-row` | Data table |
| `.annotation` | Yellow inline annotation tag |
| `.browser-chrome` / `.browser-address` | Simulated browser frame |

---

## Data References

All numbers from `archive/df/web/public/banks.json`:

- **6 banks:** Rotterdam, Amsterdam, Haaglanden, Eindhoven, Groningen, Breda
- **Aggregate stats:** 4,200 tCO₂e/yr · 7.84M kg/yr · 5,800 households/wk
- **Mock corporate:** Heineken N.V. · 600 tCO₂e · 323,389 kg · €25,000 · 8,400 people
- **Mock foodbank:** Voedselbank Amsterdam · 1,960 people reached
- **Emission factors:** produce 1.0 · bakery 1.5 · dry_goods 2.0 · prepared 3.0 · dairy 3.2 · eggs 4.5 · meat 8.5
- **NL counterfactual:** `0.93` (RIVM Afvalmonitor 2024 + CBS)
- **Attribution share:** 7.77% of Rotterdam annual baseline

---

## Implementation Notes

- Wireframe → implementation target: `src/frontend/` (Next.js 16 App Router, from `archive/df/web/`)
- Full implementation spec: `docs/specs/2026-04-25-klimaatkracht-frontend-design.md`
- shadcn/ui components: `card`, `badge`, `button`, `progress`, `separator`
- Map: `react-leaflet`
- Charts: `recharts` (`BarChart`, `PieChart`)
- NL heatmap on corporate dashboard: inline SVG (no external dep)
