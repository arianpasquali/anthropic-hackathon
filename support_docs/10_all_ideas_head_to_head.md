# All ideas — head-to-head atlas

Companion to `06_idea_ranking_v2.csv`, `08_idea_ranking_v3_post_kickoff.md`, `09_idea_head_to_head.md`, and `df/play.md`.

Every idea in the repo, organised into 14 clusters of three (matching the `df/play.md` format), plus a final cross-cluster tournament. Each cluster table compares the three angles within that problem; the tournament compares cluster winners.

**Scoring notes.**
- *v2 score* = aggregate from `06_idea_ranking_v2.csv` (11-dim equal-weight, 0–100).
- *v3 re-score* = same rubric under the post-kickoff Warchild lens (Build Local re-read as "Warchild / kickoff customer fit"; Impact & Viability re-read as "deployable to a kickoff-named customer"). Applies to v2 ideas only.
- *Warchild scores* (WC*) come from `08_idea_ranking_v3_post_kickoff.md`.
- *play.md scores* come from `df/play.md` (separate /30 rubric — not directly comparable to /100; flagged inline).

---

## Group 1 — NL Non-Profit clusters (v2)

### Cluster NP-15 — Refugees navigating digitalised Dutch bureaucracy

| Axis | NP-15-A DigiD assistant | **NP-15-B Photograph-a-letter** | NP-15-C AI + peer-navigator |
|---|---|---|---|
| v2 score | 76.4 | **87.5** | 68.7 |
| v3 re-score (Warchild lens) | ~58 | **~72** | ~50 |
| Build local | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Innovation hook | Skendy / RefuGPT-class chatbot | Camera → action card from a photographed letter | Hybrid AI + human navigator |
| Demo arc | Conversation simulating DigiD reset | Snap real Belastingdienst letter on stage → Arabic explanation + deadline | Multi-party persona walkthrough |
| Mechanics | 2 (chat + KB) | 3 (OCR + LLM + translate) | 2 (chat + handoff) |
| Claude strength | Conversational + retrieval | Vision + multilingual + structured-out | Curation + conversation |
| Partner fit | Reson8 + Solvimon | Reson8 (audio fallback) | Framer + KB |
| Ethical risk | Low | Low | Medium |
| Hallucination cost | Medium | Low (grounded in letter) | Low (human in loop) |
| Business model | Municipalities (Skendy-shaped) | Municipalities + NGOs + consumer | KB / OpenEmbassy |
| Scope at 24h | Medium | **High** | Low |
| Demo wow | Quiet | **Cinematic** | Cluttered |
| Pick when | Strong NLP team, no camera fallback | **Default for this cluster** | Strong UX + volunteer network |

### Cluster NP-20 — Domestic violence victims not reaching support

| Axis | NP-20-A Decoy safety app | **NP-20-B AI safety chatbot** | NP-20-C Frontline silent-referral |
|---|---|---|---|
| v2 score | 79.6 | **80.6** | 68.2 |
| v3 re-score (Warchild lens) | ~62 | **~70** | ~50 |
| Build local | ⭐⭐⭐⭐⭐ Veilig Thuis + LINK | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ Meldcode |
| Innovation hook | Reveal-moment decoy UX | Multilingual safety planning + risk triage | Consent-driven victim-controlled handoff |
| Demo arc | Recipe app → tap-tap-tap → safety panel | Survivor vignette → bilingual planning chat | Two-persona screens, mostly slides |
| Mechanics | 3 (UI cloak + auth + comms) | 2 (chat + KB) | 3 (intake + consent + handoff) |
| Claude strength | Long-context safety planning | Multilingual + safeguarding rubric | Classification + workflow |
| Partner fit | Framer (UX-heavy) | Reson8 + Solvimon (donations) | KB / municipality CRM |
| Ethical risk | **High** — wrong reveal hurts a victim | Medium — wrong advice harms | Medium — consent UX must be airtight |
| Hallucination cost | Medium (panic actions) | Medium | Low (human in loop) |
| Business model | Hard — who pays? Shelter funders | Clean — Veilig Thuis + GGD + insurer | Slow — institutional buyers |
| Scope at 24h | Medium-low | **High** | Low |
| Demo wow | **Cinematic reveal** | Mission narrative carries it | Slide-heavy |
| Pick when | Designer-led team, ethics confidence | **Default for this cluster** | Workflow-heavy team only |

