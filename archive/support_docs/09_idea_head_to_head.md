# Final pick & playbook — ideation head-to-head

Companion to `08_idea_ranking_v3_post_kickoff.md`. Decision frame for the three Warchild-aligned top ideas. Format mirrors `df/play.md`.

---

## Three-way head to head

| Axis | **WC2-A Offline Case Capture** | WC1-A Youth MH Companion | WC2-B Safeguarding Triage |
|---|---|---|---|
| Score | **85.3** | 81.0 | 79.3 |
| Theme: build local (Warchild fit) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Theme: communication systems (kickoff core) | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Warchild ask served | **#2 in full + partial #1 + #4 by design** | #1 in full | #2 partial |
| Innovation hook | Offline-first voice-to-CPIMS+ for unreachable field contexts | First INGO-grade youth MH companion in L1 | Warchild-policy-aligned classifier + workflow router |
| Demo arc | Airplane mode → speak 30s → structured case → sync | Youth voice in Arabic → empathetic L1 reply → intervention routing | Caseworker pastes disclosure → severity 1–4 + next-action steps |
| Visible mechanics in 60s | **4** (voice + structured extract + offline encrypt + sync) | 3 (voice + MH rubric + routing) | 3 (classify + workflow + handoff) |
| Claude strength used | Structured extraction + multilingual + schema discipline | Long-context multilingual + clinical-rubric application + safeguarding rails | Classification + policy reasoning + structured handoff |
| Partner tooling fit | Reson8 (Dutch HQ) + boxd (sync server) + Anthropic | Reson8 (counsellor side) + Anthropic | Anthropic + boxd |
| Pixel Perfect prize reach | Medium — caseworker UX in field conditions | **High** — youth-friendly L1 voice UI | Low — internal tool |
| Reachable Sat morning | **Warchild reps physically at venue + CPIMS+ schema public** | Warchild reps; needs youth-MHPSS programme lead | Warchild reps; safeguarding officer ideal |
| Ethical / liability risk | Medium — case data sensitive but on-device until review | **HIGH** — clinical-MH liability; single off-key output sinks demo | Medium — high-stakes class but human-in-loop |
| Privacy demo | **Strong** — encrypted local store + redaction shown live | Strong if on-device-first holds | Decent — short input + redaction |
| Hallucination cost if shipped | Low — caseworker reviews before commit | **High** — wrong response to youth in distress | Medium — wrong tier delays escalation |
| Business model story | **Clean** — per-seat to INGOs via CPIMS+ ecosystem (200+ deployers) | Clean — Warchild + UNICEF MHPSS + ECHO funding | Clean — bolts onto WC2-A or standalone |
| Scope confidence at 24h | **High** — narrow vertical, well-trodden patterns | Medium — multilingual + clinical rails is a lot | High — single-page tool |
| Team size sweet spot | **3** | **4** (one with clinical-MH literacy) | 2–3 |
| Total addressable demo wow | Tactile — airplane-mode toggle is theatre | Highest emotional ceiling, highest demo risk | Quiet — classifier UI not theatrical alone |
| $50 Anthropic credit fit | Excellent — short voice → short structured doc | Tight — multi-turn + long voice burns credit | Excellent — short paragraph in, short out |

## When to pick which

- **WC2-A** — your team is **3 people**, you want the **highest finishing confidence** on the menu, and you're comfortable with offline-first + a small client-side encryption story. **Best score-to-effort** in the set; the airplane-mode demo is unique among the kickoff teams; the CPIMS+ wedge gives a clean post-hackathon distribution path. **Default pick.**
- **WC1-A** — your team is **4 people including someone with clinical-MH literacy**, you have appetite for safeguarding-rail design work, and you want the highest emotional ceiling on stage. The kickoff explicitly cautioned against frontier ambition, so pick this only with clear conviction on clinical and safeguarding rigour.
- **WC2-B** — your team is **2–3 people**, or you want the simplest possible single-page tool, or you want to ship quickly and use the rest of the weekend for polish. **Best deployed as a layer inside WC2-A** rather than as a standalone — alone, the demo is dispatcher-internal-flavoured and pitches quiet.

**Default recommendation: WC2-A as the chassis with WC2-B's classifier folded in as the routing layer.** Covers Warchild Ask #2 in full, partially addresses Ask #1, and inherits Ask #4's privacy posture by design (on-device until sync). Aggregate of the combined build estimates ~83–86, beating any standalone option and delivering a richer pitch arc without doubling the work.

If the team profile fits **WC1-A** instead (4 people, clinical literacy, appetite for risk), pick that — its emotional ceiling is the highest available this weekend. The two share enough architecture (voice-in, multilingual, structured-out, safeguarding rails, Reson8 + Anthropic) that a Saturday-morning pivot from one to the other is feasible if scope blows up.

---

## Honourable mentions outside the three-way

| Idea | Aggregate | Why not in head-to-head | Where it fits |
|---|---|---|---|
| WC2-C Paper-form digitiser | 79.2 | Single-mechanic demo; weaker than WC2-A on offline + sync narrative | Strong fallback if voice on-device fails on field-noisy audio |
| WC4-A Pseudonym wallet | 77.9 | High technical depth, hardest demo to dramatise in 5 min | Best as a privacy module bolted into WC2-A's sync layer |
| NP-15-B Photograph-a-letter | 72 (re-scored) | Wrong customer for kickoff; survives only if pivoted to refugees served by Warchild NL | Fallback theme if Warchild path collapses |
| NP-20-B DV chatbot | 70 (re-scored) | Adjacent to WC1-A; converges if pivoted to Warchild adolescent MH catalogue | Folded into WC1-A's intervention library |

---

## What success looks like Sunday 15:30

Inheriting the play.md success criteria, adapted:

- 1-min video uploaded by 11:55, shot with a Warchild-shaped scenario (caseworker phone in airplane mode, real or simulated field setting)
- Live demo runs end-to-end without fallback — including the offline-to-online sync moment
- One named partner on the closing slide (Warchild themselves, ideally — they're at the kickoff)
- One specific number repeated three times. Suggested: **CPIMS+ is deployed across 200+ INGOs** or **acute humanitarian crises = ~150M children at risk** or **case-continuity gap = ~40% of handovers** (verify the last with Warchild Saturday morning)
- Q&A handled in operator language: customer (INGOs via CPIMS+ ecosystem), unit econ (per-seat or per-case), distribution (Warchild → 4 peer INGOs in year 1), risk (privacy + hallucination, both addressed by review-before-commit)

That's a top-3 finish.
