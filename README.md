# Kavel

Platform connecting Dutch corporates to foodbank climate-contribution funds. Corporates buy contribution packages; money is allocated to foodbanks weighted by CO₂e avoided and/or households served. Claude generates ESRS E5 + S3-aligned climate-contribution disclosures, streamed live via SSE.

**Positioning:** climate contribution, not offsetting. FRAME-aligned, NL-specific counterfactual, defensible to a Big-4 auditor under ESRS E5.

**Live:** https://klimaatkracht.boxd.sh

## Stack

| Layer | Tech |
|-------|------|
| Backend | FastAPI · SQLModel · SQLite (`foodbank.db`) · Alembic |
| AI | Anthropic SDK · `claude-sonnet-4-6` (reports) · `claude-haiku-4-5` (extraction) |
| Frontend | Next.js 16 · React 19 · Tailwind · Boska + Switzer (Fontshare) |
| Ingestion | Typer CLI · 5-section parallel Claude extraction · OCR fallback |
| Methodology | FRAME (Global FoodBanking Network) · CF<sub>NL</sub> = 0.93 |

## Backend setup

```bash
# Install dependencies
uv sync --extra dev

# Copy and fill environment variables
cp .env.example .env  # set ANTHROPIC_API_KEY and SESSION_SECRET

# Apply migrations
uv run alembic upgrade head

# Seed database (creates demo@acme.nl / demo1234)
python -m src.backend.seed

# Run API
uvicorn src.backend.app:app --reload
```

API docs: http://localhost:8000/docs

## Frontend setup

```bash
cd src/frontend
pnpm install
pnpm dev          # http://localhost:3000
```

Pages:

| Route | Purpose |
|-------|---------|
| `/` | Landing — pitch, traction, trust signals |
| `/marketplace` | Browse contribution packages |
| `/foodbanks` · `/foodbanks/[slug]` | Foodbank network + detail pages |
| `/methodology` | FRAME pipeline, formula, factor table, provenance ledger |
| `/faq` | Jury-grade Q&A — positioning, methodology, marketplace, ethics, business, risk |
| `/for-foodbanks` | Onboarding pitch for foodbank operators |
| `/pricing` | Package tiers |
| `/reports/sample` | Heineken Q1 2026 sample disclosure |
| `/dashboard/corporate` | Sponsor view — subscriptions, allocations |
| `/login` · `/register` | Auth |

## Ingestion pipeline

Ingest foodbank annual reports (PDF or txt) into the database:

```bash
# Single file
uv run python -m src.backend.preprocessing.cli ingest data/amsterdam-2024.pdf \
  --bank-name "Voedselbank Amsterdam" --city Amsterdam --region randstad --year 2024 \
  --provider anthropic --model claude-sonnet-4-6

# Batch (all PDFs in a directory, skips already-ingested)
uv run python -m src.backend.preprocessing.cli ingest-dir data/ \
  --provider anthropic --model claude-sonnet-4-6

# Inspect database
uv run python -m src.backend.preprocessing.cli db overview
uv run python -m src.backend.preprocessing.cli db banks
```

PDFs without extractable text fall back to the Anthropic document API (OCR).

> ⚠️ Never run `ingest-dir --force` without explicit confirmation. It overwrites all existing extractions.

## Database migrations

```bash
uv run alembic upgrade head                        # apply all pending
uv run alembic revision --autogenerate -m "desc"   # generate after model change
uv run alembic current                             # check revision
uv run alembic downgrade -1                        # roll back one step
```

Always uses `render_as_batch=True` (required for SQLite).

## Tests

```bash
uv run pytest                          # all tests
uv run pytest tests/backend/routers/   # routers only
```

In-memory SQLite via `conftest.py` fixture; integration-style, no DB mocks.

## Scripts

| Script | Purpose |
|--------|---------|
| `./scripts/dev.sh` | Start backend (`:8002`) + frontend (`:3000`) concurrently |
| `./scripts/deploy.sh` | rsync + migrate to `klimaatkracht.boxd.sh` |
| `./scripts/deploy.sh --restart` | Same + restart the server process |
| `./scripts/deploy-vercel.sh` | Deploy frontend to Vercel (uses `BACKEND_URL` env var, defaults to `https://klimaatkracht.boxd.sh`) |

```bash
# Local dev (both services)
./scripts/dev.sh

# Deploy backend to boxd VM
./scripts/deploy.sh
./scripts/deploy.sh --restart

# Deploy frontend to Vercel
./scripts/deploy-vercel.sh
```

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | yes | — | Report extraction + generation |
| `SESSION_SECRET` | no | `dev-secret-change-in-prod` | Cookie signing key |

## Documentation

| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project guide for Claude Code agents |
| `docs/methodology/FRAME-Methodology-GFN-2024.pdf` | Source methodology |
| `docs/context/finalist-pitch.md` | 2-min demo + Q&A drill |
| `docs/context/late-night-pitch-practice/pitch-v2.md` | 90s pitch storyline (5 chapters) |
| `docs/specs/` | Frontend + wireframe specs |
| `docs/superpowers/plans/` | Implementation plans (data model, API, ingestion) |

## Repo layout

```
src/
├── backend/                 # FastAPI app
│   ├── routers/             # auth, marketplace, checkout, dashboard, admin, report
│   ├── services/            # allocation engine, report streaming
│   ├── preprocessing/       # Typer CLI for ingestion
│   ├── models.py            # SQLModel tables
│   └── seed.py              # demo data
├── frontend/                # Next.js 16 app
│   ├── src/app/             # routes (see table above)
│   ├── src/components/      # nav, marketing, foodbanks, dashboard, charts
│   └── src/lib/             # methodology constants, photo helpers
docs/
├── context/                 # pitch + launch plans
├── methodology/             # FRAME PDF
├── specs/                   # design specs
└── superpowers/             # implementation plans
migrations/                  # Alembic
tests/                       # pytest
```

## License

Built for the Anthropic Hackathon (April 2026). Code under MIT pending team alignment.
