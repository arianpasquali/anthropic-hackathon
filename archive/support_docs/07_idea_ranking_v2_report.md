# Idea Ranking v2 — Report

**Source:** `06_idea_ranking_v2.csv`
**Date:** 2026-04-25
**Theme:** Build local — minorities, non-profits, municipalities, emergency services.

## Scoring Framework

Each idea scored 0–100 across 11 dimensions, equal-weighted into an aggregate.

**Ideation criteria (from `ideation_criteria.txt`):**

| Dimension | Meaning |
|---|---|
| Urgency | How critical the underlying problem is right now |
| Impact | How many people are affected |
| Feasibility | How buildable in a 24h hackathon |
| Cost Efficiency | How cheap to build (inverted cost) |
| Likelihood | How likely it works as intended (inverted risk) |
| Wow Factor | How much spectacle on stage |

**Hackathon judging criteria:**

| Dimension | Meaning |
|---|---|
| Innovation | Originality vs. prior art |
| Build Local | Fit with NL institutions, language, infra |
| Technical Execution | Engineering depth + quality of demo |
| Impact & Viability | Real-world deployment path post-hackathon |
| Pitch & Presentation | How well it lands in a 5-min jury pitch |

---

## Top 10 Ideas

### 1. NP-15-B — Photograph-a-letter translator + action advisor (87.5)
Belastingdienst/Gemeente letters are universal NL pain. OCR + LLM mature. One-screen demo with a real letter on stage. Lands with all four judges; consumer + nonprofit + municipal angle simultaneously.

### 2. ES-18-A — AR AED opening walkthrough (80.8)
Tactile demo with a real Philips HeartStart on stage. CV + AR build is non-trivial but tractable in 24h. Strong "technology saves life" pitch arc.

### 3. NP-13-A — Self-service eligibility estimator + warm handoff (80.6)
Voedselbanken NL partnership natural. Chatbot + form pre-fill fits 24h. Reaches 100k+ unreached eligible. Mission narrative crisp.

### 4. NP-20-B — AI safety-planning chatbot in Dutch + migrant languages (80.6)
DV is acute (~3% reach Veilig Thuis). LLM + KB build well-scoped. Risk: chatbot demos commoditised — execution must shine.

### 5. ES-12-A — Operational-hours overlay on HartslagNu (80.5)
HartslagNu is iconic NL infra. Map overlay self-explanatory. Toronto study shows 25% coverage uplift.

### 6. NP-20-A — Dual-purpose 'decoy' safety app with LINK integration (79.6)
Reveal moment is cinematic. Anti-discovery UX adds engineering cost. NL-specific via LINK + Veilig Thuis.

### 7. ES-04-A — Real-time OHCA call-audio classifier (explainable) (78.4)
Explainability is the differentiator vs. Corti (Blomberg JAMA RCT showed opaque alerts fail). Founder-judges (van Lanschot, Mol) respond to this category.

### 8. ES-18-B — Dispatch-optimised volunteer role assignment (78.4)
HartslagNu integration → high local credibility. Live map with named volunteers tells a crisp collaboration story.

### 9. ES-05-A — AR-guided CPR via smartphone video (78.2)
Most cinematic possible demo (phone over a mannequin). 24h AR build + consent UX is the risk.

### 10. ES-03-A — Real-time two-way speech translation overlay for 112 (76.5)
APIs mature, integration tractable. Carbyne/Prepared already deployed in US/DE — judges may see as derivative.

---

## Mid-Tier Ideas (Ranks 11–20)

| Rank | ID | Idea | Score | Note |
|---|---|---|---|---|
| 11 | NP-15-A | Multilingual DigiD / Gemeente procedural assistant | 76.4 | Skendy + RefuGPT exist; differentiation is execution. NL bureaucracy fit very strong. |
| 12 | ES-05-B | Adaptive DA-CPR script for physical-constraint scenarios | 75.6 | Branching script tractable; dispatcher-screen demo quiet vs. AR sibling. |
| 13 | ES-09-C | Explainable shadow-reasoning dispatch assistant | 74.4 | Reasoning trace lands with explainability-curious judges. Same problem as ES-04-A but applied to triage. |
| 14 | ES-10-B | LLM-driven adaptive questioning for ambiguous symptoms | 73.8 | Novel reframing of MPDS but visually quiet on stage. |
| 15 | ES-18-C | Residential-zone AED confidence nudge | 73.2 | Push notifications structurally low-drama; insight strong but doesn't pitch. |
| 16 | ES-03-B | Voice-first multilingual pre-call app (112 companion) | 72.7 | Genuinely novel caller-side approach (US11589205 covers server-side only). Pre-call adoption is the viability risk. |
| 17 | ES-04-B | Caller-smartphone OHCA visual confirmation | 72.3 | Highly novel but consent-then-camera flow clunky on stage; idea > demo. |
| 18 | ES-09-A | LLM advisory flagging likely-overtriage cases | 71.9 | Quebec 74.5% overtriage figure quantifies value. Quiet dispatcher-internal demo. |
| 19 | ES-04-C | Post-call LLM QI reviewer | 71.7 | Operationally useful, dashboard demo dead on stage. |
| 20 | ES-10-A | ML secondary-review overlay for low-priority dispatches | 70.6 | Uppsala RCT scaffolds. Synthetic call data demo needs heavy explanation. |

