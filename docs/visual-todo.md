# Visual TODO — Klimaatkracht

Per-page audit of the frontend, with concrete proposals to move the site from "bland and naked" to editorial / civic-document weight without violating the design system in `globals.css`.

**Design register:** Dutch civic editorial. Gambarino + Switzer, OKLCH-tinted neutrals, emerald accent. Existing absolute bans (already in `globals.css`): no glassmorphism, no gradient text, no neon, no border-stripe accents, no bouncy motion. "Less bland" here means **more editorial weight**, not more SaaS chrome.

**Legend:** `P0` correctness or high-impact · `P1` substantial polish · `P2` delight / showpiece.

---

## Structural blockers (do first)

- [ ] **`P0` — `/funds` route is missing.** Listed in `sitemap.ts` but no `page.tsx`. Decide: build a thin funds index, or redirect to `/marketplace` and drop from sitemap.
- [ ] **`P0` — `/foodbanks` route is missing.** Same problem. Likely worth building (counterpart to `/marketplace`), since the `[slug]` detail page exists and is good.
- [ ] **`P0` — `/pricing` violates the "identical card grids" ban** declared in `globals.css`. Needs a real rethink, not just polish (see page section below).

---

## Cross-cutting motifs (the toolkit)

These are reusable devices. Per-page TODOs reference them by name instead of repeating.

- [ ] **Document-as-imagery.** The Heineken disclosure mock on `/` is the strongest visual on the whole site. Extend that idiom: page numbers, marginalia, footer rules, SHA-256 receipts. Use it where stock photography would normally go.
- [ ] **Operations photography.** Real foodbank work in NL: crates, vans, refrigerated DCs, hands sorting, warehouse aisles. Editorial duotone (warm grey + emerald shadow). Commission or license, never stock. Build a reusable `<EditorialPhoto>` component.
- [ ] **Live data ribbon.** Promote `.kk-live-dot` to a thin top-of-page ribbon on key marketing pages: "live · last extraction 14m ago · 12 banks · €425k pre-launched". Civic, not flashy.
- [ ] **Scroll-driven number reveal.** Counters tick up on intersect, FRAME formula prints character-by-character, allocation bars fill from 0. Easing: `cubic-bezier(0.16, 1, 0.3, 1)` (already used in `kk-live-pulse`). Respect `prefers-reduced-motion`.
- [ ] **Editorial section openers.** Paired display/serif numbers (`01 / 05 — Pipeline`) with hairline rule and italic Gambarino subtitle.
- [ ] **Paper grain background.** 0.02-opacity SVG noise on `--surface-2` panels. Adds weight without competing. Skip on data-dense surfaces.
- [ ] **Marquee strips, not carousels.** For testimonials/quotes, use slow horizontal-drift scroll-snap strips, hover-pauses. Civic register, fewer dots.

---

## `/` — Landing  *(brand)*

Current: rich (10 sections), Heineken disclosure mock is the standout. Hero is text-on-white, no imagery; pilot-partner names are flat text; map feels untethered.

- [ ] **`P0` — Hero needs a second layer.** Editorial photograph (NL warehouse interior, low-key, duotone) right-aligned in the hero grid, OR a live multi-line ticker (extraction events, kg counters scrolling slowly). Not both.
- [ ] **`P0` — Pilot-partner row → real wordmarks.** Replace typeset names with actual SVG logos in monochrome at 60% opacity.
- [ ] **`P1` — Stats stack animation.** The four hero stats count up on first viewport entry, tabular nums locked.
- [ ] **`P1` — Disclosure mockup interactivity.** Make the "page 14 of 22" mockup paginate on hover/click — show 3 different ESRS sections.
- [ ] **`P1` — Map → scroll-locked storytelling.** As the user scrolls past the map section, fade in province fills sequentially (north → south).
- [ ] **`P2` — Footer marquee** of all 6 pilot-bank wordmarks + counterparties, slow drift, hover-pauses.

## `/marketplace`  *(brand)*

Current: filter row, map, fund cards. Map is identical to landing's; no visual hierarchy between sections.

