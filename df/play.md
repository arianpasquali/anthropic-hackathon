# Final pick & playbook

Companion to `research.md` and `research_circular.md`. Decision, architecture, hour-by-hour, video + demo + Q&A.

---

## Three-way head to head

| Axis | Toeslagen Reconstructor | **InrichtingsBuddy** | **OBA Co-pilot** |
|---|---|---|---|
| Score | **25** | 24 | 22 |
| Theme: access | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Theme: circular | — | ⭐⭐⭐⭐⭐ | — |
| Innovation hook | Mar 2025 dossier-policy change | Multi-modal aggregator across 4+ silos | "24% of IDO questions are DigiD" |
| Demo arc | Trauma paperwork → coherent dossier | Refugee family arrives → furnished home | Volunteer + visitor at IDO → printed card |
| Visible mechanics in 60s | 1 (deep) | **4** (vision + voice + multilingual + checkout) | 3 (vision + multilingual + voice) |
| Claude strength used | 1M long context | Vision + multilingual + doc parse + tool use | Vision + B1 rewriting + multilingual |
| Partner tooling fit | Light | Reson8 + Solvimon + Framer | Reson8 + Framer (no Solvimon hook) |
| Pixel Perfect prize reach | Low | **High** (RTL, voice-first, low-literacy) | Medium (kiosk UX) |
| Reachable Sat morning | UHT/CWS unreachable | Vluchtelingenwerk, ASKV, Buurtteam, ReShare | **Walk into OBA Bijlmer / Oosterdok** |
| Ethical / liability risk | **High** — wrong route hurts a victim | Low — wrong sofa is annoying | Low — volunteer is in the loop |
| Privacy demo | BSN, finances, IND records | Postcode, household, BSN on letter | BSN on letter (volunteer = consent context) |
| Hallucination cost if shipped | High (legal claim) | Low (item not in stock) | Low (volunteer reviews) |
| Business model story | Hard — who pays? | **Clean** — gemeente inrichtingskrediet routes through you | Clean — KB / VWS laaggeletterdheidsbudget |
| Scope confidence at 24h | Medium | Medium-low (4 vendors, i18n, checkout) | **High** (single workflow) |
| Team size sweet spot | 2–3 | **4** | **2–3** |
| Total addressable demo wow | Emotional 1-shot | 4-mechanic montage | 1 dramatic before/after |

## When to pick which

- **InrichtingsBuddy** — your team is **4 people**, you have at least one designer, and you're confident you can ship a multi-vendor demo. Best score-to-effort, two thematic frames at once, Pixel Perfect prize in reach.
- **OBA Co-pilot** — your team is **2–3 people**, or you're risk-averse on demo polish, or your strongest skill is workflow design over breadth. **Highest finishing-confidence on the menu.** You can literally walk into OBA Bijlmer Saturday morning, film a real volunteer, and have a partner quote on stage.
- **Toeslagen Reconstructor** — your team has a **strong narrative writer + someone lawyer-adjacent**, and you're willing to take on the ethical/liability framing. Wins on emotional landing if executed well; loses badly if the privacy story isn't airtight.

**Default recommendation: InrichtingsBuddy** if your team profile fits, **OBA Co-pilot** as the safe, high-confidence alternative. The two share enough architecture (vision + multilingual + Reson8 + Framer) that a Saturday-morning pivot from one to the other is feasible if scope blows up.

---

---

# Playbook A — InrichtingsBuddy

## Architecture

```
                 ┌───────────────────────────────┐
                 │  Framer / React on boxd VM    │
                 │  (RTL, voice-first, B1 + L1)  │
                 └──────────────┬────────────────┘
                                │
        ┌───────────────────────┼───────────────────────────┐
        │                       │                           │
        ▼                       ▼                           ▼
┌──────────────┐    ┌──────────────────┐         ┌────────────────────┐
│ Letter Parser│    │ Voice Intake     │         │ Inventory Aggreg.  │
│ Opus 4.7     │    │ Reson8 (NL)      │         │  ┌──────────────┐  │
│ + PII redact │    │ Claude (other L) │         │  │ ReShare fix. │  │
└──────┬───────┘    └────────┬─────────┘         │  │ Lokatie fix. │  │
       │                     │                   │  │ Buurman fix. │  │
       └─────────┬───────────┘                   │  │ Mktplaats LV │  │
                 ▼                               │  └──────┬───────┘  │
       ┌─────────────────────┐                   │         │          │
       │ Need Generator      │                   └─────────┼──────────┘
       │ Sonnet 4.6          │                             │
       │ → furniture list    │                             │
       └─────────┬───────────┘                             │
                 │                                         │
                 ▼                                         │
       ┌─────────────────────────────────────────────────┐ │
       │ Match & Rank (Sonnet 4.6 + vision)              │◀┘
       │ rank by distance, price, Stadspas, condition    │
       └─────────────────────┬───────────────────────────┘
                             │
                             ▼
                 ┌────────────────────────┐
                 │ Solvimon checkout      │
                 │ multi-vendor cart      │
                 │ Stadspas line-item     │
                 │ inrichtingskrediet bal │
                 └────────────────────────┘
```

