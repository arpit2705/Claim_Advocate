# Claim Advocate — 24-Hour Design Plan (Team of 2)

Track 2 — AI-Powered Financial Journeys | 24-hour hackathon format
*Companion to `architecture.md` — see that file for component design, schemas, API, and tech stack.*

Phases are grouped by layer (Planning → Backend → Frontend → Integration & Testing →
Presentation) so each person can see their own track clearly, while the hour ranges
stay synchronized across layers.

---

## 1. Feature List — Feasibility Classification

### 1.1 Must-have (core differentiator — cutting any of these guts the pitch)

**Shared core**
- [ ] Structured policy extraction, schema-enforced
- [ ] Clause embedding + retrieval layer
- [ ] Grounding verifier (shared logic, used by both modules)

**Module A — Pre-Submission Readiness**
- [ ] Structured extraction of submission evidence
- [ ] Readiness engine (evidence vs. matched clause requirements)
- [ ] Prioritized fix-list generator
- [ ] 3 core scenarios: missing document, inconsistent dates, genuinely ready

**Module B — Post-Rejection Adjudication**
- [ ] Structured extraction of rejection letters
- [ ] Adjudication engine with self-consistency confidence (2–3 passes)
- [ ] Appeal letter generation for questionable/misapplied verdicts
- [ ] Plain-language explanation for valid verdicts
- [ ] 3 core scenarios: valid / misapplied / ambiguous

**Calculation:** shared core (~5 hours, built together) + Module A (~6–7 hours, one
owner) + Module B (~7–8 hours, one owner, run in parallel with Module A) — total
critical path is roughly shared-core-time plus the longer of the two modules, not
the sum of both, because they run in parallel. Fits inside 24 hours with real margin.

### 1.2 Should-have (strengthens the pitch, cut first if behind schedule)

- [ ] Eval harness with quantified accuracy across both modules (8–10 scenarios each)
- [ ] Two-tab dashboard clearly showing "Before you submit" / "If you're rejected"
- [ ] Pass-by-pass transparency for Module B's self-consistency runs

**Calculation:** roughly 4–5 additional hours, mostly frontend + eval-run time.
If behind schedule, cut eval scenario count per module from 8–10 down to 5 rather
than dropping either module's eval entirely.

### 1.3 Stretch (only attempt if §1.1 and §1.2 are done and stable by hour 19)

- [ ] Lending-rejection counterfactual as a third, smaller journey
- [ ] Multi-clause handling (a case citing more than one clause, adjudicated independently)

**Calculation — honest read:** treat these purely as Q&A talking points. Do not start
either before both modules are fully stress-tested.

### 1.4 Explicitly cut (do not build, even if time remains)

- User accounts / authentication
- Persistent database beyond the demo session
- Multi-insurer clause libraries or a general-purpose policy database
- Visual polish beyond functional clarity
- Real IRDAI/insurer API integration (use static sample documents throughout)

---

## 2. Planning Phase (Hour 0–2, together)

- Finalize schemas from `architecture.md` §4 for both modules
- Hand-write scenarios: 3 for Module A (missing doc, inconsistent dates, ready),
  3 for Module B (valid, misapplied, ambiguous) — 6 hero scenarios total
- Agree on API contract (endpoint names, request/response shapes) so backend and
  frontend can be built without waiting on each other later
- **Deliverable:** schemas locked, 6 scenarios written, API contract agreed by both
  people. Nothing in this contract changes after Hour 2 without both people signing off.

---

## 3. Backend Phases

### Backend Phase 1 — Shared Core (Hour 2–7, together)
- Extraction Agent (policy + both input types) — Person 1 leads
- Clause Embedding Index + Retrieval Layer — Person 2 leads, integrated together
- Grounding Verifier — built together since both modules depend on it identically
- **Deliverable:** `/extract-policy` working; retrieval returns sane matches for all
  6 scenarios; schema frozen from this point on

### Backend Phase 2A — Module B Engine (Hour 7–15, Person 1)
- Hour 7–11: Adjudication Engine with self-consistency (2–3 passes)
- Hour 11–14: Grounding-checked Explanation Generator + Appeal Drafting Agent
- Hour 14–15: Test against all 3 Module B scenarios, fix failures
- **Deliverable:** `/adjudicate`, `/draft-appeal`, `/adjudication/pipeline` all
  returning correct, grounded results for the 3 Module B scenarios

### Backend Phase 2B — Module A Engine (Hour 7–15, Person 2, parallel to 2A)
- Hour 7–10: Readiness Engine (evidence vs. clause requirements)
- Hour 10–13: Prioritized fix-list generator
- Hour 13–15: Test against all 3 Module A scenarios, fix failures
- **Deliverable:** `/readiness/check`, `/readiness/pipeline` returning correct,
  grounded results for the 3 Module A scenarios

