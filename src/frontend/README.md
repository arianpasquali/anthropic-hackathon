# Kavel — Frontend

Next.js 16 marketing site + corporate dashboard for Kavel. Renders the marketplace, foodbank network, methodology, FAQ, and the sample ESRS E5 contribution disclosure.

> ⚠️ **Not the Next.js you know.** Version 16 has breaking changes — APIs, conventions, and file structure may differ from training data. Read `node_modules/next/dist/docs/` before writing new code. See `AGENTS.md`.

## Setup

```bash
pnpm install
pnpm dev          # http://localhost:3000
pnpm build        # production build
pnpm lint         # eslint
```

## Stack

| Layer | Tech |
|-------|------|
| Framework | Next.js 16 · React 19 · App Router |
| Styling | Tailwind v4 · CSS variables |
| Type | Boska (display serif) · Switzer (sans) · JetBrains Mono — Fontshare CDN |
| Icons | Lucide React |
| Maps | NL province heat-map (custom SVG) |

## Routes

| Path | Purpose |
|------|---------|
| `/` | Landing — pitch, traction strip, FRAME explainer, contribution callout, sample report |
| `/marketplace` | Package list with filters |
| `/foodbanks` | Foodbank network grid + map |
| `/foodbanks/[slug]` | Foodbank detail (CO₂e, food categories, demographics) |
| `/methodology` | Pipeline, formula, factor table, provenance ledger |
| `/faq` | 6 sections, 17 jury Q&A |
| `/for-foodbanks` | Foodbank operator onboarding pitch |
| `/pricing` | Tier comparison |
| `/reports/sample` | Full ESRS E5 + S3 disclosure (Heineken Q1 2026) |
| `/dashboard/corporate` | Sponsor view (subscriptions, allocations) |
| `/login` · `/register` | Auth |

## Design tokens

Defined in `src/app/globals.css`:

- `--font-display` — Boska (editorial serif, contemporary not luxury)
- `--font-sans` — Switzer (Swiss grotesk, audit-grade)
- `--color-emerald` / `--color-emerald-deep` / `--color-emerald-soft` — primary palette
- `--radius-lg`, `--radius-md` — surface radii
- `border-line`, `bg-surface`, `bg-surface-2` — neutral system

Utility classes:
- `.eyebrow` — kicker labels (uppercase, tabular)
- `.display` — display serif
- `.display-italic` — italic accent (emerald highlights, "Not offsetting.", "climate contribution.")
- `.tabular` — tabular-nums for figures

## Component organization

```
src/components/
├── nav/          # Header, Footer
├── marketing/    # landing sections, editorial photos, platform spread
├── foodbanks/    # category mix bars, foodbank cards
├── dashboard/    # corporate dashboard widgets
├── charts/       # bars, sparklines
├── map/          # NL province heat-map
├── funds/        # package tier UI
├── report/       # report layout components
└── ui/           # Badge, primitives
```

## Methodology constants

`src/lib/methodology.ts` mirrors backend FRAME constants — emission factors, NL counterfactual (0.93), category labels, source citations. Keep in sync with `src/backend/services/factors.py`.

## API integration

Frontend calls FastAPI backend via fetch in server components or route handlers. SSE streams (report generation) handled with EventSource on the client.

## Conventions

- Server components by default; client only when interactivity required (`"use client"`)
- Keep page files thin — extract sections to `src/components/`
- Tailwind utility-first, no CSS modules unless absolutely required
- All copy in English currently; ESRS sections retain Dutch terminology where appropriate