### Component contracts

**Letter Parser** (Opus 4.7, ~1 call/session)
- In: PDF or photo of AZC plaatsingsbrief / gemeente huisvestingsbesluit
- Pre: regex-redact BSN, IBAN, full DOB → keep year only
- Out: `{postcode, household_size, adults, children_ages[], bedrooms, move_date, inrichtingskrediet_amount, language_pref?}`
- Demo this: show the redaction live on screen.

**Need Generator** (Sonnet 4.6)
- In: parsed household + cultural profile (e.g. eet-op-de-grond preference, prayer space)
- Out: prioritised list `[{item, priority 1-3, qty, alt_categories[]}]`
- 30–40 line items typical for a 4-person family.

**Inventory Aggregator**
- Each source returns `{source, item_id, name, category, price_eur, condition_1to5, distance_km, photo_url, listing_lang, stadspas_eligible}`
- Real: Marktplaats live API slice (5–10 items) + your fixtures (50 ReShare, 50 Lokatie, 30 Buurman)
- Honest in pitch: "1 of 4 live; 3 fixture; partner integration is a 1-day conversation."

**Match & Rank** (Sonnet 4.6 + vision)
- For each need-line, vision-classify candidate photos, score, return top 3
- Tiebreaker: Stadspas-eligible first, then closest, then condition

**Translator/Localiser** (Sonnet 4.6)
- Translate item descriptions and the entire UI to user L1
- Verify on Saturday: ask a venue native speaker

**Checkout** (Solvimon test env)
- One cart, multiple line items tagged by source
- Apply Stadspas discount per line where eligible
- Show inrichtingskrediet remaining balance prominently
- Demo a real Solvimon test transaction — that's the moment of magic

---

## What to build vs. fake

| Component | Build for real | Fake / fixture |
|---|---|---|
| Letter parsing (Opus) | ✅ | 3 redacted sample letters |
| BSN/PII redaction | ✅ regex | — |
| Need generation | ✅ | — |
| ReShare inventory | ❌ | 50-item fixture |
| De Lokatie inventory | ❌ | 50-item fixture |
| Buurman inventory | ❌ | 30-item fixture |
| Marktplaats inventory | ✅ live API slice | — |
| Vision classification | ✅ on real photos | — |
| Multilingual UI (Arabic+Ukrainian min) | ✅ | — |
| Stadspas eligibility logic | ❌ | rule-based mock per source |
| Solvimon checkout | ✅ test env | single mock vendor key, others mocked |
| Reson8 voice (Dutch staff) | ✅ if accent works | else Claude ASR |
| Inrichtingskrediet balance | ✅ math | seeded €4k |

---

## 24-hour build plan (4 people)

**Saturday**

- **11:00–12:30** opening session (mandatory, listen for partner-tooling tips)
- **12:30–13:30** lunch + scope freeze. Roles:
  - **P1 — Backend / Letter parse:** Opus prompt, redaction, JSON schema
  - **P2 — Inventory & vision:** fixtures, Marktplaats API, classification prompts
  - **P3 — Frontend / i18n:** Framer or React, Arabic + Ukrainian + Dutch, voice surface
  - **P4 — Solvimon + Pitch:** integration, slide deck, video edit
- **13:30–18:00** vertical slice: 1 user, 1 language (Arabic), 1 vendor, end-to-end happy path
- **18:00–19:30** group dinner (mandatory)
- **19:30–22:00** vendors 2–4, Solvimon real transaction, second language (Ukrainian)
- **22:00–01:00** Stadspas logic, voice intake, polish micro-copy at B1
- **01:00–04:00** rest / fixture work / debugging

**Sunday**

