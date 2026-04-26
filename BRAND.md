# Climate Harvest — Brand voice

Single source of truth for tone, register, and copy discipline. Lives next
to `CLAUDE.md`; copy edits and new pages must conform.

## Audiences (ranked)

| # | Persona                            | Reads                          | Buys with        |
|---|------------------------------------|--------------------------------|------------------|
| 1 | Corporate CSR / sustainability lead, CFO | Methodology, fund detail, FAQ | Defensibility, citations, no hype |
| 2 | Big-4 auditor (gatekeeper of #1)   | Methodology, FAQ "Positioning"  | Provenance, cited counterfactual |
| 3 | Foodbank operator (volunteer)      | /for-foodbanks, footer          | Dignity, clarity, no jargon |
| 4 | Journalist                         | Landing, /why, /coverage        | Quotable lines, numbers that stand alone |
| 5 | Investor / hackathon jury          | All                             | Commercial signal + ambition + audit grade |

Primary register is auditor-defensible. Journalist-readability is a free
side-effect of doing #1 well: when every claim is concrete, sourced, and
restrained, it becomes copy-paste ready.

## Three voice layers

| Layer       | Where                             | Style                                | Example |
|-------------|-----------------------------------|--------------------------------------|---------|
| **Headline**   | h1 / h2, with Boska italic accent | Quotable, concrete, ≤14 words      | *"Foodbanks are climate infrastructure nobody counts."* |
| **Body**       | Section paragraphs                | Editorial, sourced, restrained     | *"73% of Dutch people in poverty are not reached by a foodbank. The gap is invisible in any official report."* |
| **Microcopy**  | CTAs, buttons, labels             | Direct, verb-first, ≤4 words       | "Browse funds →" · "Onboard your bank" · "See the gemeente-level map →" |

## The six brand-voice rules

1. **Concrete > abstract.** Never "impact" alone. Always *tCO₂e · kg rescued · households served · gemeenten reached*.
2. **Cite or stay silent.** Every numeric claim has a source line or footnote inline.
3. **Restrained > loud.** No `!`. No superlatives. No emoji in product copy.
4. **Civic > startup.** Institutional weight, Dutch register. Use *ledger · wedge · counterfactual · provenance*. Avoid *platform · synergy · disruption · transformative · revolutionary · leverage · unlock · seamless*.
5. **Contribution, not offset.** Every disclosure-related sentence holds the line. Banned terms enforced in `src/backend/services/report.py` system prompt.
6. **One quotable line per section.** Journalists copy-paste from H2s. Make every H2 stand alone.

## Operational rules (apply on every edit)

- **First sentence is the answer.** No throat-clearing.
- **One number per claim.** *"0.93 NL counterfactual"* beats *"carefully calibrated counterfactual derived from..."*.
- **Em-dashes, not exclamations.** No emojis.
- **Verbs, not adjectives.** *Audited > rigorous · disclosed > transparent · rescued > saved · ingested > onboarded.*
- **Dutch register switches when serving NL operators.** Civic functional, *u*-form, no startup slang.
- **Boska italic = the contradiction or punchline only.** *"Not offsetting." "Disclosure-ready." "One audit trail per euro."* Never decorative.
- **Numbers tabular, always.** Use `tabular` class on figures. No mixed-width digits in stats, prices, or dates.
- **Acronym discipline.** ESRS / CSRD / FRAME unexplained on first use is fine — buyers know them. Spell out only on `/faq`.

## Surface-by-surface tone mapping

| Surface                              | Tone                              | Why                                   |
|--------------------------------------|-----------------------------------|---------------------------------------|
| Landing hero, italic accents         | **2** (editorial w/ punchline)    | Earns attention, sets register        |
| Landing body sections                | **1** (strict editorial)          | Numbers carry the page                |
| /why · /coverage · /methodology      | **1** strict                      | Auditor + journalist source-of-truth |
| /marketplace · fund cards            | **1** strict, microcopy 4-word verbs | Buyer scans, decides, clicks       |
| /for-foodbanks                       | **1** + slight Dutch civic warmth | Audience = volunteer ops, not auditor |
| /pricing                             | **1** strict; emphasized tier may use one italic accent | Procurement-grade |
| /faq                                 | **1** strict, conversational tightening on questions | Builds trust |
| Disclosure document body (`/reports`) | **1** strict, **VERBATIM Dutch on disclaimer** | Drops into CSRD report |
| Chatbot replies                      | **1** + tighter (≤2 sentences per reply) | Configured guardrail |
| CTAs / buttons                       | Verb-first microcopy (≤4 words)   | Action over description              |
| Error messages / system feedback     | Civic, calm, never punishing      | Trust holds even when things break    |

## Banned terms (regression risk — grep before merge)

| Don't                       | Do                                   |
|-----------------------------|--------------------------------------|
| Verified avoided emissions  | Verified climate contribution        |
| Carbon offset / offsetting (in product copy) | Climate contribution         |
| Compliance product          | ESRS-aligned disclosure             |
| Audit-ready                 | Auditor-defensible / disclosure-ready |
| Climate neutral / CO₂-neutral | (do not use)                        |
| Compensatie / klimaatneutraal (NL) | Klimaatbijdrage              |
| Synergy · seamless · leverage · unlock · transformative | (do not use) |
| Best-in-class · industry-leading · world-class | (do not use)        |

Carbon-offset reference is allowed in `/faq` "What this is not" answers
and in the `CostEffectivenessGauge` benchmark comment, where it's
contrasted explicitly. Nowhere else.

## Quotable lines already in the build

Treat these as load-bearing — refactor with care.

- *"Foodbanks are climate infrastructure nobody counts."* — /why hero
- *"75,000 tonnes of CO₂e of climate contribution sits unattributed every year."* — /why §04
- *"The Netherlands wastes 70× more food than its foodbanks rescue."* — /methodology + /why §02
- *"Climate contribution. Not offsetting."* — landing + footer + /pricing + /faq
- *"Three tiers. One audit trail per euro."* — /pricing
- *"Operational truth on one side. Auditable disclosure on the other."* — landing PlatformSpread
- *"Where the funds land. Where the need is."* — /marketplace map
- *"Where the need is. Where the gap is."* — /coverage hero
- *"12 foodbanks · €425k · 7,718 tCO₂e"* — landing traction
- *"Demand is bounded by your network capacity."* — /for-foodbanks adoption slider

Plus one Dutch-language quotable line is missing for NL press — open
TODO in `docs/visual-todo.md`.

## Microcopy library (canonical strings)

Reuse these verbatim. Never reword in new components.

- "Browse funds →"
- "Onboard your bank"
- "Join as a food bank"
- "Buy a fund."
- "Read the FAQ →"
- "Read the FRAME methodology"
- "See the gemeente-level map →"
- "See the gemeente-level coverage map →"
- "Talk to us"

## Disclosure-page constraints (regulatory; non-negotiable)

The Dutch disclaimer block in every generated report must appear verbatim.
See `src/backend/services/report.py` `_SYSTEM` prompt.

```
> **Disclaimer.** Dit betreft een geverifieerde klimaatbijdrage, geen
> CO₂-compensatie onder ESRS E1. De gerapporteerde CO₂e wordt niet in
> mindering gebracht op de Scope 1/2/3 voetafdruk van de afnemer en
> vervangt geen wettelijke rapportageverplichting. Vermeden emissies
> worden afzonderlijk gerapporteerd overeenkomstig EFRAG E1-4 §AR-58.
> Methodologie: FRAME (Global FoodBanking Network) met Nederlandse
> counterfactual (RIVM Afvalmonitor 2024, CBS Waste Statistics).
> Aangesloten bij VCMI en Oxford Net Zero contribution-claim richtlijnen.
```

## Review checklist (every PR touching copy)

- [ ] Headlines ≤14 words; punchline-italic only on contradiction or close
- [ ] Every figure has a source line or footnote
- [ ] No banned terms (grep `verified avoided emissions · audit-ready · seamless · unlock · transformative · CO₂-neutral`)
- [ ] Numbers wrapped in `tabular`
- [ ] Microcopy reused from canonical library, not reworded
- [ ] CTA verbs ≤4 words
- [ ] No `!` outside the chat assistant's own user messages
- [ ] Dutch operator-facing strings use *u*-form, civic register
