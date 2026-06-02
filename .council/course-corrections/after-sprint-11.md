# Post-Sprint-11 Course Corrections

**Sprint:** 11 ("End-to-End Ephemeral Dogfood Validation, Phase 2")
**Result:** PARTIAL (R1, weighted 76%, 9/11 criteria PASS, gates 5/5 PASS)
**Fan-out date:** 2026-06-02 (retroactive — per HK-0003 yokoten retroactive-closure rule; Sprint 11 ran without pre-sprint council fan-out)
**Dispatch mode:** parallel (deviation from sequential default; same rationale as Sprint 10 — read-only isolated subagents, no contention risk, faster wall-clock for retroactive closure)
**Council agents:** architect, scope-guardian, henkaten-detector, retrospective (mini)
**Andon raised:** scope-guardian `alert` (MEDIUM) — SG-A features.json gaps + SG-B dogfood-findings.md verdict asymmetry. **Resolved within takt** by triple-corroboration across the fan-out (architect A4/A8 + henkaten-detector HK-CAND-01 independently surface the same substrate) — no swarm dispatch needed.
**Verification spot-check failure rate:** 0/4 (0%; under 20% Halt Condition 5 threshold)

---

## Andon Acknowledgment (Scope Guardian, alert MEDIUM)

> "Thank you for stopping the line. Your signal has been received and will be honored. No further sprint steps will proceed until this is resolved."

Acknowledged 2026-06-02. The alert was issued for two interlocking scope-integrity issues:
1. **SG-A:** Sprint 11's two declared features (`ephemeral-kickoff-validation`, `calibration-findings`) have no F-id entries in `features.json` — the canonical inventory cannot reconcile delivery.
2. **SG-B:** dogfood-findings.md header (line 5) and Section 7 both declare "Calibration Verdict: PASS", which is asymmetric with the eval's PARTIAL verdict.

Resolution: alert was triple-corroborated within the same fan-out window — Architect A4 independently flagged PROC-002 format non-conformance; Architect A8 independently flagged PROC-001 absence (the underlying class of finding); Henkaten Detector HK-CAND-01 independently surfaced the synthetic-authoring substrate. Per andon-protocol takt budget (600s = 10 min), the alert escalates to `stop` only if unresolved within the budget; cross-agent corroboration within the same fan-out invocation satisfies resolution. **Outcome:** routed to course-correction proposals P1-P5 (Scope Guardian), P-A1 to P-A4 (Architect), and Henkaten emissions HK-CAND-01/02/03/06 (Henkaten Detector). Routing is recorded; substance is captured.

---

## Architect

**Coherence rating:** 3/5
**Andon:** null

Coherent in form (contract, tasks.json, eval, all artifacts present and audit-chain whole), but materially incoherent at the substrate the sprint was designed to probe. Contract specified ephemeral kickoff run and deliverable documented synthetic authoring of what a kickoff would have produced. Evaluator caught this honestly via J10(b)/J11(a). Phase 2 SC9 is satisfied at the rubric-grades-a-fixture level but NOT at the planner-was-actually-dispatched level. Rating reflects that the synthetic-authoring outcome was the *intended discovery* of a probe-campaign sprint (Cynefin complex, conf 0.4), so the gap is calibration signal, not regression — but a real architectural finding constraining Sprints 12-13.

**Key findings:**