- **06:30–08:30** sauna optional. Polish only — feature freeze at 09:00
- **08:30–09:00** breakfast
- **09:00–10:30** rehearse 1-min video; record 3 takes
- **10:30–11:30** edit video; capture stills for thumbnails
- **11:30–11:55** upload to `joris@whale-academy.com`
- **12:00** deadline (do NOT touch after this)
- **12:00–13:30** lunch + memorise Q&A answers
- **13:30–15:00** live demo if finalist

**Hard rule:** if a feature isn't working by **Saturday 22:00**, cut it. The video is everything.

---

## 1-minute video script

Open on a face, not a screen.

**0:00–0:08** (close-up of statushouder, Arabic VO + subs)
> "Last week I left the AZC. The gemeente gave me €4,000 to furnish my new home in four weeks. I do not speak Dutch. I have never heard of a kringloop."

**0:08–0:15** (phone snaps a gemeente letter)
> VO English: "InrichtingsBuddy reads the letter — postcode, family size, move date, budget."

**0:15–0:25** (screen: structured JSON building; BSN highlighted then blurred)
> VO: "Privacy first. We redact your BSN before it leaves your phone."

**0:25–0:35** (UI in Arabic; voice line "I have two children, five and seven"; list updates)
> VO: "Tell us about your family — in your own language."

**0:35–0:48** (fast cuts of ReShare, De Lokatie, Buurman, Marktplaats logos; couch, beds, fridge, table appear)
> VO: "We search circular first. Stadspas discount applied automatically."

**0:48–0:55** (Solvimon checkout; €1,847 of €4,000; CO2 counter spins to 1.4t)
> VO: "One checkout. €2,153 left. 1.4 tons of CO2 saved."

**0:55–1:00** (Framer mockup of furnished living room; family in frame)
> VO: "InrichtingsBuddy. Built locally. For everyone."

**Production notes**
- Shoot 0:00–0:08 with a real or willing volunteer. If unavailable, use a high-quality stock face — never AI-generated, jurors will clock it.
- Subtitles in Dutch + English (the jury will read).
- Cut on the beat. 24 cuts in 60 seconds is fine.
- Lower-third on every shot showing the *real* tool firing (model name, vendor name).
- Silence > music. If music, instrumental, low.

---

## 2-minute live demo (if finalist)

| Time | Action | What the audience sees |
|---|---|---|
| 0:00–0:15 | Set the user — name, country, kids' ages | Slide with photo + family card |
| 0:15–0:35 | Upload real letter on stage; show JSON building | Live Opus call, BSN redaction visible |
| 0:35–0:55 | Switch UI to Arabic; one voice line in Arabic | Reson8/Claude ASR transcript |
| 0:55–1:25 | Inventory match across 4 vendors | Cards animate in with photos |
| 1:25–1:50 | Add to cart; Solvimon checkout; Stadspas applies | Real test-env transaction success |
| 1:50–2:00 | Close: 25k statushouders/yr; partner = Buurtteam Amsterdam | One-line CTA |

**Stage rules**
- Network can fail. Have one fixture-only fallback path on the same UI; switch with a hotkey.
- Pre-warm the model. Run the letter parse 30 seconds before going on stage so prompt cache is hot.
- Don't narrate the screen. Let it speak.

---

## Q&A prep (the operators on the panel)

**Adriaan Mol — distribution / scale**
> "Who's your real customer?"
- Gemeenten, not statushouders. 32 MRA gemeenten × ~25k statushouders/year nationally. We're a routing layer the gemeente plugs into existing inrichtingskrediet flow. Pilot: Buurtteam Amsterdam, 20 households, Q3.

**Duco van Lanschot — unit economics**
> "What does the buyer save?"
- Snuffelmug × Spaarne Werkt pilot showed 30–40% cheaper than IKEA-equivalent at equal quality. Plus labour-inclusion: Het Goed runs 982/1973 staff on Wsw contracts. We capture a 5–8% affiliate fee from kringloops + Solvimon platform margin.

**Clare Jones — viability**
> "Six orgs already do pieces of this. Why isn't it solved?"
- Exactly because there are six. None have multilingual + document-aware + multi-vendor checkout. We're the routing layer that makes the existing fragmented circular safety net usable for someone who doesn't speak Dutch.

**Ruben Timmermans — moral ambition**
> "What's the bigger frame?"
- A €4k cheque today gets spent at IKEA + ends up in Marktplaats six months later. We close that loop and give the dignity of choice in your own language. Not charity — leverage.

**The privacy question (anyone)**
> "What about the BSN on that letter?"
- Redacted client-side with regex before the model sees it. No persistence. The letter never leaves session memory. AVG-shaped roadmap from day one.

