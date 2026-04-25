# Food bank measurement + funding — head-to-head

Companion to `bank_food_idea.md`, `10_all_ideas_head_to_head.md`. The idea in `bank_food_idea.md` is one specific angle on a broader cluster: turning rescued-food climate value into food-bank funding. Splitting into three angles A/B/C in the same format as the rest of the atlas.

**Cluster ID:** FB-01 — Food banks generate uncounted climate value; corporates have unspent CSR budget. Measurement is the missing wedge.

**Source problem.** Adjacent to NP-13 (reach gap) and NP-14 (supply decline). New cluster because the wedge is **funding**, not eligibility or supply.

---

## The three angles

### FB-01-A — Avoided-emissions reporting layer (measurement only)

**Short.** Lightweight LCA tool. Food bank enters ops data; platform outputs a corporate-grade avoided-emissions report. No funding flow.

**Long.** Most food banks track rescued kg in spreadsheets but never translate it to climate impact. FB-01-A parses the messy log with Claude, normalises categories, applies WRI FLW Protocol + FAO LCA factors, and outputs three tiers: a 1-pager, a methodology PDF, a CSV. Food banks use it to sharpen existing fundraising — no marketplace, no recurring corporate revenue. Single-workflow scope, deterministic factors, highest finishing confidence in the cluster, lowest ceiling.

### FB-01-B — Blended-allocation sponsor marketplace (the proposal in `bank_food_idea.md`)

**Short.** Two-sided platform turning rescued-food emissions into corporate sponsorship. Blended allocation prevents winner-takes-most.

**Long.** Built on FB-01-A. Food banks publish verified impact + need data; CSRD-curious NL corporates browse and commit funding. The flow is not pure marketplace — corporates pick X% of the spend (impact-tied), the remaining (1-X)% is pooled and distributed by need across the network. This defuses the winner-takes-most risk the original notes flagged. Solvimon handles checkout. Pitch reframe: "measurement-and-funding infrastructure that substitutes uncategorised CSR spend with CSRD-reportable food-rescue funding." Two-sided in 24h is ambitious; demo wins when both sides update live.

### FB-01-C — Verified carbon-credit issuance

**Short.** Voluntary carbon credits from rescued food, issued via Verra / Gold Standard. Corporates buy; food banks share revenue.

**Long.** Each credit = one tCO2e avoided, registered on Verra VCS / Gold Standard / Plan Vivo. Mid-sized food banks rescue 1,500–4,000 t/year → several hundred tCO2e/year × €20–80/tonne. Highest financial ceiling in the cluster. But voluntary markets are under intense scrutiny post-2023 (Verra rainforest investigations); credibility hinges on additionality, permanence, double-counting; no widely-accepted methodology for food rescue exists yet. 24h-realistic deliverable is a v0 protocol writeup + mock Solvimon purchase, not live registry issuance. Pick only with a carbon-market specialist on the team.

---

## Three-way head to head

| Axis | FB-01-A Reporting layer | **FB-01-B Sponsor marketplace** | FB-01-C Carbon credits |
|---|---|---|---|
| Score (standalone v2-style) | 73.2 | **76.4** | 69.5 |
| v3 re-score (Warchild lens) | ~48 | ~50 | ~42 |
| Build local | ⭐⭐⭐⭐ Voedselbanken NL | ⭐⭐⭐⭐ Voedselbanken + NL corporates | ⭐⭐⭐ International issuance pathway |
| Innovation hook | First reporting layer purpose-built for food-bank LCA | **CSR-tech wedge: measurement → funding flow** | Voluntary carbon market for rescued food |
| Demo arc | Food bank inputs ops data → corporate-grade sustainability PDF | Corporate browses food banks; sponsors via blended allocation; food bank receives funds | Avoided-emissions calc → tokenised credit → corporate buys |
| Visible mechanics in 60s | 2 (data entry + LCA report) | **4** (ops data + LCA + marketplace + funding flow + Solvimon checkout) | 3 (LCA + audit trail + marketplace) |
| Claude strength used | Structured extraction from messy ops data + report drafting | Same + matching/ranking + corporate-tone narrative | Same + audit-grade reasoning trace |
| Partner tooling fit | Anthropic + Framer | **Anthropic + Solvimon (sponsor checkout) + Framer + Reson8 (NL voice intake)** | Anthropic + Solvimon (credit issuance) |
| Pixel Perfect prize reach | Low | Medium (corporate-side UX clean) | Low |
| Reachable Sat morning | Voedselbanken NL public outreach + 1 corporate sustainability lead | Same — pitch needs both sides on stage | Verra/Gold Standard contact unreachable in 24h |
| Ethical / liability risk | Low | Medium — risk of perverse incentive (well-reported food banks beat needier ones) | **High** — credit double-counting + LCA accuracy under audit |
| Privacy demo | None — ops data only | None | None |
| Hallucination cost if shipped | Low (LCA factors deterministic) | Medium (matching choices + tone of pitch) | **High** (overstated credits = greenwashing claim) |
| Business model story | Hard — who pays for the report? | **Clean** — corporate CSR budget routes through platform; blended allocation defuses pure-market dynamic | Clean *if* audit holds — credit price × volume; food banks share revenue |
| Scope confidence at 24h | **High** — single workflow | Medium — two-sided marketplace + checkout in 24h is real | Low — Verra-grade audit trail not buildable in 24h |
| Team size sweet spot | 2 | **3–4** | 4 + sustainability domain expert |
| $50 Anthropic credit fit | Excellent — short structured outputs | Good — moderate token use | Good — moderate token use |
| Demo wow | Quiet — PDF appears | Mission + business model both visible at once | Drama if Solvimon credit purchase lands live |
| Pick when | Risk-averse, finishing-confidence priority | **Default for this cluster** — most score-to-effort, two thematic frames | Strong sustainability/carbon-market team only |

