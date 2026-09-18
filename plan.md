# Claim Advocate — 24-Hour Design Plan (Team of 2)

Track 2 — AI-Powered Financial Journeys | 24-hour hackathon format
*Companion to `architecture.md` — see that file for component design, schemas, API, and tech stack.*

---

## 0. What changed in this revision

Adopted from the reviewed alternative architecture: deterministic rule engine,
contradiction detection, prompt-injection/security handling, the `insufficient_evidence`
verdict, hybrid retrieval, weighted readiness scoring, and a lightweight embedded
evidence trace. Each earns its place because it's cheap to build *and* answers a real
judge question (see §6).

Deliberately not adopted: a structured clause-hierarchy graph, a fully decomposed
10-part validator, a separate persisted `/trace/{id}` endpoint, 5-pass self-consistency
(kept at 3), and a 14-scenario eval matrix (trimmed to 8–10, prioritized for demo value
over category completeness). These cost more than they return at this scope.

---

## 1. Feature List — Feasibility Classification

### 1.1 Must-have (P0 — core differentiator, cutting any of these guts the pitch)

**Shared core**
- [ ] Input Sanitizer (delimits document text from instructions) — Python, cheap
- [ ] Structured policy extraction, schema-enforced
- [ ] Structured evidence extraction with date/amount normalization
- [ ] Hybrid retrieval: exact clause lookup + semantic search
- [ ] Deterministic Rule Engine (dates, waiting periods, deadlines, limits)
- [ ] Decision Validator (single focused function, not ten separate components)

**Module A**
- [ ] Contradiction Detector (field-by-field comparison across documents)
- [ ] Readiness Engine with weighted scoring (critical 50% / required evidence 30% / consistency 15% / supporting 5%)
- [ ] Prioritized fix-list generator
- [ ] 3 core scenarios: missing document, contradictory dates, genuinely ready

**Module B**
- [ ] Policy-Evidence Reasoner with 3-pass self-consistency
- [ ] `consistency_score` calculation (agreement rate, explicitly not a probability)
- [ ] Four-way verdict including `insufficient_evidence`
- [ ] Appeal Generator (evidence table first, then letter — grounded inputs only)
- [ ] 3 core scenarios: valid / misapplied / ambiguous → insufficient_evidence

**Calculation:** the added Python components (rule engine, contradiction detector,
sanitizer, validator) are all deterministic code — collectively adding roughly
2–3 hours to the shared-core phase, not per-module hours, since they're built once
and used by both. This still fits comfortably inside the same overall budget as the
previous single-scope plan, because deterministic code is faster to build and test
than an equivalent LLM-reasoning step would have been.

### 1.2 Should-have (P1 — strong differentiators, cut first if behind schedule)

- [ ] Eval harness with real accuracy numbers across 8–10 scenarios (trimmed from a
      14-scenario matrix — prioritize demo-relevant cases: valid, misapplied,
      wrong-clause-reference, ambiguous for Module B; missing-document,
      contradictory-dates, waiting-period-failure for Module A)
- [ ] Evidence trace shown in the UI via a "Why?" interaction
- [ ] Adversarial prompt-injection test scenario (cheap, strong Q&A payoff)

**Calculation:** roughly 3–4 hours. The adversarial test scenario specifically is
worth prioritizing even under time pressure — it's a single crafted test case, not
a new component, and it directly answers a question judges are increasingly primed
to ask.

### 1.3 Stretch (P2 — only if P0 and P1 are done and stable by hour 19)

- [ ] Lending-rejection counterfactual as a third, smaller journey
- [ ] Multi-clause handling (a rejection citing more than one clause, each adjudicated independently)
- [ ] SQLite persistence beyond the in-memory session

**Calculation — honest read:** treat these as Q&A talking points, not build targets.

### 1.4 Explicitly cut (do not build, even if time remains)

- User accounts / authentication
- Persistent database beyond the demo session (evidence trace is embedded in
  responses, not stored separately — no `/trace/{id}` endpoint)
- Structured clause-hierarchy / related-clause graph (semantic retrieval already
  surfaces related clauses at query time — no need to pre-compute and store this)
- Fully decomposed 10-part validator as ten separate components — build as one
  focused function covering the same checks
- Multi-insurer clause libraries or a general-purpose policy database
- Real IRDAI/insurer API integration (use static sample documents throughout)
- Production-scale vector database, microservices, multi-agent orchestration

---

## 2. Planning Phase (Hour 0–2, together)

- Finalize schemas from `architecture.md` §4, including the new `EvidenceFact`,
  `ContradictionFlag`, `RuleResult`, and four-way `Verdict`
- Hand-write 6 hero scenarios covering both modules (see §1.1), including at least
  one deliberately contradictory-document case and one genuinely ambiguous case that
  should resolve to `insufficient_evidence`
- Agree on the API contract — freeze it after this phase
- **Deliverable:** schemas locked, 6 scenarios written, contract agreed

---

## 3. Backend Phases

### Backend Phase 1 — Shared Core (Hour 2–8, together)
- Policy Extraction + Evidence Extraction (with normalization) — Person 1 leads
- Policy Knowledge Layer + Hybrid Retrieval (exact + semantic) — Person 2 leads
- Input Sanitizer, Deterministic Rule Engine — built together, both are small and
  used by both modules
- **Deliverable:** extraction, retrieval, sanitizer, and rule engine all tested
  against the 6 scenarios; schema and contract frozen from this point on

