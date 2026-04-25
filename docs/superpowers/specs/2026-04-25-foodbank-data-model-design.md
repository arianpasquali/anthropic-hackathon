# Foodbank Data Model — Design Spec

**Date:** 2026-04-25
**Project:** Climate-Action Packages for Dutch Foodbanks
**Stack:** Python, SQLModel (Pydantic + SQLite/Postgres), FastAPI

---

## Scope

Canonical data model for:
1. Ingesting annual foodbank PDF reports → normalized schema
2. Running FRAME CO2e calculations on extracted data
3. Driving the marketplace (Packages, FundSubscriptions, CsrReports)
4. Auth (User login/roles)

---

## Key Decisions

| Decision | Choice | Reason |
|---|---|---|
| Time granularity | Annual snapshots | Source cadence is annual PDFs |
| ORM | SQLModel | Single schema for DB + Pydantic validation |
| Provenance | Per-field `_source` + `_method` siblings | FRAME methodology requires audit trail per value |
| Donation tracking | Aggregated annual totals | Only aggregate data available in reports |
| Subscription model | One-off purchase (`FundSubscription`) | Demo scope; recurring can be added later |

---

## Data Provenance Pattern

Every nullable measurement field has two siblings:

```python
class SourceEnum(str, Enum):
    extracted = "extracted"                  # direct PDF extraction
    inferred_national_avg = "inferred_national_avg"   # NL national average applied
    inferred_category_split = "inferred_category_split"  # total kg × ratio
    inferred_calculation = "inferred_calculation"    # e.g. weekly × 52
    manual = "manual"                        # human override

# Pattern (repeated per nullable field):
kg_received_total: float | None = None
kg_received_total_source: SourceEnum | None = None
kg_received_total_method: str | None = None
# method example: "extracted from PDF p.12 table 3"
# method example: "NL RIVM 2023 category split applied to total kg"
```

---

## Entities

### Auth layer

#### `User`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| email | str unique | |
| hashed_password | str | bcrypt |
| role | RoleEnum | `corporate \| foodbank_op \| admin` |
| org_name | str? | company name for corporates |
| created_at | datetime | |

---

### Marketplace layer

#### `Package`
Portfolio/product offering — one or more foodbanks bundled with a CO2e claim and price.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| name | str | e.g. "Rotterdam Climate Package" |
| description | str? | |
| region | RegionEnum | `noord \| oost \| zuid \| west \| randstad` |
| price_eur | float | default 25000.0 |
| co2e_claim_kg | float | default 600000 (600 tCO2e) |
| is_active | bool | controls marketplace visibility |

M2M to `Foodbank` via `PackageFoodbank`.

#### `PackageFoodbank` (join table)
| Field | Type | Notes |
|---|---|---|
| package_id | FK → Package | |
| foodbank_id | FK → Foodbank | |
| weight_pct | float? | pro-rata attribution share; null = equal split |

#### `FundSubscription`
One-off purchase event: User × Package.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| user_id | FK → User | |
| package_id | FK → Package | |
| amount_eur | float | actual charged amount |
| status | StatusEnum | `pending \| paid \| failed \| refunded` |
| solvimon_id | str? | external payment reference |
| purchased_at | datetime | |
| csr_report_id | FK → CsrReport? | set once report generated |

#### `CsrReport`
Generated PDF report tied to a subscription.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| subscription_id | FK → FundSubscription | |
| frame_result_id | FK → FrameResult | |
| generated_at | datetime | |
| file_path | str | path to rendered PDF |
| template | TemplateEnum | `gri \| csrd \| esrs_e1 \| generic` |

---

### Core data layer

#### `Foodbank`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| name | str | |
| city | str | |
| region | RegionEnum | |
| is_regional_dc | bool | Rotterdam/Amsterdam/Tilburg are RDCs |
| vbn_member_id | str? | Voedselbanken Nederland member ID |