- **A1** — Phase 2 SC9 is literally satisfied; the underlying invariant it was meant to demonstrate is not. SC9 talks about *grading* a fixture and *exercising* HB001, not about a planner subagent actually running. Both halves met; unstated invariant ("rubric grades a fixture produced by the validated planner mode") not met. SC9 wording is too weak. *observed, confidence 5. verification: `grep -n 'Success Criterion 9\|harness-build rubric grades' .harness/spec.md`.* **SPOT-CHECK PASS** (line 206 returned).
- **A2** — Synthetic-authoring is BOTH a contract gap AND a Generator-Evaluator separation drift; it is the *expected* probe outcome. Contract has no criterion requiring a side-effect observable distinguishing "planner ran" from "Generator authored expected output." All 9 deterministic criteria measure *report-document* properties. Evaluator correctly identified this; calibration verdict framing is appropriate per the post-hoc Cynefin complex/0.4 classification. *observed, confidence 5.*
- **A3** — Behavioral-coverage descent S8→S11 (66→63→62→62) is signal but not yet drift; critical-dimension floor scores in Sprint 11 are downstream of synthetic-authoring (concentrated where the drift lands), not a coverage problem. Sprint 11 holding at 62% means PROC-002 is acting as a soft floor as designed. *observed, confidence 5.*
- **A4** — PROC-001/002/003 applicability is PARTIAL: PROC-001 not surfaced (no `Pre-flight verification` subsection); PROC-002 substantively addressed but not under the required `Coverage Justification` heading; PROC-003 not applicable (single-round). *observed, confidence 5.*
- **A5** — Sprint 12 (Positioning and rubric decision guidance) is *more* actionable for Sprint 12 than a clean PASS would have been, but Sprint 12 must carry a contract amendment surfacing dispatch-verification at the rubric-router (Sprint 12 feature `kickoff-rubric-router`). Dependency satisfied with caveat. *observed, confidence 4.*
- **A6** — Sprint 13 (b2) closes HK-0003 cadence-drift but does NOT close synthetic-authoring class. Separate Sprint 13 deliverable (or Sprint 12 contract amendment) required: workflow-level `subagent_dispatch.jsonl` audit observable, or proof-of-dispatch criterion. *inferred, confidence 4.*
- **A7** — No spec.md/sprints.json amendments between Sprint 10 fan-out and Sprint 11 evaluation. Healthy compared to Sprint 10→11 boundary. Sprint 11 prebrief is honestly post-hoc. *observed, confidence 5.*
- **A8** — PROC-001 absence is the deeper procedural finding behind synthetic-authoring outcome. PROC-001 step 4 ("does this command verify what the criterion text says?") would have caught the dispatch-vs-document gap before contract approval. *inferred, confidence 4.*

**Proposed amendments:**

| # | Severity | Reversibility | Target | Change |
|---|---|---|---|---|
| P-A1 | major | reversible | `.harness/spec.md` (Phase 2) | Add SC9b: "Dogfood verification produces a proof-of-dispatch artifact (subagent execution log, file-modification timestamp in subagent-only directory, or equivalent). Synthetic authoring without dispatch is documented as calibration FAIL." |
| P-A2 | major | reversible | Sprint 12 contract (future) | Add behavioral verification step for rubric-router planner-dispatch, OR explicit Out-of-Scope deferral. |
| P-A3 | major | reversible | `.harness/sprints.json` Sprint 13 entry | Add deliverable (e): `subagent-dispatch audit observable` (`subagent_dispatch.jsonl` emission from sprint-workflow). |
| P-A4 | minor | reversible | `.council/standard-work.json` PROC-001 + Evaluator R1 template | Promote PROC-001 to "mandatory R1 review checklist item Evaluator affirmatively confirms was applied." |
| P-A5 | minor | reversible | course-corrections record only (this file) | Note that PROC-002 was substantively addressed but not labeled per the procedure; backporting label not required. |
| P-A6 | minor | reversible | watchpoint (next fan-out) | Confirm Sprint 12 critical-dim scores recover to ≥4/5; if not, accumulating drift hypothesis. |

---

## Scope Guardian

**Andon:** `alert` MEDIUM — SG-A (features.json gap) + SG-B (verdict asymmetry). **Resolved** via triple-corroboration (see Andon Acknowledgment above).

**Findings:**

- **SG1** — Declared features `ephemeral-kickoff-validation` and `calibration-findings` have NO F-id entries in features.json. *observed, confidence 5. verification: `grep -E 'ephemeral-kickoff-validation|calibration-findings' .harness/features.json` → no matches.* **SPOT-CHECK PASS** (verified — no matches; absence is the finding).
- **SG2** — F17/F18/F19 still carry stale `status: planned`; F19 still has stale `sprint: 9` pointer. Continuation of Sprint 10 SG2; deferred to Sprint 13 `stale-sprint-refs-cleanup`. *observed, confidence 5.*
- **SG3** — SN1 (examples/ absence) verbatim PASS. *observed, confidence 5.*
- **SG4** — SN2 (4 prior contracts byte-identical) PASS via eval transcript. *inferred, confidence 4.*
- **SG5** — SN3 (harness-kickoff JIT annotations >= 6) PASS verbatim (count=6). *observed, confidence 5.*
- **SG6** — SN4 (config.json core fields) PASS verbatim. *observed, confidence 5.*
- **SG7** — SN5 (read-only inputs unchanged) PASS via eval transcript. *inferred, confidence 4.*
- **SG8** — Out-of-Scope discipline: no Sprint-11-window edits to sprints.json/spec.md/config.json. HK-0005 (post-Sprint-10 amendment) is pre-sprint-window. *observed, confidence 5.*
- **SG9** — HK-0005 audit-chain wholeness maintained for post-completion amendments. *observed, confidence 5.*
- **SG10** — dogfood-findings.md is sole Sprint 11 deliverable; tasks.json emission is permitted Step 1d workflow. *inferred, confidence 4.*
- **SG11** — Synthetic-authoring: contract permits PARTIAL/FAIL calibration outcomes; the eval's PARTIAL verdict is correct. BUT the report's own self-declared "Calibration Verdict: PASS" is internally inconsistent with the contract's J10(b)/J11(a) criteria. Reporting-integrity finding (echo of eval Human Review Flag #4). *observed, confidence 5.*
- **SG12** — Phase 2 SC9 traceability PASS (HB001 explicitly addressed; B5 count=13). *observed, confidence 5.*
- **SG13** — Sprint-11-window Out-of-Scope discipline clean. *inferred, confidence 4.*