- [ ] **`P0` — Hero band.** Thin band (40–60px) under the H1: live-dot + "12 funds available · last allocation computed 6m ago" + sort dropdown.
- [ ] **`P0` — Differentiate the map** from `/`'s map: color provinces by **fund availability**, clicking a province filters the fund grid above.
- [ ] **`P1` — Fund cards need depth.** Each card gets a sparkline of historical CO₂e baseline + a thumbnail of the lead bank's province silhouette.
- [ ] **`P1` — Empty / loading states** for slow `listPackages()` — skeleton cards with shimmering hairlines, not spinners.
- [ ] **`P2` — "Compare 2 funds" sticky tray** that appears when ≥2 cards are checked.

## `/methodology`  *(brand, with product texture)*

Current: long-form, formula block, emission factor table with bars. Already the most "document"-feeling page. Mostly static.

- [ ] **`P0` — Formula reveal.** `CO₂e = Σ(kgᵢ × EFᵢ) × CF_NL` types itself out on scroll (~600ms), variables highlighted in sequence. Inline "Try with sample data" calculator below (sliders for kg + category → live CO₂e output).
- [ ] **`P0` — Pipeline diagram, not a list.** The 5-step ordered list becomes a horizontal flow diagram with connecting hairlines and a small monochrome icon per step (PDF, Claude, ledger, abacus, document).
- [ ] **`P1` — Emission factors table → interactive sort.** Click any column header to sort; hover a row to highlight that bar across rows.
- [ ] **`P1` — Provenance card grid → real example.** Replace abstract description on each card with a real extracted snippet ("Page 14, Voedselbank Rotterdam annual report 2024 → 1,240,000 kg produce").
- [ ] **`P2` — Sticky table-of-contents** on the left at lg+, highlighting the current section (Pipeline, FRAME, Factors, Counterfactual, Provenance, Claim type, Trust pillars).

## `/pricing`  *(brand — currently violating own design law)*

Current: 3 identical cards, "Most popular" pill on the middle one. This is the "identical card grid" pattern explicitly banned in `globals.css`.

- [ ] **`P0` — Rethink the layout.** Not three equal cards. Try: one wide horizontal comparison table (pricing leftmost, feature checkmarks fanning right), or stacked editorial tiers (Starter narrow at top, Partner wide and emphasized in middle, Enterprise narrow at bottom) with marginalia pull-quotes.
- [ ] **`P0` — Replace "Most popular" SaaS pill** with editorial annotation: a Gambarino-italic margin note ("Recommended for first-time disclosers — covers ESRS E5 obligations end-to-end").
- [ ] **`P1` — Live price-per-tonne calculator.** Sliders for "annual CO₂e you want to disclose" → snaps to nearest tier with the math shown.
- [ ] **`P1` — Trust footer.** Thin row below the tiers: "Invoiced via Solvimon · NL VAT · 14-day refund · audited by [TBD]".
- [ ] **`P2` — Toggle Quarterly / Annual prepay** with a small "save 8%" tag.

## `/foodbanks`  *(brand)*

Current: **route does not exist.**

- [ ] **`P0` — Build the index page.** Mirror `/marketplace`'s structure: hero, NL map (this one = bank density), filterable list with name, region, kg rescued, CO₂e baseline, households, "View profile →".

## `/foodbanks/[slug]`  *(brand → product hybrid)*

Current: stat row, timeline chart, category mix, provenance, source link. Solid information, but feels like a wiki article.

- [ ] **`P0` — Hero photograph** of THIS specific bank's location (or province silhouette as fallback). Editorial duotone, dark-emerald scrim, bank name in display serif over it.
- [ ] **`P0` — "Fund this bank" sticky CTA.** Right rail: "This bank is included in 4 funds → [Browse]". Page currently dead-ends.
- [ ] **`P1` — Provenance ledger → expand-in-place.** Click a row to reveal the extracted PDF snippet (image crop or text quote).
- [ ] **`P1` — Timeline chart annotations.** Mark significant events on the year axis ("2022: warehouse expansion", "2023: regional DC merger"), pulled from a TBD `events` field.
- [ ] **`P2` — "Compared to NL average"** small inline bars next to each stat. Cheap context, big signal.