### Cluster NP-13 — Food banks reach only 15–17% of eligible

| Axis | **NP-13-A Eligibility estimator** | NP-13-B Proactive partner referral | NP-13-C Stigma-free voucher |
|---|---|---|---|
| v2 score | **80.6** | 64.5 | 64.3 |
| v3 re-score (Warchild lens) | ~52 | ~38 | ~40 |
| Build local | ⭐⭐⭐⭐⭐ Voedselbanken | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Innovation hook | Self-service eligibility + warm handoff | Wgs-style screening for food aid | UK Healthy Start NL analogue |
| Demo arc | "Am I eligible? Yes — book at nearest bank" | Multi-party institutional plumbing | Voucher app screen — looks like any payment app |
| Mechanics | 3 (estimator + booking + handoff) | 2 (screen + refer) | 2 (voucher + clearing) |
| Claude strength | Eligibility logic + multilingual | Classification | None deep |
| Partner fit | Solvimon (donations) + Reson8 | KB / GGD | Solvimon (clearing) |
| Ethical risk | Low | Medium (consent) | Low |
| Hallucination cost | Medium (wrong eligibility = denied food) | Low | Low |
| Business model | Clean — Voedselbanken + Armoedefonds | Slow — institutional | Hard — supermarket partnerships |
| Scope at 24h | **High** | Low | Low (backend-heavy) |
| Demo wow | Mission-led | Slide-heavy | Quiet |
| Pick when | **Default for this cluster** | Skip | Skip |

---

## Group 2 — NL Emergency Services clusters (v2)

### Cluster ES-03 — Language barriers in 112 calls

| Axis | **ES-03-A Translation overlay** | ES-03-B Voice-first pre-call app | ES-03-C Speech reconstruction |
|---|---|---|---|
| v2 score | **76.5** | 72.7 | 67.3 |
| v3 re-score | ~48 | ~50 | ~42 |
| Build local | ⭐⭐⭐⭐ 112 NL | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Innovation hook | Real-time dispatcher overlay | Caller-side voice-first (vs. server-side patent US11589205) | Frontier research (Venkateshperumal 2024) |
| Demo arc | Two-way live translation in dispatcher screen | Mock pre-emergency adoption | Reconstructed text — invisible to audience |
| Mechanics | 2 (STT + translate) | 3 (record + extract + transmit) | 2 (transcribe + reconstruct) |
| Claude strength | Multilingual + low-latency | Structured extraction + multilingual | Audio-context reasoning |
| Partner fit | Reson8 (NL side) | Reson8 + boxd | Anthropic only |
| Ethical risk | Medium | Medium | High (life-stakes mistranslation) |
| Hallucination cost | High (misroute) | Medium | High |
| Business model | Clean — Carbyne/Prepared have proven this | Slow — adoption pre-emergency | Research-grade |
| Scope at 24h | High | Medium | Low |
| Demo wow | Familiar genre — Carbyne/Prepared deployed | Pre-emergency demo lacks punch | Invisible payoff |
| Pick when | **Default for this cluster** if 112 cooperates | Caller-side conviction team | Skip |

### Cluster ES-04 — Dispatcher recognition of OHCA

