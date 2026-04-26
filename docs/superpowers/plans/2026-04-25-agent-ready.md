# Agent-Ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Climate Harvest discoverable and usable by AI agents per isitagentready.com criteria — llms.txt, robots.txt, sitemap, ai-plugin manifest, agent.json, Link headers, OpenAPI improvements, and markdown content negotiation.

**Architecture:** Discovery endpoints live in a dedicated router (`routers/discovery.py`, already created). App metadata improvements go in `app.py`. Existing routers get tags/summaries. Middleware adds `Link` headers for agent discoverability. Key public GET endpoints gain markdown content negotiation.

**Tech Stack:** FastAPI, Starlette middleware, Python 3.13

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/backend/routers/discovery.py` | **Already created** | llms.txt, llms-full.txt, robots.txt, sitemap.xml, /.well-known/ai-plugin.json, /.well-known/agent.json, /health |
| `src/backend/app.py` | Modify | Register discovery router, improve FastAPI metadata, add Link-header middleware |
| `src/backend/routers/auth.py` | Modify | Add tags, operation summaries |
| `src/backend/routers/marketplace.py` | Modify | Add tags, summaries, markdown response |
| `src/backend/routers/checkout.py` | Modify | Add tags, summaries |
| `src/backend/routers/dashboard.py` | Modify | Add tags, summaries, markdown response |
| `src/backend/routers/report.py` | Modify | Add tags, summaries |
| `src/backend/routers/insights.py` | Already has tags | Add summaries to remaining endpoints |
| `tests/backend/routers/test_discovery.py` | Create | Tests for all discovery endpoints |

---

### Task 1: Wire discovery router + improve app metadata

**Files:**
- Modify: `src/backend/app.py`
- Already created: `src/backend/routers/discovery.py`

- [ ] **Step 1: Write failing tests for discovery endpoints**

Create `tests/backend/routers/test_discovery.py`:

```python
import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient
from src.backend.app import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_llms_txt():
    r = client.get("/llms.txt")
    assert r.status_code == 200
    assert "Climate Harvest" in r.text
    assert r.headers["content-type"].startswith("text/plain")


def test_llms_full_txt():
    r = client.get("/llms-full.txt")
    assert r.status_code == 200
    assert "/packages" in r.text


def test_robots_txt():
    r = client.get("/robots.txt")
    assert r.status_code == 200
    assert "ClaudeBot" in r.text
    assert "Allow: /" in r.text


def test_sitemap_xml():
    r = client.get("/sitemap.xml")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/xml")
    assert "/openapi.json" in r.text


def test_ai_plugin_json():
    r = client.get("/.well-known/ai-plugin.json")
    assert r.status_code == 200
    data = r.json()
    assert data["name_for_model"] == "klimaatkracht"
    assert "openapi.json" in data["api"]["url"]


def test_agent_json():
    r = client.get("/.well-known/agent.json")
    assert r.status_code == 200
    data = r.json()
    assert "llms_txt" in data


def test_link_header_on_root():
    """Discovery Link header present on all responses."""
    r = client.get("/packages")
    assert "llms.txt" in r.headers.get("link", "")
```

- [ ] **Step 2: Run tests — expect failures (router not registered)**

```bash
uv run pytest tests/backend/routers/test_discovery.py -v
```

Expected: All fail with 404 or import error.

- [ ] **Step 3: Register discovery router and improve app metadata in `app.py`**

Replace entire `src/backend/app.py` with:

```python
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

from src.backend.database import create_db_and_tables

OPENAPI_TAGS = [
    {"name": "discovery", "description": "Agent/LLM discovery: health, llms.txt, robots.txt, manifests"},
    {"name": "auth", "description": "Registration, login, logout, current user"},
    {"name": "packages", "description": "Browse available climate impact packages (public)"},
    {"name": "checkout", "description": "Subscribe to a package and confirm payment"},
    {"name": "dashboard", "description": "Your subscriptions with CO₂e attribution per foodbank"},
    {"name": "report", "description": "Generate, stream, and download CSRD/ESRS E5 reports"},
    {"name": "insights", "description": "Public platform stats and per-foodbank FRAME data"},
    {"name": "admin", "description": "Admin-only: foodbank management"},
]