## `/funds`  *(brand)*

Current: **route does not exist.**

- [ ] **`P0` — Decision: build or remove.** Recommend redirecting `/funds` → `/marketplace` and dropping from `sitemap.ts` rather than building a duplicate.

## `/funds/[id]`  *(brand → product hybrid)*

Current: strong page — sticky buy aside, stat row, allocation table, timeline. Most data-rich marketing page.

- [ ] **`P0` — Sticky aside is too quiet.** Add: live mini-counter ("3 corporates committed this quarter"), thin progress bar showing fund capacity ("€340k / €500k allocated"), pre-launch live-dot.
- [ ] **`P0` — Allocation table → visual flow.** Small SVG sankey above the table: `€25k → 8 banks` with line widths proportional to weight.
- [ ] **`P1` — Hero needs a face.** 3-4 small circular photos of lead allocated banks' operations + "Top allocations: Rotterdam · Den Haag · Amsterdam".
- [ ] **`P1` — Methodology badges → linked.** Each Badge ("FRAME aligned", "ESRS E5 + S3"…) becomes a popover with one-sentence definition.
- [ ] **`P2` — Forecast vs realised toggle** on the timeline chart (data is already split; expose it).

## `/funds/[id]/buy`  *(product)*

Current: mock checkout form, demo card defaults, summary aside. Functional, dry.

- [ ] **`P0` — Trust strip above the form.** Thin row: "Solvimon-secured · NL VAT · Cancel any quarter · No card charged in sandbox". The "no card charged" is buried — make it impossible to miss.
- [ ] **`P0` — Order summary → printed receipt.** Restructure right aside as a printed receipt: bank logo header, line items, subtotal/VAT/total in tabular nums, footer with subscription ID. Re-uses the document-as-imagery motif.
- [ ] **`P1` — Inline field validation** with emerald checkmark when valid, civic warning treatment when not.
- [ ] **`P1` — "What happens next" mini timeline** below the form: "1. Allocation runs (instant) → 2. Quarterly disclosure ready (24h) → 3. CFO download (any time)".

## `/funds/[id]/buy/confirmed`  *(product)*

Current: badge + headline + 3 stats + two CTAs. Anticlimactic for what should be the emotional peak of the funnel.

- [ ] **`P0` — Make it a moment.** Single-screen, centered. Slow line-draw checkmark (1.2s), headline fades in after, three stats count up sequentially. No confetti.
- [ ] **`P0` — Send the receipt.** Show "Confirmation receipt sent to [email]" line and offer immediate PDF download of the subscription receipt.
- [ ] **`P1` — Live allocation reveal.** List that animates in row-by-row: "Allocated to Voedselbank Rotterdam: 31% (€7,750)…".
- [ ] **`P2` — Calendar invite for the next quarterly disclosure** ("Q2 2026 disclosure will be ready 2026-07-15 — add to calendar?").

## `/login`  *(product)*

Current: split layout, copy left, form right in bordered card. Clean, no imagery.

- [ ] **`P0` — Background ambience.** Either (a) faint SVG of NL province outlines bottom-right at 8% opacity, OR (b) a single vertical Gambarino-italic quote stretching the full left column.
- [ ] **`P1` — Demo-credentials badge** instead of the footnote. A small "Try the demo →" that auto-fills the form on click.
- [ ] **`P1` — SSO placeholders** ("Sign in with Microsoft" — most CFOs use M365). Even disabled with "coming soon" badge sells enterprise readiness.

## `/register`  *(product)*

Current: same split layout as login + role toggle (corporate/foodbank).

- [ ] **`P0` — Role toggle → branching split.** Left-side copy shifts based on selected role (corporate vs operator). Currently same copy regardless of role.
- [ ] **`P0` — Visual proof of role choice.** Pick "Food bank operator" → show thumbnail of the upload flow on the left. Pick "Corporate" → show snippet of a sample disclosure.
- [ ] **`P1` — Password strength meter** + civic-styled error treatments matching `--warning-soft`.

