# Idea Ranking v3 — Post-Kickoff Realignment

**Source inputs:** `hackhaton-info.txt`, `hackathon-kickoff-organizers-ideas.txt`, `hackathon-kickoff-organizers-openideas.txt`, `hackathon-kickoff-meeting-transcript.txt`, `06_idea_ranking_v2.csv`
**Date:** 2026-04-25
**Supersedes:** `07_idea_ranking_v2_report.md` (kept for record; ranking obsolete)

---

## 0. Executive Summary

The kickoff materially narrowed the strategic frame. Three signals dominate:

1. **Warchild is the customer.** The kickoff explicitly framed the weekend around solving "actual challenges they face," and Warchild presented four named asks. The build-local theme still applies, but the implicit deployer for top-ranked ideas is now Warchild (or a peer INGO), not Belastingdienst, 112, HartslagNu, or Voedselbanken.
2. **Tight workflow tools beat general AI apps.** Organizer notes are emphatic: "don't build a general AI app; build a tight workflow tool around a real Warchild communication/problem-reporting bottleneck."
3. **Build for current limits.** The kickoff explicitly cautioned against frontier ambition — reliable, simple, deployable workflows over agentic moonshots. Combined with the **$50 Anthropic credit cap**, this rewards short-context, structured-output designs.

Consequence: the prior v2 top 10 — almost all NL-emergency-services or NL-municipal — drop sharply on **Build Local** (now read as "Warchild fit" or "INGO fit"), **Impact & Viability** (no clear path to a Warchild deployment), and **Pitch** (kickoff narrative is Warchild-shaped). The single best idea from v2 (NP-15-B, photograph-a-letter) survives as an honourable mention only.

**New top pick:** **WC2-A — Offline-first voice-to-structured-case capture** for child protection in acute humanitarian settings. Aggregate 85.3, beating every v2 idea on the new rubric. Maps directly to Warchild Ask #2 ("Reimagining Case Management"), demos cleanly with an airplane-mode toggle, and has a credible commercial expansion path across the INGO sector.

---

## 1. What Changed at Kickoff

### 1.1 The four named Warchild asks

From `hackathon-kickoff-organizers-openideas.txt`:

| # | Ask | One-line framing |
|---|---|---|
| 1 | **Personalised Support** | Use AI to listen to youth (15–24) in conflict settings, understand needs in real time, and route to brief preventative MH interventions. |
| 2 | **Reimagining Case Management** | A low-tech / offline-capable child protection case management system that preserves quality, confidentiality, and safety in acute humanitarian crises. |
| 3 | **Re-invent Digital Mailroom** | Replace fragile Salesforce-embedded comms automation with a modular, transparent, configurable layer. |
| 4 | **Enhancing Data Privacy** | Pseudonymous longitudinal tracking of beneficiaries (children, vulnerable communities) — GDPR-compliant, low-connectivity-tolerant, useless-if-breached. |

These are authoritative — they are the actual problems Warchild presents on the kickoff stage and (per organizer notes) judges expect to see addressed.

### 1.2 Operating constraints surfaced by the kickoff

| Constraint | Implication |
|---|---|
| $50 Anthropic credit cap | Penalise long-context, multi-turn agent loops; reward short structured outputs and Haiku-class fallbacks. |
| Reson8 (Dutch STT) sponsor | Voice ideas can use Reson8 for the Dutch HQ demo; field-language voice still needs Whisper-class. |
| boxd microVMs sponsor | Low-friction deploy of demo to a public HTTPS URL — favours ideas with a server component. |
| Solvimon (monetisation) sponsor + judges from Mollie/Duna/Polarsteps | Viability pitch matters — clear initial user, painful workflow, expansion path. |
| Reliability over ambition | Steers away from real-time multimodal, on-device LLMs, or speculative agentic flows. |
| "Symbiotic with startups" framing | Wedge thinking: one tight customer, one painful workflow, then expand. |

---

## 2. Re-evaluation of v2 Top Ideas

Prior v2 winners scored under the new lens. Build Local is reframed as **"fit with Warchild or another concrete kickoff-named NGO/agency"**; Impact & Viability is reframed as **"path to deployment with this hackathon's actual customer"**.

