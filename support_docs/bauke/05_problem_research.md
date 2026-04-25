# Problem Research: Underprivileged People in the Netherlands / Amsterdam

Research gathered via parallel web-search agents, April 2026.

---

## Hackathon Context

**Event:** Whale x Anthropic: Claude Code Hackathon — April 25–26, Codam College Amsterdam
**Theme:** Build Local — products for people/sectors with less access or at risk of being left behind
**Target:** minorities, non-profits, municipalities, emergency services

### Jury & What They Care About

| Judge | Role | Lens |
|---|---|---|
| Adriaan Mol | Founder, Mollie (payments/fintech) | Business model, scale, monetization path |
| Duco van Lanschot | Founder, Duna | Product execution, founder credibility |
| Clare Jones | CEO, Polarsteps (consumer travel app) | UX quality, consumer product feel, retention |
| Ruben Timmermans | Co-founder, School of Moral Ambition | Genuine societal impact, ethical grounding |
| Jacqueline van den Ende (host) | Founder, Carbon Equity (impact investing) | Real-world viability, sustainability, measurable impact |

### Prize Categories = Judging Criteria

| Prize | Criterion | Reward |
|---|---|---|
| Launch Ready | Best overall product, idea & execution | Mac Mini + €10K Anthropic credits |
| Built Different | Best technical build | Raspberry Pi 5 + €5K Anthropic credits |
| Mic Drop Moment | Best innovation & storytelling | DJI Mic Mini + €5K Anthropic credits |
| Pixel Perfect | Best UI/UX | €1K Framer credits/person |
| Real Ones | Best real-world viability (impact + business model) | €500 cash |
| Whale's Favourite | TBA | TBA |

### Strategic Implications

- **Adriaan Mol (Mollie)** will push on: can this make money or sustain itself? Who pays? Gemeente? NGO grants? Freemium?
- **Ruben Timmermans (Moral Ambition)** will push on: is the impact real and verifiable? Are you actually reaching the people you claim to help?
- **Clare Jones (Polarsteps)** will push on: is the UX actually usable by non-tech users? Does it feel like a real product?
- **Real Ones prize** is perfectly aligned with the recommended concept — municipality/NGO licensing model for a benefits navigator is a credible business model

### Contributors (potential integration angles)

- **Framer** — rapid frontend prototyping (good for Pixel Perfect prize)
- **Duna** — Duco van Lanschot's company; building here could get direct founder attention
- **Solvimon, Ingen Housz, Creatormate, Reson8** — sponsor companies; showing integration could score points

---

---

## Problem Summary Table

| # | Problem | Impact | Size | Urgency | Feasibility | Total | AI/Hack Fit | Key Stat |
|---|---------|:------:|:----:|:-------:|:-----------:|:-----:|:-----------:|---------|
| 1 | Toeslagen bureaucracy | 5 | 5 | 4 | 4 | **18** | ⭐⭐⭐⭐⭐ | 10–30% non-take-up; ~€20B system |
| 2 | Housing crisis | 5 | 5 | 5 | 2 | **17** | ⭐ | 12–13yr Amsterdam waitlist |
| 3 | Digital exclusion | 4 | 4 | 4 | 5 | **17** | ⭐⭐⭐ | 4.5M adults lack digital skills |
| 4 | Language barrier | 4 | 4 | 4 | 4 | **16** | ⭐⭐⭐⭐⭐ | 500K+ can't function in Dutch daily |
| 5 | Debt spiral | 5 | 4 | 5 | 3 | **17** | ⭐⭐⭐⭐ | 5–7yr avg before seeking help |
| 6 | Healthcare access | 4 | 3 | 4 | 3 | **14** | ⭐⭐⭐ | 200–250K uninsured; 6–18mo GGZ wait |
| 7 | Child poverty | 4 | 3 | 4 | 3 | **14** | ⭐⭐ | 1 in 10 children; 15–20% in AMS Zuidoost |
| 8 | Employment discrimination | 3 | 4 | 3 | 3 | **13** | ⭐⭐ | 30–50% fewer callbacks for ethnic minorities |

**Recommended build:** Problems 1 + 4 + 3 combined — multilingual government document assistant with eligibility checker. No DigiD required to start.

---

## 1. Benefits / Toeslagen Bureaucracy

**Impact: 5 | Size: 5 | Urgency: 4 | Feasibility: 4 | Total: 18**

