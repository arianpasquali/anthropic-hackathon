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

**NP-15-A — Multilingual DigiD / Gemeente assistant**
*Short.* Conversational agent over DigiD + Gemeente flows in 8+ languages. Skendy / RefuGPT-class.
*Long.* Refugee opens chatbot in their L1, asks "how do I activate DigiD?"; agent walks them through with steps, screenshots, locale-aware translations of public docs. RAG over public Gemeente + Belastingdienst corpus. Skendy and RefuGPT already ship the genre; differentiation is execution quality and language coverage. Quiet demo, strong build-local fit, slow institutional sales.

**NP-15-B — Photograph-a-letter translator + action advisor**
*Short.* Camera → action card. Snap a Belastingdienst letter, get translated explanation + deadline + next 3 clicks.
*Long.* User photographs a paper or PDF letter from Belastingdienst, Gemeente, IND, UWV, or DUO. OCR + Claude vision parse out sender, type, deadline, reference, action required. Output is a one-screen card in the user's L1 with concrete steps and a deadline countdown. No tool produces this today — translation gives you text, not action. Single-screen tactile demo. Highest standalone score in v2 (87.5).

**NP-15-C — AI + peer-navigator hybrid**
*Short.* AI for routine queries; volunteer peer-navigator network (often refugees themselves) for ambiguous cases.
*Long.* AI handles common bureaucratic flows; warm handoff to a navigator on ambiguity. OpenEmbassy + Skendy partnerships natural. Two-sided workflow — onboarding navigators is the hard part. Demo is hard to compress into 5 minutes because the magic is the human pairing. Strong with UX + volunteer-network skills; weak as a standalone build.

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

**NP-20-A — Dual-purpose 'decoy' safety app with LINK integration**
*Short.* Recipe/weather utility on the surface; tap pattern reveals safety planning + LINK helpline + encrypted journal.
*Long.* Survivor under coercive control cannot install obvious safety apps without retaliation risk. NP-20-A ships a working cover app with an undiscoverable side door. Aspire 2013 and Bright Sky shipped variants; this is the NL-specific version with LINK + Veilig Thuis hooks and post-Aspire encryption. Cinematic reveal demo. Anti-discovery UX is the engineering cost; demo risk is that the "trick" is the product.

**NP-20-B — AI safety-planning chatbot in Dutch + migrant languages**
*Short.* 24/7 anonymous multilingual safety planning + risk triage, partnered with Veilig Thuis.
*Long.* Only ~3% of NL DV victims reach Veilig Thuis. Claude does in-language safety planning, risk assessment, escalation to a live counsellor. AinoAid (Finnish research) validates the concept; multilingual NL deployment is new. Single-conversation demo, scriptable survivor vignettes — but chatbot demos are commoditised. Execution quality (clinical literacy, redaction, handoff UX) is the only differentiator left.

**NP-20-C — Frontline-professional silent-referral tool**
*Short.* 60-second tool for GP/midwife/teacher + victim together: structured intake, consent screen, encrypted Veilig Thuis handoff.
*Long.* Meldcode requires NL professionals to flag suspected DV but friction is huge — paperwork, consent ambiguity, fear of breaking trust. NP-20-C compresses it: structured intake, consent screen, handoff, victim retains a copy. Real Meldcode infrastructure gap. Two personas + slides + a CRM — operationally credible, pitch-quiet.

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

**NP-13-A — Self-service eligibility estimator + warm handoff**
*Short.* Public chatbot in 8 languages: answer 6 questions, see if you qualify, click-to-book at nearest Voedselbank.
*Long.* 100k+ NL households are eligible for food aid but never reach a Voedselbank — language, dignity, paperwork. NP-13-A turns public eligibility rules into a single conversational flow with a structured booking handoff. Strong mission narrative, clean partner story (Voedselbanken NL + Armoedefonds + 150 regional banks). Risk: chatbot-to-result is a familiar genre; pitch rides on framing more than mechanics.

**NP-13-B — Proactive referral via partner-institution screening**
*Short.* GP/school/UWV signals food-insecurity risk; consent-driven referral routes to Voedselbank.
*Long.* Wgs 2021 already does this for debt (utility-default signals trigger municipal outreach). NP-13-B extends the pattern to food aid: signals (missed school meals, unpaid utility, disability application) trigger an opt-in referral. Multi-party plumbing; tractable but slow to validate; demo is mostly slides about institutional flow.