| v2 Rank | Idea | v2 Score | v3 Score | Δ | Status |
|---|---|---|---|---|---|
| 1 | NP-15-B Photograph-a-letter translator | 87.5 | **72** | -15.5 | Survives as honourable mention if pivoted to refugee families *served by* Warchild NL programmes; strong demo, wrong customer otherwise. |
| 2 | ES-18-A AR AED walkthrough | 80.8 | **48** | -32.8 | Off-customer. AED + Warchild = no logical path. Cut. |
| 3 | NP-13-A Foodbank eligibility | 80.6 | **52** | -28.6 | Off-customer (Voedselbanken, not Warchild). Cut. |
| 4 | NP-20-B DV chatbot | 80.6 | **70** | -10.6 | Adjacent: Warchild does GBV work with adolescents. Survives only if reframed for adolescent survivors *in Warchild's youth MH catalogue* — at which point it converges with the new WC1-A. |
| 5 | ES-12-A AED hours overlay | 80.5 | **45** | -35.5 | Off-customer. Cut. |
| 6 | NP-20-A Decoy safety app | 79.6 | **62** | -17.6 | Cinematic demo, off-customer. Cut unless reframed for adolescent disclosure (overlaps WC1-B). |
| 7 | ES-04-A OHCA call classifier | 78.4 | **40** | -38.4 | Off-customer. Cut. |
| 8 | ES-18-B Volunteer role assignment | 78.4 | **42** | -36.4 | Off-customer. Cut. |
| 9 | ES-05-A AR-guided CPR | 78.2 | **45** | -33.2 | Off-customer. Cut. |
| 10 | ES-03-A 112 translation overlay | 76.5 | **48** | -28.5 | Off-customer; Reson8 fit doesn't rescue it. Cut. |

**Net effect:** of the v2 top 10, only NP-15-B and NP-20-B survive as honourable mentions, and only after pivoting away from their original customer.

---

## 3. New Idea Set — Warchild-Aligned (12 ideas, 4 asks × 3 angles)

### Ask 1 — Personalised Support (youth MH triage & routing)

**WC1-A. Voice-first youth MH check-in & routing companion**
A youth (15–24) speaks 60–90s in their mother tongue about how they're doing this week. Whisper / Reson8 transcribes; Claude extracts a structured signal vector (sleep, mood, social isolation, safety concerns, somatic indicators) using a Warchild-aligned screening rubric (RHS-15 / K10-derived). The tool routes to one of N brief interventions in Warchild's catalogue (self-guided module, peer-circle invitation, counsellor referral) and triggers a safeguarding escalation if any red-flag indicator hits. Designed for low-bandwidth (audio-only fallback). Lives inside the Can't Wait to Learn / TeamUp delivery channels.

**WC1-B. Adaptive privacy-first self-screening tool**
Youth-driven self-screening with branching question flow on top of validated instruments (RHS-15, PHQ-A, K10). Tool runs entirely on-device with Claude only in escalation / interpretation; results stay local unless youth explicitly shares with a counsellor. Designed for the trust-deficit context where typing answers into a server is itself a barrier.

**WC1-C. Peer-narrative library RAG companion**
A library of 200–500 Warchild-curated youth narratives (anonymised, consented). When a youth describes a situation, retrieval surfaces "young people who felt like this said it helped to…" — a peer-modelled coping recommendation rather than a clinical instruction. Heavy human curation; Claude as the retrieval interpreter.

### Ask 2 — Reimagining Case Management (offline child protection)

**WC2-A. Offline-first voice-to-structured-case capture** ⭐
Field caseworker holds phone, speaks 30–60s in their working language about a child encounter ("Layla, age 9, Akkar camp, mother killed Friday, hasn't spoken since, sleeping on floor in mother's clothes"). Whisper transcribes on-device; Claude extracts a CPIMS+/Primero-compatible case schema (child ID, demographic, observed indicators, protection concerns, recommended next step). Stored encrypted in local SQLite; queues sync when connectivity returns. Caseworker reviews and edits before commit. Solves three real bottlenecks at once: case continuity across handovers, documentation skipped because typing on phones in field is hostile, and the field-HQ data lag.

**WC2-B. Multilingual safeguarding-disclosure triage**
Caseworker writes / records a paragraph describing a concerning disclosure or incident. Tool classifies against the Warchild safeguarding taxonomy (PSEA / CP severity 1–4 / GBV / MH emergency), proposes the next-action workflow per Warchild policy, and pre-fills the formal incident report. Hard guardrail: refuses to handle anything above its calibrated scope and routes to a named human supervisor with a structured handoff.

**WC2-C. Paper-form-to-structured-record digitiser**
Camera scan of paper case files (still standard in many acute humanitarian settings) becomes a structured digital record. Combines OCR with a Claude pass that reconciles hand-written abbreviations against a controlled vocabulary. Photographs of forms are deleted on upload; only the structured record persists. Inherits NP-15-B's demo strength but pivots the customer to Warchild caseworkers.

### Ask 3 — Re-invent Digital Mailroom (Salesforce comms)

**WC3-A. Declarative comms graph**
A YAML / UI-defined comms layer: triggers, audiences, templates, schedules, locales — all data, not code. Claude renders the actual letter / email at send time; a content-QA pass checks tone, redaction, and policy compliance before dispatch. Decouples from Salesforce internals; Salesforce stays as the data source, not the comms author.