### Scale
- ~8 million households receive toeslagen annually; total outlay €20B+
- Non-take-up: 10–30% of eligible households fail to claim one or more benefits
- Amsterdam: ~180,000 residents below/near poverty line (~22% of households); millions in benefits left unclaimed annually
- Toeslagenschandaal: 35,000+ families wrongly accused of fraud; parliamentary inquiry concluded Feb 2024; compensation ongoing

### Root Causes
- Each benefit has separate eligibility rules, income thresholds, recalculation rules
- Changes in income/household must be reported in near-real-time or create debt (terugvordering)
- Forms and MijnToeslagen portal Dutch-only
- System almost entirely online (DigiD); 2.5M Dutch adults digitally illiterate
- Post-scandal fear and distrust of Belastingdienst driving active avoidance of claiming
- National toeslagen separate from municipal benefits — multiple agencies

### Existing Solutions
- Stelselherziening (system overhaul) in progress; full replacement not before 2028–2030
- Amsterdam "Vroeg erop af" proactive outreach programs
- Sociaal Raadslieden (~30 for hundreds of thousands of potential clients in Amsterdam)
- Humanitas, Buurtteams, Nibud guidance

### Gaps
- No automated eligibility-checking tool in plain language / multiple languages
- Outreach massively underfunded relative to need
- No multilingual digital assistance in official system
- Terugvordering risk remains structural — creates rational disincentive to claim
- Post-scandal trust deficit not addressed beyond compensation payouts

---

## 2. Housing Crisis (Amsterdam)

**Impact: 5 | Size: 5 | Urgency: 5 | Feasibility: 2 | Total: 17**

### Scale
- Average social housing wait in Amsterdam: **12–13 years** (national avg 7 years)
- 100,000+ households registered on Woningnet waiting list (Amsterdam region)
- ~30,600–33,000 homeless people nationally (CBS 2022–2023); disproportionately concentrated in Amsterdam
- Average private rent Amsterdam: €1,500–1,800/month
- Social housing tenants spend ~31% of income on housing; those in private market often 40–50%+
- Rents rose 5.4% YoY in 2024 — steepest increase since 1993

### Who Is Most Affected
- **Migrants/statushouders**: 70% of homeless in G4 cities are non-European born vs 48% elsewhere
- **Youth (18–27)**: no priority in traditional time-based system; starters disadvantaged structurally
- **Low-income households**: social housing income-capped (~€47,000/year) but demand vastly outstrips supply
- Single-parent families, people with mental health issues, ex-offenders overrepresented in homelessness

### Root Causes
- Decades of undersupply — construction far below demand targets
- Post-2022 material/financing costs slowing new builds further
- Liberalization of rental market shrank social stock and inflated private rents
- Population growth (Amsterdam past 900,000; metro ~1.4M)
- Financialized private rental market — investors outprice residents
- Asylum seeker processing backlogs block social housing allocation

### Existing Solutions
- **Woonpunten system (2023)**: points-based allocation replaced pure time-based waiting; more homes now to starters/young people
- Amsterdam target: 5,000–7,500 homes/year through 2030, 40% social
- Urgency programs: statushouders, care-leavers, domestic violence victims, people exiting detention
- Housing corps (Ymere, De Key, Rochdale, Stadgenoot): manage ~230,000 social homes
- HVO-Querido, Leger des Heils: emergency shelter and transitional housing
- Wet betaalbare huur (2024): new national private rent regulation

### Gaps
- Middle segment trapped: households earning €47,000–70,000 priced out of private, excluded from social
- Build rates consistently miss targets (cost, NIMBYism, planning delays)
- Status holder backlog: municipalities routinely miss legal placement deadlines despite urgency status
- Mental health + housing integration insufficient: complex-needs people cycle between shelters and streets
- Points system still requires formal registration — undocumented migrants and working poor in informal housing excluded
- Wet betaalbare huur enforcement slow; many landlords circumvent it

---

## 3. Digital Exclusion

**Impact: 4 | Size: 4 | Urgency: 4 | Feasibility: 5 | Total: 17**

### Scale
- ~4.5–5M Dutch adults (25–30%) lack sufficient digital skills for government services
- ~2.5M are functionally illiterate
- ~40% of 75+ face serious digital difficulty
- ~6% of households lack home internet
- DigiD active users: ~17M (out of 17.9M population) — but many only nominally active