| Axis | **ES-04-A Explainable classifier** | ES-04-B Smartphone visual confirm | ES-04-C Post-call QI reviewer |
|---|---|---|---|
| v2 score | **78.4** | 72.3 | 71.7 |
| v3 re-score | ~42 | ~38 | ~36 |
| Build local | ⭐⭐⭐⭐ NL dispatch | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Innovation hook | Explainable layer over Corti baseline | Visual OHCA classification | Automated quality improvement |
| Demo arc | Audio playback + reasoning trace overlay | Consent-then-camera flow | Dashboard of flagged calls |
| Mechanics | 3 (classify + explain + suggest) | 3 (consent + capture + classify) | 2 (transcribe + flag) |
| Claude strength | Explainability + tool use | Vision | Long-context QI |
| Partner fit | Anthropic only | Reson8 | Anthropic only |
| Ethical risk | Medium | Medium (consent) | Low |
| Hallucination cost | High (life stakes) | High | Low |
| Business model | Clean — Corti is €60M+ exit | Uncertain caller adoption | Modest — QI budgets exist |
| Scope at 24h | Medium | Low | Medium |
| Demo wow | Lands with founder-judges (van Lanschot, Mol) | Clunky | **Dead on stage** |
| Pick when | **Default for this cluster** | Skip — idea > demo | Skip |

### Cluster ES-05 — Dispatcher-assisted CPR refusal/delay

| Axis | **ES-05-A AR-guided CPR** | ES-05-B Adaptive DA-CPR script | ES-05-C Audio metronome |
|---|---|---|---|
| v2 score | 78.2 | 75.6 | 70.3 |
| v3 re-score | ~45 | ~42 | ~40 |
| Build local | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| Innovation hook | Phone over mannequin → AR overlay guides compressions | Branching MPDS adapted to constraints | Stayin'-Alive bpm at 112 trigger |
| Demo arc | **Most cinematic possible** — phone on chest, real-time AR | Dispatcher screen with branching text | Audio plays |
| Mechanics | 4 (vision + depth + voice + overlay) | 2 (script + branch) | 1 (audio) |
| Claude strength | Vision + real-time guidance | Conversational branching | None |
| Partner fit | Anthropic + boxd | Anthropic only | None |
| Ethical risk | Medium | Low | Low |
| Hallucination cost | High (wrong depth call) | Low | None |
| Business model | Heart foundations + 112 + consumer | 112 only | Feature, not product |
| Scope at 24h | **Low** — AR + consent UX in 24h is the risk | High | Trivial |
| Demo wow | **Highest in repo** if it works | Quiet | "We built a metronome" sinks ambition |
| Pick when | Team has CV/AR muscle | **Default if AR not viable** | Never standalone |

### Cluster ES-09 — Dispatch overtriage

| Axis | ES-09-A Overtriage flag | ES-09-B Self-service chatbot in-call | **ES-09-C Explainable shadow-reasoning** |
|---|---|---|---|
| v2 score | 71.9 | 68.2 | **74.4** |
| v3 re-score | ~40 | ~36 | ~44 |
| Build local | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Innovation hook | Quebec 74.5% overtriage measured value | Portugal INEM pilot precedent | Reasoning trace addresses Blomberg JAMA RCT |
| Demo arc | Quiet flag on dispatcher screen | "Redirected from 112 to chatbot" — socially delicate | Reasoning side panel during high-stakes decision |
| Mechanics | 2 (classify + flag) | 3 (handoff + chat + escalate) | 3 (classify + reason + display) |
| Claude strength | Classification + advisory | Conversational + handoff | Reasoning + explainability |
| Partner fit | Anthropic only | Anthropic + Reson8 | Anthropic only |
| Ethical risk | Low | Medium (tone) | Medium |
| Hallucination cost | Medium | High | High |
| Business model | Dispatch centres | huisartsenpost + 112 | Dispatch centres + EENA |
| Scope at 24h | High | Medium | Medium |
| Demo wow | Quiet | Off-tone | Lands with explainability-curious judges |
| Pick when | Operational pitch team | Skip | **Default for this cluster** |

### Cluster ES-10 — Dispatch undertriage