**WC3-B. Mailroom MCP server** ⭐
Expose the comms primitives — `build_letter`, `build_email`, `segment_audience`, `schedule`, `log_send`, `explain_send` — as an MCP server that an internal Warchild agent can compose. The hero demo: a non-technical Warchild ops person describes a comms intent in natural language ("send the recurring-donor lapse warning in EN/NL one week before lapse, exclude anyone who donated in the last 30 days") and Claude composes the actual flow via tool calls. This is the kickoff theme realised: a tight workflow tool, transparent by design.

**WC3-C. Comms explainer dashboard**
Every triggered comm gets a one-screen "why this fired, what data it pulled, what tone was chosen" panel. Supports rollback, A/B framing variants, and human override. The transparency story is strong but the demo is structurally a dashboard.

### Ask 4 — Enhancing Data Privacy (pseudonymous longitudinal tracking)

**WC4-A. Local-first pseudonym wallet**
A child gets a deterministic-but-irreversible identifier derived from a salted biometric or a paper-card seed. HQ databases store only opaque hashed tokens; longitudinal linkage works without any field able to re-identify the child. Even if the entire HQ database is exfiltrated, the data is unlinkable to any individual. Demo: simulate a breach live and show that the dump is unusable.

**WC4-B. K-anonymity / differential-privacy reporting pipeline**
Donor and internal reports get auto-aggregated with a privacy budget that mathematically bounds re-identification risk. Lower demo punch than WC4-A; higher operational fit.

**WC4-C. Threshold-cryptography access control**
Sensitive case decryption requires N-of-M staff keys (e.g., country lead + safeguarding officer + protection-cluster lead). A single compromised account yields nothing. Technically deep; demos as a key-ceremony walkthrough, which is hard to dramatise in 5 min.

---

## 4. Scoring (same 11-dim rubric as v2)

| Rank | ID | Idea | Aggregate |
|---|---|---|---|
| **1** | **WC2-A** | **Offline voice-to-structured-case capture** | **85.3** |
| 2 | WC1-A | Voice-first youth MH check-in & routing | 81.0 |
| 3 | WC2-B | Multilingual safeguarding-disclosure triage | 79.3 |
| 4 | WC2-C | Paper-form-to-structured-record digitiser | 79.2 |
| 5 | WC4-A | Local-first pseudonym wallet | 77.9 |
| 6 | WC1-B | Adaptive privacy-first self-screening | 76.4 |
| 7 | WC3-B | Mailroom MCP server | 75.9 |
| 8 | WC1-C | Peer-narrative library RAG companion | 75.5 |
| 9 | WC4-C | Threshold-cryptography access control | 73.6 |
| 10 | WC4-B | K-anonymity reporting pipeline | 72.5 |
| 11 | WC3-A | Declarative comms graph | 71.6 |
| 12 | WC3-C | Comms explainer dashboard | 71.4 |

Honourable mentions from v2 under the new lens:
- **NP-15-B Photograph-a-letter** (re-scored 72) — converges with WC2-C if pivoted to Warchild caseworker paper-form digitisation; otherwise off-customer.
- **NP-20-B DV chatbot** (re-scored 70) — converges with WC1-A if reframed for adolescent survivors served by Warchild's youth MH programmes.

---

## 5. Top 3 Shortlist — Detailed

### 5.1 ⭐ WC2-A — Offline voice-to-structured-case capture (85.3)