**The hallucination question**
> "What if Claude invents a sofa that isn't at ReShare?"
- Every match is grounded in the actual inventory query. The model classifies and ranks; it never generates an item. If the inventory is empty, the UI says so.

**The "why not IKEA" question**
> "Direct people to IKEA + done?"
- That's status quo. Today's spend leaks out of the city's circular economy on day one. We measure ~1.4t CO2 saved per furnishing in our model — at 25k statushouders/year that's 35kt CO2/year, ~3% of Amsterdam's housing-construction footprint.

**The "shouldn't the gemeente build this" question**
> "Why aren't the gemeente building this?"
- They're trying — see Spaarne Werkt's Snuffelmug pilot. We're the technology partner. Same way Buurtteam doesn't build their own CRM.

---

## Reach-out list (Saturday 11:00 if possible)

Two-line message to each, asking for a 5-minute call or a quote:

- **Vluchtelingenwerk Amsterdam** — info-amsterdam@vluchtelingenwerk.nl
- **ASKV** — info@askv.nl
- **Buurtteam Amsterdam** — via the gemeente liaison
- **Leger des Heils ReShare Store Amsterdam** — they have local store managers
- **Stichting Snuffelmug / Spaarne Werkt** — they ran the exact pilot

A single "we mention you on stage if you give us 5 minutes" call dramatically improves the Local score.

---

## What success looks like Sunday 15:30

- 1-min video uploaded by 11:55
- Live demo runs end-to-end without fallback
- One named partner on the closing slide
- One specific number repeated three times (suggested: **25,000 statushouders/year**, or **€4,000 × 25k = €100M annual circular-furnishing flow at stake**)
- Q&A handled in operator language: customer, unit econ, distribution, risk

That's a top-3 finish.

---

# Playbook B — OBA Co-pilot

The simpler, higher-confidence path. One workflow, one venue, one printed card.

## What it is

A tablet kiosk at the IDO desk inside every Amsterdam library. A citizen who can't read Dutch hands a gemeente / Belastingdienst / UWV / IND letter to a volunteer. Volunteer places it under the tablet camera. In 8 seconds:

1. Letter is parsed (sender, deadline, action required, reference number)
2. Translated to B1 Dutch + the citizen's L1 (Arabic / Tigrinya / Turkish / Ukrainian / Russian)
3. The next 3 concrete steps are generated from a pre-baked playbook ("open MijnOverheid → click X → click Y")
4. Voice plays in the citizen's L1 if they can't read
5. A small thermal printer prints a take-home card with the steps + reference number

## Architecture

```
                 ┌──────────────────────────────────┐
                 │ Framer/PWA tablet UI             │
                 │ (huge camera button, icon langs) │
                 └─────────────┬────────────────────┘
                               │
                               ▼
                 ┌──────────────────────────────────┐
                 │ Letter Parser (Opus 4.7)         │
                 │ + PII redact (regex pre-pass)    │
                 │ → {sender, action, deadline,     │
                 │    ref_no, type, summary_b1_nl}  │
                 └────────┬─────────────────┬───────┘
                          │                 │
                          ▼                 ▼
              ┌────────────────────┐  ┌─────────────────────┐
              │ Translator + B1    │  │ Next-Step Lookup    │
              │ Sonnet 4.6         │  │ Sonnet 4.6 + RAG    │
              │ → L1 + B1 NL       │  │ over playbook bank  │
              └─────────┬──────────┘  └─────────┬───────────┘
                        │                       │
                        └───────────┬───────────┘
                                    ▼
                       ┌────────────────────────┐
                       │ Output layer:          │
                       │  - on-screen card      │
                       │  - voice (Reson8 TTS)  │
                       │  - thermal print       │
                       └────────────────────────┘
```

### Component contracts

**Letter Parser (Opus 4.7)**
- In: photo of overheid letter (any of: Belastingdienst, gemeente, UWV, IND, DUO, MijnOverheid, CJIB)
- Pre: regex-redact BSN, IBAN, full DOB → year only
- Out: `{sender_org, letter_type, action_required, deadline_iso, reference_number, original_summary_b1_nl}`

**Translator + B1 Rewriter (Sonnet 4.6)**
- In: parsed letter + target language
- Out: `{summary_l1, summary_b1_nl}` — both at A2/B1 reading level