| Axis | ES-10-A ML secondary review | **ES-10-B Adaptive questioning** | ES-10-C Callback prioritisation |
|---|---|---|---|
| v2 score | 70.6 | **73.8** | 68.4 |
| v3 re-score | ~38 | ~42 | ~36 |
| Build local | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Innovation hook | Uppsala RCT scaffolding | Adaptive MPDS — never deployed | ML-prioritised callback queue |
| Demo arc | Synthetic call data + flag overlay | Dispatcher receives suggested next question | Priority queue dashboard |
| Mechanics | 2 (classify + flag) | 2 (rubric + suggest) | 2 (predict + queue) |
| Claude strength | Classification | Conversational reasoning | Risk prediction |
| Partner fit | Anthropic only | Anthropic only | Anthropic only |
| Ethical risk | Medium | Low | Medium |
| Hallucination cost | High | Medium | Medium |
| Business model | Dispatch centres | Dispatch centres + MPDS partner | Dispatch centres |
| Scope at 24h | Medium | Medium | Medium |
| Demo wow | Needs heavy explanation | Quiet but clean | Dashboard — dead on stage |
| Pick when | Skip | **Default for this cluster** | Skip |

### Cluster ES-12 — AED temporal-access gap

| Axis | **ES-12-A Hours overlay HartslagNu** | ES-12-B Residential AED neighbour | ES-12-C IoT cabinet unlock |
|---|---|---|---|
| v2 score | **80.5** | 67.3 | 65.5 |
| v3 re-score | ~45 | ~38 | ~32 |
| Build local | ⭐⭐⭐⭐⭐ HartslagNu | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Innovation hook | Sun 2016 gap formalised, never deployed | Globally novel programme | IoT retrofit |
| Demo arc | Map overlay with open/closed status | Programme-level slides | Live cabinet unlock — if it works |
| Mechanics | 2 (data + routing) | 1 (programme) | 3 (sensor + unlock + dispatch) |
| Claude strength | None deep | Coordination | None |
| Partner fit | HartslagNu + Hartstichting | Hart foundations + insurers | Municipalities + hardware vendor |
| Ethical risk | Low | Medium (liability) | High (failed unlock during emergency) |
| Hallucination cost | Low | Low | High |
| Business model | Hartstichting + insurers | Multi-quarter operational | Per-unit municipality |
| Scope at 24h | **High** | **Prohibitive** | **Prohibitive** |
| Demo wow | Familiar map genre, lands clean | No on-stage moment | Dramatic IF prototype works |
| Pick when | **Default for this cluster** | Skip | Skip — props logistics |

### Cluster ES-18 — Bystander AED use ~4%

| Axis | **ES-18-A AR AED walkthrough** | ES-18-B Volunteer role assignment | ES-18-C Residential AED nudge |
|---|---|---|---|
| v2 score | **80.8** | 78.4 | 73.2 |
| v3 re-score | ~48 | ~42 | ~38 |
| Build local | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ HartslagNu | ⭐⭐⭐⭐ |
| Innovation hook | Cross-manufacturer AR overlay | PulsePoint 23% problem solved by role optimisation | Residential-zone training decay addressed |
| Demo arc | Real Philips HeartStart on stage + phone overlay | Live map with named volunteers + roles | Push notification + 60s quiz |
| Mechanics | 3 (vision + AR + voice) | 3 (notify + assign + map) | 2 (push + quiz) |
| Claude strength | Vision + multimodal | Coordination + dispatch logic | Personalised micro-content |
| Partner fit | Philips/Zoll co-sponsor + Reson8 | HartslagNu + GoodSAM | Hart foundations |
| Ethical risk | Low | Low | Low |
| Hallucination cost | Medium (wrong instruction) | Low | Low |
| Business model | Heart foundations + AED manufacturers | Clean — HartslagNu + EU peers | Municipalities |
| Scope at 24h | Medium | Medium | High |
| Demo wow | **Tactile + cinematic** | Live coordination story | Quiet |
| Pick when | **Default for this cluster** | Strong coordination/UX team | Skip |

---

## Group 3 — Warchild clusters (v3)

### Warchild Ask #1 — Personalised Support (youth MH)

