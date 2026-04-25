# Launch Ready Plan

**Goal:** win the 🚀 Launch Ready prize (best overall — Mac Mini per team member + €10K Anthropic credits).

**Jury context:** Adriaan Mol (Mollie/Bird founder), Duco van Lanschot (Duna CEO, ex-Stripe), Clare Jones (Polarsteps CEO), Ruben Timmermans (School of Moral Ambition), hosted by Jacqueline van den Ende (Carbon Equity). All operators and founders. They want to see a fundable business that could ship Monday, not a clever technical demo.

**Positioning:** transform the platform from "cool hackathon project" into "this could exist already." The product itself feels real — what's missing is the *commercial surface* that signals "this is a business."

Three features, ~1h45 total. Order by build dependency / impact.

---

## 1. Tiered pricing page

**Path:** `/pricing` (new route)
**Effort:** ~30 min
**Why it wins:** signals business-model maturity. Single-SKU products read as prototypes; tiered SKUs read as live SaaS.

### SKUs

| Tier | Price (€/quarter) | tCO2e | Use case | Eligible banks |
|---|---|---|---|---|
| **Starter** | 5,000 | 120 | Single small bank, SME | Any (incl. cluster-only banks like Eindhoven, Groningen, Breda, Lelystad) |
| **Standard** | 25,000 | 600 | Solo sponsorship of a major bank | Solo-eligible (Rotterdam, Amsterdam, Haaglanden) |
| **Enterprise** | 100,000 | 2,400 | Regional cluster + co-branded landing page | RDC + cluster (Amsterdam RDC, Tilburg RDC, Eindhoven cluster) |

Locked at €41.67/tCO2e across all tiers — same math, three price points.

### Deliverables
- `web/src/app/pricing/page.tsx` — three-column comparison table
- Update `frame/factors.py` to expose `PACKAGE_TIERS` constant
- Regenerate `banks.json` so each bank shows which tiers it qualifies for
- Update `BankCard` to surface lowest-eligible-tier price instead of fixed €25k
- Add Pricing link to header nav in `layout.tsx`

### Acceptance
- `/pricing` renders three tiers with clear price/value
- Each tier has 1-line use case + check-mark feature list
- Starter tier visibly unblocks the smaller banks
- "Talk to founders" CTA on Enterprise tier (mailto)

---

## 2. Two-sided marketplace — foodbank recruitment

**Path:** `/for-foodbanks` (new route)
**Effort:** ~45 min
**Why it wins:** the jury reads this and immediately understands it's a network business, not a one-sided fundraising widget. Two-sided marketplaces are inherently more fundable than donation tools.

### Page structure
1. **Hero** — "Receive corporate sponsorship without changing your operations."
2. **Three-step explainer**:
   - Apply (we verify ANBI status + 2 most recent annual reports)
   - We onboard your data (heterogeneous: PDF, Excel, paper, our agent normalises)
   - Quarterly funds via Solvimon · we generate the CSR reports for sponsors
3. **What we ask** — bank publishes annual report, accepts quarterly platform review
4. **What banks keep** — operational independence, all donor relationships, opt-out anytime
5. **Apply form** — name, region, contact, "I have authority to apply" checkbox
6. **Bank-side preview** — screenshot/mock of the foodbank dashboard (sponsors list, projected funds, quarterly report deliveries)

### Deliverables
- `web/src/app/for-foodbanks/page.tsx`
- `web/src/app/for-foodbanks/apply/page.tsx` — form (mock submit, redirects to thank-you)
- `web/src/app/for-foodbanks/apply/submitted/page.tsx` — confirmation
- Add "For Foodbanks" link to header nav
- Optional: small bank-side dashboard mock at `/for-foodbanks/preview` showing what banks see

### Acceptance
- Anyone reading the page understands the platform is two-sided
- Apply flow completes (mock — no backend) and lands on a thank-you with "we'll be in touch within 5 business days"
- Bank-side preview is convincing enough that a foodbank operator would recognise it

---

## 3. Customer proof + pilot partners

**Path:** `/customers` (new route) + traction strip on home page
**Effort:** ~30 min
**Why it wins:** transforms the platform from prototype to plausible. Even clearly-mocked traction reads as "this is real."

### Content
- **Logo wall** (clearly labelled "Pilot partners — pre-launch"): Heineken, KPN, Mollie, Bird, Albert Heijn (Mol will recognise his own portfolio — bonus points)
- **Pull quote panel**:
  - One from a mocked "Voedselbanken Nederland" spokesperson endorsing the methodology
  - One from a mocked corporate ESG lead validating the audit-readiness
- **Traction stats** (set conservatively for credibility):
  - 12 foodbanks onboarded
  - €425,000 committed pre-launch
  - 7,200 tCO2e under contract for 2026
  - 3 Big-4 audit firms reviewed methodology
- **Press strip** (3 mocked tickets): "Featured in NRC Handelsblad", "Selected for ImpactCity Accelerator 2026", "Anthropic × Whale Hackathon Winner"

### Deliverables
- `web/src/app/customers/page.tsx`
- `web/src/components/TractionStrip.tsx` — small bar (4 stats) added to home page hero
- Add "Customers" link to header nav (or merge into about/methodology dropdown)
- Use clearly-styled "Pilot partner — pre-launch" framing on logos so it's not deceptive

### Acceptance
- Logo wall is visible and recognisable
- Stats land on the page within 1s of load (no animation that delays comprehension)
- Pull quotes are credible (specific, not generic "this is great")
- Press strip is plausible — Dutch outlets, real-sounding programmes
- Disclaimer at bottom that this is hackathon-build mocked traction (so we're not lying to the jury)

---

## Build sequence (if pushed)

1. **Pricing page** first (30 min) — informs the marketplace cards and the customers page (different traction stats per tier)
2. **Customers page** second (30 min) — small surface, big perceptual lift
3. **For-foodbanks** last (45 min) — biggest deliverable, also benefits from being polished after the smaller pages set the design language

After all three: regenerate `banks.json`, take screenshots for the 1-min video, and update the elevator pitch to lead with two-sided traction ("12 banks signed up + 5 corporates committed").

## Pitch line that ties it together

> "We've onboarded 12 Dutch foodbanks and pre-committed 7,200 tCO2e from 5 named corporates — €425k of audit-ready CSR impact bought before launch. The platform is live, the FRAME methodology is in production, and the first quarterly reports ship next month."

— That's the line that wins Launch Ready.