app = FastAPI(
    title="Climate Harvest",
    version="1.0.0",
    summary="Dutch platform connecting corporates to foodbank climate impact funds.",
    description=(
        "Corporates subscribe to impact packages. Funds are allocated to Dutch foodbanks "
        "weighted by verified CO₂e savings (FRAME methodology) and households served. "
        "CSRD/ESRS E5-compliant reports are generated by Claude Sonnet and streamed as SSE.\n\n"
        "**Public endpoints:** `/packages`, `/insights/aggregate`, `/insights/banks`\n\n"
        "**Authentication:** Cookie session via `POST /auth/login`. "
        "Register at `POST /auth/register`.\n\n"
        "**Agent discovery:** [`/llms.txt`](/llms.txt) · "
        "[`/.well-known/ai-plugin.json`](/.well-known/ai-plugin.json)"
    ),
    contact={"name": "Climate Harvest", "email": "contact@klimaatkracht.nl"},
    license_info={"name": "Proprietary"},
    openapi_tags=OPENAPI_TAGS,
)


class AgentDiscoveryMiddleware(BaseHTTPMiddleware):
    """Add Link header pointing to llms.txt on all responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["Link"] = '</llms.txt>; rel="describedby"; type="text/plain"'
        return response


app.add_middleware(AgentDiscoveryMiddleware)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


from src.backend.routers import auth as auth_router  # noqa: E402
from src.backend.routers import marketplace as marketplace_router  # noqa: E402
from src.backend.routers import checkout as checkout_router  # noqa: E402
from src.backend.routers import dashboard as dashboard_router  # noqa: E402
from src.backend.routers import admin as admin_router  # noqa: E402
from src.backend.routers import report as report_router  # noqa: E402
from src.backend.routers import insights as insights_router  # noqa: E402
from src.backend.routers import discovery as discovery_router  # noqa: E402

app.include_router(discovery_router.router)
app.include_router(auth_router.router)
app.include_router(marketplace_router.router)
app.include_router(checkout_router.router)
app.include_router(dashboard_router.router)
app.include_router(admin_router.router)
app.include_router(report_router.router)
app.include_router(insights_router.router)
```

- [ ] **Step 4: Run tests — expect pass**

```bash
uv run pytest tests/backend/routers/test_discovery.py -v
```

Expected: All 8 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/backend/routers/discovery.py src/backend/app.py tests/backend/routers/test_discovery.py
git commit -m "feat: agent-ready discovery endpoints, Link header middleware, OpenAPI metadata"
```

---

### Task 2: Add OpenAPI tags and summaries to all routers

**Files:**
- Modify: `src/backend/routers/auth.py`
- Modify: `src/backend/routers/marketplace.py`
- Modify: `src/backend/routers/checkout.py`
- Modify: `src/backend/routers/dashboard.py`
- Modify: `src/backend/routers/report.py`
- Modify: `src/backend/routers/admin.py`

Tags tell agents which logical group an endpoint belongs to. Summaries appear in the OpenAPI spec and help LLMs pick the right endpoint.

- [ ] **Step 1: Write test verifying tags appear in OpenAPI spec**

Add to `tests/backend/routers/test_discovery.py`:

```python
def test_openapi_tags_present():
    r = client.get("/openapi.json")
    assert r.status_code == 200
    spec = r.json()
    tags_used = {
        tag
        for path in spec["paths"].values()
        for method in path.values()
        for tag in method.get("tags", [])
    }
    for expected_tag in ["auth", "packages", "checkout", "dashboard", "report", "insights"]:
        assert expected_tag in tags_used, f"tag '{expected_tag}' missing from OpenAPI spec"


def test_openapi_summaries_present():
    r = client.get("/openapi.json")
    spec = r.json()
    missing = []
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            if "summary" not in op:
                missing.append(f"{method.upper()} {path}")
    assert missing == [], f"Endpoints missing summaries: {missing}"
```

- [ ] **Step 2: Run test — expect failure**

```bash
uv run pytest tests/backend/routers/test_discovery.py::test_openapi_tags_present tests/backend/routers/test_discovery.py::test_openapi_summaries_present -v
```

Expected: FAIL — tags missing from most routers.

- [ ] **Step 3: Update `src/backend/routers/auth.py`**

Change `router = APIRouter(prefix="/auth")` to:
```python
router = APIRouter(prefix="/auth", tags=["auth"])
```

Add `summary=` to each endpoint:
- `POST /auth/register` → `summary="Register a new corporate account"`
- `POST /auth/login` → `summary="Authenticate and get session cookie"`
- `POST /auth/logout` → `summary="Clear session cookie"`
- `GET /auth/me` → `summary="Current authenticated user"`

Example for register:
```python
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse,
             summary="Register a new corporate account")
```

- [ ] **Step 4: Update `src/backend/routers/marketplace.py`**

```python
router = APIRouter(prefix="/packages", tags=["packages"])
```

Summaries:
- `GET /packages` → `summary="List available impact packages"`
- `GET /packages/{package_id}` → `summary="Get a single impact package"`

- [ ] **Step 5: Update `src/backend/routers/checkout.py`**

```python
router = APIRouter(tags=["checkout"])
```

Summaries:
- `POST /packages/{package_id}/checkout` → `summary="Subscribe to an impact package"`
- `GET /checkout/{sub_id}/confirm` → `summary="Confirm mock payment and trigger allocation"`
- `GET /checkout/{sub_id}` (if exists) → `summary="Get subscription status"`

- [ ] **Step 6: Update `src/backend/routers/dashboard.py`**

```python
router = APIRouter(prefix="/dashboard", tags=["dashboard"])
```

Summaries:
- `GET /dashboard` → `summary="List your subscriptions with CO₂e totals"`
- `GET /dashboard/{sub_id}` → `summary="Subscription detail with per-foodbank allocation"`

- [ ] **Step 7: Update `src/backend/routers/report.py`**

```python
router = APIRouter(prefix="/report", tags=["report"])
```

Summaries:
- `POST /report/{sub_id}/generate` → `summary="Trigger CSRD/ESRS E5 report generation"`
- `GET /report/{sub_id}/stream` → `summary="Stream report as SSE chunks"`
- `GET /report/{sub_id}/download` → `summary="Download saved markdown report"`

- [ ] **Step 8: Update `src/backend/routers/admin.py`**

Add `tags=["admin"]` to router and summaries to endpoints.

- [ ] **Step 9: Run all tests**

```bash
uv run pytest tests/backend/routers/test_discovery.py -v
uv run pytest -v
```

Expected: All pass.

- [ ] **Step 10: Commit**

```bash
git add src/backend/routers/auth.py src/backend/routers/marketplace.py \
        src/backend/routers/checkout.py src/backend/routers/dashboard.py \
        src/backend/routers/report.py src/backend/routers/admin.py \
        tests/backend/routers/test_discovery.py
git commit -m "feat: add OpenAPI tags and summaries to all routers"
```

---

### Task 3: Markdown content negotiation on public GET endpoints

Agents that request `Accept: text/markdown` get human-readable summaries instead of JSON. Implement for the two most useful public endpoints: `GET /packages` and `GET /insights/aggregate`.

**Files:**
- Modify: `src/backend/routers/marketplace.py`
- Modify: `src/backend/routers/insights.py`

- [ ] **Step 1: Write failing tests**

Add to `tests/backend/routers/test_discovery.py`:

```python
def test_packages_markdown_negotiation():
    r = client.get("/packages", headers={"Accept": "text/markdown"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/markdown")
    assert "## Impact Packages" in r.text
    assert "€" in r.text or "EUR" in r.text


def test_aggregate_markdown_negotiation():
    r = client.get("/insights/aggregate", headers={"Accept": "text/markdown"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/markdown")
    assert "tCO₂e" in r.text or "CO2" in r.text
```

- [ ] **Step 2: Run — expect failure**

```bash
uv run pytest tests/backend/routers/test_discovery.py::test_packages_markdown_negotiation tests/backend/routers/test_discovery.py::test_aggregate_markdown_negotiation -v
```

Expected: FAIL — returns JSON regardless of Accept header.

- [ ] **Step 3: Update `GET /packages` in `src/backend/routers/marketplace.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse

@router.get("", response_model=list[PackageResponse], summary="List available impact packages")
def list_packages(
    request: Request,
    profile: Optional[str] = None,
    session: Session = Depends(get_session),
):
    q = select(Package).where(Package.is_active == True)
    if profile:
        try:
            q = q.where(Package.impact_profile == ImpactProfileEnum(profile))
        except ValueError:
            pass
    packages = [_pkg_to_response(p) for p in session.exec(q).all()]

    if "text/markdown" in request.headers.get("accept", ""):
        lines = ["## Impact Packages\n"]
        for p in packages:
            lines.append(f"### {p.name}")
            lines.append(f"- **Region:** {p.region}")
            lines.append(f"- **Price:** €{p.price_eur:.0f}")
            lines.append(f"- **CO₂e claim:** {p.co2e_claim_kg:,.0f} kg")
            lines.append(f"- **Impact profile:** {p.impact_profile}")
            if p.description:
                lines.append(f"\n{p.description}")
            lines.append("")
        return PlainTextResponse("\n".join(lines), media_type="text/markdown; charset=utf-8")

    return packages
```

- [ ] **Step 4: Update `GET /insights/aggregate` in `src/backend/routers/insights.py`**

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse

@router.get("/aggregate", response_model=AggregateStats)
def aggregate_stats(request: Request, session: Session = Depends(get_session)) -> AggregateStats:
    """Platform-wide totals: tCO₂e, kg rescued, households, bank count."""
    # ... existing computation code unchanged ...
    stats = AggregateStats(
        banks_count=len(banks),
        total_tco2e_yr=round(total_tco2e, 1),
        total_kg_rescued_yr=round(total_kg, 0),
        total_households_wk=total_hh,
    )

    if "text/markdown" in request.headers.get("accept", ""):
        md = (
            "## Climate Harvest Platform Stats\n\n"
            f"- **Foodbanks tracked:** {stats.banks_count}\n"
            f"- **Total CO₂e avoided:** {stats.total_tco2e_yr:,.1f} tCO₂e/year\n"
            f"- **Food rescued:** {stats.total_kg_rescued_yr:,.0f} kg/year\n"
            f"- **Households served weekly:** {stats.total_households_wk:,}\n"
        )
        return PlainTextResponse(md, media_type="text/markdown; charset=utf-8")

    return stats
```

Note: The existing loop computing `total_tco2e`, `total_kg`, `total_hh` stays unchanged — only add the `request` param and the markdown branch at the end.

- [ ] **Step 5: Run tests**

```bash
uv run pytest tests/backend/routers/test_discovery.py -v
uv run pytest -v
```

Expected: All pass.

- [ ] **Step 6: Commit**

```bash
git add src/backend/routers/marketplace.py src/backend/routers/insights.py \
        tests/backend/routers/test_discovery.py
git commit -m "feat: markdown content negotiation on /packages and /insights/aggregate"
```

---

### Task 4: Verify agent readiness end-to-end

- [ ] **Step 1: Start server and spot-check endpoints manually**

```bash
uvicorn src.backend.app:app --reload &
sleep 2

curl -s http://localhost:8000/llms.txt | head -10
curl -s http://localhost:8000/robots.txt | grep ClaudeBot
curl -s http://localhost:8000/.well-known/ai-plugin.json | python3 -m json.tool | head -20
curl -s -I http://localhost:8000/packages | grep -i link
curl -s -H "Accept: text/markdown" http://localhost:8000/packages | head -15
curl -s http://localhost:8000/health
```

Expected outputs:
- `llms.txt`: starts with `# Climate Harvest`
- `robots.txt`: contains `User-agent: ClaudeBot` and `Allow: /`
- `ai-plugin.json`: valid JSON with `name_for_model: klimaatkracht`
- Link header: `</llms.txt>; rel="describedby"`
- Markdown packages: starts with `## Impact Packages`
- Health: `{"status": "ok"}`

- [ ] **Step 2: Check OpenAPI spec has all tags**

```bash
curl -s http://localhost:8000/openapi.json | python3 -c "
import json, sys
spec = json.load(sys.stdin)
tags = {t for p in spec['paths'].values() for m in p.values() for t in m.get('tags', [])}
print('Tags found:', sorted(tags))
"
```

Expected: `['admin', 'auth', 'checkout', 'dashboard', 'discovery', 'insights', 'packages', 'report']`

- [ ] **Step 3: Kill server, run full test suite**

```bash
kill %1 2>/dev/null; uv run pytest -v
```

Expected: All tests pass, zero failures.

- [ ] **Step 4: Final commit**

```bash
git add -p  # stage any remaining changes
git commit -m "feat: agent-ready complete — llms.txt, robots.txt, manifests, Link headers, markdown negotiation"
```

---

## Checklist: isitagentready.com criteria

| Criterion | Implemented | Where |
|-----------|-------------|-------|
| robots.txt with AI bot rules | ✅ | `GET /robots.txt` |
| Sitemap | ✅ | `GET /sitemap.xml` |
| Link response header | ✅ | `AgentDiscoveryMiddleware` |
| llms.txt | ✅ | `GET /llms.txt` |
| llms-full.txt | ✅ | `GET /llms-full.txt` |
| Markdown content negotiation | ✅ | `/packages`, `/insights/aggregate` |
| ai-plugin.json (plugin manifest) | ✅ | `GET /.well-known/ai-plugin.json` |
| Agent card / agent.json | ✅ | `GET /.well-known/agent.json` |
| OpenAPI spec with tags + summaries | ✅ | All routers + FastAPI metadata |
| Health endpoint | ✅ | `GET /health` |
| MCP server | ❌ Not built | Future work — add `mcp/` router with tools |
| OAuth discovery | ❌ Not built | Future work — cookie auth only for now |
| x402 payment protocol | ❌ Not applicable | Uses mock payment flow |