### Who Is Most Affected
- Elderly (65+): largest group
- Low-literacy adults (~2.5M)
- Non-western migrants and asylum seekers (language + system unfamiliarity + BSN required for DigiD)
- Undocumented people: fully excluded (no BSN = no DigiD = no access to any government service)
- Low-income households (device/connectivity barriers)

### Root Causes
- Mandatory digitization of government services without adequate offline fallback
- DigiD app now requires smartphone with NFC — excludes elderly and low-income
- Complex bureaucratic language in forms
- No identity verification path for migrants without BSN
- Rapid digital-only rollout outpacing support infrastructure

### Existing Solutions
- Digisterker: ~40,000 participants/year (vs millions excluded)
- 166+ library DigiHulp desks
- Humanitas / Buurtteams volunteer home support
- Informatiepunt Digitale Overheid (IDO) at libraries (rolled out 2022–2023)
- Some municipalities offer phone-based service lanes as fallback

### Gaps
- Programs reach tens of thousands; excluded population is millions
- One-time training doesn't keep up with constantly changing portals
- Legal obligation for non-digital access exists but inconsistently enforced
- Migrants and undocumented fully outside all programs requiring BSN
- Rural/mobility-limited people can't reach library-based support
- No good DigiD alternative for those without NFC smartphones

---

## 4. Language Barriers

**Impact: 4 | Size: 4 | Urgency: 4 | Feasibility: 4 | Total: 16**

### Scale
- ~2.5M people in NL have low literacy including limited Dutch proficiency (~1 in 9 adults)
- Amsterdam: ~57% of population non-Dutch born or second generation
- 500,000+ people cannot adequately function in Dutch in daily life

### Who Is Most Affected
- First-generation labor/family migrants (Moroccan, Turkish, Surinamese, Ghanaian communities)
- Recent asylum seekers
- Elderly migrants who never received formal Dutch education
- Family migrants who must self-finance integration courses

### Impact on Access
- **Healthcare**: Migrants more likely to be admitted to and die in hospital; prenatal screening info omitted due to language barriers; elderly migrants can't follow written medical instructions
- **Employment**: Language proficiency single largest predictor of labor market integration
- **Government services**: Benefits, legal rights, housing applications require Dutch literacy — errors lead to loss of entitlements
- **Legal vulnerability**: Dependence on intermediaries increases exploitation risk

### Existing Solutions
- Wet Inburgering 2022: mandates B1 Dutch within 3 years for non-EU migrants
- 461 Taalpunten (down from 722) at library service areas
- Tel mee met Taal: ~90,000 participants by 2017, ongoing
- VluchtelingenWerk, Stichting Lezen & Schrijven, municipal social services

### Gaps
- Family migrants must self-pay for courses (€2,000–5,000) — prohibitive on low income
- B1 threshold (raised in 2022) sharply increases exam failure, especially older/low-education learners
- Taalpunten dropped 36% in capacity
- No statutory right to medical or legal interpreter in NL
- Informal workers fully excluded from employer-sponsored integration pathways

---

## 5. Debt Spiral (Schuldhulpverlening)

**Impact: 5 | Size: 4 | Urgency: 5 | Feasibility: 3 | Total: 17**

### Scale
- ~1.5M Dutch households carry problematic debt (~1 in 6)
- ~700,000–800,000 in "severe" problematic debt
- Average debt in trajectories: €35,000–€45,000 (toeslagen victims often €60,000+)
- Average years before seeking help: **5–7 years**
- Statutory intake window: 8 weeks; actual wait to start trajectory: 3–12 months

### Root Causes
- Toeslagenaffaire: wrongly imposed repayments cascaded into rent arrears, missed health insurance premiums
- High eigen risico and dental/mental health co-payments push households into medical debt
- Rising social rents + housing scarcity → rent arrears
- Energy price shocks (2022–2024)
- ZZP/freelancers: no income buffer, limited safety-net access
- Toeslagen recalculations create retroactive debt

### Existing Solutions
- Gemeentelijke schuldhulpverlening (statutory, every municipality)
- WSNP court-ordered debt restructuring (18-month, leads to clean slate)
- Nibud budgeting tools and income norms
- Humanitas thuisadministratie volunteers
- Geldfit.nl self-assessment portal
- Vroeg Signalering (since 2021): utilities/housing corps report arrears >2 months to municipalities
- GKB 0% interest debt consolidation loans

