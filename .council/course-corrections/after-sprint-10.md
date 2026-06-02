# Post-Sprint-10 Course Corrections

**Sprint:** 10
**Result:** PASS (R1, weighted 100%, gates 5/5)
**Fan-out date:** 2026-06-01
**Dispatch mode:** parallel (deviation from sequential default; rationale: read-only isolated subagents, no contention risk, faster wall-clock)
**Council agents:** architect, scope-guardian, henkaten-detector, retrospective (mini)
**Andon raised:** scope-guardian `alert` (SG5 — B7 verification command vacuously passing). **Resolved within takt** via architect swarm follow-up.

---

## Architect

**Coherence rating:** 5/5
**Andon:** null

**Key findings:**

- **A1** — Sprint 10 delivers F19 (Harness-build Planner mode) in conformance with Phase 2 vision. *observed, confidence 5.*
- **A2** — DEC-0006 (A6) `playbook_stage` scoping honored: zero occurrences in default-path Artifact 2 block; confined to `## Harness-Build Mode` section. *observed, confidence 5.*
- **A3** — All 5 SN1 verbatim backward-compat anchors return count=1; Rules section's 7 bullets preserved. *observed, confidence 5.*
- **A4** — All 7 stage names match `rubrics/harness-build.md` verbatim. *observed, confidence 5.*
- **A5** — Dual-signal mode detection (config.json + prompt keyword) is architecturally sound. *observed, confidence 5.*
- **A6** — features.json F19 entry is stale (`sprint: 9`, `status: planned`); should be `sprint: 10, status: implemented`. **Deferred** to Sprint 13 `stale-sprint-refs-cleanup`. *observed, confidence 5.*
- **A7** — spec.md "sprints 10-12 planned" line is stale post-Sprint-10. **Deferred** to Sprint 13. *observed, confidence 4.*
- **A8** — Sprint 11 dogfood preconditions met (S7+S8+S10 all PASS). *observed, confidence 5.*
- **A9** — Sprint 13 amendment (71ce8e7) is symmetric and coherent: b1 (pre-sprint advisory) + b2 (post-sprint mandatory auto-trigger) share config trigger + andon-stop protocol. Closure-by-construction for HK-0003. *observed, confidence 5.*
- **A10** — HK-0003 / HK-0004 still classified; closure scheduled for Sprint 13. *observed, confidence 5.*
- **A11** — planner.md 70 → 179 lines: well within bounds, no documented limit on agent files. *observed, confidence 4.*

**Proposed amendments (deferrable to Sprint 13 contract):**

- **Amendment-1** (minor) — Sprint 13 contract should add a criterion specifying what happens if `/henkaten-council:council-autorun` exits non-zero or times out (surface error, write stub course-corrections, or treat as andon-stop).
- **Amendment-2** (minor) — Sprint 13 should clarify whether b2 auto-trigger fires for non-PASS sprints. Recommended default: yes (failure is exactly when council attention matters most).

---

## Scope Guardian

**Andon:** `alert` — SG5 (B7 verification command vacuously passing). **Resolved** via architect swarm follow-up.

**Findings:**

