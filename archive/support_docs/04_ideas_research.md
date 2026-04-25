# Ideas Research: 30 Candidate Solutions for the Top-10 Problems

**Structure:** Three ideas per problem × 10 problems = 30 candidate ideas. Each idea identifies:
- **Concept** — what the solution is.
- **How it addresses the problem** — the causal path from intervention to outcome.
- **Source / research gap** — a paper, product, or deployment that demonstrates the idea is viable *and* identifies the specific gap it would fill.

Ideas within a problem are deliberately differentiated by approach (technical, workflow, organisational) so that ranking in Turn 4 has real variance to score.

---

## ES-03 — Language barriers in 112 calls

### Idea ES-03-A. Real-time two-way speech translation overlay for 112 dispatchers
**Concept.** AI-driven simultaneous audio translation integrated into the dispatcher workstation: inbound audio transcribed and translated to Dutch on screen in real time; dispatcher replies typed or spoken in Dutch are translated back to the caller's language via TTS. Language auto-detection on the first spoken words.
**How it addresses ES-03.** Eliminates the 5-minute third-party-interpreter handoff that currently causes non-English callers to hang up (50% in Delaware County data) and produces the 125% response-time inflation documented in prehospital emergency-care research.
**Source / gap.** Carbyne APEX Translation launched this capability in 2023 and claims native-language auto-detection; Prepared 911 ships a similar bot in 40+ languages; Germany's Ludwigshafen dispatch integrated a 42-language Fraunhofer-backed system in 2024 but explicitly notes it takes a year-plus to complete auxiliary features and has no published accuracy-under-stress evaluation. **Research gap:** none of these are deployed on Dutch 112 infrastructure; none have published accent/dialect accuracy data for Arabic, Ukrainian, Turkish, or Tigrinya (the most-relevant languages for NL). (https://carbyne.com/resources/press/carbynes-apex-emergency-call-handling-system-now-offers-ai-driven-two-way-translation-capabilities-to-improve-9-1-1-response-time-and-accuracy/, https://www.aibase.com/news/11407)

### Idea ES-03-B. Voice-first multilingual pre-call app (112 companion)
**Concept.** A native-language voice-first app that records a 10-second emergency statement, extracts structured fields (what, where, how many), translates to Dutch, and transmits to 112 via data channel with GPS before a voice call is established. Reduces dispatcher cognitive load on non-Dutch calls.
**How it addresses ES-03.** Captures the critical first-30-seconds of information — where and what — even when the live call is impeded by language. Serves as a bridge, not a replacement.
**Source / gap.** Existing NL 112-app variants target deaf/HoH users and require Dutch text input. Multilingual text-to-112 exists in some US states but isn't voice-first. Patent US11589205 (Motorola, 2023) describes "audio forking" for emergency translation but is provider-side infrastructure, not caller-side. **Research gap:** no caller-side multilingual voice-native pre-call app deployed in the EU. (https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/11589205)