### Gaps
- Stigma: people wait 5–7 years before seeking help
- Applications require extensive documentation — impossible for low-literacy/non-Dutch speakers without help
- ZZP applicants often rejected from minnelijk traject by creditors
- Excluded groups: undocumented people, homeless, people with untreated mental health/addiction issues
- Municipal capacity shortfalls — 8-week statutory norm frequently breached
- ~30–40% recidivism within 3–5 years (no structural income improvement)
- Toeslagen victims: compensation received but third-party debts not automatically cleared

---

## 6. Healthcare Access

**Impact: 4 | Size: 3 | Urgency: 4 | Feasibility: 3 | Total: 14**

### Scale
- ~200,000–250,000 people uninsured (despite mandatory coverage)
- ~20% of Dutch residents skip/postpone care due to eigen risico; 35–40% among low-income
- GGZ wait times: 6–18 months for specialized mental health (legal norm: 14 weeks)
- Zorgtoeslag non-take-up: ~300,000–400,000 eligible people don't claim

### Most Affected
- Low-income households in the overlap zone (too much for full support, too little to cover deductibles)
- Undocumented migrants: entitled to "medically necessary" care only; MAWZ reimbursement scheme poorly known
- Homeless people: no fixed address blocks insurance registration
- People in debt restructuring: zorgtoeslag can be suspended during schuldsanering

### Existing Solutions
- Zorgtoeslag (income-based subsidy)
- CAK compulsory enrollment for uninsured + government premium billing
- MAWZ scheme for uninsured/undocumented (administrative friction deters use)
- GGD Amsterdam: free STI, TB, vaccination, outreach
- Dokters van de Wereld: free clinics for uninsured/undocumented in Amsterdam
- Gemeentelijke collectieve zorgverzekering for minima residents

### Gaps
- Eigen risico €385 = among highest mandatory deductibles in Europe
- GGZ capacity crisis — structural Treeknorm violation, no interim support
- MAWZ scheme administrative friction → providers refuse undocumented patients
- Address-dependency: GP registration, insurance, zorgtoeslag all require BRP address
- Coordination failure for complex cases (homeless + addiction + mental illness)
- 300,000–400,000 eligible people don't claim zorgtoeslag (complexity, language, distrust)

---

## 7. Child Poverty

**Impact: 4 | Size: 3 | Urgency: 4 | Feasibility: 3 | Total: 14**

### Scale
- National: ~93,000 children (2.8%) in poverty; ~245,000 (7.5%) in near-poverty — ~1 in 10 children
- Amsterdam citywide: ~10–13% child poverty rate
- Nieuw-West, Noord, Zuidoost: 15–20% (3–4x national average)
- High-risk groups: single-parent families, non-EU migration background households, long-term benefits-dependent families
- Energy/inflation crisis 2022–2023 reversed years of decline

### Impact
- Lower educational achievement, higher dropout risk, no access to tutoring/extracurriculars
- Worse nutrition, dental delays, many children lack glasses
- Social exclusion: can't afford sports clubs, school trips, birthday parties
- Intergenerational poverty transmission — high probability of remaining poor as adults

### Existing Solutions
- Kindpakket: municipal in-kind support (sports, culture, school supplies) — G4 cities all operate one
- Voedselbanken: ~170,000+ users nationally, ~50 locations in Amsterdam region
- Schoolontbijt: school breakfast programs in high-poverty schools, expanding nationally
- Jeugdfonds Sport & Cultuur: subsidizes sport/culture participation
- Schuldhulpverlening for families with debt

### Gaps
- **Non-take-up**: 20–40% of eligible families don't claim benefits — stigma, language, complexity, post-toeslagen distrust
- Fragmentation: programs spread across municipalities, charities, national gov with poor coordination
- Undocumented children entirely outside formal support
- Kindpakket is in-kind only — doesn't address structural income shortfall (rent, food, utilities)
- Stigma: visible targeting (special passes) deters use in culturally diverse communities
- Reactive, not preventive: interventions activate after poverty established

---

## 8. Employment Discrimination

**Impact: 3 | Size: 4 | Urgency: 3 | Feasibility: 3 | Total: 13**

### Scale
- Ethnic minority applicants receive 30–50% fewer callbacks despite identical CVs (audit studies)
- Non-western ethnic minority unemployment: ~3x native Dutch rate (10–12% vs 3–4%)
- Wage gap: 10–20% even after controlling for education and sector
- Amsterdam Moroccan-Dutch youth unemployment: ~20%+ vs ~8% city average