| Axis | **WC1-A Voice-first MH check-in** | WC1-B Adaptive self-screening | WC1-C Peer-narrative RAG |
|---|---|---|---|
| v3 score | **81.0** | 76.4 | 75.5 |
| Build local (Warchild) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Innovation hook | First INGO youth MH companion in L1 | On-device privacy-first screening | RAG on consented peer narratives |
| Demo arc | Youth speaks Arabic → empathetic Arabic reply → routing | Branching screening flow | "Young people who felt like this said it helped to…" |
| Mechanics | 3 (voice + classify + route) | 2 (branch + score) | 2 (retrieve + interpret) |
| Claude strength | Long-context multilingual + clinical rubric + safeguarding rails | Classification + branching | Retrieval + empathetic interpretation |
| Partner fit | Reson8 + Anthropic | Anthropic only | Anthropic + boxd |
| Ethical risk | **HIGH** — clinical-MH liability | Medium | Medium (curation quality) |
| Hallucination cost | **High** — wrong response to youth in distress | Medium | Medium |
| Business model | Warchild + UNICEF MHPSS + ECHO | Warchild only | Warchild + content licensing |
| Scope at 24h | Medium | High | Medium |
| Demo wow | **Highest emotional ceiling** | Quiet | Touching but quiet |
| Pick when | **4 people + clinical literacy** | Risk-averse standalone | Strong content team |

### Warchild Ask #2 — Reimagining Case Management

| Axis | **WC2-A Offline voice-to-case** | WC2-B Safeguarding triage | WC2-C Paper-form digitiser |
|---|---|---|---|
| v3 score | **85.3** | 79.3 | 79.2 |
| Build local (Warchild) | ⭐⭐⭐⭐⭐ verbatim Ask #2 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Innovation hook | Offline-first voice-to-CPIMS+ | Policy-aligned classifier + workflow router | Camera scan → structured case |
| Demo arc | Airplane-mode → speak → record → sync | Paragraph in → severity + next-action | Paper form under camera → record |
| Mechanics | **4** (voice + extract + encrypt + sync) | 3 (classify + workflow + handoff) | 3 (OCR + reconcile + commit) |
| Claude strength | Structured extraction + multilingual + schema discipline | Classification + policy reasoning | Vision + reconciliation |
| Partner fit | Reson8 + boxd + Anthropic | Anthropic + boxd | Anthropic |
| Ethical risk | Medium (sensitive cases on-device) | Medium (high-stakes class) | Low |
| Hallucination cost | Low (review-before-commit) | Medium | Low |
| Business model | **Clean** — per-seat to 200+ INGOs via CPIMS+ | Bolts onto WC2-A | Same as WC2-A |
| Scope at 24h | **High** | High | High |
| Demo wow | Tactile — airplane-mode toggle is theatre | Quiet | Hero-shot if printer available |
| Pick when | **Default for this cluster + repo overall** | Layer inside WC2-A | Fallback if voice fails on field audio |

### Warchild Ask #3 — Re-invent Digital Mailroom

| Axis | WC3-A Declarative comms graph | **WC3-B Mailroom MCP server** | WC3-C Comms explainer |
|---|---|---|---|
| v3 score | 71.6 | **75.9** | 71.4 |
| Build local (Warchild) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Innovation hook | Config-as-data comms layer | Comms primitives as MCP tools | Transparent why-fired panel |
| Demo arc | Config UI walkthrough | Non-technical ops person describes intent → Claude composes flow via tool calls | Per-comm explanation panel |
| Mechanics | 2 (DSL + render) | 3 (tools + agent + render) | 2 (trace + UI) |
| Claude strength | Rendering + content QA | **Tool use + agentic composition** | Reasoning + transparency |
| Partner fit | Anthropic only | Anthropic + boxd (MCP server hosting) | Anthropic only |
| Ethical risk | Low | Medium (agent miscomposes flow) | Low |
| Hallucination cost | Low (config) | Medium | Low |
| Business model | Warchild + every Salesforce-burdened NGO | Same — broader appeal via MCP | Warchild only |
| Scope at 24h | Medium (Salesforce hostile) | High (MCP server is well-trodden) | Medium |
| Demo wow | Config UI = dead on stage | **MCP live demo lands with technical judges** | Dashboard — quiet |
| Pick when | Skip — internal IT flavour | **Default for this cluster** | Skip |