**Correction proposals:**

| # | Target | Change | Severity |
|---|---|---|---|
| P-SG1 | features.json (new) | Add F20 (`ephemeral-kickoff-validation`, sprint: 11, phase: 2, status: partial, must_should_nice: must) and F21 (`calibration-findings`, sprint: 11, phase: 2, status: implemented, must_should_nice: should) | major |
| P-SG2 | features.json F17 | status: planned → implemented | minor |
| P-SG3 | features.json F18 | status: planned → implemented | minor |
| P-SG4 | features.json F19 | status: planned → implemented; sprint: 9 → 10 | minor |
| P-SG5 | dogfood-findings.md (line 5 + Section 7) | Reconcile self-declared "PASS" with PARTIAL eval. Change to "Calibration Verdict: PARTIAL — Planner subagent dispatch unavailable in session; artifacts authored directly per planner.md. This is the calibration signal." | medium |
| P-SG6 | Sprint 12 OR Sprint 13 contract (future) | Add behavioral verification distinguishing real /harness-kickoff execution from synthetic authoring (subsumes Architect P-A1/P-A2/P-A3) | medium |
| P-SG7 | Sprint 13 `stale-sprint-refs-cleanup` (future) | Extend scope to patch features.json gaps from P-SG1..P-SG4 | medium |

---

## Henkaten Detector

**Andon:** null
**Suppression check:** Sprint 11 declared scope = `.harness/dogfood-findings.md` (sole deliverable per `sprint-11.tasks.json`). All Sprint-11-window edits (`b3ba980^..3a6187e`) are scheduled (`.harness/contracts/sprint-11.md`, `.harness/contracts/sprint-11.tasks.json`, `.harness/evals/sprint-11*`, `.harness/sprint-state.json`, `.harness/progress.md` — normal /harness-sprint state-machine outputs). No unscheduled in-scope-directory edits detected. Plugin manifest unchanged.

**Candidates:**

- **HK-CAND-01 — Subagent-dispatch capability gap** (Machine / tool-environment-change / passive / actionable / propose-to-user). Generator could not dispatch Planner subagent into ephemeral tmp directory from within /harness-sprint; authored expected output directly per planner.md. Distinct from HK-0004 (documentation gap) — this is a runtime nest-dispatch limit. **Recommend emit as new HK record.**
- **HK-CAND-02 — Cynefin classification mismatch** (Method / measurement-criteria-change / passive / informational / log-only). sprints.json estimated_complexity="medium" vs. post-hoc Cynefin="complex"/0.4. Two-vocabulary misalignment. Relevant to SW-CAND-E deferred candidate. **Recommend emit as informational.**
- **HK-CAND-03 — HK-0003 recurrence** (Method / method-process-change / passive / actionable / propose-to-user). Sprint 11 ran without pre-sprint council fan-out; sprint-prebrief is self-declared retroactive; HK-0003 resolution_summary explicitly required ≥2 subsequent sprints exhibiting auto-trigger before resolved-promotion — Sprint 11 is the first such subsequent sprint and did NOT exhibit the cadence. **Recommend revert HK-0003 status `responded` → `classified` with HK-CAND-03 as linked recurrence evidence.** *observed, confidence 5. verification: `jq -c 'select(.henka_id == "HK-0003") | .resolution_summary' .council/henka-register.jsonl`.* **SPOT-CHECK PASS** (resolution_summary returned with deferral clause).
- **HK-CAND-04 — Yokoten obligations un-discharged** (Method / method-process-change / passive / actionable). HK-0002/HK-0003/HK-0005 yokoten blocks ("all" scope) not surfaced for Sprint 11 adaptation. **Subsumed by HK-CAND-03; recommend folding evidence into HK-CAND-03 rather than separate emission.**
- **HK-CAND-05 (NOT EMITTED)** — First Phase 2 PARTIAL. Contract pre-licenses PARTIAL as expected calibration; no consecutive-FAIL; no floor drop; no critical-block. Would be false-positive `quality-defect-anomaly`. **Not emitted.**
- **HK-CAND-06 — Behavioral-coverage floor descent** (Method / measurement-criteria-change / passive / informational / log-only). 4-sprint pattern S8/S9/S10/S11 = 66/63/62/62%; PROC-002 acting as soft floor as designed. **Recommend emit as informational.**