**Why it wins.** It is the single Warchild ask (#2) that is most cleanly hackathon-shaped: low-tech, offline-capable, context-resilient, narrow scope, deployable. It also implicitly addresses Ask #4 (privacy) because everything stays on-device until sync, and partially addresses Ask #1 (the structured fields can route to interventions). It is a tight workflow tool around a real Warchild communication bottleneck — exactly the kickoff brief.

**Demo arc (5 min).**
1. (15s) "This is what a child protection caseworker carries in Akkar refugee camp today: a phone with no reliable signal, ten cases per day, a paper notebook."
2. (60s) Pick up the phone. Hit airplane mode. Tap record. Speak in Arabic (or English) for 30 seconds about a fictional case. Watch the structured CPIMS+ record assemble live. Edit one field. Commit locally.
3. (45s) Show the encrypted local store. Show that nothing left the device.
4. (30s) Toggle airplane mode off. Watch the queued case sync to a boxd-hosted backend with end-to-end audit trail.
5. (60s) Show three handed-off cases threading into a continuous file across two caseworker phones — case continuity solved.
6. (30s) The pitch: "$50 of Claude credit handles 1,000 cases. One hackathon weekend; one INGO; one workflow; expandable across the 200+ INGOs using CPIMS+."

**24h build path.**
- Hour 0–4: schema (CPIMS+ subset) + extraction prompt + golden-set of 30 voice samples in 3 languages
- Hour 4–10: on-device voice capture, local SQLite, queue-and-sync server on boxd
- Hour 10–16: local encryption + audit log + caseworker review/edit UI
- Hour 16–22: reliability harness (offline replay, partial-record resume, edit conflict resolution); demo polish
- Hour 22–24: rehearsal, fallback paths

**Risks.**
- Whisper accuracy on Arabic/Pashto/Tigrinya in field-noisy audio. **Mitigation:** ship 3 pre-recorded golden samples; demo with those if live recording degrades.
- Schema mismatch with what Warchild actually uses. **Mitigation:** ask Warchild representatives at the kickoff for their actual schema; CPIMS+ is the safe default.
- Sync conflict UX. **Mitigation:** last-write-wins per field with a single-line "X overwrote Y at T" audit row is acceptable for v1.

---

### 5.2 WC1-A — Voice-first youth MH check-in (81.0)

**Why it ranks here.** Most directly addresses Ask #1, which is the most narratively powerful ask for the jury (mental health for youth in conflict). The demo, done well, is the most emotional moment available to any team this weekend.

**Risks that hold it below WC2-A.**
- High stakes for any classification or response error in the MH domain; a single off-key model output in the demo can sink the pitch.
- Long voice + multi-turn = burns Anthropic credits faster than WC2-A.
- Kickoff explicitly cautioned against frontier ambition; this is the most ambitious option in the set.

**Pick this if** the team has clinical-MH literacy on board and is confident in safeguarding rails.

---

### 5.3 WC2-B — Multilingual safeguarding triage (79.3)

**Why it ranks here.** A natural extension of WC2-A; can ship as the *severity-routing layer* on top of WC2-A in the same weekend. As a standalone, it is operationally critical but less cinematic.

**Strategic note.** The strongest single-team build is probably **WC2-A as the chassis with WC2-B's classifier wired in** — both Warchild asks #2 and (partial) #1 covered, one demo arc, one customer. That combination would aggregate higher than either alone (~83–86) and gives a richer pitch arc without doubling the build.

---

## 6. Cross-Cutting Patterns Under the New Lens

**What lifts an idea now:**
- **Direct map to one of the four Warchild asks.** Anything outside those four needs a strong story for why a kickoff-named customer would deploy it.
- **Offline-first or low-bandwidth-tolerant.** Mentioned twice in Warchild's asks (#2, #4); mentioned in organizer notes as a current-limits theme.
- **Short structured outputs, not long generations.** Cost-aware design under the $50 cap.
- **Tactile, reliable demo path** — kickoff explicitly preferred reliable workflows over ambitious frontier loops.

**What sinks an idea now:**
- **Wrong customer.** The kickoff is a Warchild-shaped weekend. Most of the v2 top 10 are wrong-customer.
- **Long agent loops, multi-turn frontier behaviour.** Penalised by both the $50 cap and the kickoff "build for current limits" guidance.
- **Internal-IT-flavoured workflow tools** (most of Ask #3) — important but pitch-quiet.
- **Cryptographic depth without a tactile demo** (WC4-B/C) — judges respect it, audience does not feel it.

---

## 7. Recommendation

**Build WC2-A as the chassis, fold in WC2-B's safeguarding classifier as the routing layer.** This delivers Warchild Ask #2 in full, partially addresses Ask #1, and inherits Ask #4's privacy posture by design (on-device until sync). It is the highest-aggregate option in the set, has the cleanest 5-minute demo arc, and offers a credible startup-style wedge: one INGO → one workflow → CPIMS+ ecosystem (200+ deployers).

**Fallback if the team has clinical-MH expertise:** WC1-A (Voice-first youth MH check-in). Highest emotional ceiling, highest demo risk.

**Avoid:** anything from the v2 top 10 unless explicitly pivoted to a kickoff-named customer; long-context multi-turn agent designs; internal-IT comms refactors (Ask #3) unless the team includes a Salesforce specialist with an unfair starting position.

---

## 8. Open Questions to Ask Warchild at the Kickoff

These determine whether WC2-A's defaults are correct and should be asked in the first 30 minutes:

1. Which case-management standard is in use today — CPIMS+, Primero, RapidPro, custom?
2. What is the field-staff working-language distribution (Arabic / Pashto / Dari / Tigrinya / Ukrainian / Spanish / English) and which two should the demo cover?
3. What is the existing safeguarding taxonomy (severity tiers, escalation paths, named role for handoff)?
4. What does "offline" mean operationally — hours, days, intermittent? Drives the sync-queue tolerances.
5. Which donor reporting standard requires the structured fields — UNICEF CPIMS+ Core Indicators, ECHO, BPRM?
6. What is the device baseline in the field — Android version range, RAM ceiling? Drives whether on-device Whisper is realistic vs. server-side.
