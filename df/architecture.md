# Platform Architecture — Climate-Action Packages for Dutch Foodbanks

## What it is

A two-sided marketplace with a FRAME-aligned attribution engine and an agentic data pipeline.

- **Corporates** browse Dutch foodbanks, buy €25,000 Climate-Action Packages tied to a specific bank (or regional cluster), and receive quarterly audit-ready CSR reports.
- **Foodbanks** get a low-effort sponsorship channel — they upload existing operational data (PDF/Excel/CSV) and the platform converts it into FRAME-aligned tCO2e and routes funds in.
- The platform keeps the methodology honest, generates the reports, and handles the money.

Each €25k package = 600 tCO2e avoided (€41.67/tCO2e — credible Gold Standard-track range).

## Architecture

```
┌────────────────────────────────────────────────────────────────┐
│  CORPORATE BUYER                          FOODBANK OPERATOR    │
│  ─────────────────                        ──────────────────   │
│  Marketplace (map of NL)                  Upload data (PDF,    │
│  → Pick bank/cluster                       Excel, CSV) or      │
│  → See live impact data                    auto-scrape         │
│  → Buy €25k package (Solvimon)             Claim sponsorships  │
│  → Receive quarterly PDF                   Receive funds       │
└────────────────────┬─────────────────────────┬─────────────────┘
                     │                         │
              ┌──────▼─────────────────────────▼──────┐
              │   1. INGESTION AGENT (Claude)         │  ← "Built Different"
              │   - PDF/Excel/CSV parser              │
              │   - Category classifier               │
              │   - Anomaly flagger                   │
              │   - Schema: kg × category × source    │
              └──────────────┬────────────────────────┘
                             │
              ┌──────────────▼────────────────────────┐
              │   2. FRAME ENGINE (deterministic)     │
              │   - Emission factors by category      │
              │   - NL-specific counterfactual        │
              │   - Pro-rata attribution to sponsors  │
              │   - Outputs: tCO2e, methodology trail │
              └──────────────┬────────────────────────┘
                             │
       ┌─────────────────────┼─────────────────────┐
       │                     │                     │
┌──────▼───────┐    ┌────────▼────────┐    ┌───────▼────────┐
│ 3. MARKET-   │    │ 4. PAYMENTS     │    │ 5. REPORT GEN  │
│    PLACE     │    │ (Solvimon)      │    │ (Claude)       │
│ Next.js +    │    │ Checkout +      │    │ Quarterly PDF, │
│ map of NL    │    │ recurring +     │    │ GRI/CSRD       │
│ Bank cards   │    │ wire to bank    │    │ formatted      │
└──────────────┘    └─────────────────┘    └────────────────┘
```

Hosted on **boxd** (microVM + HTTPS URL — sponsor tooling).

## Layer-by-layer

| Layer | Tech | Why it matters |
|---|---|---|
| **1. Ingestion agent** | Claude with tool use (pdf-extract, classifier, validator) | Solves a real messy-data problem; visibly *thinks*; the live demo beat |
| **2. FRAME engine** | Python, ~150 lines, fully deterministic | Auditable, jury can read it; not a black box |
| **3. Marketplace** | Next.js + Mapbox + Tailwind | B2B ESG manager UX; Pixel Perfect prize lives here |
| **4. Solvimon checkout** | Sponsor SDK | Required tooling; recurring billing is a real B2B feature |
| **5. Report generator** | Claude + react-pdf or Playwright→PDF | Magic moment: live PDF generation on stage |

## FRAME methodology (what the report is built on)

Three input layers feed the audit-ready report; transparency about which is which is what makes it auditable rather than just impressive-looking.

### 1. Operational data from the foodbank (per quarter)
- kg food rescued, broken down by category (produce, dairy, bakery, meat, prepared)
- source (retail/wholesale/farm/manufacturer) and counterfactual disposal route (in NL: usually incineration-with-energy-recovery, not landfill — this changes the math vs. US FRAME defaults)
- households served, meals distributed, region

### 2. Standard emission factors (public, citable)
- FAO Food Wastage Footprint, WRAP UK, RIVM/CBS for NL-specific waste routes
- FRAME methodology document from Global Foodbanking Network for the calculation framework
- Cited in the report appendix, footnoted per number

### 3. Attribution math
- Corporate's €25k buys a *pro-rata share* of the foodbank's actual quarterly rescue activity
- Chain: € sponsored → % of quarterly operational budget → attributed kg food rescued → tCO2e avoided via FRAME factors

### What Claude actually does
- Composes narrative around computed figures (does not invent numbers)
- Writes the methodology appendix in audit-ready prose
- Adapts tone/format to the corporate's CSR template (GRI, CSRD, ESRS E1)
- Flags assumptions explicitly ("counterfactual assumes NL incineration mix, not landfill")

The numbers come from a deterministic FRAME calculator (Python). Claude wraps them in defensible language and a corporate-grade document.

## Unit economics (validated)

- **€25,000 = 600 tCO2e** = €41.67 / tCO2e (mid-to-high tier voluntary carbon market; credible)
- 600 tCO2e ÷ ~2.5 kg CO2e per kg rescued ≈ **240 tonnes of food rescued per package**
- NL national: ~40,000 t/yr food rescued (68.1M units × ~0.6 kg cross-validated)
- Implies the package only fits banks rescuing >240 t/yr → **the ~10–15 largest banks**, with smaller banks bundled into regional clusters