**NP-13-C — Stigma-free supermarket voucher model**
*Short.* Card looks like any payment card; backs onto NGO/municipality clearing layer at the supermarket POS.
*Long.* UK Healthy Start ships exactly this and works at scale. NP-13-C is the NL analogue: clearing layer between supermarket POS and Voedselbanken/municipality budget; eligible categories enforced at line level. Dignity-preserving (no one sees you're using food aid). Backend is the build (clearing infra, fraud control, store onboarding); demo looks like any payment app — insight is the model, not the screen.

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

**ES-03-A — Real-time two-way speech translation overlay for 112**
*Short.* Caller speaks Arabic; dispatcher hears Dutch + sees translation; types Dutch; caller hears Arabic.
*Long.* Mature APIs (Whisper + Azure + Google), tractable integration if 112 cooperates. Carbyne and Prepared have shipped this in US/DE; differentiation is dialect coverage, latency, and accuracy on emergency vocabulary. Strong build local; weak innovation. Demo will be recognised as a known genre. Operationally compelling; unlikely to wow a Dutch-startup-judge panel that knows Carbyne.

**ES-03-B — Voice-first multilingual pre-call app (112 companion)**
*Short.* App records 10s emergency statement in user's L1, structures fields, transmits to 112 with GPS before voice connects.
*Long.* Patent US11589205 (Motorola, 2023) covers the server-side equivalent; no caller-side voice-first app exists in the EU. User in distress speaks "fire, third floor, 2 children", app extracts fields, sends to 112 data channel, then connects voice. Reduces dispatcher cognitive load on non-Dutch calls. Adoption is the viability risk — pre-emergency install requires NL-wide push from a 112 partner.

**ES-03-C — LLM speech reconstruction for panicked callers**
*Short.* Model rebuilds intelligible speech from disfluent / panicked caller audio with confidence bands.
*Long.* Venkateshperumal et al. 2024 validated on synthetic data only — no deployment. Caller in panic produces fragments; model fills in plausible reconstruction; dispatcher sees both raw and reconstructed. Frontier research, no production proof. Reconstructed text looks like ordinary transcription on stage. High life-stakes risk if mistranslated; needs an honest uncertainty story.

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

**ES-04-A — Real-time OHCA call-audio classifier (explainable)**
*Short.* Classifier flags likely cardiac arrest in real time; dispatcher sees a reasoning trace explaining why.
*Long.* Corti is the €60M baseline; Blomberg 2021 JAMA RCT showed black-box dispatcher alerts don't change outcomes. ES-04-A's contribution is the explainability layer — when the model fires, the dispatcher sees key phrases, breathing pattern, witness language. Audio + Claude classifier + reasoning panel. Lands with founder-judges (van Lanschot, Mol). Demo is audio-with-overlay — useful but not stunning.

**ES-04-B — Caller-smartphone OHCA visual confirmation**
*Short.* Caller's phone camera classifies arrest scene; dispatcher sees a live confidence score.
*Long.* No purpose-built visual-OHCA classifier exists in literature or deployment. Caller is asked to point camera at the patient; CV scores chest movement, skin colour, posture. Genuinely novel; consent-then-camera UX is clunky on stage. High build cost (CV + workflow + caller-side consent). Idea > demo.

**ES-04-C — Post-call LLM QI reviewer**
*Short.* Batch tool reviews archived dispatch calls and flags likely missed OHCA recognitions for quality improvement.
*Long.* Quality-improvement budgets are modest but exist. Tool ingests archived audio under GDPR-compliant agreement, transcribes, applies a Corti-style classifier offline, surfaces calls where the on-shift dispatcher likely missed an OHCA. Useful, technically tractable. Demo is a dashboard — operationally credible but dead on stage.

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

**ES-05-A — AR-guided CPR via smartphone video**
*Short.* Phone camera + AR overlay guides bystander compressions in real time. Voice metronome paces.
*Long.* User holds phone over the chest of a person in arrest; AR overlay shows correct hand placement + visual depth-target via accelerometer or camera-based motion estimation. Linderoth 2015 validated the premise; no RCT of AR-CPR. Most cinematic possible demo (phone over a mannequin, arrows light up). 24h build risk: depth estimation, AR registration, consent flow. If AR not in scope, fall back to ES-05-B.

**ES-05-B — Adaptive DA-CPR script for physical-constraint scenarios**
*Short.* Branching CPR script that adapts to caller's described constraints (single rescuer, narrow space, elderly patient).
*Long.* Current MPDS scripts are one-size-fits-all. Caller says "I'm alone with my elderly father in a bathroom" and the script branches: simplified compression-only protocol, no rescue breaths, foot positioning advice. LLM + MPDS knowledge base; clean dispatcher-screen demo. Less cinematic than AR, higher 24h scope confidence.

**ES-05-C — Audio metronome + calming soundscape**
*Short.* Stayin'-Alive bpm audio plays automatically when 112 confirms CPR-in-progress.
*Long.* Trivial audio pipeline; mobile + dispatcher both easy. Stayin' Alive metronomes exist as standalone apps; the contribution is the auto-trigger via 112 integration. Honestly: this is a feature, not a hackathon-headliner. "We built a metronome" sinks ambition signal with founder-judges. Only viable as a sub-component of ES-05-A or ES-05-B.

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

**ES-09-A — LLM advisory flagging likely-overtriage cases**
*Short.* Dispatcher sees a non-blocking flag when MPDS coding looks like likely overtriage.
*Long.* Quebec studies measured 74.5% overtriage. ES-09-A is a non-blocking advisory: when the dispatcher selects a high-priority code and the call signals (audio + symptom pattern) suggest a lower urgency, a flag appears. Dispatcher-internal demo. Useful, commercially credible, visually quiet on stage.

**ES-09-B — In-call non-urgent self-service chatbot**
*Short.* Mid-call handoff from 112 to a triage chatbot for confirmed non-urgent calls.
*Long.* Portugal INEM piloted with ChatGPT. Call comes in, dispatcher confirms non-urgent, offers caller a chatbot handoff (huisartsenpost or similar); chatbot continues triage and returns to dispatcher only on escalation. Acting out "we're redirecting you from 112 to a chatbot" is socially delicate on stage. Tech demo fights the framing.

**ES-09-C — Explainable shadow-reasoning dispatch assistant**
*Short.* Side panel shows the model's reasoning trace alongside the dispatcher's coding choice.
*Long.* Direct response to Blomberg JAMA RCT's finding that opaque AI fails. Model shadows the dispatcher; when its inference diverges from the dispatcher's coding, a reasoning side-panel appears. Doesn't autonomously act; the dispatcher stays in control. Lands with explainability-curious judges; reasoning trace UX is subtle but tractable in 24h.

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

**ES-10-A — ML secondary-review overlay for low-priority dispatches**
*Short.* Classifier flags low-priority dispatches at risk of being undertriage; dispatcher sees a non-blocking review prompt.
*Long.* Uppsala RCT NCT04757194 scaffolds the approach. Synthetic call data + classifier + dispatcher-screen flag. The classifier is the easy part; selling the explanation to a dispatcher who already coded the call low is the hard part. Demo needs heavy explanation; impact is real but invisible.

**ES-10-B — LLM-driven adaptive questioning for ambiguous symptoms**
*Short.* Real-time suggestion of the next question to ask when symptom pattern is ambiguous.
*Long.* MPDS revisions take years; ES-10-B layers an adaptive question-suggestion engine on top of the existing dispatcher script. When ambiguity is high (chest pain + back pain + sweating + nausea), the model suggests "have you taken any medication today?" Dispatcher accepts or ignores. Novel framing, feasible in 24h, quiet on stage.

**ES-10-C — Post-dispatch callback prioritisation**
*Short.* ML-prioritised queue of post-dispatch callbacks based on deterioration risk.
*Long.* Discretionary callback is standard practice for borderline calls. ES-10-C predicts which callbacks have the highest deterioration risk and orders the queue. Useful but invisible — "we save lives by ordering a list" doesn't land in 5 minutes. Best as a feature inside a larger product.

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

**ES-12-A — Operational-hours overlay on HartslagNu**
*Short.* Per-AED open/closed schedules overlaid on the HartslagNu map and on dispatcher routing.
*Long.* Sun et al. 2016 formalised the temporal-access gap; no EU deployment encodes hours in routing. Crowdsourced verification + partnership integration with HartslagNu. Toronto study suggests 25% coverage uplift possible. Map-with-filter demo is canonical "I get it immediately." Familiar genre; lands clean.

**ES-12-B — 24/7 residential AED neighbour programme**
*Short.* Programme that opts private-AED owners into a community-share registry for off-hours dispatch.
*Long.* No global programme treats private AEDs as a public asset for off-hours use. ES-12-B is a registry + consent + verification + dispatch-integration scheme. Programme-level innovation. Multi-quarter operational build, not a 24h hackathon. No demo moment.

**ES-12-C — Remote-unlock outdoor AED cabinet (IoT retrofit)**
*Short.* Hardware retrofit lets dispatcher remotely unlock outdoor AED cabinets in real time.
*Long.* Industry whitepapers propose this; not deployed in NL or EU. Cabinet retrofit + IoT module + dispatch integration. Live unlock on stage would be dramatic but logistics + hardware in 24h is prohibitive. Pick only with hardware muscle and a borrowed cabinet.

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

**ES-18-A — AR AED opening walkthrough**
*Short.* Phone camera + AR overlay guides a bystander through opening + using any AED model on the spot.
*Long.* Most public OHCAs have an AED nearby that goes unused — bystander confidence collapses at the moment of need. Multi-manufacturer: point camera at a Philips HeartStart, Zoll, or Defibtech, model identifies it, AR overlay shows arrows on the device for "press button A, place pads here, follow voice." Tactile demo with a real device on stage. Strong "technology saves life" arc. CV + cross-manufacturer model library is the build cost.

**ES-18-B — Dispatch-optimised volunteer role assignment**
*Short.* HartslagNu volunteers each receive a specific role (AED, compressions, traffic) instead of "go help."
*Long.* PulsePoint internal data shows 23% volunteer response rate problem; no role-optimisation solution exists. ES-18-B optimises across the volunteer pool — closest gets AED-fetch, second-closest gets compressions, others routed to traffic/door. HartslagNu integration enables a high-fidelity demo. Coordination story tells crisply on stage.

**ES-18-C — Residential-zone AED confidence nudge**
*Short.* Push notifications + 60-second AED micro-quiz to residents of high-OHCA postcodes.
*Long.* Targets the residential-zone AED training-decay problem. Residents who opted in to HartslagNu in their area get periodic micro-training prompts. Build is a notification system + content engine. Push notifications are structurally low-drama on stage; insight is sophisticated, demo is quiet.

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

**WC1-A — Voice-first youth MH check-in & routing**
*Short.* Youth speaks 60–90s in L1; structured signal vector + routing to brief intervention; safeguarding rails.
*Long.* Targets Warchild Ask #1 in full. Whisper transcribes; Claude extracts a Warchild-aligned screening rubric (RHS-15 / K10-derived: sleep, mood, isolation, safety, somatic), routes to one of N brief interventions in Warchild's catalogue or escalates on red-flag indicators. Audio-only fallback for low-bandwidth. Lives inside Can't Wait to Learn / TeamUp delivery channels. Highest emotional ceiling in the repo; highest demo risk because off-key MH outputs sink the pitch.

**WC1-B — Adaptive privacy-first self-screening**
*Short.* Branching on-device screening over RHS-15 / PHQ-A / K10. Results stay local unless youth shares.
*Long.* Built for the trust-deficit context where typing answers into a server is itself a barrier. Youth-driven flow on the device; Claude only invoked for interpretation/escalation. Validated instruments mean screening logic is largely deterministic. Lower ceiling than WC1-A, lower risk. Useful as a fallback or as a prelude to WC1-A's voice surface.

**WC1-C — Peer-narrative library RAG companion**
*Short.* 200–500 anonymised consented youth narratives; retrieval returns "young people who felt like this said it helped to..."
*Long.* Peer-modelled coping recommendation rather than clinical instruction. Curation is the hard part; Claude is the retrieval interpreter. Touching demo if curation quality is high. Builds a content asset Warchild extends over time. Less mechanical than the other two; pitch leans on library quality, not algorithm.

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

**WC2-A — Offline-first voice-to-structured-case capture**
*Short.* Caseworker speaks 30–60s; phone produces a CPIMS+-shaped record offline; sync queue flushes to HQ when online.
*Long.* Direct hit on Warchild Ask #2. Whisper on-device transcribes; Claude extracts CPIMS+/Primero schema; encrypted SQLite stores locally; sync queue flushes on reconnect. Caseworker reviews and edits before commit (hallucination guard). Solves three real bottlenecks: case continuity across handovers, documentation skipped because typing is hostile, field-HQ data lag. Cleanest 5-min demo arc in the repo (airplane-mode toggle is theatre). Wedge: CPIMS+ ecosystem (200+ INGOs).

**WC2-B — Multilingual safeguarding-disclosure triage**
*Short.* Caseworker pastes/records a disclosure; tool classifies severity 1–4, suggests next-action workflow, hard-routes to a named human.
*Long.* Junior staff often miscalibrate severity; escalation delays harm children. Classification against Warchild safeguarding taxonomy (PSEA / CP / GBV / MH emergency) + workflow renderer + structured handoff. Hard guardrail: refuses anything above its calibrated scope. Best deployed as the routing layer inside WC2-A — alone, the demo is dispatcher-internal-flavoured.

**WC2-C — Paper-form-to-structured-record digitiser**
*Short.* Camera scan of paper case file → reconciled structured digital record. Photos deleted on upload.
*Long.* Paper case files are still standard in many acute humanitarian settings. OCR + Claude reconciliation against a controlled vocabulary handles hand-written abbreviations. Photos are deleted; only the structured record persists. Inherits NP-15-B's demo strength but pivots the customer to Warchild caseworkers. Best as a fallback if voice-on-device fails on field-noisy audio.

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

**WC3-A — Declarative comms graph**
*Short.* YAML/UI-defined comms layer (triggers, audiences, templates, locales) decoupled from Salesforce. Claude renders at send time.
*Long.* Replaces fragile Salesforce-embedded comms automation. Config-as-data. Claude is the runtime renderer + content-QA pass (tone, redaction, policy). Salesforce stays as data source, not comms author. Strong architecture story, weak pitch — config UI is dead on stage. Internal-IT flavour.

**WC3-B — Mailroom MCP server**
*Short.* Comms primitives (build_letter, segment_audience, schedule, log_send) exposed as MCP tools an internal agent composes.
*Long.* Non-technical Warchild ops describes intent in natural language ("send the recurring-donor lapse warning in EN/NL one week before lapse, exclude anyone who donated in the last 30 days") and Claude composes the actual flow via tool calls. Hero demo: live MCP composition. Lands with technical judges. Higher ceiling than WC3-A because the demo is interactive.

**WC3-C — Comms explainer dashboard**
*Short.* One-screen "why this fired, what data it pulled, what tone was chosen" panel for every triggered comm. Supports rollback + A/B.
*Long.* Transparency layer over the comms system. Useful operationally (audit trail, debugging mis-fires, rollback). Demo is structurally a dashboard. Best as a sub-feature of WC3-A or WC3-B.

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

**WC4-A — Local-first pseudonym wallet**
*Short.* Deterministic-but-irreversible identifier from biometric/paper-card seed. HQ stores only opaque hashes.
*Long.* Direct hit on Warchild Ask #4. Cohort linkage works (same child across visits = same hash) without HQ ever holding re-identification data. Demo: simulate a breach live, show the dump is unusable. Best deployed as a privacy module on top of WC2-A's sync layer.

**WC4-B — K-anonymity / differential-privacy reporting pipeline**
*Short.* Donor and internal reports auto-aggregated with a privacy budget that mathematically bounds re-identification risk.
*Long.* Differential-privacy-aware pipeline; mathematically guarantees no individual is re-identifiable from a published report. Lower demo punch than WC4-A; higher operational fit for funder-required transparency. Best paired with WC4-A.

**WC4-C — Threshold-cryptography access control**
*Short.* Sensitive case decryption requires N-of-M staff keys (e.g. country lead + safeguarding officer).
*Long.* Single compromised account yields nothing. Technically deep; demos as a key-ceremony walkthrough, hard to dramatise. Pick if the team has cryptographic specialists. Best as a security primitive under the rest of the WC4 stack.

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

**Toeslagen Reconstructor**
*Short.* Trauma victim hands their paperwork pile to the model; model assembles a coherent legal dossier with timeline + gaps.
*Long.* March 2025 dossier-policy change lets childcare-benefits scandal victims submit an unstructured paperwork pile for review. The 1M-context model ingests the pile, builds a timeline, flags missing documents, drafts the structured dossier. Emotional one-shot demo. High liability if a misroute hurts a victim — privacy story has to be airtight. Hard to identify the buyer (UHT? CWS? gemeente?).

**InrichtingsBuddy**
*Short.* Refugee arrives with a gemeente housing letter; app aggregates 4+ circular furniture vendors with multilingual UI + Solvimon checkout.
*Long.* 25k statushouders/year × €4k inrichtingskrediet = €100M/yr circular-furnishing flow. App parses the gemeente letter (Opus, with redaction), generates a household need list, matches across ReShare + De Lokatie + Buurman + Marktplaats, applies Stadspas, checks out via Solvimon. Multi-modal aggregator with 4 visible mechanics. Pixel Perfect prize reach is high (RTL, voice-first, low-literacy). Best score-to-effort in the play.md trio if team is 4 people including a designer.

**OBA Co-pilot**
*Short.* Tablet kiosk at every OBA library IDO desk. Volunteer scans citizen's letter; tablet prints take-home action card in citizen's L1 + B1 Dutch.
*Long.* Volunteers at the Informatiepunt Digitale Overheid (230 desks nationally; 24% of questions are DigiD) help citizens read state letters. OBA Co-pilot scans the letter under camera (Opus + redaction), translates + B1-rewrites, looks up next-step playbook, prints a thermal card with the 3 concrete clicks. Highest finishing-confidence path: walk into OBA Bijlmer Saturday morning, film a real volunteer, have a partner quote on stage. Card-out-of-printer is the moment.

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