## Bottom Tier (Ranks 21–30)

| Rank | ID | Idea | Score | Note |
|---|---|---|---|---|
| 21 | ES-05-C | Audio metronome + calming soundscape | 70.3 | Trivial to build, but "we built a metronome" sinks ambition signal with founder-judges. |
| 22 | NP-15-C | AI + peer-navigator hybrid | 68.7 | Two-sided workflow. Hard to demo end-to-end; soul of idea fights pitch format. |
| 23 | ES-10-C | Post-dispatch callback prioritisation | 68.4 | CAD integration required. "Save lives by ordering a list" doesn't land in 5 min. |
| 24 | ES-09-B | In-call non-urgent self-service chatbot | 68.2 | Portugal INEM pilot precedent. "Redirected from 112 to chatbot" is socially delicate framing. |
| 25 | NP-20-C | Frontline-professional silent-referral tool | 68.2 | Real Meldcode gap but multi-party demo mostly slides + personas. |
| 26 | ES-12-B | 24/7 residential AED neighbour programme | 67.3 | Globally novel programme but multi-quarter operational build, not 24h hackathon. |
| 27 | ES-03-C | LLM speech reconstruction for panicked callers | 67.3 | Frontier research (Venkateshperumal 2024 on synthetic only). Reconstructed text invisible to audience. |
| 28 | ES-12-C | Remote-unlock outdoor AED cabinet (IoT retrofit) | 65.5 | Hardware + IoT + dispatch glue prohibitive in 24h. Live cabinet unlock would be dramatic if achievable. |
| 29 | NP-13-B | Proactive referral via partner-institution screening | 64.5 | Wgs 2021 debt analogue. Multi-party plumbing pitches as institutional diagrams. |
| 30 | NP-13-C | Stigma-free supermarket voucher model | 64.3 | UK Healthy Start proves model. Demo looks like any payment app; insight is the model not the screen. |

---

## Cross-Cutting Patterns

**What lifts an idea up:**
- **Single-screen, tactile demo.** A real artefact on stage (letter, AED, mannequin) outperforms dashboards every time. NP-15-B, ES-18-A, ES-05-A all win on this axis.
- **NL-specific institutional anchor.** Belastingdienst, Voedselbanken, HartslagNu, Veilig Thuis, LINK — naming a Dutch system the judges recognise immediately scores Build Local at 85+ and primes Impact & Viability.
- **Mission urgency that reads in 30 seconds.** DV (NP-20), OHCA (ES-04, ES-05, ES-18), refugees navigating bureaucracy (NP-15) all carry the narrative without needing setup.

**What sinks an idea:**
- **Multi-party workflows.** NP-13-B/C, NP-20-C, ES-10-A — anything requiring two personas to collaborate on stage collapses into slides.
- **Dispatcher-internal tooling.** ES-09-A, ES-10-A/C, ES-04-C are operationally credible but visually inert; jurors don't feel the impact.
- **Hardware or 1+ year deployment.** ES-12-B/C, NP-13-C are right ideas at the wrong forum.
- **Familiar-genre demos in saturated categories.** ES-03-A loses to NP-15-B not on merit but because translation overlays are visibly deployed elsewhere already.

**Risk flags on top picks:**
- **NP-15-B (#1):** demo collapses if OCR fails on a real letter — practise with 3+ varied letter types and have a fallback.
- **ES-18-A (#2):** physical AED + working AR overlay in 24h is the build risk; mock the CV with a marker if needed.
- **NP-20-B (#4):** chatbot demos are commoditised — only wins if the survivor-vignette execution is unusually good.
- **ES-05-A (#9):** AR + consent UX is a lot of moving parts; if pruned to "metronome with on-screen depth bar" it merges with ES-05-C.

---

## Recommendation

Three-way shortlist for the build decision, optimising different axes:

1. **NP-15-B** — highest aggregate, lowest-risk demo, broadest judge appeal. **Default pick.**
2. **ES-18-A** — most cinematic stage moment if the AR build holds. **Pick if confident on CV/AR depth.**
3. **NP-20-B** — strongest mission narrative; pick if team has chatbot-UX craft to differentiate from a sea of LLM wrappers. **Pick if narrative + Dutch-language polish is the strength.**

Avoid: anything ranked below 73 unless a specific team strength inverts the demo problem.