## Data sources collected

`/Users/diederik.f/Claude/whale/data/` — 28 PDFs + 25 extracted text files across 13 Dutch foodbanks.

### National (Voedselbanken Nederland)
- Jaarverslag 2023, 2024
- Feiten en Cijfers 2023, 2024

### Per-bank reports
| Bank | Year(s) | Headline figure |
|---|---|---|
| Rotterdam | 2024 | 80,000 kg/wk regional (4,160 t/yr); RDC for 33 satellite banks |
| Amsterdam | 2024, 2023 | 1,535 hh / 3,799 wkly / 11,600 regional; RDC for 18 banks |
| Haaglanden | 2024, 2023 | 2,904 hh / 6,840 ppl; clean 25-article parcel breakdown |
| Utrecht | 2024, 2023 | 561 hh wkly |
| Eindhoven | 2024, 2023 | 32,000 parcels/yr (€1.1M food); cluster of 10 banks |
| Tilburg | 2023 | RDC for 29 banks in NB+Zeeland; 20k ppl/wk |
| Groningen | 2024, 2023 | RDC for northern provinces; 1,675 hh |
| Breda | 2025, 2024 | **507,496 kg/yr** (gold standard kg figure) |
| Den Bosch | 2024, 2023 | 549 hh end-2024; 200 vrijwilligers |
| Nijmegen | 2023 | ~800 parcels/wk |
| Amstelveen | 2023 | 125–145 parcels/wk |
| Lelystad | 2024, 2023 | ~200 gezinnen/wk |
| Woerden | 2024 | 146 hh/wk; 220,000 units = €550k food value |

### Heterogeneity (the platform's value-add)
Reporting differs wildly across banks:
- Rotterdam reports in **kg/week**
- Breda in **kg/year**
- Eindhoven in **parcels + retail value**
- Haaglanden in **articles by category**
- Woerden in **units + value**

The ingestion agent normalising this is the "Built Different" demo beat — a real problem solved on stage.

## Demo cohort (the 5 banks we lead with)

1. **Rotterdam** — regional anchor, hard kg figure
2. **Amsterdam** — capital, RDC story (18 banks)
3. **Breda** — clean explicit kg/yr
4. **Eindhoven** — Brainport, growth + cluster narrative
5. **Groningen** — north, smaller — shows the cluster sponsorship case

Covers all five major regions of NL. Lets us show:
- Direct €25k packages for Rotterdam, Amsterdam, Breda, Eindhoven (each big enough)
- Regional cluster package for Groningen + smaller northern banks

## Demo flow (1-min video + 2-min stage)

1. **(0:00) Hook** — Voedselbank Rotterdam: "4,160 tonnes of food saved per year. 10,400 tCO2e avoided. None of this is on a corporate's CSR report."
2. **(0:10) Buy** — corporate ESG manager opens marketplace, picks Rotterdam, buys €25k Climate-Action Package via Solvimon.
3. **(0:25) Magic moment** — ingestion agent parses Rotterdam's actual 2024 jaarverslag PDF live; FRAME engine computes attribution.
4. **(0:40) Reveal** — quarterly CSR PDF generates on screen — branded, methodology appendix, FRAME-aligned, signed.
5. **(0:50) Close** — money flows to the foodbank. Tagline + sponsor logos.

## 24-hour build plan (4 people, parallel tracks)

| Track | Owner | Deliverable | Hard cuts |
|---|---|---|---|
| **A: Marketplace + corporate flow** | 1 | Next.js, 5 banks hardcoded, map of NL, Solvimon checkout | No corporate login — single-tenant demo |
| **B: Ingestion agent + FRAME engine** | 1 | Claude tool-calling, parses real Rotterdam/Breda/Haaglanden PDFs from `/data` | Only Dutch banks; only 5 categories |
| **C: Report generator + PDF rendering** | 1 | Claude prompt + react-pdf template, branded | One report template; no email delivery |
| **D: Story + UX polish + deploy** | 1 | Framer landing, copy, video, boxd deploy | — |

**Cut hard:** foodbank login, multi-corporate dashboards, real wire transfers (mock), historic backfill, anything that doesn't appear in the 1-min video.

## Prize alignment

- **Built Different** — ingestion agent is genuinely hard agentic work (heterogeneous PDFs → normalized FRAME schema)
- **Pixel Perfect** — B2B ESG marketplace is a clean canvas; Framer landing
- **Mic Drop** — live PDF generation moment + "€1 = €12 social value (Deloitte)" line
- **Real Ones** — Voedselbanken Nederland is a real partner; FRAME is a real GFN methodology; ANBI tax structure exists; numbers are real
- **Launch Ready** — deployable Monday; pilot conversation with VBN is realistic

## Key open decisions

1. **Featured banks** — confirmed: Rotterdam, Amsterdam, Breda, Eindhoven, Groningen (regional cluster).
2. **Package tiers** — single €25k tier OR add smaller (€5k = 120 tCO2e) to fit small banks?
3. **Cluster vs. individual** — does a corporate sponsor *one* bank, or *one region*? (Recommended: support both, default to cluster for banks <500 t/yr.)