### Warchild Ask #4 — Enhancing Data Privacy

| Axis | **WC4-A Pseudonym wallet** | WC4-B K-anonymity reporting | WC4-C Threshold cryptography |
|---|---|---|---|
| v3 score | **77.9** | 72.5 | 73.6 |
| Build local (Warchild) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Innovation hook | Local-first irreversible IDs from biometric/paper-card seed | Differential-privacy reporting pipeline | N-of-M staff keys decrypt sensitive cases |
| Demo arc | Simulate breach live → dump unusable | Donor report with privacy budget shown | Key-ceremony walkthrough |
| Mechanics | 3 (seed + hash + linkage) | 2 (aggregate + budget) | 3 (key gen + share + threshold) |
| Claude strength | None deep — cryptographic | None deep | None deep |
| Partner fit | boxd (mock breach env) | Anthropic only | Anthropic only |
| Ethical risk | Medium (consent on biometric seed) | Low | Medium (key-loss recovery) |
| Hallucination cost | None — deterministic | None | None |
| Business model | All sensitive-data INGOs | Donor-report add-on | All INGOs (high-sensitivity) |
| Scope at 24h | Medium | Medium | Low (crypto in 24h hard) |
| Demo wow | "Even if hacked, identities safe" lands | Quiet | Key ceremony hard to dramatise |
| Pick when | **Default for this cluster** + privacy module for WC2-A | Reporting-team play | Crypto-savvy team only |

---

## Group 4 — Reference: `df/play.md` trio

Already documented head-to-head in `df/play.md`. Score scale is /30, not /100. Re-stated here for cross-comparison.

| Axis | Toeslagen Reconstructor | **InrichtingsBuddy** | OBA Co-pilot |
|---|---|---|---|
| play.md score | **25** | 24 | 22 |
| Build local | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ + circular bonus | ⭐⭐⭐⭐⭐ |
| Innovation hook | Mar 2025 dossier-policy change | Multi-modal aggregator across 4+ silos | "24% of IDO questions are DigiD" |
| Demo arc | Trauma paperwork → coherent dossier | Refugee family arrives → furnished home | Volunteer + visitor at IDO → printed card |
| Mechanics | 1 (deep) | **4** (vision + voice + multilingual + checkout) | 3 (vision + multilingual + voice) |
| Claude strength | 1M long context | Vision + multilingual + doc parse + tool use | Vision + B1 rewriting + multilingual |
| Partner fit | Light | Reson8 + Solvimon + Framer | Reson8 + Framer |
| Ethical risk | **High** — wrong route hurts a victim | Low | Low |
| Hallucination cost | High (legal claim) | Low (item not in stock) | Low (volunteer reviews) |
| Business model | Hard — who pays? | **Clean** — gemeente inrichtingskrediet | Clean — KB / VWS laaggeletterdheidsbudget |
| Scope at 24h | Medium | Medium-low (4 vendors, i18n, checkout) | **High** |
| Demo wow | Emotional 1-shot | 4-mechanic montage | 1 dramatic before/after |
| Pick when | Strong narrative writer + lawyer-adjacent | **4 people, designer included** | **2–3 people, risk-averse, walk into OBA Sat morning** |

---

## Group 5 — Tournament of cluster winners (cross-cluster final)

Top idea per cluster, scored under the **post-kickoff Warchild lens**. NL-only ideas penalised heavily on Build Local + Impact & Viability because the kickoff narrowed the customer to Warchild.