- **SG1** — All three Sprint 10 features delivered, named correctly, undistorted: `planner-harness-build-mode`, `stage-aligned-decomposition`, `playbook-stage-traceability`. *observed, confidence 5.*
- **SG2** — features.json F17/F18/F19 carry stale `planned` status; F19 also has stale `sprint: 9` pointer. *observed, confidence 5.*
- **SG3** — Two Sprint 10 feature slugs (`stage-aligned-decomposition`, `playbook-stage-traceability`) have no F-id in features.json. Pre-existing baseline gap. *observed, confidence 5.*
- **SG4** — A6 invariant honored by inspection: all 10 `playbook_stage` occurrences in planner.md are at lines ≥ 96, inside `## Harness-Build Mode`. *observed, confidence 5.*
- **SG5** — **(ALERT, MEDIUM)** B7 verification command vacuously passes. The awk anchor `/^## Artifact 2/` matches no heading in planner.md — the actual heading is `### Artifact 2:` (h3). PASS verdict still correct (A6 invariant honored by inspection), but the gate provides zero protective signal for future sprints. R2 reviewer asserted the anchor worked without independent verification. *observed, confidence 5.*
- **SG6** — All 5 SN gates verifiably PASS the verbatim re-check. *observed, confidence 5 (SN1, SN3); inferred, confidence 4 (SN2, SN4, SN5).*
- **SG7** — Sprint 13 plan amendment (71ce8e7) extends deliverable (b) from singular pre-sprint gate to bidirectional gates without a separate DEC entry. Pattern-matches HK-0003's documented failure mode (orchestrator-initiated plan amendment outside council fan-out). Recommends DEC-0011 to capture user in-session authorization. *observed, confidence 4.*
- **SG8** — Sprint 13's `protects_prior` correctly bounds the SN2 carve-out (renumbering-only). *observed, confidence 5.*
- **SG9** — Sprint 10 sole-file-modified claim consistent with evidence. *inferred, confidence 4.*
- **SG10** — Plan amendment 71ce8e7 confined to declared files (sprints.json + spec.md). *inferred, confidence 4.*

**Correction proposals:**

| # | Target | Change | Severity |
|---|---|---|---|
| P1 | features.json F17 | `status: planned → implemented` | minor |
| P2 | features.json F18 | `status: planned → implemented` | minor |
| P3 | features.json F19 | `status: planned → implemented`, `sprint: 9 → 10` | minor |
| P4 | features.json (new) | Add canonical entries for `stage-aligned-decomposition` and `playbook-stage-traceability` | major (scope inventory completeness) |
| P5 | decision-log.jsonl | Append DEC-0011 ratifying 71ce8e7 b1→b1+b2 extension under user in-session authorization | major (audit chain integrity) |
| P6 | Sprint 13 contract (future) | Fix B7 awk anchor in sprint-10.md (under SN2 carve-out) | medium |

---

## Henkaten Detector

**Andon:** null

