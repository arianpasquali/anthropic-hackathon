# Klimaatkracht

Platform connecting Dutch corporates to foodbank climate impact funds. Corporates buy impact packages; money is allocated to foodbanks weighted by CO₂e savings and/or households served. Claude generates CSRD/ESRS E5-compliant reports streamed via SSE.

**Live:** https://klimaatkracht.boxd.sh

## Stack

FastAPI + SQLModel + SQLite + Anthropic SDK + Typer CLI (preprocessing). Frontend: HTMX + Jinja2 + Tailwind (in progress).

## Setup

```bash
# Install dependencies
uv sync --extra dev

# Copy and fill environment variables
cp .env.example .env  # set ANTHROPIC_API_KEY and SESSION_SECRET

# Seed database (creates demo@acme.nl / demo1234)
python -m src.backend.seed

# Run server
uvicorn src.backend.app:app --reload
```

Open http://localhost:8000/docs for the API.

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

PDFs without extractable text automatically fall back to the Anthropic document API (OCR).

## Database migrations

```bash
uv run alembic upgrade head                        # apply all pending
uv run alembic revision --autogenerate -m "desc"   # generate after model change
uv run alembic current                             # check revision
```

## Tests

```bash
uv run pytest                          # all tests
uv run pytest tests/backend/routers/  # routers only
```

## Deploy

```bash
./scripts/deploy.sh            # sync + migrate (skip restart if running)
./scripts/deploy.sh --restart  # sync + migrate + restart server
```

Deploys to `klimaatkracht.boxd.sh` via rsync + SSH.

## Environment variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | yes | — | For report extraction and generation |
| `SESSION_SECRET` | no | `dev-secret-change-in-prod` | Cookie signing key |
