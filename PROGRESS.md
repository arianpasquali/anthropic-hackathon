# Build Progress — Klimaatkracht API

**Last updated:** 2026-04-25 ~18:30
**Branch:** main
**Stack:** FastAPI + SQLModel + SQLite + HTMX + Anthropic SDK

---

## What's done

| Task | Status | Commit |
|------|--------|--------|
| Dependencies (fastapi, jinja2, anthropic, itsdangerous, httpx) | ✅ | 20925b7 |
| ImpactProfileEnum + Package.impact_profile, top_n | ✅ | 180d6d3 |
| Allocation model | ✅ | b6605d5 |
| Allocation engine (compute_allocations) | ✅ | c464838 |
| Auth service (hash_password, session cookie, get_current_user) | ✅ | 96098ab |
| Seed data (10 food banks, 3 packages, demo@acme.nl/demo1234) | ✅ | 955d5d9 |
| FastAPI app skeleton (src/backend/app.py) | ✅ | 72b611c |
| Auth routes (POST /auth/register, /auth/login, /auth/logout, GET /auth/me) | ✅ | 06276ab |
| Marketplace routes (GET /packages, GET /packages/{id}) | ✅ | 4faa856 |
| Checkout routes (POST /packages/{id}/checkout, POST /checkout/{sub_id}/pay, GET /checkout/{sub_id}/confirm) | ✅ | 4faa856 |
| Dashboard routes (GET /dashboard, GET /dashboard/{sub_id}) | ✅ | background agent |
| Admin routes (GET /admin/foodbanks) | ✅ | background agent |
| Report service (Claude SSE streaming) + routers | ✅ | — |

---

## What's still needed

### Task 12: Report generation (Claude SSE) ✅ DONE
- [x] `src/backend/services/report.py` — Claude SSE streaming, saves to data/reports/
- [x] `src/backend/routers/report.py` — POST /report/{sub_id}/generate, GET /report/{sub_id}/stream (SSE), GET /report/{sub_id}/download
- [x] Router registered in app.py
- [x] CsrReport.frame_result_id nullable

### Task 14: Frontend / templates
- [ ] Base template (base.html) with Tailwind CDN + HTMX CDN
- [ ] packages/index.html — package grid with HTMX filter buttons
- [ ] packages/detail.html — package detail with fund button
- [ ] packages/_card.html — HTMX partial card
- [ ] checkout/confirm.html — confirm page with pay button
- [ ] checkout/success.html — success page
- [ ] dashboard/index.html — subscription list
- [ ] dashboard/detail.html — allocation breakdown + CO2e bar chart
- [ ] report/_stream.html — SSE streaming container
- [ ] auth/login.html + auth/register.html
- [ ] admin/foodbanks.html
- [ ] static/css/main.css

---

## Key file locations

```
src/backend/
  app.py                    # FastAPI app, router registration
  database.py               # engine, get_session, create_db_and_tables
  seed.py                   # run with: python -m src.backend.seed
  models/
    allocation.py           # Allocation(id, subscription_id, foodbank_id, weight_pct)
    enums.py                # ImpactProfileEnum, RegionEnum, StatusEnum, etc.
    foodbank.py             # Foodbank, AnnualReport
    frame.py                # FrameResult (co2e_total_kg, counterfactual_route, etc.)
    marketplace.py          # Package, FundSubscription, CsrReport
    measurements.py         # FoodVolume, FoodCategories, PeopleServed, Operations, Donations
    user.py                 # User(id, email, hashed_password, role, org_name)
  routers/
    auth.py                 # /auth/* routes
    marketplace.py          # /packages routes
    checkout.py             # /checkout + /packages/{id}/checkout
    dashboard.py            # /dashboard (done by background agent)
    admin.py                # /admin (done by background agent)
  services/
    allocation.py           # compute_allocations(session, subscription_id, commit=False)
    auth.py                 # hash_password, get_current_user, COOKIE_NAME

src/frontend/               # EMPTY — templates not built yet
tests/
  backend/
    conftest.py             # session fixture
    models/                 # all model tests (42 passing)
    services/               # allocation engine tests
    routers/                # auth, marketplace, checkout, dashboard, admin tests
```

## Demo credentials
- URL: http://localhost:8000
- Login: demo@acme.nl / demo1234
- Start server: `uvicorn src.backend.app:app --reload`
- Seed DB: `python -m src.backend.seed`

## Report generation spec (Task 12)
Claude streams CSRD report text via SSE. Key design:
- POST /report/{sub_id}/generate → create CsrReport record → return {job_id}
- GET /report/{sub_id}/stream → StreamingResponse(text/event-stream) — Claude streams markdown
- GET /report/{sub_id}/download → serve saved report file
- services/report.py builds prompt from: company name, package, total CO2e, allocation breakdown
- Uses `claude-sonnet-4-6` with system prompt for CSRD/ESRS E5 language
- CsrReport.frame_result_id must be nullable (fix in marketplace.py)
- ANTHROPIC_API_KEY env var required