**Suppression check:** Sprint 10 deliverables (planner.md, .harness/* state files written by Step 5 workflow, eval/contract artifacts) are all `scheduled` — suppressed. Two files outside Sprint 10 scope were touched in the review window: `.harness/sprints.json` and `.harness/spec.md` via commit 71ce8e7 (post-Sprint-10 plan amendment). One composite Henkaten candidate fired.

**Candidate:**

- **HK-CAND-01** — Sprint 13 scope extension (71ce8e7 plan amendment).
  - `sprint_context: 10` · `fourM_axis: Method` · `category: scope-change` · `change_origin: active` · `impact_level: actionable`
  - User-authorized in-session 2026-06-01; reversible (git revert); strengthens governance rather than weakens.
  - `response_type: log-only` — already user-authorized & DEC-0010-ratified; appending HK-0005 completes the audit chain.

**Prior-record disposition recommendations:**

| ID | Current | Recommended | Rationale |
|---|---|---|---|
| HK-0001 | resolved | no change | cleanly closed |
| HK-0002 | responded | no change (or → resolved at next fan-out) | DEC-0007 ratified; downstream-conformed via Sprint 9 schema port |
| **HK-0003** | classified | **→ responded** | Sprint 10 ran with council fan-out; DEC-0010 + HK-CAND-01 institutionalize closure via Sprint 13 b2 auto-trigger. `resolved` deferred until S13 lands. |
| HK-0004 | classified | no change | closure waits on Sprint 13 deliverable (a) — workflow-step port |

---

## Retrospective (mini mode — capture-only)

**Andon:** null
**No standard-work proposals** (mini mode rule).

**Learning Points:**

1. The Evaluator caught a real B7 ambiguity that would have failed a correct implementation. Fix via `awk`-bounded extraction was specific and verified. *observed, confidence 5.*
2. The "7 rules vs 6 rules" miscount in J11/SN1 was a self-contradicting count-vs-enumeration error caught by simple counting. R2 fix was partial — J11(c) corrected to "7", but SN1 prose retained "six rules" with a clarifying note bolted on. *observed, confidence 5.*
3. planner.md grew 70 → 179 lines (+155%); harness-build extension is ~109 lines. Fine for one mode; if Phase 2 keeps appending mode sections (rag-system, cli-tool, etc.) file will balloon. *observed, confidence 4.*
4. B5 is acknowledged-redundant with SN1 and self-violates the contract's own behavioral classification rule (pre-sprint ≠ post-sprint expected). 8% behavioral weight on a partly-redundant criterion. *observed, confidence 4.*
5. Single-commit implementation landed clean; R1 PASSed all 11 criteria + 5/5 gates with no retries. Friction is upstream (contract drafting), not in build. *observed, confidence 5.*

**Pattern Observations (for next pdca cycle):**

- **Evaluator-catches-contract-bug** is now consistent across S8/S9/S10 — three sprints, three R1 NEEDS REVISIONs citing deterministic flaws. Reliable strength of the loop AND signal that Generator pre-flight is weak. *inferred, confidence 4.*
- **Behavioral coverage trending toward the 60% floor in Phase 2:** S8=66%, S9=63%, S10=62%. Downward trend may indicate cost-minimizing behavior (target just-above-floor); flagged for pdca. *inferred, confidence 3.*
- **Contract negotiation rounds > implementation rounds** is the Phase 2 default. Sprints 7-10 all took R1→R2 contract; all four passed implementation in R1. Cost migrated upstream. *observed, confidence 4.*

---

## Verification Spot-Checks (Step 1C.4)

All four agent claims independently re-verified by the orchestrator. Each sample claim was randomly chosen from the agent's `observed` claims.

| Agent | Sampled claim | Command | Expected | Observed | Verdict |
|---|---|---|---|---|---|
| architect | A2: SN1 anchors intact | `grep -c '^- \*\*Stay at the product level\.' planner.md` && `grep -c '^- \*\*estimated_complexity\*\*' planner.md` | 1, 1 | 1, 1 | PASS |
| scope-guardian | SG4: playbook_stage location | `grep -n 'playbook_stage' planner.md` first match | line ≥ 96 | line 96 | PASS |
| henkaten-detector | HK-CAND-01: amendment language present | `grep -cE 'bidirectional\|post-sprint auto-trigger\|post-Sprint-10 per user' sprints.json` | ≥ 1 | 1 | PASS |
| retrospective | size growth point | `wc -l plugins/trine-eval/agents/planner.md` | 179 | 179 | PASS |

**Spot-check failure rate: 0/4 = 0%.** Well under the 20% threshold (Halt Condition 5).

**Bonus verification (architect-proposed B7 fix):** `awk '/^### Artifact 2:/,/^## [A-Z]/' planner.md | grep -c 'playbook_stage'` returns **0** (the corrected gate would PASS — A6 invariant honored).

---

## Andon Alert Resolution (SG5 → architect swarm)

- **Originator:** scope-guardian
- **Type:** alert
- **Reason:** B7 verification command's `awk '/^## Artifact 2/,/^## [A-Z]/'` matches no heading in planner.md (actual is `### Artifact 2:` at line 28). Gate is vacuously passing. Audit-correctness, not execution risk.
- **Swarm:** scope-guardian + architect (per `swarm_request: ["architect"]`)
- **Architect concurrence:** CONCUR with SG5 — Sprint 10 PASS verdict still valid (A6 invariant honored by inspection per prior A2 finding); root cause is R2 reviewer transcription error (asserted awk anchor matches without independent grep verification).
- **Resolution:** alert → resolved (within takt — 600s budget, resolved in ~5min)
- **Fix routing:** Sprint 13 deliverable (d) under SN2 carve-out — one-line anchor fix to sprint-10.md changing `/^## Artifact 2/` to `/^### Artifact 2:/` with boundary `/^## [A-Z]\|^### [A-Z]/`.
- **Process improvement note:** R2 fix verifications must run the literal command, not reason about it. Captured in retrospective LP1 + Architect rec for Sprint 13.