## `/dashboard/corporate`  *(product)*

Current: dense, 8+ sections — map, gauges, allocation table, scorecards. Already busy. Risk here isn't "bland" — it's "cluttered."

- [ ] **`P0` — Hero compression.** Compress header into a single 80px band: org name + tier badge + status + amount + CTA. Push the dashboard up.
- [ ] **`P0` — Tier-1 stat row → narrative numbers.** Each of the 4 stats gets a tiny inline sparkline (last 4 quarters, 60×16px) under it.
- [ ] **`P1` — Empty state needs more.** Add a preview thumbnail of what the dashboard WILL look like (greyscale ghost) + 3 testimonial-style quotes from pilot corporates rotating on a slow scroll-snap marquee.
- [ ] **`P1` — Geographic coverage hover sync.** Hover a province on the map → list row highlights, and vice versa.
- [ ] **`P1` — "Generate report" should be a moment.** When user clicks "View CSR report →", brief "Composing your disclosure…" splash with the live-dot before routing.
- [ ] **`P2` — Print stylesheet.** Should be screenshot-able and PDF-printable. Tabular nums + page-break rules + "printed by [name] on [date]" footer.

## `/dashboard/foodbank`  *(product)*

Current: header, 3 stat cards, upload widget + how-it-works aside, reveal-on-upload section. Hardcoded to "amsterdam" demo.

- [ ] **`P0` — Empty state IS the page.** Until upload, the page is mostly placeholders. Treat the upload widget as the hero — 60% of viewport, strong dropzone visual (paper-stack illustration in monochrome, drag-and-drop affordance with emerald glow on dragover).
- [ ] **`P0` — Upload progress is the showpiece.** When a PDF is dropped, screen reorganizes: dropzone shrinks to a sidebar tile, live extraction stream appears center-screen ("Reading section 3/5: Food categories…", "Extracted: 1,240,000 kg produce", "Provenance: page 14, table 3.1"). Currently just toggles a `revealed` boolean.
- [ ] **`P1` — Sponsor activity feed.** Once funded, the "Active sponsors" stat expands into a list of corporates who've committed, with their tier and logo.
- [ ] **`P1` — Year-over-year comparison.** Once an operator has uploaded ≥2 reports, show a delta chart of CO₂e baseline.

## `/reports/[subId]`  *(product, brand-grade craft)*

Current: thin shell — header and `<ReportStream>`. Stream component does all the work.

- [ ] **`P0` — Treat the streamed report as a printed document.** Wrap `<ReportStream>` in a paper-style frame: A4-proportions container, faint top/bottom hairlines, page number footer, "Generated by Claude · timestamp · SHA-256" subtle header. Same idiom as the Heineken mockup on `/`.
- [ ] **`P0` — Streaming state needs identity.** While Claude streams: `[● live] Claude is composing your disclosure · Section 3 of 7` with thin pulsing line (not a spinner). When done, line goes solid and "Download PDF / .md" toolbar fades in.
- [ ] **`P1` — Right-rail outline.** As headings stream in, populate a clickable TOC on the right.
- [ ] **`P1` — Citation tooltips.** Footnote markers in the streamed text become hoverable: "Voedselbank Rotterdam Annual Report 2024, p. 14".
- [ ] **`P2` — Side-by-side mode.** Toggle for "Show source PDFs alongside" — split view with disclosure on left, source PDF page on right at the relevant citation.

---

## Sequencing recommendation

Build **one cross-cutting motif end-to-end** before touching individual pages. Pick **operations photography** (commission/curate the duotone treatment, define how it sits behind text, build a `<EditorialPhoto>` component). That single decision unlocks: hero on `/`, hero on `/foodbanks/[slug]`, ambient on `/login`, and lead images in `/funds/[id]`.

In parallel: **fix `/funds` and `/foodbanks` (routes missing)** and **rethink `/pricing`** (currently violates the design law). Those are correctness, not polish.