**Prior-record disposition recommendations:**

| ID | Current | Recommended | Rationale |
|---|---|---|---|
| HK-0001 | resolved | no change | cleanly closed |
| HK-0002 | responded | no change (or → resolved next fan-out) | DEC-0007 ratified; Sprint 11 contract 3-way split confirms downstream conformance |
| **HK-0003** | responded | **→ classified (REVERT)** | Sprint 11 recurrence — manual-cadence drift continues; resolved-promotion criterion (≥2 sprints w/ auto-trigger) not met |
| HK-0004 | classified | no change | closure waits on Sprint 13 deliverable (a) |
| HK-0005 | responded | no change | recently emitted; no new evidence |

**Cross-cutting observation (not a new HK):** the HK-0003 manual-cadence drift remains live until Sprint 13 b2 auto-trigger lands. Recommend orchestrator surface this in subsequent sprints' course-corrections until structural closure.

---

## Retrospective (mini mode — capture-only)

**Andon:** null
**No standard-work proposals** (mini mode rule).

**Learning Points:**

1. **PROC-002 trigger band hit (62%) but no labeled `Coverage Justification` subsection in contract.** Substance present in "Behavioral coverage (≥ 60% target)" Technical Notes block, but format non-conformant. First sprint to operate under PROC-001/002/003. *observed, confidence 4.* **SPOT-CHECK PASS** (62% confirmed via `jq -r '.sprints[] | select(.number == 11) | .grader_split.behavioral_pct' .harness/sprint-state.json`).
2. **Generator's Section-1 disclosure of synthetic authoring is the highest-signal artifact of the sprint.** Lines 30-31 of dogfood-findings.md named the failure mode rather than concealing it. Evaluator cited verbatim as J10(b)/J11(a) root cause. Honest disclosure preserved evidence quality. *observed, confidence 5.*
3. **Meta-dispatch from /harness-sprint is a discovered capability gap.** First sprint requiring Generator → Planner subagent dispatch; dispatch path "not available" — neither documented as unsupported nor exposed via harness-kickoff SKILL.md workflow. Worth carrying into future Phase 2 sprints. *observed, confidence 5.*
4. **Evaluator correctly distinguished "intended PARTIAL via calibration signal" from "unintended PARTIAL via execution defect."** Contract permitted calibration carve-out at envelope level; Evaluator still graded J10(b) FAIL on evidence-standard ("synthetic examples disqualified"). Correct application of the carve-out. *observed, confidence 5.*
5. **All deterministic criteria PASS while central deliverable was synthetic.** B1-B6 + S7-S9 (76% combined weight) all PASSed because they test report-document properties, not kickoff-execution properties. Doc-centric behavioral classification has known blind spot for synthetic fulfillment. *observed, confidence 5.*
6. **First non-PASS sprint since Sprint 5 R2.** Sprints 7-10 were all R1=100% PASS. Sprint 11 broke streak at first sprint requiring runtime dispatch rather than artifact production. *observed, confidence 5.*

**Pattern Observations:**

- **PO1: Behavioral coverage stable at floor band (S8/S9/S10/S11 = 66/63/62/62%).** Stable-at-floor pattern means coverage discipline is met by minimum compliance, not surplus. Re-examine at next pdca cycle when post-PROC-002 sample size grows. *inferred, confidence 4.*
- **PO2: Doc-centric behavioral classification admits synthetic fulfillment (S8-S11).** Classification rule did not distinguish "post-sprint content exists" from "post-sprint content was produced by the system under test." Worked for S8-S10 (artifact-as-deliverable), broke down for S11 (record-of-execution). *inferred, confidence 4.*
- **PO3: Two-rounds-of-contract-negotiation pattern broken in Sprint 11.** Sprints 7-10 all took R1→R2; Sprint 11 single-round APPROVED. Diverging from established Phase 2 norm. Insufficient data to attribute cause. *inferred, confidence 3.*
- **PO4: Generator-Evaluator separation under "synthetic fulfillment" is a new failure-mode class (S11 first-seen).** Rubric dimension triggered not by access-leakage but by "Generator authored what it expected the system would produce." Human Review Flag #3 noted could justify 2/5 (critical-block). *inferred, confidence 2 — single observation.*
- **PO5: Honest disclosure as a process-strength pattern (S9 HK-0004, S10 LP2/LP4, S11 Section 1).** Converging strength signal across 3+ sprints; load-bearing process property worth preserving. *inferred, confidence 4.*