### Idea ES-03-C. LLM-based speech reconstruction for panicked/disfluent callers
**Concept.** An LLM-based module running on the dispatcher side that reconstructs incomplete speech from non-native-language callers — filling contextual gaps ("car… hit… my mother… bleeding…" → structured incident report) and providing severity classification. Trained on prior call transcripts with caller emotional-state annotations.
**How it addresses ES-03.** Language difficulty compounds with panic; existing translation products assume fluent input. A reconstruction layer handles the real linguistic pattern of stressed multilingual calls.
**Source / gap.** Venkateshperumal et al. (arXiv 2412.16176, 2024) propose exactly this as an LLM + RAG architecture with reported 100% conceptual precision on test cases but only lab-bench evaluation. **Research gap:** no real-system deployment; no evaluation on multilingual input; explicit future-work direction in the paper. (https://arxiv.org/pdf/2412.16176)

---

## NP-20 — Domestic-violence victims not reaching support services

### Idea NP-20-A. Dual-purpose "decoy" safety app with Dutch risk-assessment integration
**Concept.** App that presents to an observer as a mundane utility (recipe, weather, podcast app) while containing an encrypted evidence journal, a silent-SOS button (triple-tap or volume-key sequence), Dutch-language risk assessment (LINK tool, shortened for self-administration), and a routing engine that chooses Veilig Thuis, 112, or a trusted contact based on current risk level.
**How it addresses NP-20.** The documented reason 97% of DV victims don't reach Veilig Thuis is the combination of monitoring-by-abuser and fear of formal channels. A decoy app + anonymous routing + self-pacing ("talk to me when you're ready") removes the two biggest barriers at once.
**Source / gap.** Aspire News (2013, 300k downloads) pioneered the decoy pattern but had catastrophic security failures (unsecured cloud storage, exposed voice recordings — TechCrunch 2020). Bright Sky (UK + global) is well-regarded but identifies as a DV app — not truly decoyed. Mellaard & van Meijl (2021) document NL's "regime of deficiency" — fragmented services — meaning a Dutch-specific router is needed. **Research gap:** no NL-specific decoy app with LINK integration; no safety-proven architecture post-Aspire failure. (https://techcrunch.com/2020/06/25/aspire-app-dr-phil/, https://journals.sagepub.com/doi/full/10.1177/1463499620958857)

### Idea NP-20-B. AI-driven safety-planning chatbot in Dutch + migrant languages
**Concept.** Text-based chatbot that guides victims through safety-plan construction in their own words — identifying escalation patterns, validating experiences ("what you describe is coercive control"), generating a personal action plan, and surfacing next-step options calibrated to risk. Available 24/7, anonymous, in Dutch/Arabic/Turkish/Polish/Ukrainian.
**How it addresses NP-20.** Mijke Caminada (Valente) explicitly advocates for "a 24/7 independent anonymous helpline". A chatbot is the only way to deliver zero-wait-time 24/7 service in 5+ languages on sub-€100k/year budget. Doesn't replace human advocates — escalates warm to Veilig Thuis when user consents.
**Source / gap.** AinoAid (Finnish research chatbot, PMC12817862, 2025) completed usability testing with survivors; explicit finding that AI chatbots for DV are still research-stage; survivor concerns about AI limitations documented. **Research gap:** no Dutch-language deployment; no multilingual version; no research-to-production pathway demonstrated. (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12817862/)

### Idea NP-20-C. Frontline-professional silent-referral tool
**Concept.** Tool for GPs, midwives, teachers, and pharmacists: when a DV screening conversation triggers concern, the professional logs a structured note + consent request on a tablet; the patient sees the request framed as "share with helper" and chooses whether to authorise. On authorisation, Veilig Thuis receives a warm, pre-enriched referral. Works inside privacy regulations by being victim-consent-driven.
**How it addresses NP-20.** Per CBS/WODC, a third of victims do discuss their situation with a social worker, psychologist, or GP — but only 3% reach Veilig Thuis. The gap is the handoff. Existing Reporting Code (Meldcode Huiselijk Geweld) is a 5-step paper protocol; automating the handoff while preserving victim agency is the wedge.
**Source / gap.** Baker McKenzie Resource Hub documents the Meldcode steps; GREVIO (2025) report flags insufficient coordination between Veilig Thuis and partner services. No purpose-built professional-side tool for victim-consented silent referral in the Netherlands. (https://resourcehub.bakermckenzie.com/en/resources/fighting-domestic-violence/europe/the-netherlands/, https://www.coe.int/en/web/portal/-/violence-against-women-netherlands-legal-and-policy-changes-praised)

---

## NP-15 — Refugees cannot navigate digitalised Dutch bureaucracy

### Idea NP-15-A. Multilingual DigiD / Gemeente procedural assistant
**Concept.** AI assistant that operates as a persistent "guide" through Dutch e-government interactions: explains what DigiD is in native language, walks through BSN application, explains tax letters, handles Gemeente portal steps (registering address, applying for benefits), drafts responses to official correspondence. Integrated with public-sector APIs where available; falls back to OCR + LLM where not.
**How it addresses NP-15.** The compounding of digital + Dutch + bureaucratic complexity is identified by multiple studies as the primary integration obstacle for first-year newcomers. A single conversational assistant substitutes for a knowledgeable friend — which 90% of newcomers don't have.
**Source / gap.** Skendy (CommuniCity 2025, Amsterdam + Prague demo) is the closest deployment but in pilot with ~40 hours of co-creation, not scaled to full Dutch government. RefuGPT (ACM Digital Government 2025) validates the LLM + RAG architecture for Swiss Ukrainians but is monolingual English+Ukrainian and Swiss-only. **Research gap:** no production NL-scale deployment; no integration with actual DigiD/MijnOverheid flows. (https://communicity-project.eu/2025/04/11/an-ai-tool-to-support-immigrants-and-refugees-with-administrative-tasks/, https://dl.acm.org/doi/full/10.1145/3735140)

### Idea NP-15-B. Photograph-a-letter translator + action advisor
**Concept.** User photographs any official Dutch letter (Belastingdienst, UWV, gemeente, landlord). App OCRs, translates to native language, summarises the action required, deadline, and consequences of inaction. Offers to draft a response, add a reminder, or escalate to a volunteer advisor. Fully offline-capable on-device for privacy.
**How it addresses NP-15.** Refugees consistently report that the #1 bureaucracy problem is not speaking to officials — it's understanding letters. Weeks can pass where a letter sits ignored because the recipient doesn't know whether it's a bill, a deadline, or a scam.
**Source / gap.** OpenEmbassy's directory of newcomer tools lists "App to translate letters understandably at your language level" as one entry — a generic translation tool, not a structured action advisor. The Oxford AFAR report (Ozkul 2023) maps AI-for-migration tools and documents no OCR-driven structured-action tool. **Research gap:** existing translation tools produce text; none produce "what do I do and by when". (https://www.openembassy.nl/en/for-newcomers/, https://www.hertie-school.org/fileadmin/2_Research/1_About_our_research/2_Research_centres/Centre_for_Fundamental_Rights/AFAR/Automating-immigration-and-asylum_Ozkul.pdf)

### Idea NP-15-C. AI + peer-navigator hybrid with OpenEmbassy Q&A integration
**Concept.** AI front-end handles 80% of procedural questions (what form, which office, what deadline). When the AI detects emotional complexity, cultural nuance, or a case with conflicting rules, it pairs the user with a peer navigator (refugee who successfully went through the same process) for a scheduled chat. AI + peer share context; peer time is used only for high-value interactions.
**How it addresses NP-15.** Pure AI solutions miss cultural context (how to ask a civil servant for an exception, when to escalate, what Dutch directness means in practice). Pure peer-navigator solutions (like OpenEmbassy's current model) don't scale past ~10% success because human time is a hard bottleneck.
**Source / gap.** OpenEmbassy / Welcome NL (MIT Solve 2019 application) has validated the peer-navigator model at small scale; 30% of their team are newcomers in paid jobs. No system combines AI efficiency with peer-cultural authenticity in a single workflow. (https://solve.mit.edu/solutions/7310)

---

## ES-12 — AED temporal-access gap (off-hours closures)

### Idea ES-12-A. Operational-hours crowdsourced overlay on HartslagNu
**Concept.** A supplementary dataset keyed to the HartslagNu AED registry (~27k AEDs in NL) that records each device's actual operational hours + weekend status + seasonal closures. Owners and volunteer verifiers update; HartslagNu's routing logic queries this dataset at dispatch time and penalises closed AEDs. UI visualises to bystander: "AED 200m is CLOSED; AED 340m is OPEN."
**How it addresses ES-12.** The Sun et al. (JACC 2016) study of Toronto showed 21.5% of public OHCAs near a registered AED occurred when the AED was actually inaccessible, and spatiotemporal optimisation could improve coverage by 25.3%. Dutch HartslagNu is the closest to world-leading for volunteer routing — but its AED registry does not carry operational-hour metadata.
**Source / gap.** Sun et al. (2016, PMC4992180) formalised the problem; Karlsson et al. 2019 confirmed in Swedish data. HartslagNu documentation and Stan-app data structure have no dedicated hours field. **Research gap:** no EU deployment that explicitly encodes per-AED hours and uses it in dispatch routing. (https://pmc.ncbi.nlm.nih.gov/articles/PMC4992180/, https://pmc.ncbi.nlm.nih.gov/articles/PMC8136701/)

### Idea ES-12-B. Residential "24/7 AED neighbour" programme
**Concept.** Identify residential owners of private AEDs (e.g., cardiac patients who have one at home, small-business owners with workplace devices), enrol them into a 24/7-activatable responder list with consent. On nearby OHCA, dispatcher routes both the device and the owner (or a nearby HartslagNu volunteer to fetch it). Explicit consent model addresses liability.
**How it addresses ES-12.** The vast majority of OHCAs occur at night at home (see ES-13); no PAD-program AED is accessible at that moment. Private AEDs outnumber public ones in NL, and most sit behind locked doors 24/7. Unlocking even a small fraction expands coverage dramatically.
**Source / gap.** AHA / JAHA 2025 AED Symposium discusses residential AED coverage but no systematic private-enrolment programme exists. HartslagNu focuses on volunteer humans, not volunteer devices. **Research gap:** trust/liability/consent model for private-AED-as-public-asset is unexplored in NL. (https://pmc.ncbi.nlm.nih.gov/articles/PMC12132870/, https://pmc.ncbi.nlm.nih.gov/articles/PMC8136701/)

### Idea ES-12-C. Remote-unlock outdoor AED cabinet
**Concept.** Physical retrofit: weatherproof outdoor cabinet with IoT-enabled remote unlock. On dispatch trigger, the cabinet unlocks for the specific bystander (QR code confirming location + case ID). Device remains locked outside of dispatched events to prevent theft. Piloted at 10 currently-indoor AED locations per city.
**How it addresses ES-12.** Converts business-hours AEDs into 24/7 AEDs without the cost of new hardware. Addresses the majority-case of "the device is there but the building is locked".
**Source / gap.** Cabinet-deployed AEDs exist in sports clubs and public spaces but generally use physical keypads or emergency-break-glass. Remote-unlock integration with dispatch infrastructure has been proposed (Rho-sigma AED Locator 2022 whitepaper) but not deployed in NL; HartslagNu Stan app doesn't have cabinet-unlock hooks. **Research gap:** no NL deployment; no consent / governance framework for dispatch-controlled physical-access devices. (https://pmc.ncbi.nlm.nih.gov/articles/PMC8136701/)

---

## ES-04 — Dispatcher recognition of out-of-hospital cardiac arrest

### Idea ES-04-A. Real-time call-audio ML classifier for OHCA (Corti-style, explainable)
**Concept.** ML model listens to live 112 call audio, detects OHCA cues (agonal breathing sounds, caller phrases, silence patterns), and presents an alert to the dispatcher with a severity score and — critically — a short explanation ("detected agonal breath at 23s; caller phrase 'not breathing normally' at 31s").
**How it addresses ES-04.** Byrsell et al. 2021 (Swedish retrospective): ML recognised 36% within first minute vs 25% for humans, and 28 seconds faster on average. Every minute saved in defibrillation translates to 7–10% additional survival.
**Source / gap.** Corti AI (Copenhagen) achieves 93–95% OHCA detection retrospectively, but the Blomberg et al. 2021 JAMA RCT showed no statistically significant improvement in live recognition — attributed to dispatcher alert fatigue and lack of explanation. Research explicitly identifies "AI cannot explain how it makes decisions" as the key failure mode. **Research gap:** explainable-AI layer on top of Corti-style classifier; NL-Dutch-language validation; alert-fatigue mitigation. (https://www.jamanetwork.com/journals/jamanetworkopen/fullarticle/2780906 — referenced via EENA/Corti AI4EMS materials)

### Idea ES-04-B. Caller-smartphone OHCA visual confirmation
**Concept.** During a 112 call, dispatcher can send the caller a link that, on tap, activates the caller's phone camera. A lightweight on-device model identifies patient posture + visible chest movement. Information flows to dispatcher: "caller's phone confirms patient is supine, no observable chest rise". Used as adjunct to audio, not replacement.
**How it addresses ES-04.** The hardest recognition cases are those where the caller is emotionally overwhelmed and can't describe breathing. A 3-second video can be more informative than a 30-second conversation.
**Source / gap.** RapidSOS HARMONY includes video streaming for emergency calls but not targeted OHCA recognition. Carbyne supports live video for context. **Research gap:** no purpose-built visual OHCA classifier that runs on the caller's device; no privacy-preserving workflow demonstrated. (https://rapidsos.com/public-safety/transcription-translation/)

### Idea ES-04-C. Post-call quality-improvement LLM reviewer
**Concept.** Asynchronous batch analysis: every 112 call that resulted in cardiac arrest is analysed post-hoc by an LLM that produces a structured review (did the dispatcher ask the key questions, when was arrest recognised, what cues were missed). Feeds individualised retraining modules.
**How it addresses ES-04.** Dispatch-QI programmes exist but are manual and review <5% of calls. LLM-assisted review lets every OHCA call contribute to institutional learning, surfacing systemic patterns (e.g., a particular team misses seizure-like-activity cues).
**Source / gap.** Lewis et al. (PMID 23983252) document that recognition time varies by dispatcher training; current QI programmes rely on supervisor sampling. **Research gap:** no deployment of LLM-based dispatch QI at scale; no privacy-preserving audio-analysis workflow validated for EU GDPR. (https://pubmed.ncbi.nlm.nih.gov/23983252/)

---

## NP-13 — Food banks reach only 15–17% of eligible population

### Idea NP-13-A. Self-service eligibility estimator with warm handoff
**Concept.** Anonymous chatbot that walks a user through income-minus-fixed-costs calculation (the Voedselbanken Nederland formula), estimates eligibility, and — if the user consents — pre-fills the Voedselbank intake form and routes to the nearest Voedselbank with capacity. In Dutch + Arabic + Turkish + Ukrainian + Polish.
**How it addresses NP-13.** The 15–17% reach is driven largely by stigma + procedural opacity. Many near-eligible households never check because the rules are unclear and formal application is psychologically costly. Anonymous self-check is low-friction first step.
**Source / gap.** Voedselbanken Nederland has an application process but it's paper-heavy in many regions; Leiden International Centre documentation indicates significant front-door complexity. US-side, Plentiful, OasisInsight, and PlanStreet provide operational software but none has an EU/NL deployment; none handle the "am I eligible" question from the client side. **Research gap:** no NL consumer-facing eligibility estimator; no A/B tested stigma-reduction UX. (https://www.leideninternationalcentre.nl/get-advice/blogs/food-banks-in-the-netherlands, https://www.plentifulapp.com/)

### Idea NP-13-B. Proactive referral via partner-institution screening
**Concept.** Integrate with GPs, schools (via CJG), debt-counselling (schuldhulpverlening), and UWV to add a 10-second screening question: "Do you have enough to eat this week?" Positive answers trigger (with consent) a Voedselbanken referral with pre-filled data. Similar pattern to Dutch Vroegsignalering schuldhulp model.
**How it addresses NP-13.** A large fraction of eligible non-users are already in touch with public institutions but are not asked. Adding a single screening question converts passive touchpoints into active referrals.
**Source / gap.** Vroegsignalering schuldhulp (early debt signalling) is operational since 2021 under Wgs; no equivalent programme exists for food insecurity despite the same structural conditions. **Research gap:** no NL pilot of screen-and-refer for food aid; no data on yield per screening touchpoint. (https://www.schuttelaar-partners.com/update/week-of-the-food-banks/3197)

### Idea NP-13-C. Stigma-free supermarket voucher model
**Concept.** Eligible households receive a monthly app-based voucher (€30–50) redeemable at ordinary supermarkets (Albert Heijn, Jumbo, Lidl) for fresh produce + staples. Supermarkets reimburse via central clearing. Indistinguishable at the till from any other discount. Funded from existing Voedselbank operating budget plus supermarket co-pay.
**How it addresses NP-13.** The stigma of "going to the food bank" is one of the biggest reach barriers. A grocery voucher removes the branded-charity interaction entirely. UK's Healthy Start voucher scheme reports ~80% uptake among eligible, vs. 15–17% for NL food banks.
**Source / gap.** Voedselbanken Nederland's 2024 consultation paper on modernisation flags "dignity" but doesn't propose voucher pilots. UK Healthy Start is the closest template but is means-tested and pregnancy/infant-focused, not general. **Research gap:** no NL voucher-based food-aid pilot at scale. (https://edepot.wur.nl/566460)

---

## ES-10 — Dispatch undertriage delays time-critical care

### Idea ES-10-A. ML secondary-review overlay for low-priority dispatches
**Concept.** When a call is classified as low-priority (P3/P4), an ML model runs a parallel analysis on call audio + structured data + caller demographics. If it predicts >X% deterioration risk, it flags for a supervising nurse's 10-second review before the ambulance is actually dispatched-low or not-dispatched.
**How it addresses ES-10.** Undertriage (5–28% in observational studies) happens when flow-chart-based MPDS/ProQA protocols miss context that a risk-scoring model can capture — e.g., elderly patients with atypical chest pain often undertriage in MPDS.
**Source / gap.** The Swedish RCT NCT04757194 (Uppsala + Västmanland) is actively evaluating exactly this paradigm; results pending. Multiple observational studies (Møller 2018, Elfström 2022) document the undertriage problem. **Research gap:** no production deployment; no validation on NL dispatch data; explainability of the risk score not yet published. (https://clinicaltrials.gov/study/NCT04757194, https://pmc.ncbi.nlm.nih.gov/articles/PMC5747276/)

### Idea ES-10-B. LLM-driven adaptive questioning for ambiguous symptoms
**Concept.** When a caller reports an ambiguous symptom cluster (chest tightness + fatigue, abdominal pain in elderly, sudden confusion), the LLM suggests 2–3 discriminating follow-up questions to the dispatcher in real time — drawn from the evidence base for differentiating benign from time-critical presentations.
**How it addresses ES-10.** MPDS is comprehensive but flat — hundreds of questions organised by presenting complaint. An adaptive layer that narrows questions based on call context converts generic-protocol to personalised-protocol.
**Source / gap.** Elfström et al. 2022 (PMC8744325) document that allergic reactions, diabetic problems, and heart conditions are undertriaged >10% even in experienced systems. MPDS improvements happen at the protocol-revision cycle (years), not adaptive. **Research gap:** no deployment of LLM-driven question-suggestion in 112; no evaluation of impact on recognition time vs. overtriage rate. (https://pmc.ncbi.nlm.nih.gov/articles/PMC8744325/)

### Idea ES-10-C. Post-dispatch proactive callback prioritisation
**Concept.** For patients sent an ambulance at low priority (longer wait), an ML model prioritises which cases deserve proactive callback during the wait. Dispatcher queue surfaces "patient at postcode X, waiting 42 min, 78% deterioration-risk flag — call back now". Frees dispatchers to make the right callbacks instead of all or none.
**How it addresses ES-10.** Current callbacks are dispatcher-discretionary and inconsistent. A risk-prioritised queue converts callback from luck to policy.
**Source / gap.** BMC Emergency Medicine 2024 (stroke decision-making at EMCC) documents that dispatchers struggle to prioritise callback time. **Research gap:** no prioritisation tool; no workflow integration with CAD systems. (https://link.springer.com/article/10.1186/s12873-024-01129-0)

---

## ES-05 — Dispatcher-assisted CPR refusal and delay

### Idea ES-05-A. AR-guided CPR via smartphone video
**Concept.** During a cardiac-arrest call, dispatcher can trigger a link-send to the caller's phone. On tap, the caller's camera shows an AR overlay with compression rate, depth feedback, position guidance, a metronome, and a calming voice. Caller sees both patient and overlay simultaneously.
**How it addresses ES-05.** Linderoth et al. (2015, CCTV + audio analysis of OHCA) showed that video feedback closes the gap between heard instructions and actual action. Median time to first compression is ~176s; a 30-second reduction plausibly translates to ~3% additional survival.
**Source / gap.** Linderoth 2015 validated the premise with CCTV in ambulance services; RapidSOS and Carbyne support video in principle but none are purpose-built for AR CPR coaching. **Research gap:** no RCT of AR-guided CPR; no 112 workflow integration. (https://www.sciencedirect.com/science/article/pii/S0300957215002464)

### Idea ES-05-B. Adaptive DA-CPR script for physical-constraint scenarios
**Concept.** Instruction engine that branches based on caller-reported constraints: "I can't move him" → leave patient where they are, clear under-back, compress on mattress with door as board; "I'm alone and it's my husband" → put phone on speaker, count with me; "I have arthritis" → knee compressions, upper-body weight, pause rotation. Replaces one-size-fits-all script.
**How it addresses ES-05.** A 2025 scoping review (*Internal and Emergency Medicine*) identifies "could not move the patient" as a major delay cause; current scripts assume the caller can get the patient flat on the floor.
**Source / gap.** *Resuscitation* (2020, PMC10656878) details bystander emotional-stress patterns; Linderoth 2015 cataloged refusal reasons. **Research gap:** no adaptive protocol; no evaluation of branching script vs. MPDS baseline. (https://link.springer.com/article/10.1007/s11739-025-03991-7, https://pmc.ncbi.nlm.nih.gov/articles/PMC10656878/)

### Idea ES-05-C. Audio metronome + background calming soundscape
**Concept.** Separate from dispatcher voice, caller's phone plays a 110-bpm metronome tone (optimal compression rate) and a low-frequency grounding tone shown in psychological research to reduce acute panic. Runs in parallel with dispatcher instruction; caller can keep phone in pocket or next to patient.
**How it addresses ES-05.** Dispatcher voice is often overwhelmed by caller emotional state. A non-verbal rhythmic channel maintains compression cadence even when verbal comprehension breaks down.
**Source / gap.** "Stayin' Alive" metronome apps exist but require active use by caller. No 112-integrated metronome that plays automatically on call-connect. **Research gap:** no evaluation of automatic audio-metronome on compression-rate compliance. (https://www.ahajournals.org/doi/10.1161/CIR.0000000000001054)

---

## ES-18 — Bystander AED use remains very low (~4%)

### Idea ES-18-A. AR model-specific AED opening walkthrough
**Concept.** Bystander points phone at any AED (Philips, Zoll, Cardiac Science, Defibtech). Computer vision recognises model; AR overlay highlights "press here to open," "place this pad here," with synchronised voice. Eliminates the "I don't know how to use it" intimidation.
**How it addresses ES-18.** 4% usage is not mostly a coverage problem — it's a confidence problem. Good Samaritan protections are well-established; what's missing is real-time competence support at the moment of action.
**Source / gap.** *Cureus* 2023 systematic review (PMC10676231) identifies lack of training refresh as a primary barrier; AED manufacturers publish model-specific videos but none are AR-overlay on the physical device. **Research gap:** no AR AED assistant app; no cross-manufacturer model recognition library. (https://pmc.ncbi.nlm.nih.gov/articles/PMC10676231/)

### Idea ES-18-B. Dispatch-optimised volunteer + AED assignment
**Concept.** Extension to HartslagNu that, on OHCA alert, sends specific instructions to specific responders: "Person A: go to AED at café Laan (open); Person B: go directly to patient and start compressions; Person C: escort paramedics from street". Solves the "many volunteers, no one goes" problem known in PulsePoint data.
**How it addresses ES-18.** PulsePoint (US, 5,500+ communities) reports that only 23% of notifications result in responder action, and 28% of responders who start don't arrive. The failure mode is ambiguity about whose job is what. Explicit role assignment at dispatch converts a crowd into a team.
**Source / gap.** PulsePoint RCT by Brooks et al. is underway but addresses activation rates, not assignment quality. HartslagNu Stan-app documents volunteer response patterns but doesn't assign specific roles. **Research gap:** no role-assignment algorithm in deployment; no evaluation against free-for-all model. (https://pulsepoint.org/research)

### Idea ES-18-C. Residential-zone AED confidence nudge
**Concept.** Every 6 months, residents within 300m of a registered AED receive a push notification: "Your neighbourhood AED is 200m away at address X. Try the 60-second use-from-memory quiz." Gamified micro-training. When called to respond, confidence is higher because the location was recently relevant.
**How it addresses ES-18.** PAD-program training effectiveness decays within months; most potential responders have trained only once in their lives if ever. Residential proximity is the strongest predictor of actual response; tying training to proximity is an obvious combination.
**Source / gap.** AHA training-decay literature documents 3–6 month skill loss; residential-zone nudges don't exist in PAD programs. **Research gap:** no deployed programme; no A/B test of nudge frequency vs. response rate. (https://pmc.ncbi.nlm.nih.gov/articles/PMC12132870/)

---

## ES-09 — Dispatch overtriage strains ambulance resources

### Idea ES-09-A. LLM decision support flagging likely-overtriage cases
**Concept.** LLM runs parallel to dispatcher; when the MPDS/ProQA classification gives an urgent category but the full call context suggests lower acuity (e.g., 30-year-old with "abdominal pain" for three days who decided to call today), it displays a non-blocking advisory: "overtriage risk flag: consider nurse secondary review." Dispatcher can accept, dismiss, or escalate.
**How it addresses ES-09.** Quebec 2021–2023 study showed 74.5% overtriage; abdominal pain, falls, and psychiatric complaints showed >90% overtriage rates. An explicit flag gives the dispatcher a legitimate reason to pause before burning an urgent unit.
**Source / gap.** Scandinavian Journal of Trauma, Resuscitation and Emergency Medicine (2025, the Quebec MPDS study) documents scale; no countermeasure deployment. **Research gap:** no LLM-advisory deployment; no evaluation of impact on overtriage rate vs. undertriage rate tradeoff. (https://link.springer.com/article/10.1186/s13049-025-01410-6)

### Idea ES-09-B. In-call non-urgent self-service chatbot
**Concept.** When dispatcher identifies a call as probable non-urgent (e.g., symptom of 4 days, no red flags), offer the caller an in-call handoff to a chatbot that handles appointment booking with huisartsenpost, pharmacy advice, or symptom triage — with safety-net escalation if caller indicates worsening. Frees dispatcher for genuinely urgent calls.
**How it addresses ES-09.** NL's huisartsenpost out-of-hours triage is phone-based and already congested; an LLM-first layer for non-urgent cases acts as release valve.
**Source / gap.** Portugal's ChatGPT triage pilot (INEM) is exploring similar territory but is experimental and not public. **Research gap:** no NL deployment; no evaluation of safety-net false-negative rate. (https://eena.org/knowledge-hub/documents/multilingual-112-calls/)

### Idea ES-09-C. Explainable shadow-reasoning assistant for dispatchers
**Concept.** A "second pair of eyes" AI that, for every call, produces a structured reasoning trace: "this call was classified Priority 1 due to keyword 'chest pain' at 00:12. Context suggests Priority 3 is more appropriate because: age < 35, pain rated 2/10, duration 3 days. Dispatcher should consider asking about [X, Y, Z]." Non-blocking display.
**How it addresses ES-09.** The EENA/Corti AI4EMS initiative has flagged explainability as the #1 gap preventing Corti-style black-box AI from influencing dispatch decisions. Explainable reasoning traces convert AI from "alert fatigue source" to "cognitive partner."
**Source / gap.** Blomberg 2021 JAMA RCT demonstrated that opaque AI alerts don't improve dispatch decisions; Corti's own research acknowledges explainability as a key open problem; EENA/Corti AI4EMS explicitly targets this. **Research gap:** no deployed explainable dispatch AI; no user study comparing explainable vs. opaque on dispatcher trust + outcome metrics. (https://eena.org/events/ai4ems-webinar-series/)

---

## Cross-cutting observations for Turn 4 ranking

A few things worth naming before scoring:

**Technology-cluster reuse.** Several ideas share the same core technology: ES-04-A, ES-05-A, ES-09-A, ES-09-C, ES-10-A, ES-10-B all depend on LLM/ML analysis of dispatch audio + structured data. A hackathon team that builds one can likely demo a variant of another. This compounds the "cardiac-arrest cluster" observation from Turn 2.

**Partner dependencies.** Ideas vary widely in what they require from outside the hackathon team. Lowest partner dependency: NP-15-B (letter translator; self-contained), NP-13-A (eligibility estimator; public rules), ES-18-A (AR AED walkthrough; public AED models). Highest partner dependency: ES-04-A (needs call-audio access), ES-10-A (needs CAD integration), ES-12-B (needs private-AED-owner consent infrastructure).

**Originality differentiation.** Ideas vary in how novel they are vs. existing products. Highly novel: NP-20-A (NL-decoy app + LINK), NP-15-B (photo-to-action), ES-12-B (24/7 private AED), ES-18-B (role-assignment at dispatch). Largely derivative: ES-03-A (Carbyne-style translation), NP-13-A (US food-bank-software style).

**Feasibility-novelty tradeoff.** The most feasible ideas are often the least novel (because they exist elsewhere). The most novel ideas often have no deployment precedent (because the problem is hard). This tension will show up in the Turn 4 ranking between Feasibility and Originality scores.

These observations are meta — not directly scored. But they'll help explain the ranking when you see it.