**Next-Step Lookup (Sonnet 4.6 + small playbook bank)**
- Pre-baked playbooks for the top ~10 letter types: DigiD reset, toeslagen wijziging, gemeente WMO, UWV, IND vergunning, CJIB boete, DUO, kwijtschelding, zorgtoeslag, AOW.
- 24% of IDO questions are DigiD — make sure that playbook is gold.
- Out: numbered steps, each step has `{verb, target_url_or_address, what_to_have_in_hand}`.

**Output**
- Tablet renders: original letter (zoomable) | L1 translation | B1 NL | step card
- Reson8 TTS for L1 voice playback (or Claude audio output if Reson8 lacks the language)
- Print: browser print API → bluetooth thermal printer (Epson TM-m30 or similar). The printed card is the *moment of magic* — judges remember it.

## What to build vs. fake

| Component | Build for real | Fake / fixture |
|---|---|---|
| Letter parsing (Opus) | ✅ | 5 redacted sample letters across letter types |
| BSN/PII redaction | ✅ regex | — |
| B1 + L1 translation | ✅ | — |
| Voice playback (Reson8 TTS) | ✅ Dutch + Arabic | — |
| Playbook RAG | ✅ for top 5 letter types | other 5 → static fallback |
| Thermal print | ✅ if you can borrow a printer | else PDF download |
| Tablet UI | ✅ (Framer or PWA) | — |

Borrowing a thermal printer for the live demo is worth a 30-min Saturday-morning errand. Brunswick / printer rental shops in Amsterdam stock them; or borrow from a hospitality team at Codam. The card-coming-out moment is the highest-impact 4 seconds of the demo.

## 24-hour build plan (2–3 people)

**Saturday**

- **11:00–12:30** opening session
- **12:30–14:00** scope freeze. Roles for 3 people:
  - **P1 — Backend + RAG:** Opus prompt, redaction, playbook bank for 5 letter types
  - **P2 — Frontend + i18n:** Framer/PWA, 2 languages minimum (Dutch staff + Arabic), tablet form factor
  - **P3 — Pitch + voice + print:** Reson8 TTS, thermal printer, slide deck, video edit
- **14:00–18:00** vertical slice: 1 letter type (DigiD reset), 1 user language (Arabic), end-to-end on tablet
- **18:00–19:30** dinner
- **19:30–22:00** add 4 more letter types, 2nd language (Ukrainian or Tigrinya), thermal print integration
- **22:00–01:00** voice playback, B1 micro-copy polish, 5 redacted sample letters
- **01:00** stop. Sleep matters for delivery on Sunday.

**Sunday**

- **06:30–08:30** sauna optional / polish only
- **08:30–09:00** breakfast
- **09:00–10:00** **shoot the video at OBA Bijlmer or Oosterdok** if a librarian/volunteer is willing — even 30 minutes of real-venue footage transforms the local fit
- **10:00–11:30** edit; record voiceover
- **11:30–11:55** upload
- **12:00** deadline
- **13:30–15:00** live demo if finalist

## 1-minute video script

Real venue, real volunteer if possible. The OBA backdrop alone wins points.

**0:00–0:08** (wide shot of the IDO desk inside OBA Bijlmer; volunteer + citizen sitting together)
> VO: "Every day at the Informatiepunt Digitale Overheid, retired volunteers help citizens read their letters from the gemeente, the Belastingdienst, the IND. 24% of those questions are about DigiD."

**0:08–0:18** (citizen hands letter to volunteer; volunteer places it under the tablet camera)
> VO: "OBA Co-pilot reads the letter in eight seconds."

**0:18–0:28** (split screen: original letter | parsed JSON building, BSN visibly blurring)
> VO: "Privacy first. We redact your BSN before anything goes to the model."

**0:28–0:40** (UI flips to Arabic; voice plays in Arabic; subtitles in Dutch)
> VO: "Your letter — explained, in your own language."

**0:40–0:52** (thermal printer whirs; card slides out; volunteer hands it to citizen)
> VO: "Three steps. Open MijnOverheid. Click 'Toeslagen.' Click 'Wijzigen.' On a card you take home."

**0:52–1:00** (close on the citizen reading the card; smile)
> VO: "OBA Co-pilot. Built for the volunteers who hold the line. 1.8 million low-literate adults in the Netherlands. We start with one letter."

## 2-minute live demo