| Rank | Idea | Cluster | Score (post-kickoff) | One-liner | Verdict |
|---|---|---|---|---|---|
| 1 | **WC2-A Offline voice-to-case** | WC Ask #2 | **85.3** | Airplane-mode → 30s voice → CPIMS+-shaped case → sync | **Build this** |
| 2 | WC1-A Youth MH check-in | WC Ask #1 | 81.0 | Youth speaks L1 → empathetic reply + routing | Pick if 4 people + clinical literacy |
| 3 | WC2-B Safeguarding triage | WC Ask #2 | 79.3 | Disclosure → severity + workflow + handoff | **Fold into WC2-A as routing layer** |
| 4 | WC2-C Paper-form digitiser | WC Ask #2 | 79.2 | Paper case under camera → structured record | Fallback for WC2-A if voice on-device fails |
| 5 | WC4-A Pseudonym wallet | WC Ask #4 | 77.9 | Local-first irreversible IDs; demo a live breach | **Best as privacy module bolted into WC2-A** |
| 6 | WC3-B Mailroom MCP server | WC Ask #3 | 75.9 | Comms primitives as MCP tools; ops describes intent | Pick if technical-judge-leaning, Salesforce-savvy |
| 7 | NP-15-B Photograph-a-letter | NP-15 | 72 (re-scored) | Snap Belastingdienst letter → Arabic action card | **Strong fallback if Warchild path collapses** |
| 8 | NP-20-B DV chatbot | NP-20 | 70 (re-scored) | Multilingual safety planning chatbot | Pivot to Warchild adolescent MH = WC1-A |
| 9 | InrichtingsBuddy (`play.md`) | play.md | 24/30 | Refugee arrival → furnished home, multi-vendor | Cross-rubric — see `df/play.md` |
| 10 | OBA Co-pilot (`play.md`) | play.md | 22/30 | Volunteer + visitor at IDO → printed card | Cross-rubric — see `df/play.md` |
| 11 | Toeslagen Reconstructor (`play.md`) | play.md | 25/30 | Trauma paperwork → coherent dossier | Cross-rubric — see `df/play.md` |
| 12 | NP-13-A Foodbank eligibility | NP-13 | 52 (re-scored) | Self-service eligibility + warm handoff | Off-customer for kickoff |
| 13 | ES-18-A AR AED walkthrough | ES-18 | 48 (re-scored) | Real Philips HeartStart + AR overlay on stage | Off-customer for kickoff |
| 14 | ES-12-A AED hours overlay | ES-12 | 45 (re-scored) | Map overlay with open/closed AEDs | Off-customer |
| 15 | ES-04-A OHCA explainable classifier | ES-04 | 42 (re-scored) | Audio playback + reasoning trace | Off-customer |
| 16 | ES-05-A AR-guided CPR | ES-05 | 45 (re-scored) | Phone over mannequin + AR compression overlay | Off-customer |
| 17 | ES-03-A 112 translation overlay | ES-03 | 48 (re-scored) | Two-way live translation in dispatcher screen | Off-customer; Carbyne/Prepared deployed already |
| 18 | ES-09-C Explainable shadow-reasoning | ES-09 | 44 (re-scored) | Dispatcher reasoning side-panel | Off-customer |
| 19 | ES-10-B LLM adaptive questioning | ES-10 | 42 (re-scored) | Suggested next-question for ambiguous symptoms | Off-customer |

---

## Headline call

**Tier 1 (build):** WC2-A as chassis + WC2-B classifier folded in + WC4-A privacy module on the sync layer. Covers Warchild Asks #2 in full + partial #1 + #4 by design. Aggregate of the combined build estimates ~83–86, beating any standalone option.

**Tier 2 (alternative):** WC1-A if team profile fits (4 people, clinical-MH literacy, appetite for safeguarding rigour). Highest emotional ceiling on the menu; highest demo risk too.

**Tier 3 (fallback):** NP-15-B (Photograph-a-letter) if Warchild path collapses Saturday morning. Carries 87.5 on its own rubric, ~72 under post-kickoff lens; cinematic standalone demo even outside Warchild fit. Or `df/play.md`'s OBA Co-pilot for the safest finishing-confidence path.

**Avoid:** anything from the v2 NL-emergency-services clusters unless explicitly pivoted to a kickoff-named customer; long-context multi-turn agent designs (penalised by $50 cap and "build for current limits"); standalone privacy ideas without a tactile demo (WC4-B/C).
