# Klimaatkracht — API Design Spec

**Date:** 2026-04-25
**Stack:** FastAPI + HTMX + Jinja2 + SQLModel + SQLite
**Scope:** Backend API routes, data model extensions, allocation engine, auth, HTMX patterns

---

## Context

Klimaatkracht is a marketplace where Dutch corporates fund food banks and receive CSRD-aligned CO2e impact reports. Corporates choose a "Climate-Action Package" (CO2-focused, social-focused, or balanced), the platform dynamically allocates their contribution across the top N food banks matching that profile, and Claude generates a CSRD-ready PDF report.

---

## Data Model Additions

The existing spec (`2026-04-25-foodbank-data-model-design.md`) is extended with:

### `ImpactProfileEnum`
```python
class ImpactProfileEnum(str, Enum):
    co2_focus = "co2_focus"       # top N by FrameResult.co2e_total_kg
    social_focus = "social_focus"  # top N by PeopleServed.households_weekly
    balanced = "balanced"          # weighted blend of both
```

### `Package` additions
| Field | Type | Notes |
|---|---|---|
| impact_profile | ImpactProfileEnum | drives allocation ranking |
| top_n | int | default 50 — how many food banks to include |

### `Allocation`
One row per food bank per purchase. Created at checkout from dynamic ranking.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | |
| subscription_id | FK → FundSubscription | |
| foodbank_id | FK → Foodbank | |
| weight_pct | float | proportional share; sum across subscription = 1.0 |

`amount_eur` and `co2e_attributed_kg` are **computed at read time**:
- `amount_eur = subscription.amount_eur × weight_pct`
- `co2e_attributed_kg = foodbank.latest_frame_result.co2e_total_kg × weight_pct`

This keeps allocations stable as the fund grows.

---

## Allocation Engine

Called at checkout after payment confirmation.

**Input:** `subscription_id`, `package.impact_profile`, `package.top_n`

**Algorithm:**
1. Query all food banks with a `FrameResult` and `PeopleServed` record
2. Score each:
   - `CO2_FOCUS`: score = `co2e_total_kg`
   - `SOCIAL_FOCUS`: score = `households_weekly`
   - `BALANCED`: score = `0.5 × norm(co2e_total_kg) + 0.5 × norm(households_weekly)`
3. Take top N by score
4. Normalize scores to `weight_pct` (each bank's score ÷ sum of top N scores)
5. Write `Allocation` rows

---

## Auth

- `User` model with `role: RoleEnum (corporate | foodbank_op | admin)`
- Login sets signed session cookie containing `user_id`
- FastAPI `Depends(get_current_user)` on protected routes
- HTMX requests get `HX-Redirect: /login` (not HTTP 302) when unauthenticated
- Registration creates `corporate` role user; admin users seeded manually

---

## API Routes

All routes return Jinja2-rendered HTML. HTMX routes return partial fragments.

### Auth
```
GET  /login                     → login page
POST /login                     → authenticate → set cookie → redirect /packages
GET  /register                  → register form
POST /register                  → create User (corporate) → redirect /login
POST /logout                    → clear cookie → redirect /login
```

### Marketplace
```
GET  /packages                  → package grid (full page)
GET  /packages?profile=co2      → HTMX partial: filtered package cards
GET  /packages/{id}             → package detail + projected allocation preview
POST /packages/{id}/checkout    → create FundSubscription (pending) → redirect /checkout/{id}/confirm
```

### Purchase Flow
```
GET  /checkout/{sub_id}/confirm → confirm page: company details + allocation preview
POST /checkout/{sub_id}/pay     → mock payment → status=paid → run allocation engine → redirect /checkout/{sub_id}/success
GET  /checkout/{sub_id}/success → success page + link to dashboard
```

### Dashboard
```
GET  /dashboard                 → user's subscriptions + aggregate CO2e
GET  /dashboard/{sub_id}        → purchase detail: allocation breakdown + report status
```

### CSR Report
```
POST /report/{sub_id}/generate  → start Claude generation → return job status fragment
GET  /report/{sub_id}/stream    → SSE: streams Claude output live into page
GET  /report/{sub_id}/download  → serve generated report file
```

### Admin
```
GET  /admin/foodbanks            → foodbank list + scores
POST /admin/foodbanks/{id}       → update foodbank data / trigger re-ingestion
```

---

## HTMX Patterns

| Pattern | Usage |
|---|---|
| `hx-get` + `hx-swap="innerHTML"` | Package filter by impact profile (no full reload) |
| `hx-post` + `hx-indicator` | Pay button shows spinner during checkout |
| `hx-ext="sse"` | Report stream: Claude output appears live in `<div id="report-output">` |
| `HX-Redirect` header | Auth redirect without full page HTMX swap |
| `HX-Trigger` header | Fire toast notification on purchase success |

---

## Error Handling

- FastAPI exception handlers return HTMX-compatible HTML fragments
- `HX-Trigger: {"showToast": "message"}` pattern for user-facing errors
- No JSON error responses reach the UI
- 404 and 500 return full-page error templates

---

## Out of Scope

- Recurring billing / subscription renewal
- Real payment processing (mock only)
- Email delivery of reports
- Multi-corporate shared dashboards
- Food bank operator portal (data seeded by admin)
