# Circular Economy × Access — Amsterdam research

Companion to `research.md`. Same hackathon, same five-axis judging. Pure B2B circularity tools (Madaster, etc.) score badly on the Build Local theme; the strong angles sit at the **intersection of Dutch circular policy and structurally excluded groups** (statushouders, low-income, voedselbank klanten, kids without laptops).

---

## 1. Amsterdam Circular Strategy — what's measured, what's missing

- **Targets unchanged:** halve primary abiotic raw materials by 2030, fully circular by 2050. Baseline 2016. Material use in 2020 ~equal to 2016 — almost no progress in the first four years.
- **Live operational doc:** *Uitvoeringsagenda Circulair 2023–2026* — 70+ projects, €17M, 100% circular procurement target by 2030. Voortgangsrapportage 2025: 60% of 110 activities started, 25% completed.
- **Data gap admitted in the Monitor:** "knowledge of circular transition still in its infancy"; structural insight is missing.
- Sources: [Monitor CE](https://onderzoek.amsterdam.nl/publicatie/de-monitor-circulaire-economie-op-hoofdlijnen) · [Uitvoeringsagenda](https://openresearch.amsterdam/nl/page/102487/uitvoeringsagenda-circulair-2023-2026) · [Voortgangsrapportage](https://openresearch.amsterdam/nl/page/132430/voortgangsrapportage-uitvoeringsagenda-circulaire-economie-2023%E2%80%932026)

**Pitch — Buurt-Circulair:** point phone at a kringloop receipt / Repair Café slip / Voedselbank pickup → Claude vision extracts kg/€/CO2 saved, attributes to your postcode, Reson8-narrated B1 Dutch dashboard the gemeente can plug into the Monitor.

---

## 2. Repair access

- **Repair Café network:** founded 2009 in Amsterdam-West (Martine Postma). Today: **3,818 cafés worldwide, ~40 in Amsterdam, 305,649 logged repairs.**
- **EU Right to Repair (2024/1799):** in force 30 Jul 2024; NL transposition due **31 Jul 2026**. Adds duty to repair beyond warranty, +12 month guarantee extension.
- **Nationaal Reparateursregister:** launched 20 Mar 2025, 300+ vetted repairers.
- **Reparatiebonus:** does **not** exist in NL yet. Austria reimburses 50% up to €200; France's Bonus Réparation runs at €62M/yr. EUR + Consumentenbond lobbying.
- ~1.2M NL households below social minimum can't afford a €80 vacuum repair.
- Sources: [NOS 15 jr Repair Café](https://nos.nl/artikel/2541164-repair-cafes-bestaan-15-jaar-fabrikanten-maken-repareren-nog-te-moeilijk) · [EU Dir 2024/1799](https://eur-lex.europa.eu/eli/dir/2024/1799/oj/eng) · [Reparateursregister](https://www.nationaalreparateursregister.nl/) · [EUR: VAT not enough](https://www.eur.nl/en/news/why-vat-reduction-repairs-not-solution)

**Pitch — RepairWijzer:** photo your kapotte apparaat → Claude vision IDs make/model + likely fault from voice symptoms (Arabic/Tigrinya/Turkish via Reson8) → nearest Reparateursregister entry + Repair Café slot + B1 repair-vs-replace cost/CO2 verdict + pre-filled application for the future reparatiebonus.

---

## 3. Second-hand & Stadspas

- **BKN Monitor 2023:** 150 kt collected, 10M+ products reused. Het Goed: 31 stores, 1,973 employees, **982 on Wsw/participation contracts** (the sector is itself a labour-inclusion engine). 24 kringloops in Amsterdam.
- **Stadspas Amsterdam (~245k holders):** 25% off De Lokatie (max €50, 3×/wk) · all RataPlan locations · 40% off ~38 clothing repair shops · 40% shoe/bag repair (since 1 Aug 2024).
- Broken: discount network is a static list; no "near me," no item-level inventory, Dutch only. Kringloops don't share inventory digitally — finding a winter coat size 42 means visiting 5 stores.
- Sources: [BKN Monitor](https://www.kringloopnederland.nl/bestanden/bkn-monitor-2023.pdf) · [Stadspas De Lokatie](https://www.amsterdam.nl/stadspas/stadspasacties/lokatie-kringloopwinkel/) · [Alle kringloops Amsterdam](https://amorpha.nl/alle-kringloopwinkels-amsterdam/)

**Pitch — KringloopRadar:** kringloop staff snap shelf photo → Claude tags item/size/condition/category in 9 languages → Stadspas-houder asks "winterjas maat 42 onder €15" via Reson8 in own language → routed list with discount pre-applied. Solvimon = checkout.

---

## 4. Food rescue & voedselbank

- **Voedselbanken NL 2024:** 144,750 people, 32,558 households/wk, 180 lokale voedselbanken. Redistribute only **1–2% of food that would otherwise be wasted**. Counter-intuitive: less supermarket waste = less inflow.
- **Sector waste split (2,350 kt total, 134 kg/cap):** huishoudens **55%** · verwerkers 18% · landbouw 11% · horeca 9% · supermarkets **only 7%** (0.92% of volume).
- **Too Good To Go NL:** ~4M users, 22M meals saved.
- **Instock:** restaurants closed 2024, pivoted to **InstockMarket** B2B catering wholesale of rescue food.
- Sources: [Voedselbanken jaarcijfers](https://voedselbankennederland.nl/voedselbanken-nederland-publiceert-jaarcijfers/) · [CBS schakel armoede/verspilling](https://www.cbs.nl/nl-nl/corporate/2025/08/voedselbanken-schakel-tussen-armoede-en-verspilling) · [Monitor Voedselverspilling 2025](https://www.tweedekamer.nl/downloads/document?id=2025D06881)

**Pitch — Halal Surplus Match:** voedselbank scans incoming pallet → Claude vision = SKU + ingredients + halal/kosher/lactose/allergen flags from packaging photo. Reson8 voice intake "geen varkensvlees, baby 8 maanden" → personalized box composition. Reads non-EU labels.

---

## 5. Statushouder furnishing — the biggest fresh opportunity

- **Inrichtingskrediet:** one-time loan when statushouder leaves AZC for social housing, typically **€3–6k**, paid in cash/in-kind. Most recipients buy at IKEA/Action because they don't know kringloops exist.
- **Circular alternatives in silos:** Leger des Heils ReShare (~23M kg textiles/yr, ReshareStore Amsterdam, full house clearances) · Snuffelmug × Spaarne Werkt 2022–2024 pilot (fully reused furnishing + 5–10 jobs/project) · Buurman & Buurman, Retoertje, Present Den Haag, JIT.
- NL housing taakstelling: ~25–30k statushouders/year across gemeenten.
- Broken: 4-week window to furnish a home in a new language; 6+ disconnected circular options.
- Sources: [RefugeeHelp inrichting](https://www.refugeehelp.nl/nl/status-holder/article/100002-dit-moet-je-weten-als-je-van-de-gemeente-een-woning-krijgt-en-je-het-huis-wilt-inrichten) · [Divosa inrichtingskrediet](https://www.divosa.nl/publicaties/handreiking-financieel-ontzorgen-en-financiele-zelfredzaamheid/het-technisch-proces-van-financieel-ontzorgen/op-welke-manier-zet-je-het-inrichtingskrediet) · [Retoertje](https://www.retoertje.nl/blogs/tipseninspiratie/woningen-inrichten-statushouders-betaalbaar-snel/) · [ReshareStore Amsterdam](https://www.legerdesheils.nl/locatie/leger-des-heils-resharestore-amsterdam) · [Ombudsman: statushouders in de knel](https://www.nationaleombudsman.nl/nieuws/column/2022/statushouders-in-de-knel)

**Pitch — InrichtingsBuddy:** statushouder uploads AZC housing assignment letter → Claude (document understanding) parses postcode + bedroom count + family size → generates furniture shopping list → matches each item against ReShare/De Lokatie/Buurman/Marktplaats inventory in their L1 with ETA + Stadspas discount. Solvimon = single-cart checkout across vendors. Reson8 = voice in own language.

---

## 6. Construction & demolition

- **Houtbouw Pact MRA 2025–2030** (signed 20 Nov 2025): 32 MRA gemeenten commit to 20% timber/bio-based new homes; ~3,000 timber homes/yr. HAUT timber tower banked 1,800t CO2.
- **Madaster + Cirkelstad + Dexes** won the €750k MRA datamarkt prijs jointly. Insert + BAM Circular Building Platform = active reuse marketplaces.
- **Buurman:** circular bouwmarkt — Rotterdam, Utrecht, Antwerpen, Nijmegen, Arnhem, Amsterdam.
- Broken: Madaster/Insert are enterprise-grade. A particulier renovating can't query "4 m² oak floorboards near 1015XK."
- Sources: [Houtbouw Pact](https://builtbn.org/knowledge/resources/covenant-timber-construction-mra-2021-2025/) · [Madaster](https://madaster.nl/en/) · [Cirkelstad/BAM](https://www.cirkelstad.nl/inspiratie/bams-circular-building-%C2%ADplatform-marktplaats-voor-hergebruik-in-de-bouw/) · [Buurman](https://buurman.org/)

**Pitch — BuurtBouwmarkt:** DIY user photographs kapotte deur/plint/raamkozijn → Claude vision = type + material + dimensions → query Buurman + Insert + Madopt + Marktplaats → ranked by distance + Stadspas eligibility + sloop-vs-buy CO2 receipt for the gemeente Monitor.

---

## 7. Tool libraries

- **Peerby** (2011): NL's largest peer sharing platform.
- **Blauwe Duim** (Staatsliedenbuurt): long-running Bibliotheek voor Voorwerpen, paper member ledger.
- No Amsterdam-wide directory of "Bibliotheek voor Voorwerpen" pilots.

**Pitch — NonprofitLeen:** voedselbank/buurthuis/school says "I need a ladder Saturday" via Reson8 → Claude routes to Peerby + Blauwe Duim + Repair Café tool drawer + similar non-profit; auto-generates Dutch loan-receipt PDF; Solvimon handles deposit; reservation booked. boxd microVMs = per-org sandbox.

---

## 8. Textile + UPV

- **UPV Textiel** (Stb. 2023/132, in force 1 Jul 2023): producers responsible for collection/recycling/reuse. Targets escalate **50% by 2025 → 75% by 2030** (25% domestic reuse). 305 kt/yr placed on NL market.
- Sympany + ReShare are the two big collectors; flows are disconnected.
- Sources: [Sympany UPV](https://www.sympany.nl/nieuws/besluit-upv-textiel-opsomming/) · [ILT UPV textiel](https://www.ilent.nl/onderwerpen/producentenverantwoordelijkheid/upv-textiel)

**Pitch — TextielTracer:** photograph a label → Claude reads multilingual material composition + brand → fibre + recyclability + UPV producer → suggests donate (ReShare) / dropbin (Sympany) / repair (Stadspas tailor) / resell (Vinted). Auto-generates the brand's UPV reporting line.

---

## 9. E-waste × digital inclusion

- **Stichting Leergeld 2024:** **185,817 children supported** (up from 181,717). 37,000+ kids got a bike. Laptops standard.
- **Digidromen + HP + Aces Direct:** ~2,400 children/yr get full refurbished Win11 setup.
- **Stichting Allemaal Digitaal:** Rijksoverheid donates afgeschreven laptops.
- **Closing The Loop** (2012): 1-for-1 — every refurb phone sold in NL = one waste phone retrieved from Cameroon/Malawi/Nigeria/Uganda/SA. Crossed 1M phones.
- Broken: Leergeld + Digidromen + municipal regelingen = 3+ application paths in Dutch with paper/PDF forms.
- Sources: [Leergeld](https://www.leergeld.nl/) · [Digidromen](https://www.digidromen.nl/) · [iBestuur: Rijk geeft laptops](https://ibestuur.nl/artikel/rijk-geeft-afgeschreven-laptops-aan-mensen-in-armoede/) · [Allemaal Digitaal 2025](https://www.allemaal-digitaal.nl/de-impact-van-allemaal-digitaal-in-2025/)

**Pitch — LeergeldExpress:** parent uploads inkomensverklaring / Stadspas / school enrolment letter (any photo, any language) → Claude parses entitlement, fills Leergeld + Digidromen forms, matches family to nearest refurbisher's stock with right L1 keyboard + screenreader pre-imaged. Reson8 explains next steps in Arabic/Ukrainian/Tigrinya.

---

## 10. Recent policy hooks

| Event | Date | Hackathon angle |
|---|---|---|
| EU Right to Repair 2024/1799 | 30 Jul 2024 | NL transposition due 31 Jul 2026 |
| Nationaal Reparateursregister | 20 Mar 2025 | NL anchor for EU Repair Platform |
| UPV Textiel | 1 Jul 2023 (75% by 2030) | Producer reporting now mandatory |
| Houtbouw Pact MRA 2025–2030 | 20 Nov 2025 | 20% timber, ~3,000 homes/yr |
| Voortgangsrapportage Uitvoeringsagenda CE | 2025 | 60% of 110 activities started |
| Voedselbank dilemma (less waste = less inflow) | Aug 2025 CBS | Real, fresh narrative |
| Stadspas: schoenreparatie + tassen toegevoegd | 1 Aug 2024 | Repair access broadened |

---

## Scoring against the 5 jury criteria

Same scale as `research.md`. Innov · Local · Tech · Impact · Pitch.

| Idea | Innov | Local | Tech | Impact | Pitch | **Total** |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **InrichtingsBuddy** (statushouder furnishing) | 4 | 5 | 5 | 5 | 5 | **24** |
| **Halal Surplus Match** (voedselbank) | 4 | 5 | 4 | 5 | 5 | **23** |
| **LeergeldExpress** (laptops for poor kids) | 3 | 5 | 5 | 5 | 5 | **23** |
| **Buurt-Circulair** (citizen dashboard) | 5 | 5 | 4 | 3 | 4 | **21** |
| **KringloopRadar** (Stadspas + kringloop) | 3 | 5 | 4 | 4 | 4 | **20** |
| **RepairWijzer** (repair access) | 4 | 4 | 4 | 3 | 4 | **19** |
| **BuurtBouwmarkt** (DIY construction reuse) | 3 | 4 | 4 | 3 | 3 | **17** |
| **NonprofitLeen** (tool library) | 3 | 4 | 4 | 3 | 3 | **17** |
| **TextielTracer** (UPV textile) | 3 | 4 | 4 | 3 | 3 | **17** |

**Cross-list comparison vs. the access ideas in `research.md`:**

| Idea | Total |
|---|:--:|
| Toeslagen Dossier Reconstructor (access) | **25** |
| **InrichtingsBuddy** (circular) | **24** |
| Halal Surplus Match (circular) | 23 |
| LeergeldExpress (circular) | 23 |
| OBA Co-pilot (access) | 22 |
| 112-Tekstbrug (access) | 22 |
| Casework Co-pilot (access) | 22 |

The circular pivot does **not** cost you. InrichtingsBuddy is the second-best idea on the whole menu, behind only the Toeslagen Reconstructor — and arguably has a more pleasant demo arc (statushouder gets a home vs. parent reconstructs a trauma dossier).

---

## Technical implementation — how to make this load-bearing on Claude

### Model routing (saves credits + latency)

- **Claude Sonnet 4.6** for: orchestration, marketplace queries, multilingual chat turns, simple form fills. Cheap, fast.
- **Claude Opus 4.7** for: parsing the Dutch government letter (AZC plaatsingsbrief, inkomensverklaring), the high-stakes one-shot. Worth the cost on one or two calls per session.
- **Prompt caching:** cache the system prompt + the marketplace inventory snapshot. With 1k–10k items in context it's a 10× cost saver.

### Vision (the moat for InrichtingsBuddy / Halal / KringloopRadar)

- Use Claude vision for label/object/letter classification — don't reach for a separate CV pipeline.
- Real-world photos in poor lighting break naive prompts. Test with **synthetic + 10 real samples Saturday morning** before the demo locks.
- For products: ask Claude to return *structured JSON* (name, category, size, condition 1–5, language of label, allergens). Validate with a JSON schema; retry once on parse failure.
- For government letters: redact BSN/personal data with a regex pass **before** sending to the model. Show this redaction on stage — judges will ask about privacy.

### Multilingual (the moat for everything)

- Don't just translate UI strings — verify with native speakers at the venue. Tigrinya, Twi, Dari are the long tail Google Translate gets wrong.
- Persist user language preference per session.
- Reson8 (Dutch ASR) earns goodwill from the NL judges — but check if it handles Dutch *with an accent* (statushouder use case). If not, run pure-Claude ASR for non-Dutch input and Reson8 for Dutch staff input.

### Document understanding

- Inrichtingskrediet besluit, AZC plaatsingsbrief, inkomensverklaring, Stadspas → all PDFs with predictable structure.
- Use Opus 4.7 with the PDF as input + a structured-output prompt. Demo: "watch this 800-line C1 Dutch besluit become a 3-line plan in Arabic in 8 seconds."
- Long-context (1M) means you can stuff the *full* gemeente regelingen catalogue + the user's letter together and ask "which regelingen apply to this household?" — exactly what humans do at the Buurtteam.

### Marketplace data — the inventory problem

- **Nobody publishes kringloop inventory.** ReShare, Marktplaats, De Lokatie all have closed catalogs.
- Realistic 24-hour move: build a **fixture set** (50–200 items per source, hand-scraped or synthetic) and design the API contract a real partner *would* expose. Don't oversell as "live" on stage — say "we have a working contract; integration is a 1-day partner conversation."
- Marktplaats has a documented API; you can pull a small slice live to make one of the four marketplaces real.

### Solvimon

- Genuinely useful for circular ideas: a furniture cart that crosses 4 vendors, or a donation top-up on a voedselbank box, or a Stadspas-discount checkout. Set up the donation/checkout flow on Saturday morning so it's not a Sunday-12:00 panic.
- For non-profits, "donate the difference" between IKEA and ReShare is a powerful demo moment.

### Framer (the Pixel Perfect prize, €1k credits/member)

- Worth 30 minutes of your team's design time. The Pixel Perfect prize is genuinely winnable for circular ideas because the user is low-literacy/non-Dutch — accessibility is the design.
- Large fonts, RTL support, voice-first surface, picture-based navigation. Avoid Material Design defaults — they'll look like every other team.

### boxd

- Useful only if you have **multi-tenant** logic (per-NGO sandboxes for NonprofitLeen, per-voedselbank for Halal). Otherwise skip it; one VPS is fine.

### What to fake vs. build (for InrichtingsBuddy specifically)

| Component | Build for real | Fake / fixture |
|---|---|---|
| AZC letter parsing | ✅ real Opus call | use 2–3 redacted sample letters |
| Furniture list generation | ✅ real Sonnet call | — |
| ReShare inventory query | ✅ HTTP wrapper | seeded fixture (50 items) |
| Marktplaats inventory | ✅ live API slice | — |
| De Lokatie / Buurman | ❌ | fixture (no public API) |
| Multilingual UI | ✅ real i18n | — |
| Stadspas discount eligibility | ❌ | rule-based mock |
| Cross-vendor checkout (Solvimon) | ✅ real Solvimon test env | single mock vendor |
| Reson8 voice in Arabic | ✅ if it works for non-Dutch; else Claude ASR | — |

---

## Recommendation

**If you're keeping the access lens: stay on Toeslagen Reconstructor (25/25).**

**If you want the circular framing: go InrichtingsBuddy (24/25).** It's the one circular idea that doesn't sacrifice on Build Local fit, and the demo arc is unbeatable: a Syrian family lands in social housing on Saturday morning, by Sunday 12:00 they have a fully circular furnished home routed through ReShare + De Lokatie + Marktplaats, in Arabic, with their Stadspas discount applied, paid in one Solvimon checkout against their inrichtingskrediet.

**Backup circular pick: Halal Surplus Match (23/25).** Easier scope, more visceral demo (you can literally bring a pallet of food on stage), and Voedselbank Amsterdam is reachable Saturday morning.

**Avoid in circular:** BuurtBouwmarkt, NonprofitLeen, TextielTracer — all score 17 and lack a sympathetic protagonist in the demo.

**Hybrid play (interesting):** InrichtingsBuddy + Halal Surplus Match share 80% of the architecture (multilingual voice + vision + multi-source matching + Solvimon checkout). You could legitimately build one platform with two demos and pitch "the access layer for Amsterdam's circular safety net." That positioning would be unique against 100 competitors.