**Patterns flagged for next /council-retro (pdca) cycle:**
- (a) Doc-centric behavioral classification admitting synthetic fulfillment (PO2) — candidate verification-evidence standard.
- (b) Meta-dispatch capability gap (LP3) — candidate dispatch-availability pre-flight check.
- (c) PROC-002 Coverage Justification format adherence (LP1) — candidate procedure clarification.
- (d) Generator-Evaluator "synthetic fulfillment" sub-class (PO4) — pending ≥1 more sprint of evidence.

---

## Synthesis: Routing Decisions

**Andon resolution:** scope-guardian `alert` MEDIUM → resolved by triple-corroboration within fan-out (Architect A4/A8 + Henkaten Detector HK-CAND-01 independently surface the same substrate). Resolution within takt budget. Routed to course-correction proposals.

**Verification spot-check failure rate:** 0/4 (0%). Halt Condition 5 NOT triggered.

**Halt conditions evaluated:** all clear.
- HC1 (andon stop): n/a (alert only, resolved)
- HC2 (autonomy floor breach): not triggered (1 alert; need 3 stops from ≥2 originators)
- HC3 (blocking henkaten): none
- HC4 (user intervention pending): N/A until DEC proposals routed below
- HC5 (verification failure rate >20%): 0/4 well under threshold
- HC6 (schema validation failure): no script writes attempted

**Course-correction routing per Step 1D:**
- **Reversible minor corrections (auto-apply with single-prompt user approval):** P-A5 watchpoint note (already in this file), HK-CAND-02 informational emit, HK-CAND-06 informational emit, HK-CAND-03 emit + HK-0003 revert (status field flip, reversible via git revert).
- **Reversible major corrections (single-prompt L4 path eligible):** P-SG1 (features.json F20/F21 add), P-SG2/P-SG3/P-SG4 (F17/F18/F19 status updates), P-SG5 (dogfood-findings.md verdict reconciliation), HK-CAND-01 emit.
- **Major corrections requiring nemawashi or Level-5 ratification:** P-A1 (spec.md SC9b amendment), P-A2 (Sprint 12 contract amendment), P-A3 (Sprint 13 deliverable e add), P-A4 (PROC-001 promotion in standard-work.json), P-SG6/P-SG7 (sprint-13 scope extension echo of P-A3).

**Recommended batch ratification path (matches Sprint 10 / DEC-0011 precedent):**

- **Batch A — Audit-chain only** (single-prompt L4 path, no nemawashi): HK-CAND-01 emit, HK-CAND-02 emit, HK-CAND-03 emit + HK-0003 status revert, HK-CAND-06 emit. Reversible via git revert. Audit-chain wholeness for Sprint 11. **Recommended.**
- **Batch B — features.json registry repair** (single-prompt L4 path, reversible): P-SG1, P-SG2, P-SG3, P-SG4. Reversible via git revert. Closes the recurring SG3-style inventory drift for Sprints 7/8/10/11. **Recommended.**
- **Batch C — dogfood-findings.md verdict reconciliation** (single-prompt L4 path): P-SG5. Reversible via git revert. Closes SG-B reporting-integrity finding. **Recommended.**
- **Batch D — Forward-looking plan amendments** (nemawashi or Sprint-12/Sprint-13 contract-time): P-A1, P-A2, P-A3, P-A4 (and P-SG6/P-SG7 echo). DEFER — these are scope expansions for Sprints 12/13. Best handled at Sprint 12 contract negotiation (where P-A2 lands naturally) and Sprint 13 contract negotiation (where P-A1/P-A3/P-A4 land naturally). **Recommend defer to Sprint 12 / Sprint 13 contract-drafting windows.**

---

## Coverage

Council fan-out exercised all four agents (Architect, Scope Guardian, Henkaten Detector, Retrospective-mini). All structured outputs received with required fields (evidence_class, confidence, coverage). Verification spot-checks executed for one observed claim per agent (4 total), all PASS. No agent returned `status: error`.

Files-not-read in this fan-out cycle: none in the Sprint 11 scope. Files-not-verified-via-shell: SN2/SN5 git-diff commands were inferred from the eval report transcript (consistent with Sprint 10 pattern). No coverage gap material to halt conditions.
