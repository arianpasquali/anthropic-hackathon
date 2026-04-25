# Klimaatkracht — Architecture Plan for Demo-Ready Build

*24-hour hackathon scope. Architecture optimized for stage demo, not production. Honest separation between what's real, what's mocked, and what's roadmap.*

---

## 1. Demo-driven design

The architecture exists to serve one thing: a five-minute stage demo that shows the round-trip between corporate buyer, food bank operations, and verified impact report. Every architectural choice is justified by whether it makes that demo land. Production-readiness is explicitly out of scope.

**The demo flow we're building toward.**

1. (~45 sec) A corporate sustainability manager lands on Klimaatkracht's marketplace, browses Climate-Action Packages, picks one, and completes purchase. She sees confirmation and a forecast of impact.
2. (~60 sec) Cut to a food bank volunteer at the loading dock. He scans a few barcodes from real grocery items, photographs an unlabeled crate of vegetables. The system classifies, weighs, and logs each donation. A real-time CO2e counter increments.
3. (~75 sec) Cut back to the corporate buyer. An impact report has been generated for her — branded to her company, in her CSR framework's voice, with audit trail. She opens it and reads aloud one paragraph.
4. (~30 sec) Pull back to a network view: this same loop happening across three Voedselbank chapters simultaneously, total tonnes scaling. The narrative beat: "this is how an entire underfunded sector becomes a climate-finance asset."
5. (~30 sec) Close with the unit economics math from the pitch.

Total: ~4 minutes of demo, ~1 minute of pitch wraparound. Everything in the architecture supports this flow.

## 2. System architecture overview

Three thin slices, one shared backend. The slices are deliberately decoupled because they're three different demo moments — the buyer flow, the volunteer flow, and the report — and we cannot afford coupling failures during a live stage demo.

```
+----------------------+  +----------------------+  +----------------------+
|   Buyer Marketplace  |  |  Volunteer Intake    |  |   Report Generator   |
|   (Next.js web)      |  |  (Mobile PWA)        |  |   (Server-side LLM)  |
+----------+-----------+  +----------+-----------+  +----------+-----------+
           |                         |                         |
           v                         v                         v
+--------------------------------------------------------------------------+
|                       Shared Backend (FastAPI)                            |
|   - Sponsorship records   - Intake events    - Impact computations        |
|   - CO2e coefficient lookup table   - Anomaly flags  - Audit log          |
+--------------------------------------------------------------------------+
                                    |
                                    v
                         +----------------------+
                         |   PostgreSQL +       |
                         |   object storage     |
                         |   (Supabase or       |
                         |    SQLite + S3)      |
                         +----------------------+
```

The buyer and volunteer surfaces never talk to each other directly — they share the database. The report generator polls for new intake events and produces fresh report content on demand. This isolation is what lets the demo recover gracefully if any single component glitches mid-demo.

## 3. Component-by-component build plan

### 3.1. Buyer marketplace (Next.js)

The customer-facing surface that has to look like a product, not a hackathon project. This is where we spend the most polish budget.

**Pages.**

- Landing — value proposition, three example packages, methodology link, pricing.
- Browse — grid of Climate-Action Packages filterable by region, impact volume, focus area.
- Package detail — projected CO2e savings, partner food bank, methodology footnote, "purchase" CTA.
- Checkout — corporate details form, contract preview (auto-generated PDF), confirmation. We mock payment with a "Sponsor Now" button that bypasses Stripe for the demo. (In production, Stripe + manual contract review.)
- Buyer dashboard — a single sponsored package, real-time impact counter, downloadable reports list.

**Build details.**

- Next.js 15 with App Router, deployed to Vercel. Tailwind for styling. shadcn/ui for component library — these defaults give us a reasonable design system without spending time picking one.
- Five seeded Climate-Action Packages hardcoded in the database. Real food bank partner names (with explicit "demo data" disclaimers). Plausible numbers based on the Navarra study's 32:1 ratio scaled to chapter size.
- Buyer dashboard pulls live numbers from the shared database — when a volunteer scans a barcode in another window, the dashboard's counter increments. This is the key demo moment that makes the product feel real.

