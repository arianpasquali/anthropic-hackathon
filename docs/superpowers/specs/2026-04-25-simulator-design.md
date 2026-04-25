# FRAME Impact Simulator — Design Spec

**Date:** 2026-04-25  
**Status:** Approved for implementation

## Overview

Interactive simulator embedded in the `/banks/[id]` page. Lets corporate visitors adjust donation amount and instantly see attributed CO₂e avoided, food rescued, and the bank's social reach. Supports CSRD/ESRS E5 reporting by exposing a full methodology trail.

## Placement

New section inserted below existing food category mix bar, above the sticky buy sidebar. Does **not** replace or rewrite existing page content.

---

## Hero Panel (dark emerald)

Three numbers displayed side by side:

| Metric | Default (€25,000) | Source |
|--------|-------------------|--------|
| tCO₂e avoided | 600 | `amount_eur ÷ 41.67` |
| kg food rescued | 323,189 | `attributed_tco2e × 1000 ÷ weighted_ef` |
| Households/week | 4,700+ (Rotterdam) | VBN jaarverslag 2024 — RDC + 33 satellites |

Header copy: _"Sponsoring [bank] means supporting a network that reaches:"_

The households figure is a **static bank property** (not derived from donation amount). It shows the full network reach of the RDC including satellite banks.

---

## Donation Slider

- Range: €5,000 – €100,000
- Default: €25,000
- Numeric input synced with slider
- All three hero numbers recompute on change (client-side, instant)

---

## Category Breakdown Chart

Horizontal bar chart: tCO₂e attributed per food category.

Computed from: `attributed_tco2e × category_share × EF[cat] / weighted_ef_sum`

Categories (Rotterdam defaults):

| Category | Share | EF (kg CO₂e/kg) | Color |
|----------|-------|-----------------|-------|
| produce | 50% | 1.0 | green |
| dry goods | 18% | 2.0 | blue |
| dairy | 10% | 3.2 | orange |
| bakery | 10% | 1.5 | purple |
| meat | 5% | 8.5 | red |
| prepared | 5% | 3.0 | yellow |
| eggs | 2% | 4.5 | slate |

---

## Methodology Trail (collapsible)

Collapsed by default. Expands to show 5 numbered steps with inline citations.

```
Step 1 — Bank throughput: {annual_kg_rescued} kg/yr rescued
Step 2 — Weighted EF: Σ(share × EF[cat]) × 0.93 (NL counterfactual) = {weighted_ef}
Step 3 — Bank annual: {annual_kg} × {weighted_ef} ÷ 1000 = {annual_tco2e} tCO₂e/yr
Step 4 — Attribution: €{amount} ÷ €41.67 = {attributed_tco2e} tCO₂e | {attributed_tco2e}×1000÷{weighted_ef} = {attributed_kg} kg
Step 5 — Social reach: {households_per_week}+ hh/wk across {bank_name} + {n_satellites} satellite banks (VBN 2024)
Sources: FAO FWF · WRAP · RIVM · GFN FRAME · VBN jaarverslag 2024
```

---

## FRAME Attribution Math

All computation is deterministic client-side TypeScript, mirroring `archive/df/frame/calculator.py`.

```
weighted_ef = Σ(category_share × emission_factor[cat]) × CF_NL
CF_NL = 0.93
PRICE_PER_TCO2E = 41.67

attributed_tco2e = amount_eur / PRICE_PER_TCO2E
attributed_kg    = attributed_tco2e * 1000 / weighted_ef
```

Category breakdown:
```
category_tco2e[cat] = attributed_tco2e × (share[cat] × EF[cat]) / Σ(share × EF)
```

---

## Architecture

**No API round-trip.** Pure client-side computation.

- New file: `src/lib/frame.ts` — exports `computeImpact(bankId, amountEur)` returning `FrameResult`
- New component: `src/components/ImpactSimulator.tsx` — slider + hero + chart + methodology trail
- Consumed by: `src/app/banks/[id]/page.tsx` (extend, do not rewrite)
- Bank data: read from existing `src/lib/mock.ts` `BANKS` map; add `households_per_week` and `n_satellites` fields

---

## Data Contract

```typescript
interface BankData {
  id: string
  name: string
  annual_kg_rescued: number
  households_per_week: number
  n_satellites: number
  category_mix: Record<string, number>  // shares sum to 1.0
}

interface FrameResult {
  attributed_tco2e: number
  attributed_kg: number
  households_per_week: number          // static from bank
  category_breakdown_tco2e: Record<string, number>
  methodology_trail: string[]
}
```

---

## Out of Scope

- Server-side computation (math is too simple to warrant API)
- Saving simulation results (buy flow handles that)
- Custom category mix editing
- Multi-bank comparison in simulator (handled elsewhere in marketplace)
