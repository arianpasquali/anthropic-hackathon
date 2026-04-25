# Sociaal Raadslieden Amsterdam — Use Cases

10 concrete, realistic client scenarios ranked by impact, size, urgency, and AI feasibility (1–5 each).

**Context:** Sociaal Raadslieden operate from 39 buurtteam locations across Amsterdam. Free walk-in service, no appointment. Serve residents earning under ~€32,000/yr. Core work: explain government letters, help draft bezwaarschriften, check eligibility for unclaimed benefits.

---

## Ranked Use Cases

| # | Use Case | Impact | Size | Urgency | Feasibility | Total |
|---|----------|:------:|:----:|:-------:|:-----------:|:-----:|
| 1 | Terugvordering huurtoeslag | 5 | 5 | 5 | 5 | **20** |
| 2 | DUO inburgeringslening statushouder | 5 | 3 | 5 | 5 | **18** |
| 3 | Bijstand maatregel bezwaar | 4 | 4 | 5 | 4 | **17** |
| 4 | CAK bestuursrechtelijke premie | 4 | 4 | 4 | 4 | **16** |
| 5 | Huurverhoging bezwaar corporatie | 3 | 4 | 5 | 4 | **16** |
| 6 | Belastingaangifte gecorrigeerde aanslag | 4 | 4 | 4 | 4 | **16** |
| 7 | Bijzondere bijstand ontdekken | 3 | 5 | 2 | 5 | **15** |
| 8 | AIO-toeslag SVB niet-gebruik | 5 | 3 | 3 | 4 | **15** |
| 9 | WW-weigering flex/ZZP | 4 | 3 | 4 | 3 | **14** |
| 10 | WMO-aanvraag thuiszorg | 4 | 3 | 2 | 3 | **12** |

---

## Detailed Scenarios

### 1. Terugvordering huurtoeslag — Score: 20

**Scenario:** Client (60, Moroccan-Dutch, Nieuw-West) brings a Belastingdienst letter demanding €4,200 back in huurtoeslag overpayment. Adult child registered at their address triggered automatic income recalculation. Client doesn't understand why, doesn't know they have 6 weeks to object.

**What AI does:** Read letter → explain the reason for reclaim in plain language → flag 6-week bezwaar deadline → explain grounds for appeal → connect to Sociaal Raadslied for drafting.

**Why top score:** Very high financial stakes, extremely common case type (income/household changes are constant), hard deadline creates urgency, letter explanation + deadline alert is well within AI capability.

---

### 2. DUO inburgeringslening statushouder — Score: 18

**Scenario:** Client (29, Syrian refugee) just passed inburgeringsexamen after 3 years. Receives DUO bill for €10,000 for the inburgeringscursus. Arrives in panic — doesn't know the debt is automatically kwijtgescholden (forgiven) upon passing the exam.

**What AI does:** Read DUO letter → identify it as inburgeringslening → explain the kwijtschelding rule → confirm no payment needed → explain how to verify status via DUO MijnDUO.

**Why high score:** Huge financial relief for one of the most vulnerable groups; the answer is clear and unambiguous (rule is binary: passed = forgiven); prevents unnecessary panic payments.

---

### 3. Bijstand maatregel bezwaar — Score: 17

**Scenario:** Client (42, single mother) had bijstand cut 20% for 3 months because she missed a DWI afspraak when her phone broke. Brings maatregel besluitbrief. Needs to understand the decision and whether it can be contested.

**What AI does:** Read maatregel letter → explain what a maatregel is and why it was imposed → explain right to bezwaar within 6 weeks → explain what constitutes dringende reden (grounds for reversal) → connect to Raadslied for drafting.

**Why high score:** Direct income loss, clear time pressure, happens constantly in bijstand population, AI can explain options even if drafting requires human.

---

### 4. CAK bestuursrechtelijke premie — Score: 16

**Scenario:** Client (51, bijstand) stopped paying zorgverzekering 8 months ago. CAK now deducts 130% premium directly from his uitkering. His income suddenly dropped. Brings CAK letter confused about why his uitkering is lower.

**What AI does:** Read CAK letter → explain bestuursrechtelijke premie route → explain how to exit (pay arrears + take out regular policy + request CAK termination) → calculate the cost difference → connect to Sociaal Raadslied.