**What we are not building.** Real Stripe integration. Real contract law (the contract PDF is a template with fields filled in). Real KYC. Multi-buyer dashboards. Account management. Password reset. All of these are needed for production; none are needed for the demo.

### 3.2. Volunteer intake PWA (mobile-first web app)

The component that establishes credibility. If the intake doesn't feel real, the verification claim fails and the whole pitch unravels. We invest disproportionately here.

**Three input modes, in order of demo importance.**

1. *Barcode scan* — primary demo mode. Uses the device camera + html5-qrcode library. Resolves to OpenFoodFacts API (~3M EU products). Shows: product name, weight, category, projected CO2e impact. Volunteer confirms with one tap. This is the visceral demo moment — phone camera at a real Albert Heijn package, instant readout.
2. *Photo of unlabeled item* — secondary demo mode. Camera captures crate of vegetables; image goes to Claude Sonnet 4.5 via API with a structured prompt asking for food category, estimated weight (using a reference object if visible), and confidence score. Output is FRAME-aligned category. Volunteer can correct and the correction is logged for future training (we don't actually train, but the pipe exists).
3. *Voice / bulk entry* — tertiary, deferred. "18 kilos of apples from AH Centraal." Whisper API transcribes; LLM parses to structured intake. Probably cut from 24-hour scope.

**Build details.**

- PWA built with Next.js (same monorepo as buyer marketplace) so we share components and styling.
- Camera access via standard MediaDevices API. Barcode reading client-side (html5-qrcode), no server roundtrip. Vision classification server-side (Claude Sonnet 4.5 via Anthropic API).
- OpenFoodFacts integration is unauthenticated, free, and reliably available — we cache popular Dutch SKUs locally to handle the demo even if the API is slow.
- CO2e coefficient lookup table is a static JSON file derived from Poore & Nemecek 2018 (the dataset FRAME uses). About 40 food categories, each with a kg CO2e / kg food coefficient. We'll bias coefficients conservatively for buyer-credibility reasons.

**What's mocked.** The "verification audit trail" is real (we genuinely log every intake event with timestamps, photos, classifications) but we don't have actual third-party audit. We frame this as "audit-ready," which is honest — the trail exists; auditors haven't yet been engaged.

### 3.3. Report generator (server-side LLM pipeline)

The component where AI does its highest-value work. Each corporate buyer gets a custom report tuned to their CSR framework, voice, and industry.

**Pipeline.**

1. Triggered when the buyer dashboard requests a report (button click) or on a quarterly cadence (cron, mocked in demo).
2. Server queries database for all intake events attributed to this buyer's sponsored package within the reporting period.
3. Aggregates: total tonnes food rescued, total CO2e avoided, breakdown by category, by chapter, by retailer-source.
4. Buyer profile (industry, CSR framework, prior reports) is loaded from a small JSON config we hardcode for demo buyers.
5. LLM (Claude Sonnet 4.5) generates the narrative report sections using a structured prompt with: aggregated numbers, methodology citations, buyer context, target framework.
6. Report assembled into branded PDF using a template (HTML → PDF via Puppeteer or react-pdf).
7. Stored in object storage; URL returned to buyer dashboard.

**The prompt strategy.** We want reports that sound like they were written by the buyer's own sustainability team. The prompt includes:

- Two example paragraphs from the buyer's prior CSR report (or the closest analog we can find publicly — most large Dutch corporates publish CSR reports on their websites)
- The aggregated impact numbers as structured data
- Strict constraints: no greenwashing language, every claim numerically grounded, methodology footnotes inline
- Specific framework framing (CSRD ESRS-E1 categories, GRI, SASB) based on buyer profile

We probably get better-than-expected results because the underlying numbers are concrete and the corporate-CSR genre is well-represented in training data.

**What's mocked.** Multi-buyer reports (only one or two work for demo). Buyer-specific brand-asset injection (logos, colors) is hardcoded for the demo buyers. Translation to non-English / non-Dutch output.

### 3.4. Shared backend

Where the three surfaces meet. FastAPI with SQLAlchemy because Python plays well with the Anthropic SDK and pandas-style aggregations.

**Schema, simplified.**

```
sponsorships
  id, corporate_id, package_id, amount_eur, tonnes_co2e_committed,
  start_date, end_date, status

intake_events
  id, chapter_id, sponsorship_id (nullable; attributed via fair allocation),
  timestamp, source_retailer, food_category, weight_kg,
  co2e_kg_avoided, classification_method (barcode|vision|voice),
  classification_confidence, photo_url (nullable), volunteer_id

co2e_coefficients
  food_category, kg_co2e_per_kg_food, source_citation

reports
  id, sponsorship_id, period_start, period_end, generated_at,
  pdf_url, llm_model, prompt_hash, narrative_text

audit_log
  id, timestamp, actor (system|volunteer|corporate),
  action_type, target_id, details_json
```

**Attribution logic — the unsexy thing that matters.** When a corporate sponsors 600 tonnes from Voedselbank Leiden, and Leiden processes 800 tonnes that quarter, how do we attribute which intake events count toward this sponsor vs. another? For demo purposes, we use proportional allocation (each sponsor gets their share of the period's actual impact). The audit log records the allocation method and timestamp, so an auditor could later challenge the methodology and we can show our reasoning. This is the kind of plumbing that doesn't make the demo but does make the pitch defensible when judges probe.

**Anomaly detection — minimal but visible.** A simple rule-based flagger: if a chapter's reported daily intake deviates >2σ from its 30-day rolling average, log a flag. We won't have time to build sophisticated detection, but having even rule-based flags running visibly during the demo signals the system has integrity controls.

### 3.5. Hosting and infrastructure

**Stack.**

- Frontend (buyer + volunteer): Next.js → Vercel
- Backend: FastAPI → Railway or Fly.io
- Database: Supabase (Postgres + auth + storage in one) — the simplest path that gives us real auth, real storage, real Postgres without infrastructure work
- Object storage for PDFs and intake photos: Supabase Storage
- LLM: Anthropic API (Claude Sonnet 4.5, vision and text)
- Domain: register klimaatkracht.nl or .com on day one if available; otherwise a Vercel subdomain works for demo

**Deployment cadence during the hackathon.** Continuous deployment from main branch on push. Vercel + Railway both support this out of the box. We want every team member's commits live on the demo URL within a minute, so we can sanity-check on real devices throughout.

**Demo-day reliability tactics.**

- Pre-warmed seed data: 50+ realistic intake events already in the database before demo starts, attributed to a fictional prior sponsorship, so charts look populated
- Pre-generated reports: full PDFs already in storage with the demo buyer's name, so if the LLM hangs during demo we display the cached version
- Offline fallback: if the OpenFoodFacts API is slow, our cache of common Dutch SKUs handles the demo barcodes
- Two laptops on stage, one as primary and one as backup with the same demo state — if one freezes, switch
- All API keys in environment variables with rate-limit headroom

## 4. AI architecture: where the value is real

I want to be specific about where AI does work that wouldn't otherwise get done, vs. where we'd be sprinkling AI for marketing reasons.

**Vision classification of unlabeled intake.** This is genuine work. Roughly 30% of food bank intake is loose produce, bakery, prepared foods — no barcode possible. A volunteer can describe it but that's slow and inconsistent. Claude Sonnet 4.5 vision processes a crate photo in 2-3 seconds, returns structured output with category and weight estimate, and the volunteer corrects rather than describes from scratch. This makes the intake step fast enough that volunteers will actually do it consistently — which is the precondition for the entire verification claim.

**Buyer-tuned report narrative.** Each corporate's CSR framework and tone differs. Today, a nonprofit fundraiser might write a generic impact report and leave the corporate's team to rewrite it. Klimaatkracht's LLM does the rewriting in advance, producing report drafts that drop into the corporate's editorial flow with minimal touching. This is real time savings on both sides — and it's what makes the unit economics work, because every additional buyer doesn't proportionally increase our reporting workload.

**Conversational query interface for chapter ops.** Deferred from 24-hour scope but worth flagging. "Show me which retailer donations had highest variance last month" — chapters with no data analyst can ask questions in Dutch and get answers from their own operational data. Production-relevant; demo-irrelevant.

**Anti-fraud anomaly detection.** Rule-based for the demo, ML in production. The pitch reads better when we mention this exists than when we elaborate the implementation, so we keep it minimal but visible.

**Where we're explicitly not using AI.** Generating fake CO2e coefficients. Synthesizing intake data. Auto-approving buyer sponsorships. Anywhere the AI would replace an audit-traceable computation with a probabilistic one. The methodology has to be defensible to Jacqueline van den Ende's most skeptical question, which means the impact numbers come from coefficients × measurements, never from LLM judgment.

## 5. Data and methodology

The credibility of the entire pitch rests on the methodology being defensible. Three pillars:

**Coefficients from peer-reviewed sources.** Poore & Nemecek 2018 (the dataset behind the FAO's GHG-LCA reference work) provides per-kg CO2e values for ~40 food categories. WUR's Dutch food-LCA database adds Netherlands-specific adjustments. We use the conservative end of published ranges to avoid over-claiming.

**Counterfactual = landfill emissions.** FRAME's baseline assumption: rescued food would have ended up in landfill, where organic decomposition produces methane. We adopt the same baseline. This is conservative because some surplus would alternatively have been composted or anaerobically digested (lower emissions counterfactual) — meaning our claimed avoided emissions are if anything overestimates of the marginal impact. We disclose this honestly in the methodology footnote.

**Operational footprint subtraction.** Following Navarra's 2022 published methodology: we subtract the chapter's own operational emissions (driving, refrigeration, electricity) from the gross avoided figure. The Navarra ratio of 32:1 accounts for this. We use a simplified approximation in the demo (estimated kWh × Dutch grid intensity, estimated km × diesel intensity); production would integrate with chapter-level energy bills.

**Double-counting risk.** The honest concern is that the donating retailer (Albert Heijn) is also claiming the waste reduction in its Scope 3 reporting. If we're claiming the same tonne for Klimaatkracht's buyer and Albert Heijn is claiming it in their CSRD, that's double-counting. Our defensible position: we claim the *food rescue and use* impact (rerouting food from waste stream to consumption); the retailer is claiming the *waste avoidance* (reducing their disposal volume). These are distinct interventions in the lifecycle. Whether auditors will accept this distinction is genuinely uncertain — we flag this in our methodology page rather than hide it.

## 6. Build plan: 24 hours, four phases

**Hours 0–4: foundation.** Repo setup, Vercel and Railway projects, Supabase project, Anthropic API keys, base Next.js scaffold with shadcn/ui, FastAPI scaffold, schema migrations. By hour 4 we have empty pages live on the demo URL.

**Hours 4–10: ingest pipeline (the hardest single component).** Barcode scan → OpenFoodFacts → CO2e calculation → database. Photo capture → Claude vision → classification → database. Volunteer PWA shell. Real-time counter on a placeholder page. By hour 10 we can scan a real barcode at the dock and see numbers update.

**Hours 10–16: marketplace and sponsorship flow.** Buyer landing, browse, package detail, checkout (mocked payment), confirmation. Buyer dashboard with live impact counter. By hour 16 we have a buyer's-eye-view that works end-to-end.

**Hours 16–22: report generation.** LLM prompt engineering for buyer-specific reports. PDF template. Branded output. Connect to dashboard. By hour 22 we have a generated report that someone can read aloud convincingly.

**Hours 22–24: demo polish.** Seed data tuning. Practice runs. Backup plans. Pre-generation of fallback assets. Slide preparation for the pitch frame. Final landing-page copy. By hour 24 we're rehearsing the five-minute demo on the stage equivalent.

**Hours we cut if we slip.** Voice intake. Anomaly detection visualization. Multi-chapter network view. Conversational query. Two of the five buyer packages.

## 7. Team structure

**Realistic team for this scope: 4 people.**

- **Frontend lead.** Next.js, Tailwind, shadcn/ui. Owns buyer marketplace and volunteer PWA shells. The polish person.
- **Backend lead.** FastAPI, Postgres, attribution logic, audit log. Owns the shared backend and methodology implementation.
- **AI / pipelines lead.** LLM prompts for vision classification, report generation. Owns the Anthropic integrations and the methodology coefficients dataset.
- **Demo / pitch lead.** Pitch deck, methodology page, demo scripting, run-of-show, judge anticipation, backup plans. Owns the five-minute stage performance.

If we're three people, the demo lead doubles as frontend or backend. If we're five, we add a fifth role focused on partnerships and outreach (calling Voedselbank Leiden during the hackathon to see if they'd back the pitch, for instance).

## 8. Risks and pre-mortem

**Risk: Anthropic API rate-limit hit during demo.** Mitigation: pre-generate the demo report and cache it; use it as fallback if live generation hangs.

**Risk: live barcode scan fails on stage (lighting, network).** Mitigation: have three pre-tested barcodes that we know resolve cleanly. Don't ad-lib with random products.

**Risk: a judge asks an additionality question we can't answer.** Mitigation: own this in the methodology page upfront. Don't pretend the additionality question is trivial. If a judge asks, the right answer is "you're right that's a real risk, here's the boundary we've drawn and why" — not a deflection.

**Risk: the methodology is perceived as too loose.** Mitigation: lean hard into FRAME alignment. Cite Navarra's peer-reviewed math. Show the coefficient table. Conservative-bias every estimate. The credibility frame is "we use the rigorous methodology without the certification overhead, because we're not selling registry credits."

**Risk: a judge points out that food bank intake is already partly funded by retailers and that we're double-charging.** Mitigation: address this in the methodology before being asked. The retailer ESG claim is for their disposal-cost avoidance and waste-reduction targets. Our claim is for the use-not-waste impact. These are separable, but acknowledge the overlap honestly.

**Risk: the demo flow has too many moving parts.** Mitigation: the architecture's three-slice decoupling is specifically to handle this. If the report generator fails, the demo still works through "here's the pre-generated report we ran earlier this morning." If the volunteer PWA fails, the demo works through "here are intake events from yesterday." Each component has a graceful-degradation fallback.

**Risk: scope creep during the build.** Mitigation: the four-phase hour budget is a constraint, not a target. If we're behind at hour 10, we cut from the right side of the plan, not the left.

---

## Open questions worth pressure-testing

A few decisions where pushback would help:

- The decision to host backend on Railway vs. doing a single-deploy Supabase Edge Functions setup. Railway is more flexible; Supabase is simpler. If your team is Postgres-fluent, Supabase Edge Functions might collapse hours 0–4 into hours 0–1.
- The decision to use Claude Sonnet 4.5 for vision classification rather than a cheaper model. Sonnet 4.5 is overkill for "is this a tomato or a cucumber" but the demo benefits from being indistinguishable from premium classification. Haiku 4.5 would save costs and probably suffice.
- Whether to attempt to get a Voedselbank chapter on the phone during the hackathon. The pitch is materially stronger with a named partner ("we spoke with Voedselbank Leiden this morning, they're supportive") even if not formally committed. The risk is wasted hours if no one picks up.
- Whether the methodology page should be its own component on the marketplace site vs. an FAQ link. I'd lean toward its own page — it signals seriousness — but it's effort that doesn't directly support the demo flow.