| Time | Action | Audience sees |
|---|---|---|
| 0:00–0:15 | Set up: 1 slide on the IDO + the 24% DigiD stat | One number on screen |
| 0:15–0:30 | Hand "volunteer" a real Belastingdienst letter; place under camera | Live capture, redaction running |
| 0:30–0:55 | Opus parse → JSON appears → translation | Side-by-side NL + Arabic |
| 0:55–1:25 | Press voice button; Arabic plays through speaker | Audience hears |
| 1:25–1:50 | Thermal printer prints card; hand to "citizen" | The card is the moment |
| 1:50–2:00 | Close: 230 IDO desks, KB partner, pilot ask | Single CTA slide |

**The card is your peak moment.** Make sure the printer works. Print on plain receipt paper with a clean visual — gemeente blue header, big numbers for the steps, reference number, deadline.

## Q&A prep

**Adriaan Mol — distribution**
> "Who pays?"
- KB (Koninklijke Bibliotheek) coordinates IDOs nationally; the budget already exists and grows. ~230 IDO desks at €500/yr per desk = €115k baseline ARR. Bigger play: the laaggeletterdheidsbudget at SZW (~€60M annually). We don't invent a buyer — we plug into one that's hiring volunteers right now.

**Duco van Lanschot — unit economics**
> "What's the ROI for KB?"
- IDO volunteers spend ~6 minutes per case manually translating + Googling the next step. We compress to ~90 seconds. With ~500k DigiD-related cases/year nationally, that's ~40k volunteer-hours saved — the equivalent of hiring 25 FTEs without paying anyone.

**Clare Jones — viability**
> "Isn't this just Google Translate plus an LLM?"
- Translation is 20% of the value. The other 80% is the **next-step playbook** — handing someone a printed card with the exact 3 clicks. That isn't built into Google Translate, gov.nl, or any existing helpdesk. And we own the IDO context: the volunteer reviews everything, so the model is in a guarded loop.

**Ruben Timmermans — moral ambition**
> "What's the bigger frame?"
- The library is the last public space in the Netherlands where help is unconditional. There are 1.8 million low-literate adults in NL, and they're the ones the digital state leaves behind hardest. Volunteers — mostly retirees — keep the line. We give them superpowers. Not charity. Multiplication.

**Jacqueline van den Ende (host) — impact**
> "What's the metric you'd report?"
- Volunteer-minutes saved per letter (target: from 6 to 1.5), citizen self-resolution rate after they leave the IDO (today: ~40%; target: 70%).

**The privacy question**
> "BSN on every letter you scan?"
- Redacted client-side via regex *before* any model call. No persistence after session. Volunteer is physically present, so consent context is unambiguous — same as today's manual help. AVG-first roadmap.

**The hallucination question**
> "What if the model says click Z when the right click is Y?"
- The next-step content is RAG'd from a curated playbook bank we maintain — not free-generated. The volunteer reviews before printing. If we can't match a letter type to a playbook, we fall back to "ask Digihulplijn 0800-1508" rather than guessing.

**The "couldn't libraries just train volunteers more" question**
- Volunteers are mostly 70+. We're not replacing them; we're amplifying. The volunteer is still the human in the loop, doing the empathy work the model can't.

## Reach-out list (Saturday 11:00)

A 5-minute walk from Codam puts you near no library, but a 15-minute bike ride hits OBA Oosterdok or OBA Bijlmer. Both run IDOs.

- **OBA Bijlmer IDO** — walk in Saturday afternoon and ask for the IDO coordinator
- **OBA Oosterdok IDO** — same
- **KB IDO program lead** — email Saturday, follow up Monday
- **Stichting Lezen & Schrijven** — for laaggeletterdheid framing
- **Stichting Pharos** — cultural-health-literacy interpreter network

A single 5-minute on-camera quote from an OBA librarian ("yes, we'd use this tomorrow") is the most powerful single thing you can do for the Local score.

## Numbers to repeat 3 times

- **24%** of IDO questions are DigiD
- **230** IDO desks across NL
- **1.8 million** low-literate adults in the Netherlands

## Why OBA might actually beat InrichtingsBuddy on stage

Even though OBA scores 22 vs 24 on paper, three things can flip it:

1. **The thermal-printer card is more memorable than a Solvimon checkout.** Physical artefacts win in a 100-team competition.
2. **You can shoot the video in a real OBA branch** with real volunteers — InrichtingsBuddy's video is at risk of looking staged.
3. **Lower scope = fewer demo failure modes** = higher chance of a clean live demo. A clean demo at 22 beats a broken one at 24.

If your team is risk-averse, has a strong workflow designer, and can secure a printer + an OBA branch quote: pick OBA.