### Backend Phase 2A — Module B Core (Hour 8–15, Person 1)
- Hour 8–12: Policy-Evidence Reasoner with 3-pass self-consistency + consistency_score
- Hour 12–14: Decision Validator (single function) + Appeal Generator (grounded-only)
- Hour 14–15: Test against all Module B scenarios, including the insufficient_evidence case
- **Deliverable:** `/adjudicate`, `/draft-appeal`, `/adjudication/pipeline` returning
  correct, grounded results, including a correct abstention on the ambiguous scenario

### Backend Phase 2B — Module A Core (Hour 8–15, Person 2, parallel)
- Hour 8–11: Contradiction Detector
- Hour 11–14: Readiness Engine with weighted scoring + fix-list generator
- Hour 14–15: Test against all Module A scenarios
- **Deliverable:** `/readiness/pipeline` returning correct results, including a
  correctly flagged contradiction

### Backend Phase 3 — Eval Harness + Adversarial Test (Hour 15–17, split then merged)
- Each person builds eval runs for their module's scenario set (trimmed to 8–10 total)
- Build the prompt-injection adversarial test case together
- **Deliverable:** real accuracy numbers for both modules; documented proof the
  sanitizer holds against an injected instruction

---

## 4. Frontend Phases

### Frontend Phase 1 — UI Shell (starts Hour 15, Person 2, once Module A backend is stable)
- Two-tab layout: "Before You Submit" / "If You're Rejected," with mock data first
- **Deliverable:** static shell navigable end-to-end

### Frontend Phase 2 — Wire to Backend + Evidence Trace (Hour 17–20, together, Person 2 leads)
- Connect both tabs to their pipeline endpoints
- Build the "Why?" interaction showing the embedded evidence trace
  (verdict → clause → fact → source document → page)
- Show contradictions, rule results, and consistency_score clearly labeled as
  agreement-rate, not probability
- **Deliverable:** working end-to-end UI for both modules with a working trace view

---

## 5. Integration & Testing Phases

### Integration Phase 1 — Stress-Test (Hour 20–22, together)
- Run all 6 hero scenarios end-to-end, live, multiple times
- Confirm the insufficient_evidence and contradiction-detection scenarios both
  demo cleanly — these are the two most novel moments, worth extra rehearsal time
- **Deliverable:** all scenarios reproducible on demand, no crashes

---

## 6. Presentation Phase

### Presentation Phase 1 — Deck & Rehearsal (Hour 22–24, together)
- Finalize the deck with real eval numbers and the Python-vs-LLM component table
  from `architecture.md` §3 — this table is your direct, rehearsed answer to
  "isn't this just an LLM wrapper?"
- Rehearse the pitch split by module
- **Deliverable:** demo-ready deck, rehearsed pitch, 6 scenarios locked

---

## 7. Phase Timeline at a Glance

| Hour | Planning | Backend | Frontend | Integration | Presentation |
|---|---|---|---|---|---|
| 0–2 | Scope & scenarios (together) | — | — | — | — |
| 2–8 | — | Shared core (together) | — | — | — |
| 8–15 | — | Module B (P1) / Module A (P2), parallel | — | — | — |
| 15–17 | — | Eval + adversarial test (split → merged) | UI shell starts (P2) | — | — |
| 17–20 | — | — | Wire + evidence trace (together) | — | — |
| 20–22 | — | — | — | Stress-test (together) | — |
| 22–24 | — | — | — | — | Deck & rehearsal (together) |

---

## 8. Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Schema/API contract drift between backend and frontend | High if not managed | Freeze at end of Planning Phase; changes after that require both people's sign-off |
| Inconsistent date/amount formats across documents cause false contradiction flags | Medium — new risk with this revision | Normalize dates/amounts to a consistent format (ISO dates, numeric amounts) *inside* the extraction step, before the Python comparison runs |
| One backend module finishes late and delays frontend wiring | Medium | Both modules scoped to roughly equal effort; cut should-have items (§1.2) first if one runs over |
| Self-consistency passes disagree unpredictably | Medium | If passes disagree substantially, this should correctly resolve to `insufficient_evidence` — treat this as a feature working, not a bug to suppress |
| Live demo network/API latency | Low-medium | Pre-run and cache responses for all 6 hero scenarios as a fallback |
| Judges perceive two modules as disconnected | Medium | Frame explicitly as "one engine, two moments," backed by the shared-core diagram |
| Judge asks "isn't this just an LLM wrapper?" | High (expect this) | Walk through the Python-vs-LLM component table directly — most components are deterministic code, the LLM is used only where language interpretation is unavoidable |
| Judge asks "what does your confidence score mean?" | High (expect this) | Point to the `consistency_score` naming and disclaimer explicitly — it measures reasoning-pass agreement, not probability of correctness |

---

## 9. Calibration Notes (honest self-assessment of this plan)

- The added Python components (rule engine, contradiction detector, sanitizer,
  validator) are net time-savers, not net time-costs — deterministic code is faster
  to build and test than the LLM-reasoning steps they replace would have been, and
  they reduce live-demo failure risk by removing LLM calls from the critical path
  wherever a rule can do the job instead.
- The trimmed eval set (8–10 scenarios vs. the original 14) is a deliberate quality-
  over-coverage call — a demo win comes from a few scenarios executing flawlessly and
  legibly, not from covering every category listed in a spec.
- `insufficient_evidence` is a trust feature, not a fallback to be embarrassed about —
  rehearse presenting it as evidence the system knows its own limits, since that's
  a stronger answer to "what happens when your AI is wrong" than any accuracy number.
- The biggest real risk remains coordination, not hours — the new date/amount
  normalization requirement is the one place this revision adds a genuinely new
  failure mode; treat it as seriously as the original schema-freeze risk.