## When to pick which

- **FB-01-A** — your team is **2 people**, you want a single clean workflow, and you're happy to pitch the measurement layer as a stand-alone wedge with a "marketplace is v2" slide. Lowest risk; lowest ceiling.
- **FB-01-B** — your team is **3–4 people including someone who can sell the corporate-CSR side credibly**, and you can secure a quote from one Voedselbanken regional + one corporate sustainability lead by Saturday afternoon. **Highest score-to-effort in this cluster**; matches the kickoff "wedge thinking" framing exactly (clear initial user, painful workflow, expansion path).
- **FB-01-C** — your team has **sustainability-credit domain expertise** and is willing to take on the audit/credibility framing. Genuinely novel; loses badly if the LCA story isn't airtight enough to survive a "this is greenwashing" question.

**Default recommendation: FB-01-B (blended-allocation sponsor marketplace).** It's the version in `bank_food_idea.md` and it's the right call. The blended-allocation insight — *some funding tied to measured impact, some by need* — is the answer to the biggest risk the original notes flagged (winner-takes-most dynamic). Frame the pitch on that.

---

## How this cluster compares against the rest of the repo

Under the **post-kickoff Warchild lens**, FB-01-B drops to ~50 (off-customer; Voedselbanken, not Warchild). Under the **v2 NL build-local lens**, FB-01-B at 76.4 sits between **NP-13-A (80.6)** and the **ES-09-C / ES-10-B / NP-15-A** band — solid mid-tier, not top.

**Verdict.** FB-01-B is a credible fallback if the Warchild path collapses Saturday morning. It is not better than WC2-A (85.3) or WC1-A (81.0) for this hackathon's stated kickoff customer, but it has a cleaner business-model story than most of the v2 NP cluster and a sharper wedge than NP-13-A.

**If picked, the Q&A pre-empts:**

- *"Won't this push food banks to compete?"* — Blended allocation. % tied to impact, % to need. Spelt out as a config knob.
- *"Why corporate, not gemeente?"* — Gemeente already funds Voedselbanken modestly; corporate CSR is the unaddressed addressable budget. NL corporate sustainability spend is in the €100Ms; food-bank funding is single-digit % of that today.
- *"Why now?"* — CSRD reporting requirements (EU 2024+) make corporates hungry for verifiable scope-3-adjacent climate stories. Rescued-food avoided emissions is a new, ownable narrative.
- *"What if the LCA is wrong?"* — Use FAO + WRI FLW Protocol factors as the floor; flag uncertainty bands; never claim what you can't substantiate.

---

## To add to `10_all_ideas_head_to_head.md` Group 5 tournament

| Rank insertion | Idea | Cluster | Score (post-kickoff) | One-liner | Verdict |
|---|---|---|---|---|---|
| ~12 | **FB-01-B Sponsor marketplace** | FB-01 | 76.4 standalone / ~50 post-kickoff | Food bank ops data → LCA report → blended-allocation corporate sponsorship | **Strong fallback if Warchild path collapses** |

(Sits between NP-15-B at 72 post-kickoff and NP-20-B at 70 post-kickoff. Higher standalone than either, but takes the same off-customer penalty.)