**Why high score:** Ongoing financial harm every month, very common in bijstand population, well-defined process to resolve.

---

### 5. Huurverhoging bezwaar corporatie — Score: 16

**Scenario:** Client (67, Turkish-Dutch, Oost) receives huurverhogingsvoorstel from Ymere raising rent 10%. Doesn't know she can object via Huurcommissie within 6 weeks. Brings the letter.

**What AI does:** Read verhogingsbrief → explain legal max rent increase → check whether increase exceeds legal cap → explain Huurcommissie bezwaar procedure → flag 6-week deadline → provide Huurcommissie contact.

**Why high score:** Time-critical (6-week window), common among social housing tenants, AI can do the legal cap check directly.

---

### 6. Belastingaangifte gecorrigeerde aanslag — Score: 16

**Scenario:** Client (44, Surinamese-Dutch, Zuidoost) receives correctiebrief from Belastingdienst claiming €1,800 owed in inkomstenbelasting because a bijbaan wasn't declared. Doesn't know if it's correct or what to do.

**What AI does:** Read correctiebrief → explain what triggered the correction → explain how to verify using jaaropgave → explain bezwaar route if incorrect → flag 6-week deadline.

**Why high score:** Large financial claim, high anxiety moment, common pattern, AI can explain the logic even if verification requires document review.

---

### 7. Bijzondere bijstand ontdekken — Score: 15

**Scenario:** Client (35, working poor) needs €400 for glasses and €200 for school supplies for children. Has never heard of bijzondere bijstand. Comes to Raadslied for general money advice.

**What AI does:** During intake conversation → identify likely eligibility → explain bijzondere bijstand → explain what costs are covered → explain that DWI application is needed → pre-fill eligibility questions.

**Why notable:** Massive non-take-up problem (estimated 20–40% of eligible families don't claim). AI proactively surfacing this during any conversation is high-leverage. Urgency is low because no deadline, but size is enormous.

---

### 8. AIO-toeslag SVB niet-gebruik — Score: 15

**Scenario:** Client (72, Moroccan-born, late migration to NL) receives AOW of €400/month — far below bijstandsnorm for elderly (€1,100+). Has never worked in NL before age 45 so AOW is partial. Doesn't know AIO supplement exists.

**What AI does:** Ask basic questions about age, AOW amount, household → identify likely AIO eligibility → explain SVB AIO supplement → calculate approximate top-up → connect to SVB application.

**Why notable:** Ongoing monthly income boost, extremely underused by elderly migrants, clear eligibility rule. The payoff is permanent and large.

---

### 9. WW-weigering flex/ZZP — Score: 14

**Scenario:** Client (38) worked on a flex contract, applied for WW, was denied because UWV counted freelance side income as ZZP activity. Brings UWV besluit and payslips.

**What AI does:** Read UWV besluit → explain the wekeneis and urensystematiek → explain why ZZP income affected the claim → explain whether bezwaar is viable → flag deadline.

**Why lower score:** More complex eligibility reasoning, requires income document analysis, higher chance of AI error on edge cases.

---

### 10. WMO-aanvraag thuiszorg — Score: 12

**Scenario:** Client (55, ill, limited mobility) doesn't know home care or huishoudelijke hulp can be arranged via WMO. Daughter has been doing everything. Raadslied initiates WMO-aanvraag.

**What AI does:** Explain WMO, what it covers, how to apply via gemeente loket, what the eigen bijdrage (CAK) looks like.

**Why lower score:** Less urgent (no letter/deadline), more assessment-based (gemeente decides per case), lower feasibility for AI to go beyond information provision.

---

## Key Observations for Product Design

**Best demo scenario:** Use case #2 (DUO inburgeringslening). Client arrives in panic over €10K bill. AI reads letter, explains in Arabic/Turkish, delivers instant relief: "this debt is automatically forgiven because you passed." Emotionally powerful, factually unambiguous, demonstrates multilingual + OCR + eligibility check in one flow.

**Most impactful at scale:** Use case #7 (bijzondere bijstand). Not a letter-reading task but a proactive eligibility discovery during any conversation. Surfacing this for the thousands of people who don't know it exists has compounding impact.

**Common pattern across all cases:** Every scenario has a **deadline** (6-week bezwaar window) that clients miss because they don't understand the letter. Deadline detection + plain-language deadline explanation is a high-value feature in every case.