### Most Affected
- Moroccan-Dutch and Turkish-Dutch (steepest hiring discrimination in audit studies)
- Surinamese and Antillean applicants
- Asylum seekers and recently naturalized citizens (diploma recognition, language, network gaps)
- Underprivileged neighborhoods: Bijlmer, Slotervaart, Osdorp

### Existing Solutions
- Anti-Discriminatie Bureaus (ADBs) / Discriminatie.nl Amsterdam — complaint-driven, no enforcement power
- Anoniem solliciteren pilots (voluntary, very low employer uptake)
- AWGB legislation + NLA labor inspectorate
- Diversity charters, SER diversity targets for boards
- Actieplan arbeidsmarktdiscriminatie (2022): large employer self-audits

### Gaps
- ADBs underfunded, reactive, reach tiny fraction of actual discrimination
- Anoniem solliciteren: bias resurfaces at interview stage; employers resist
- Enforcement negligible — labor inspectorate rarely investigates proactively
- Self-audits are box-ticking, no independent verification
- Network hiring and implicit interview bias structurally untouched
- No mandatory hiring-outcome diversity reporting for most employers
- Intersectionality ignored (ethnic minority + low income + low education compounds disadvantage)

---

## Cross-Cutting Observations

Several problems share the same root causes and reinforce each other:

| Root Cause | Problems It Drives |
|---|---|
| Language barrier | Toeslagen non-take-up, debt spiral delay, healthcare avoidance, employment exclusion |
| Digital exclusion | Toeslagen non-take-up, zorgtoeslag non-claim, inability to access any government service |
| Address-dependency of systems | Healthcare access, schuldhulp exclusion, undocumented people excluded from everything |
| Fear / distrust of government | Toeslagen non-claim, delayed debt help |
| No statutory interpreter rights | Healthcare harm, legal vulnerability |
| Fragmented systems | Debt + healthcare + housing crisis compound each other with no single entry point |

**Highest leverage intervention point:** Something that combines proactive eligibility detection + multilingual plain-language guidance + no DigiD required to get started would hit toeslagen, debt, healthcare non-take-up, and digital exclusion simultaneously.

---

## Hackathon + AI Feasibility Evaluation

Evaluated on two axes: **hackathon buildability** (demo-able in 24h, scoped prototype) and **AI leverage** (AI genuinely load-bearing vs. decorative).

### 1. Toeslagen Bureaucracy — ⭐⭐⭐⭐⭐ Best fit

**Tech angle:** Eligibility checker + multilingual application assistant
**AI role:** Core. LLM parses complex eligibility rules, explains in plain language, translates, walks user through aanvraag step-by-step
**Demo:** User uploads a Belastingdienst letter in Turkish → AI explains what it means and what to do next
**Buildable in 24h:** Yes — chatbot + eligibility logic + multilingual = standard LLM app
**Gap it fills:** No tool like this exists; Sociaal Raadslieden massively capacity-constrained
**Risk:** Hallucinated eligibility rules could mislead → need disclaimers + rule grounding

---

### 2. Housing — ⭐ Weak fit

**Tech angle:** Limited. Core problem is supply shortage, not information gap
**AI role:** Marginal — could help navigate urgency procedures or understand rights
**Demo:** Hard to demo impact; Woningnet already exists
**Verdict:** Skip. Tech cannot fix 12-year waitlists.

---

### 3. Digital Exclusion — ⭐⭐⭐ Medium fit

