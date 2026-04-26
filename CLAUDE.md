# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Klimaatkracht** — a platform connecting Dutch corporates to foodbank climate-contribution funds. Corporates buy contribution packages; money is allocated to foodbanks weighted by CO₂e avoided and/or households served. Claude generates ESRS E5 + S3-aligned climate-contribution disclosures streamed via SSE.

Positioning: **climate contribution, not offsetting.** FRAME-aligned, NL-specific counterfactual (CF=0.93), defensible to Big-4 auditor under ESRS E5.

Stack: FastAPI + SQLModel + SQLite (`foodbank.db`) + Anthropic SDK + Typer CLI (ingestion). Frontend: Next.js 16 + React 19 + Tailwind v4 in `src/frontend/`.

## Commands

```bash
# Install
uv sync --extra dev

# Run server
uvicorn src.backend.app:app --reload

# Seed database (creates demo@acme.nl / demo1234)
python -m src.backend.seed

# Run all tests
uv run pytest

# Run single test file
uv run pytest tests/backend/routers/test_auth.py

# Run single test
uv run pytest tests/backend/routers/test_auth.py::test_login_success
```

## Architecture

### Data flow

1. **Ingestion** (`src/backend/preprocessing/` — in progress): Typer CLI reads foodbank annual report PDFs, runs 5 parallel Claude Haiku extractions (one per measurement section), writes structured data into SQLModel tables with provenance tracking (`source=extracted`, `method=<citation>`).

2. **Allocation engine** (`services/allocation.py`): `compute_allocations(session, subscription_id)` scores all foodbanks by CO₂e impact and/or households served (controlled by `Package.impact_profile`: `co2_focus | social_focus | balanced`), takes top N, normalizes weights to `weight_pct` fractions.

3. **Report generation** (`services/report.py`): `stream_report(session, sub_id)` calls `claude-sonnet-4-6` with a Dutch CSRD/ESRS E5 system prompt, streams SSE chunks to the client, and saves the final markdown to `data/reports/{sub_id}.md`.

### Key model relationships

```
User → FundSubscription → Package
                       ↓
                  Allocation (weight_pct per Foodbank)
                       ↓
            Foodbank → AnnualReport
                            ↓
                 FrameResult (co2e_total_kg, counterfactual_route)
                 FoodVolume / FoodCategories / PeopleServed / Operations / Donations
```

`FrameResult.co2e_total_kg` is the computed CO₂e figure used by the allocation engine. Each measurement field in `measurements.py` has a `_source: SourceEnum` and `_method: str` sibling — the `_check_provenance` validator enforces that if a value is set, its source must also be set.

### Auth

Cookie-based sessions using `itsdangerous.URLSafeTimedSerializer` (7-day TTL). `get_current_user` is a FastAPI dependency; `require_admin` wraps it with role check. Unauthenticated requests get 303 redirect to `/login`.

### Router layout

| Prefix | File | Description |
|--------|------|-------------|
| `/auth` | `routers/auth.py` | register, login, logout, /me |
| `/packages` | `routers/marketplace.py` | list/filter packages |
| `/checkout` | `routers/checkout.py` | create subscription, mock payment, confirm |
| `/dashboard` | `routers/dashboard.py` | subscription list, allocation detail with CO₂e |
| `/admin` | `routers/admin.py` | foodbank list (admin role only) |
| `/report` | `routers/report.py` | generate, stream (SSE), download |

### Testing

Tests use an in-memory SQLite engine (via `conftest.py` `session` fixture). All router tests use `httpx.TestClient`. No mocking of the database — integration style against real SQLModel.

## Database migrations (Alembic)

```bash
# Apply all pending migrations
uv run alembic upgrade head

# Generate migration after model changes (autogenerate detects schema drift)
uv run alembic revision --autogenerate -m "describe_change"

# Check current revision
uv run alembic current

# Downgrade one step
uv run alembic downgrade -1
```

Config: `alembic.ini` + `migrations/env.py`. env.py imports all models via `src.backend.models` and reads `DATABASE_URL` from `src.backend.database`. Always use `render_as_batch=True` (required for SQLite column changes).

After adding/changing a model field: run `revision --autogenerate`, review the generated file in `migrations/versions/`, then `upgrade head`.

## Git

Work directly on `main`. No feature branches.

## Environment

`ANTHROPIC_API_KEY` — required for report generation  
`SESSION_SECRET` — defaults to `"dev-secret-change-in-prod"`

## Ingestion pipeline rules

- **Never run `ingest-dir --force` without explicit user confirmation.** It overwrites all existing DB extractions (including higher-quality model runs) with whatever model is passed.
- Ask before any force-refresh or batch re-ingest operation.

## Frontend (Next.js 16)

Lives in `src/frontend/`. Routes: `/`, `/marketplace`, `/foodbanks` (+ `[slug]`), `/methodology`, `/faq`, `/for-foodbanks`, `/pricing`, `/reports/sample`, `/dashboard/corporate`, `/login`, `/register`.

Type system: Boska (display serif) + Switzer (sans) via Fontshare CDN. Design tokens in `src/frontend/src/app/globals.css`. See `src/frontend/README.md` for setup and `src/frontend/AGENTS.md` for the Next.js 16 caveat (breaking changes vs. training data — read `node_modules/next/dist/docs/` before writing new code).

```bash
cd src/frontend && pnpm install && pnpm dev   # http://localhost:3000
```

## Ingestion pipeline

Built. CLI lives in `src/backend/preprocessing/`. Original plan in `docs/superpowers/plans/2026-04-25-ingestion-pipeline.md`. Quick reference:

```bash
uv run python -m src.backend.preprocessing.cli ingest <pdf>      # single
uv run python -m src.backend.preprocessing.cli ingest-dir data/  # batch
uv run python -m src.backend.preprocessing.cli db overview       # inspect
```