### Backend Phase 3 — Eval Harness (Hour 15–17, split then merged)
- Each person builds eval runs for their own module's scenario set
- Merge into a single `/eval/run` reporting both modules' accuracy
- **Deliverable:** real accuracy numbers for both modules (e.g. "Module A: 9/10,
  Module B: 8/10") — backend work is functionally complete after this phase

---

## 4. Frontend Phases

### Frontend Phase 1 — UI Shell (can start Hour 15, Person 2, once Module A backend is stable)
- Build the two-tab page layout: "Before you submit" (Module A) and "If you're
  rejected" (Module B), with placeholder/mock data first
- **Deliverable:** static shell navigable end-to-end, not yet wired to real endpoints

### Frontend Phase 2 — Wire to Backend (Hour 17–20, together, Person 2 leads)
- Connect both tabs to their respective pipeline endpoints (`/readiness/pipeline`,
  `/adjudication/pipeline`)
- Build the results views: readiness score + fix list (Module A), verdict + matched
  clause + appeal draft (Module B)
- **Deliverable:** working end-to-end UI for both modules, using real backend responses

---

## 5. Integration & Testing Phases

### Integration Phase 1 — Stress-Test (Hour 20–22, together)
- Run all 6 hero scenarios end-to-end, live, multiple times, across both modules
- Fix any brittleness — non-negotiable at 24 hours with two modules in play
- Confirm switching between the two tabs doesn't break either module's state
- **Deliverable:** all 6 hero scenarios reproducible on demand, no crashes

---

## 6. Presentation Phase

### Presentation Phase 1 — Deck & Rehearsal (Hour 22–24, together)
- Finalize the PPT with real numbers from Backend Phase 3 for both modules
- Include the two-module architecture diagram and ownership split as evidence of
  deliberate scope, not scope creep
- Rehearse the pitch split by module — each person demos the module they built
- **Deliverable:** demo-ready deck, rehearsed pitch, 6 scenarios locked

---

## 7. Phase Timeline at a Glance

| Hour | Planning | Backend | Frontend | Integration | Presentation |
|---|---|---|---|---|---|
| 0–2 | Scope & scenarios (together) | — | — | — | — |
| 2–7 | — | Shared core (together) | — | — | — |
| 7–15 | — | Module B (P1) / Module A (P2), parallel | — | — | — |
| 15–17 | — | Eval harness (split → merged) | UI shell starts (P2) | — | — |
| 17–20 | — | — | Wire to backend (together) | — | — |
| 20–22 | — | — | — | Stress-test (together) | — |
| 22–24 | — | — | — | — | Deck & rehearsal (together) |

---

## 8. Risk Register

| Risk | Likelihood | Mitigation |
|---|---|---|
| Schema/API contract drift between backend and frontend | High if not managed | Freeze the contract at end of Planning Phase (Hour 2); any change after that requires both people's sign-off |
| One backend module finishes late and delays frontend wiring | Medium | Both modules are scoped to roughly equal effort (§1.1); if one runs over, cut that module's should-have items (§1.2) first |
| Extraction fails on messy/scanned PDFs | Medium | Use clean, text-based sample PDFs throughout for both modules |
| Self-consistency passes disagree unpredictably (Module B) | Medium | If passes disagree on >30% of scenarios, fall back to a simpler confidence heuristic |
| Live demo network/API latency | Low-medium | Pre-run and cache responses for all 6 hero scenarios as a fallback |
| Judges perceive two modules as two disconnected demos | Medium | Frame the pitch explicitly as "one engine, two moments" and show the shared core in the architecture diagram |
| Judge asks "how do you know it's not hallucinating" | High (expect this question) | Point directly to the shared Grounding Verifier (`architecture.md` §3) — same answer covers both modules |

---

## 9. Calibration Notes (honest self-assessment of this plan)

- The two-module scope is justified specifically *because* it's a team of two with a
  genuinely shared core — a solo builder should not attempt this.
- Module A is intentionally scoped lighter (checklist-style reasoning) than Module B
  (multi-pass adjudication) — this isn't an oversight, it reflects that pre-submission
  readiness is a genuinely simpler reasoning task.
- The biggest real risk in this plan is coordination, not hours — contract drift after
  the Planning Phase is the single most likely thing to cost time on the day. Treat the
  Hour 2 freeze as a hard rule, not a suggestion.
- Frontend Phase 1 starting at Hour 15 (before backend is fully done) is intentional —
  building the UI shell against mock data while Module A's backend is being finished
  avoids frontend sitting idle, but only works because the API contract was frozen at
  Hour 2. Without that freeze, this parallelization would backfire.