**Tech angle:** Voice interface + simplified UI removing DigiD dependency for getting *information* (can't replace DigiD for actual transactions)
**AI role:** Genuine — WhatsApp/voice bot answers "hoe vraag ik huurtoeslag aan?" in multiple languages without requiring DigiD to start
**Best angle:** AI assistant for library DigiHulp volunteers — helps them help clients 5x faster
**Buildable in 24h:** Yes if scoped to info/guidance layer, not actual government integration
**Verdict:** Strongest as supporting layer combined with problems 1 or 4

---

### 4. Language Barrier — ⭐⭐⭐⭐⭐ Best fit

**Tech angle:** Bureaucratic document translator + plain-language explainer
**AI role:** Core. LLMs excel at translation + bureaucratic simplification
**Demo:** User photos a letter from gemeente/Belastingdienst → gets explanation in Arabic/Turkish/Tigrinya + next steps
**Buildable in 24h:** Yes — OCR + LLM prompt = working prototype in hours
**Gap it fills:** No such tool exists for NL government documents at this quality
**Verdict:** Strongest standalone AI use case. Naturally combines with problem 1.

---

### 5. Debt Spiral — ⭐⭐⭐⭐ Strong fit

**Tech angle:** Schuldhulp intake assistant — helps people prepare documentation/info needed to enter a trajectory
**AI role:** Strong — guided conversation maps debt situation, identifies creditors, explains what happens next, drafts budget overview
**Demo:** User describes situation in plain language → AI generates structured intake summary ready for schuldhulpverlener
**Buildable in 24h:** Yes — conversational intake form is classic LLM use case
**Gap it fills:** Schuldhulpverleners overloaded; better-prepared clients = faster processing; lowers 5–7 year shame/delay barrier
**Verdict:** High AI leverage, fills real capacity gap

---

### 6. Healthcare Access — ⭐⭐⭐ Medium fit

**Tech angle:** Rights navigator for uninsured/undocumented — explain MAWZ scheme, free clinics, what "medically necessary" means
**AI role:** Genuine but narrow — information and routing, not treatment
**Demo:** "I have no insurance and need to see a doctor" → AI explains Amsterdam-specific options
**Gap it fills:** MAWZ scheme unknown even to providers; routing to Dokters van de Wereld has real value
**Verdict:** Solid but narrower audience than problems 1/4/5

---

### 7. Child Poverty — ⭐⭐ Weak fit

**Tech angle:** Kindpakket navigator, benefits eligibility for families
**AI role:** Limited — mostly overlaps with problem 1 (toeslagen)
**Verdict:** Address as sub-feature of problem 1, not standalone

---

### 8. Employment Discrimination — ⭐⭐ Weak fit

**Tech angle:** AI bias audit tool, anonymous CV rewriter, discrimination complaint assistant
**AI role:** Possible — LLM could flag biased job postings or help draft ADB complaints
**Gap it fills:** Real, but enforcement is weak so tool impact unclear
**Verdict:** Hard to show measurable impact in hackathon context

---

## Recommended Hackathon Concept

**Build one thing that solves problems 1 + 4 + 3 together:**

> **Multilingual government document assistant** — AI that:
> 1. Reads any government letter (OCR) and explains it in plain language in your language
> 2. Checks what benefits you're entitled to based on your situation
> 3. Guides you through next steps without requiring DigiD to get started
> 4. Connects you to local help (Sociaal Raadslieden, Dokters van de Wereld, Humanitas)

**AI is genuinely load-bearing** — multilingual understanding, bureaucratic translation, eligibility reasoning are tasks where LLMs outperform any rule-based system. Demo is clear, audience is real, gap is documented.

---

## Pre-Build Considerations — Ranked

Criteria adapted for hackathon context:
- **Pre-build urgency** (1–5): must decide before writing code
- **Pitch impact** (1–5): how much addressing this improves winning chances
- **Feasibility** (1–5): addressable within 24h

| # | Consideration | Urgency | Pitch | Feasibility | Total | Action |
|---|--------------|:-------:|:-----:|:-----------:|:-----:|--------|
| 1 | **Scope — pick true MVP** | 5 | 5 | 5 | **15** | Decide before first line of code |
| 2 | **Liability model** | 4 | 5 | 5 | **14** | Bake "guide not advise, always connect to human" into product + pitch |
| 3 | **Language prioritization** | 5 | 4 | 5 | **14** | Pick 3 languages (Arabic, Turkish, Tigrinya); build demo around one |
| 4 | **User access paradox** | 4 | 5 | 4 | **13** | Frame tool as for intermediaries (DigiHulp volunteers, Humanitas) not just end-users |
| 5 | **Business model answer** | 3 | 5 | 5 | **13** | Gemeente licensing model — prepare slide, no need to build |
| 6 | **Competitor landscape** | 4 | 4 | 5 | **13** | Quick research now; know what to say when judges ask |
| 7 | **Demo moment design** | 3 | 5 | 4 | **12** | Plan early: photograph real letter on stage → Turkish explanation in 10s |
| 8 | **Data source for eligibility** | 5 | 3 | 3 | **11** | Highest technical risk; validate approach before building eligibility layer |
| 9 | **Partner validation** | 2 | 4 | 3 | **9** | Cold-contact Humanitas/Sociaal Raadslieden tonight; informal "we'd use this" = Real Ones prize |
| 10 | **GDPR** | 2 | 2 | 5 | **9** | Easy to solve: no data storage, ephemeral processing; say it once in pitch |

### MVP Decision (Consideration #1 — most critical)

Three options ranked by 24h buildability vs. pitch strength:

| Option | What it is | Builds in 24h | Pitch strength |
|--------|-----------|:-------------:|:--------------:|
| **A. Letter explainer only** | OCR → plain-language explanation + next step in user's language | Yes, comfortably | Strong — clear demo, focused story |
| **B. Letter explainer + eligibility check** | A + conversational intake to check what benefits apply | Yes, tight | Strongest — two problems solved, still demo-able |
| **C. Full platform** | B + resource finder + case management | No | Weakest — unfocused, half-finished |

**Recommendation: Option B.** Letter explainer is the hook; eligibility check is the depth judges need for Real Ones prize.

---

## Competitor Landscape

### Gap summary table

| Capability | MijnOverheid | Regelhulp | Geldfit | OpenEmbassy | Turn2us (UK) | Propel (US) | Our Concept |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Reads official letters via OCR | No | No | No | No | No | No | **Yes** |
| Plain-language explanation | No | No | No | Human only | Partial | No | **Yes** |
| Non-Dutch languages (Arabic, Turkish) | No | No | **Yes** ⚠️ | Human only | No | No | **Yes** |
| Benefit eligibility check | No | No | Partial | No | Yes (UK only) | Yes (US only) | **Yes** |
| Connects to local help orgs | No | Links only | Coaches only | Yes (human) | No | Partial | **Yes** |
| WhatsApp/voice accessible | No | No | No | Partial | No | No | **Yes** |

**Verdict: gap is real and confirmed.** No existing tool combines OCR letter comprehension + multilingual explanation + eligibility check + warm referral.

### Key existing tools (fact-checked)

**Dutch government**
- **MijnOverheid** — delivers official letters digitally; Dutch-only, no explanation, requires DigiD. Delivers the problem, doesn't solve it. ✓ Accurate.
- **Regelhulp.nl** — referral/orientation hub for care and social support (NOT an eligibility wizard — overstated). Dutch-only, no letter reading, no multilingual. Links users to local loket, doesn't determine eligibility itself. ✓ Dutch-only confirmed, ⚠️ "eligibility wizard" was an overstatement.
- **Geldfit.nl** — ⚠️ **"Dutch-only" was WRONG.** Supports 6 languages: Dutch, English, Polish, Bulgarian, Romanian, Arabic, Papiamentu. Also broader than debt — covers general financial stress, budgeting, income support, financial coaches. Still no letter reading or OCR. Update gap table accordingly.
- **Zelfredzaamheidsmeter** — primarily a professional caseworker tool, but citizen-facing variants exist in some municipalities. Dutch-only. ⚠️ "caseworker only" is incomplete — some self-service variants deployed locally.

**NGO / gemeente**
- **OpenEmbassy (Amsterdam)** — ⚠️ mischaracterised as "peer navigator." Actually a knowledge/research/policy platform with a WhatsApp/Telegram helpdesk. Lists partner apps (Tolkapp, Taaly, Welcomeapp) but doesn't build them. Multilingual (Arabic, Dutch, Ukrainian, English) ✓. No AI/OCR ✓.
- **Skendy** (not Skenky — misspelling) **(CommuniCity pilot, AMS + Prague 2025)** — AI mobile app: translates government letters and utility bills, organizes documents, sets admin deadline reminders, AI chatbot with knowledge base. "~40-user pilot" was a misread — "40 hours of co-design sessions" not 40 users. No OCR confirmed ✓. Still in pilot, not production-deployed ✓. **Most credible prior art.**
- **Formulierenbrigade (Amsterdam)** — ⚠️ name unverifiable in public sources; may be colloquial/local. In-person volunteer form-help services do exist at Amsterdam libraries (hulp bij formulieren) but specific branded programme could not be confirmed. No digital component found ✓.

**International (not in NL)**
- **Turn2us (UK)** — benefits eligibility calculator + grants search + PIP Helper + telephone advisers. English-only ✓, UK-system-specific ✓. Broader than "calculator only" — undersold in original description.
- **Propel / Fresh EBT (US)** — ⚠️ "narrow scope" significantly outdated. Now a full low-income financial platform: EBT/WIC/TANF/cash benefits, job listings, grocery deals, fraud monitoring, deposit predictions. Has launched AI-powered fraud detection. Still US-only ✓.
- **Findhelp / Aunt Bertha (US)** — ⚠️ "no eligibility" is wrong. Now includes Benefits Eligibility & Enrollment, social needs screening, closed-loop referrals, case management (Kiip platform). US-only ✓. No letter reading ✓. Much more than a directory.
- **RefuGPT (Swiss, 2025)** — real, peer-reviewed ACM paper (DOI: 10.1145/3735140). Bi-layered LLM+RAG, tested with 15 Ukrainian refugees in Switzerland. Academic proof-of-concept ✓, not production-deployed ✓. Ukraine-specific, not generic.

**Revised gap assessment:** Geldfit's Arabic/multilingual support partially overlaps our concept on language, but has no letter reading and is money/debt-scoped only. Skendy is the strongest prior art — acknowledge it directly in pitch as validation, then differentiate on OCR, eligibility layer, and production ambition.

**Key pitch insight:** Skendy is the most credible precedent — cite it as proof the problem is real and the AI approach is viable, then explain what we add: OCR of actual letters, eligibility checking, and a path to production scale.

---

## NGO Landscape — Amsterdam / Netherlands

Tiered by fit with a multilingual government letter + eligibility tool.

### Tier 1 — Highest fit (direct daily need)

| NGO | Target group | Scale | Key pain point | Tech-readiness |
|---|---|---|---|---|
| **Sociaal Raadslieden Amsterdam** | Anyone needing help with gov correspondence, benefits, debt, housing rights | ~30 advisors for 900K+ residents | Massive capacity gap — advisors spend most time explaining letters + checking eligibility | Medium-low |
| **Humanitas (Thuisadministratie)** | Low-income, elderly, debt spiral | ~40,000 helped/yr nationally | Volunteers are generalists; time lost decoding eligibility rules limits throughput | Medium |
| **VluchtelingenWerk Nederland** | Asylum seekers + recognized refugees | ~50,000/yr; strong AMS presence | Language barrier is primary bottleneck; same letters (Belastingdienst, UWV, COA) explained repeatedly in multiple languages | Medium-high |
| **Buurtteams Amsterdam** | Residents with complex multi-domain problems | City-wide; tens of thousands of contacts/yr | Generalist workers check eligibility from memory; no systematic tool | Medium |

### Tier 2 — Strong fit, operational angle

| NGO | Target group | Scale | Key pain point |
|---|---|---|---|
| **Leger des Heils** | Homeless, addiction, ex-offenders | National; significant AMS presence | Clients excluded from benefits they qualify for (no fixed address, can't navigate system) |
| **HVO-Querido** | Homeless + psychiatric in Amsterdam | ~3,000–4,000/yr | Staff do huge reactive admin; eligibility checker would free capacity |
| **Voedselbank Amsterdam** | Low-income families | Only 15–17% of eligible population reached | Eligibility criteria poorly understood; stigma causes self-exclusion; no multilingual outreach |
| **GGD Amsterdam** | Uninsured/undocumented, public health | Municipality-level | MAWZ scheme almost unknown even to providers; multilingual health entitlement explanation needed |

### Tier 3 — Indirect fit

| NGO | Key pain point |
|---|---|
| **Dokters van de Wereld** | Intake staff manually explain MAWZ rights daily in multiple languages |
| **Stichting Lezen & Schrijven / Taalpunten** | Literacy + language barrier compound; AI that reads letters aloud would be transformative |
| **OpenEmbassy** | WhatsApp helpdesk bottlenecked; explicitly tech-oriented; partner to CommuniCity pilots; highest tech-readiness |

### Cross-cutting operational pain points

1. **Same letters explained repeatedly** — Belastingdienst, UWV, gemeente bijstand, zorgtoeslag letters consume advisor time every day. AI triage = direct multiplier on capacity.
2. **Eligibility knowledge gaps** among generalist volunteers — structured checker reduces errors, improves claim rates.
3. **Language fragmentation** — Arabic, Turkish, Tigrinya, Polish, Ukrainian all needed; no org has systematic coverage across all.
4. **Capacity ceiling** — Sociaal Raadslieden has ~30 advisors for a city of 900,000 with 22% near-poverty. Any triage layer has outsized leverage.

### Best partnership targets for hackathon pitch

Contact tonight framed as "can we reference you in our demo?"
1. **OpenEmbassy** — highest tech-readiness, already in CommuniCity space, will validate quickly
2. **VluchtelingenWerk** — known to explore tech partnerships, exact use case match
3. **Sociaal Raadslieden Amsterdam** — most acute capacity gap, perfect poster child for the problem
