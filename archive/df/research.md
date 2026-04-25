# BUILD LOCAL — Access Gaps in Amsterdam / NL

Research brief for the Anthropic x Whale hackathon (25–26 April). Concrete, named opportunities a 2–4 person team can prototype in 24 hours with Claude.

---

## 1. Digital divide in Amsterdam / NL

- **3M people** aged 16–75 struggle with reading/writing/arithmetic; **1.8M adults** have low language proficiency. ([Stichting Lezen en Schrijven](https://www.lezenenschrijven.nl/))
- ~20% of NL lacks basic digital "knoppenkennis"; **40–45%** among 65+. ([Seniorenzelfaanzet](https://seniorenzelfaanzet.nl/ouderen-lang-niet-allemaal-digivaardig/))
- **DigiD = #1 pain point** — 24% of all questions at Informatiepunten Digitale Overheid (IDOs). ([NOS](https://nos.nl/l/2482218))
- IDOs sit inside ~95% of municipalities (incl. **OBA Amsterdam**); **Digihulplijn 0800-1508** national. ([Bnetwerk](https://www.bibliotheeknetwerk.nl/dashboard/dashboard-ido))
- Government letters routinely above B1 reading level. ([Gebruiker Centraal](https://www.gebruikercentraal.nl/dat-miljoenen-mensen-worstelen-met-de-digitale-overheid-ligt-natuurlijk-niet-aan-de-overheid/))

**Pitch — "OBA Co-pilot":** Tablet kiosk for IDO volunteers. Snap a photo of an overheid letter → Claude explains in B1 Dutch, Tigrinya, Arabic, Turkish or Ukrainian, generates the next concrete step, prints a to-do card. Voice via Reson8 for non-readers.

---

## 2. Municipality / overheid pain

- **Toeslagenaffaire:** 87% completed integral assessment; supplementary-damage processing won't finish by 2027. Government **stopped assembling personal dossiers in March 2025** — parents must self-reconstruct. ([Rekenkamer](https://www.rekenkamer.nl/publicaties/rapporten/2025/05/21/hersteloperatie-toeslagen), [Rijksoverheid](https://www.rijksoverheid.nl/actueel/nieuws/2025/07/04/gedupeerde-ouders-krijgen-keuze-uit-twee-routes-voor-aanvullende-schade))
- **Schuldhulpverlening Amsterdam** via Buurtteam: statutory 4-week max, real waits weeks–months. ([Buurtteam Amsterdam](https://www.buurtteamamsterdam.nl/schuldhulpverlening-amsterdam/))
- **Bijstand application:** ~1 hour, heavy documentation, 6-week bezwaar window. ([Buurtteam Amsterdam](https://www.buurtteamamsterdam.nl/uitkering-aanvragen-amsterdam/))
- **WMO**: 6-week decision; rules notoriously complex. ([Gemeente Amsterdam](https://www.amsterdam.nl/zorg-en-ondersteuning/wmo/wmo-voorzieningen-aanvragen-regelen/))

**Pitches:**
- **Toeslagen Dossier Reconstructor** — parents upload paperwork → Claude builds timeline + drafts route-1/2 application. Long-context play.
- **Bijstand-in-een-uur** — voice intake any language → Claude fills the gemeente form + checklist + bezwaar template.

---

## 3. Non-profits in Amsterdam

- **Voedselbanken NL 2025:** ~155,600 clients (+7.5% YoY); Stichting Tweede Kans (Oost) at risk. ([Gemeente.nu](https://www.gemeente.nu/sociaal/aantal-klanten-voedselbanken-stijgt-in-2025-met-75-procent/))
- **HVO-Querido:** >18,000 homeless in Amsterdam-Amstelland 2025; 1,367 rough sleepers. ([HVO-Querido](https://hvoquerido.nl/hoe-word-je-dakloos-in-amsterdam/))
- **Leger des Heils:** average 13-month shelter stay; undocumented turned away while beds unused. ([Leger des Heils](https://www.legerdesheils.nl/artikel/crisissituatie-dak-en-thuisloosheid))
- **ASKV** (Chris Lebeaustraat 4): legal/medical/social aid for *undocumented*; volunteer interpreters. ([ASKV](https://www.askv.nl/))
- **Vluchtelingenwerk Amsterdam:** ~7k statushouders; ~2.5-yr caseload per worker. ([O&S Amsterdam](https://onderzoek.amsterdam.nl/publicatie/vluchtelingenmonitor-2025))
- **Pantar:** 2,500 employees with work disabilities; structurally underfunded.

**Pitches:**
- **Voedselbank Match** — scan crate, match to dietary/cultural restrictions, print multilingual recipe cards.
- **Casework Co-pilot for Vluchtelingenwerk / ASKV** — Reson8 transcribes intake → Claude drafts bezwaar/IND letter + structured notes + client-language checklist. Cuts admin 30–50%.

---

## 4. Emergency services

- **112 SMS** for deaf/HoH requires pre-registration; the **Tolkcontact NGT app only runs 07:00–22:00**, leaving a 9-hour overnight gap. ([Politie](https://www.politie.nl/informatie/hoe-bereik-ik-alarmnummer-112-als-ik-doof-of-slechthorend-ben.html))
- **113:** 400–500 conversations/day with suicidal callers. ([113.nl](https://www.113.nl/))
- **Veilig Thuis 2025:** 315k contacts, 136k reports nationally; ~9k in Amsterdam. ([CBS](https://www.cbs.nl/nl-nl/nieuws/2026/17/opnieuw-meer-meldingen-en-adviezen-veilig-thuis))
- **Slachtofferhulp:** sexual-abuse requests +27% H1 2025. ([Slachtofferhulp](https://www.slachtofferhulp.nl/nieuws-overzicht/2025/drempel-aangifte-seksueel-geweld/))

**Pitches:**
- **112-Tekstbrug** — PWA: typed/voice description → structured, location-tagged 112 message with triage classification. Closes the 9-hr NGT gap.
- **Veilig Thuis Triage Companion** — caller in Tigrinya/Arabic/Turkish; operator gets Dutch summary + DASH risk score.
- **Aangifte Coach** — victim narrates events in own language; Claude produces chronological, evidence-tagged Dutch aangifte.

---

## 5. Minority communities in Amsterdam

- City: **9.1% Moroccan, 8.8% Surinamese, 5.3% Turkish, 1.5% Antillean**. ([Republiek Allochtonie](https://www.republiekallochtonie.nl/blog/feiten/samenstelling-van-de-amsterdamse-bevolking))
- **Bijlmer:** 10–15k Ghanaian/Nigerian, 25k Surinamese, 5–6k Antillean; 1 in 5 Ghanaians self-report poor Dutch. ([NOS](https://nos.nl/l/2216570))
- **Ukrainians:** ~115k in NL; ~8k initially placed in Amsterdam; >60% working-age in paid work. ([CBS](https://longreads.cbs.nl/asielenintegratie-2025/oekrainers-in-nederland/))
- **Eritreans:** mostly young, low-educated, Tigrinya-only; cultural mediators identified as missing link. ([KIS](https://www.kis.nl/artikel/eritreeers-nederland-alles-anders))
- **GGZ access** for migrants blocked by interpreter shortage + cultural mismatch. ([UvA](https://www.uva.nl/content/nieuws/persberichten/2025/06/vluchtelingen-en-migranten-vinden-vaak-juiste-ggz-zorg-niet.html))

**Pitches:**
- **Cultural Mediator-in-a-Box** — Claude + Reson8 as Tigrinya/Arabic/Dari/Turkish ↔ Dutch live interpreter inside a GGZ intake; produces SOAP note for clinician. Aware of culture-specific somatisation.
- **Recogin Radio Bot** — WhatsApp bot for Bijlmer Ghanaian community in Twi/English with audio replies; meets people on the channel they actually use.

---

## 6. Small / under-resourced sectors

- **GP shortage:** 777k–926k Dutch lack a huisarts; ~60% of practices on patiëntenstop in 2024. Admin = #1 burnout driver. ([Rekenkamer](https://www.rekenkamer.nl/actueel/nieuws/2025/04/02/1-op-20-nederlanders-zoekt-andere-huisarts))
- **Mantelzorgers:** ~5M in NL; **825k** care intensively; **22% feel overburdened** (vs 14% in 2020). ([Movisie](https://www.movisie.nl/artikel/5-miljoen-nederlandse-mantelzorgers-feiten-cijfers))
- **MBO students:** in one institution, **68% of first-years below 2F reading level**. ([Onderwijsinspectie](https://www.onderwijsinspectie.nl/onderwerpen/staat-van-het-onderwijs/nieuws/2025/4/16/nederlandse-leerlingen-kwetsbaar-in-veranderende-wereld))

**Pitches:**
- **Huisarts Admin Off-Loader** — Reson8 dictates → Claude returns SOAP note, ICPC code, specialist referral, B1 patient summary in 30s.
- **Mantelzorg Concierge** — WhatsApp helper: tracks meds, parses WMO/PGB letters, drafts replies, flags burnout signals.
- **MBO Reader's Aide** — photograph contract → A2/B1 rewrite + audio + comprehension quiz.

---

## 7. Policy hooks (last 12–18 months)

- **EU AI Act in NL:** banned uses + AI literacy mandatory since 2 Feb 2025; **2 Aug 2026 = high-risk obligations for governments**. AP coordinates 10 sectoral regulators. ([AP](https://www.autoriteitpersoonsgegevens.nl/en/themes/algorithms-ai/eu-ai-act))
- **Kinderarmoede 2024 (CBS, Dec 2025):** 93k minors in poor households; **7.3%** in households where breadwinner born abroad vs 1.2% Dutch-born. ([CBS](https://longreads.cbs.nl/leven-in-armoede-2025/hoeveel-kinderen-zijn-arm/))
- **Toeslagenaffaire:** dual-route choice for supplementary damage (July 2025). ([Rijksoverheid](https://www.rijksoverheid.nl/actueel/nieuws/2025/07/04/gedupeerde-ouders-krijgen-keuze-uit-twee-routes-voor-aanvullende-schade))

**Pitches:**
- **AI Act Compliance Sidekick for Gemeenten** — reads algoritmeregister + procurement contracts, drafts Article 6 risk classification + DPIA. Real Aug-2026 deadline = real customer.
- **Toeslagen-route Picker** — plain-language wizard: Route 1 (CWS) vs Route 2 (UHT) + personalised timeline.

---

## Why these play to Claude's strengths

| Strength | Best fits |
|---|---|
| Multilingual (Tigrinya, Arabic, Twi, Turkish, Ukrainian) | Cultural Mediator, Recogin Radio, Veilig Thuis Triage, Aangifte Coach |
| Long-document understanding | Toeslagen Dossier Reconstructor, AI Act Sidekick, OBA Co-pilot |
| B1 Dutch rewriting | OBA Co-pilot, MBO Reader's Aide, Mantelzorg Concierge |
| Voice (Reson8) | 112-Tekstbrug, Huisarts Off-Loader, Casework Co-pilot |
| Structured form-filling | Bijstand-in-een-uur, Aangifte Coach |

**Strongest 24-hour bets** (demoability × impact × named customer):

1. **OBA Co-pilot for IDOs** — partner already exists in every library
2. **Casework Co-pilot for Vluchtelingenwerk / ASKV** — clear interpreter-shortage pain
3. **Huisarts Admin Off-Loader** — direct ROI story, 1-in-20 patient gap
4. **112-Tekstbrug** — visible, emotional, clear before/after

---

## Scoring against the 5 jury criteria

Scale 1–5 per axis. Criteria: (1) Innovation & creativity · (2) Build Local theme fit · (3) Technical execution · (4) Impact & viability · (5) Pitch & presentation.

| Idea | Innov | Local | Tech | Impact | Pitch | **Total** |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **Toeslagen Dossier Reconstructor** | 5 | 5 | 5 | 5 | 5 | **25** |
| **OBA Co-pilot for IDOs** | 3 | 5 | 4 | 5 | 5 | **22** |
| **112-Tekstbrug** (NGT 9-hr gap) | 4 | 5 | 4 | 4 | 5 | **22** |
| **Casework Co-pilot (Vluchtelingenwerk/ASKV)** | 3 | 5 | 5 | 5 | 4 | **22** |
| **Cultural Mediator-in-a-Box (GGZ)** | 4 | 4 | 5 | 4 | 4 | **21** |
| **Aangifte Coach (Slachtofferhulp)** | 4 | 4 | 4 | 4 | 5 | **21** |
| **Veilig Thuis Triage Companion** | 3 | 5 | 4 | 4 | 4 | **20** |
| **Mantelzorg Concierge** | 3 | 4 | 4 | 4 | 4 | **19** |
| **AI Act Compliance Sidekick** | 3 | 4 | 4 | 4 | 2 | **17** |
| **Huisarts Admin Off-Loader** | 2 | 3 | 4 | 4 | 4 | **17** |

**Notes on the low scorers:**
- **Huisarts Admin Off-Loader** — fights the theme ("doctors" aren't "left behind"), and the space is crowded (Tortus, Heidi, Captain). Jury will deduct on Innovation and Local.
- **AI Act Sidekick** — strong B2G case, but a compliance tool is a hard pitch on a hackathon stage. The room wants emotional.

---

## How to win each axis

### 1. Innovation & creativity
- Pick a hook competitors won't have. The strong ones in this brief: **the March 2025 toeslagen-dossier policy change** (state stopped assembling personal dossiers — you give them back), **the 9-hour overnight NGT gap** in 112 service, **B1 + voice for non-readers** at the IDO desk.
- Avoid generic "Claude-wrapped chatbot for X". Show one mechanic that *only* works because the model is this capable (1M context reconstruction, real-time multilingual SOAP, multi-doc cross-reference).

### 2. Build Local theme
- **Name a real partner on slide 1.** "We built this with the IDO at OBA Bijlmer" beats "for non-profits". If you can DM Vluchtelingenwerk / ASKV / Buurtteam Saturday morning and get a quote or a 5-minute call, do it.
- **Use a real Dutch artefact.** A real (redacted) Belastingdienst letter, a real DigiD screenshot, real Tigrinya audio. Localness is shown, not stated.
- **The judging panel is Dutch operators** (Mol, van Lanschot, Jones, Timmermans). They will instantly clock fake locality.

### 3. Technical execution
- **Lean on Claude's load-bearing strengths**, not a thin wrapper:
  - **Long context (1M)** → the toeslagen play is custom-built for this
  - **Multilingual** → Tigrinya, Twi, Arabic, Turkish, Ukrainian (verify quality before pitching)
  - **Vision** → photographing letters at the IDO kiosk
  - **Structured output** → form-filling, ICPC codes, DASH risk scores
- **Use partner tooling where it earns its keep**:
  - **Reson8** (Dutch ASR, free tier) — the NL judges will appreciate; load-bearing for any voice idea
  - **Solvimon** — donations/checkout for non-profit ideas (Voedselbank, ASKV, school of moral ambition style)
  - **boxd** — gives each agent a microVM with public HTTPS; useful if you spin sub-agents per case
  - **Framer** — for the Pixel Perfect prize, design the kiosk/app surface in Framer
- **Don't fake the demo.** Pre-cache fixtures for reliability, but the model call must be real on stage.

### 4. Impact & viability
- Open with **a number of people affected today** and close with **a 12-month rollout path**. Example for OBA Co-pilot: "230 IDO desks · 2.6M overheid letters/year · pilot in 3 OBA branches by Q3."
- Identify **who pays**. Gemeente budget? VWS subsidy? Funder? Donations via Solvimon? "Real Ones" prize specifically rewards this.
- Address the **failure mode honestly** in one sentence. Hallucination on legal text? "Cite and link to the source paragraph; never invent a clause."

### 5. Pitch & presentation
- **1-min submission video format:**
  1. 0:00–0:10 — the user (face, voice, problem) — not the tech
  2. 0:10–0:35 — live mechanic in 2 cuts (input → magic → output)
  3. 0:35–0:50 — one number that lands the impact
  4. 0:50–1:00 — named partner + ask
- **2-min live finalist demo:** run the real flow once, end-to-end. Have a backup fixture if the network dies, but don't open with it.
- **2-min Q&A:** the panel are operators. Pre-bake answers for: privacy/AVG, hallucinations on legal docs, who pays, why now, why not just a Google form. Adriaan Mol will ask about distribution.

---

## Recommendation

**Primary pick: Toeslagen Dossier Reconstructor.** Highest score on all five axes, perfect Claude long-context fit, the March 2025 policy change is a fresh and emotional hook no other team will have. Risks: privacy framing must be airtight (handle PDFs locally / in-session), and you need 5–10 real (synthetic but realistic) artefacts to demo on.

**Backup pick: OBA Co-pilot for IDOs.** Easier to demo (hold up a letter), guaranteed Local fit, and you can plausibly walk into the OBA Saturday morning. Smaller innovation ceiling but very hard to score badly on.

**Wildcard if your team has a strong storyteller: 112-Tekstbrug.** The most emotional pitch of the bunch and the NGT 9-hour-gap fact lands instantly. Watch the technical scope — the meldkamer integration is the part you fake.

**Avoid: Huisarts Off-Loader, AI Act Sidekick.** Both score badly on Local + Pitch and are hard to recover from.