#### `AnnualReport`
Root record per bank per year. Links to raw PDF on disk.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| foodbank_id | FK → Foodbank | |
| year | int | |
| period_start | date | |
| period_end | date | |
| raw_file_path | str | path to source PDF/TXT |
| ingested_at | datetime | |
| ingestion_model | str | Claude model ID used for extraction |

All measurement tables below are 1:1 children of `AnnualReport`.

---

### Measurement tables (all fields nullable with provenance siblings)

#### `FoodVolume`
| Field | Type |
|---|---|
| kg_received_total | float? |
| kg_via_national_dc | float? |
| kg_direct | float? |
| waste_pct | float? |
| parcels_distributed | int? |
| avg_products_per_parcel | float? |
| pct_schijf_van_vijf | float? |
| food_value_eur | float? |

#### `FoodCategories`
FRAME emission factors apply per category. Fallback: NL national average distribution.

| Field | Type | Notes |
|---|---|---|
| kg_produce | float? | aardappelen, groente, fruit |
| kg_meat_fish | float? | vlees & vis |
| kg_dairy_eggs | float? | zuivel & eieren |
| kg_dry_goods | float? | droge kruidenierswaren |
| kg_bread_bakery | float? | brood |
| kg_prepared | float? | bereid voedsel |
| kg_non_food | float? | hygiene, household items |

**NL fallback category split** (used when only total kg available):
- produce 37%, dairy_eggs 16%, dry_goods 18%, bread_bakery 11%, meat_fish 6%, prepared 8%, non_food 4%
- Source: Voedselbanken Nederland Feiten & Cijfers 2024 + RIVM

#### `PeopleServed`
| Field | Type | Notes |
|---|---|---|
| households_weekly | int? | primary impact metric |
| individuals_total | int? | households × avg size |
| children_count | int? | |
| pct_under_18 | float? | national: 37% |
| pct_single_adults | float? | national: 45% |
| pct_single_parent | float? | national: 28% |
| pct_families | float? | national: 23% |
| pct_couples | float? | national: 4% |

#### `Operations`
| Field | Type | Notes |
|---|---|---|
| volunteers_count | int? | |
| distribution_locations | int? | physical sites |
| satellite_banks_served | int? | for RDC banks only |
| annual_budget_eur | float? | |
| total_expenditure_eur | float? | |
| counterfactual_route | CounterfactualEnum | always explicit for FRAME audit; NL default: `incineration_energy_recovery` |

`CounterfactualEnum`: `incineration_energy_recovery | landfill | composting`

#### `Donations`
| Field | Type |
|---|---|
| food_supermarket_kg | float? |
| food_company_kg | float? |
| food_dc_kg | float? |
| money_individuals_eur | float? |
| money_companies_eur | float? |
| money_orgs_eur | float? |
| money_government_eur | float? |

---

### Computed output

#### `FrameResult`
Outputs of the deterministic FRAME engine. Stored separately from inputs so methodology is auditable.

| Field | Type | Notes |
|---|---|---|
| report_id | FK → AnnualReport 1:1 | |
| co2e_total_kg | float | sum of all categories |
| co2e_produce_kg | float | |
| co2e_meat_fish_kg | float | |
| co2e_dairy_eggs_kg | float | |
| co2e_dry_goods_kg | float | |
| co2e_bread_kg | float | |
| emission_factor_source | str | e.g. "FAO Food Wastage Footprint 2013 + WRAP UK" |
| methodology_version | str | e.g. "FRAME-NL-v1.0" |
| computed_at | datetime | |

---

## Entity Relationship Summary

```
User ──────────────────── FundSubscription ──── Package ──── PackageFoodbank ──── Foodbank
                                │                                                     │
                           CsrReport                                           AnnualReport
                                │                                               /  |  |  \  \
                          FrameResult ◄──────────────────────── FoodVolume  FoodCategories
                                                                PeopleServed  Operations  Donations
```

---

## Out of Scope (this spec)

- Recurring billing / subscription renewal
- Multi-corporate dashboards
- Foodbank operator login portal
- Email delivery of CSR reports
- Historic data backfill beyond available PDFs
