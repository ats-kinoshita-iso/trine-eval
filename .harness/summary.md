# Eval Summary

## Overview

- Sprints completed: **10** (Phase 1: 1–5; Phase 2: 6–10)
- Final pass rate: **100%** — all 139 criteria + gates passed after retries (114 success + 25 gates)
- First-round pass rate: **98.6%** — 137/139 passed without retry
- Average rounds per sprint: **1.2** — 8 sprints PASSED on round 1; 2 sprints (4, 5) needed round 2
- All five rubric dimensions exceed the 4/5 floor as of Sprint 10
- Phase 2 closed **all 10 gaps** identified by the gap analysis at `.harness/playbook-alignment-2026-04.md`

## Consistency Metrics

For Phase 2 sprints (6–10), `config.trials == 1`, so per-trial pass rate `p = round-1 pass rate` and pass@1 = pass^1 = p. For Phase 1 sprints (1–5), the harness predates the trial loop — only round files exist, so consistency is reported as the **deprecated `pass@rounds` / `pass^rounds`** retry-derived metric per `skills/harness-summary/SKILL.md`. Statistically valid pass@k / pass^k requires at least 2 trials per round; this project ran every sprint at `trials = 1`, so the trial-based metric is degenerate and the reportable consistency signal is the round-1 pass rate.

| Sprint | p (R1 success+gate) | k (rounds) | pass@k | pass^k | Notes |
|--------|---------------------|------------|--------|--------|-------|
| 1 | 1.000 | 1 | 100.0% | 100.0% | Phase 1 — single round |
| 2 | 1.000 | 1 | 100.0% | 100.0% | Phase 1 |
| 3 | 1.000 | 1 | 100.0% | 100.0% | Phase 1 |
| 4 | 0.917 | 2 | 99.3% (deprecated `pass@rounds`) | 84.0% (deprecated `pass^rounds`) | Phase 1 — R1 FAIL on C8 (PostToolUse hook only echoed) |
| 5 | 0.929 | 2 | 99.5% (deprecated `pass@rounds`) | 86.2% (deprecated `pass^rounds`) | Phase 1 — R1 FAIL on C10 (bootstrap integration not referenced) |
| 6 | 1.000 | 1 | 100.0% | 100.0% | Phase 2 kickoff — `config.trials==1`, single-trial mode |
| 7 | 1.000 | 1 | 100.0% | 100.0% | Phase 2 |
| 8 | 1.000 | 1 | 100.0% | 100.0% | Phase 2 — contract took 2 negotiation rounds (eval R1 PASS) |
| 9 | 1.000 | 1 | 100.0% | 100.0% | Phase 2 |
| 10 | 1.000 | 1 | 100.0% | 100.0% | Phase 2 |

- Overall first-round pass rate: **98.6%** (137/139)
- Overall pass^k (Phase 2 only, valid metric): **100%** (5 sprints all PASS at trials=1)
- Phase 1 deprecated pass^rounds average: **94.0%**
- Consistency gap (overall): **1.4%** — one round-1 failure in Phase 1 (Sprint 4 C8) and one in Phase 1 (Sprint 5 C10); zero round-1 failures in Phase 2. Both Phase 1 R1 failures were cross-file integration defects, not capability gaps.

**Important caveat on the consistency metric.** With `trials == 1` across all 10 sprints, this project produced **no statistically valid pass@k / pass^k consistency measurement**. The first-round pass rate is the strongest consistency signal available, and it is 98.6% across the meta-eval. To produce a valid consistency metric, the planned synthetic verification sprint would set `trials >= 3` and re-run a representative sample at fixed code state.

## Per-Sprint Results

| # | Title | Verdict | Rounds | Success Criteria | Gates | Weighted | First-Round | Edge Case Pass Rate |
|---|-------|---------|--------|------------------|-------|----------|-------------|---------------------|
| 1 | Grading hierarchy & contract structure | PASS | 1 | 13/13 | 2/2 | 100% | 100% | N/A |
| 2 | Evaluator separation & isolation | PASS | 1 | 9/9 | 2/2 | 100% | 100% | N/A |
| 3 | Metrics, saturation, & summary upgrades | PASS | 1 | 9/9 | 2/2 | 100% | 100% | N/A |
| 4 | Context engineering & structured state | PASS | 2 | 10/10 | 2/2 | 100% | 91.7% | N/A |
| 5 | Bootstrap, calibration, & ACI | PASS | 2 | 12/12 | 2/2 | 100% | 92.9% | N/A |
| 6 | Statistical foundation (trials, sandbox, tasks.json) | PASS | 1 | 12/12 | 3/3 | 100% | 100% | N/A |
| 7 | Capability/regression dual-track | PASS | 1 | 13/13 | 3/3 | 100% | 100% | N/A |
| 8 | Claude 4.6 adaptive thinking & Batch API | PASS | 1 | 13/13 | 3/3 | 100% | 100% | N/A |
| 9 | Full transcript capture | PASS | 1 | 11/11 | 3/3 | 100% | 100% | N/A |
| 10 | Completeness — edge cases, Playwright, hygiene | PASS | 1 | 12/12 | 3/3 | 100% | 100% | N/A |

**Edge Case Pass Rate is N/A across all 10 sprints** — Sprint 10 introduced the optional `## Edge Case Criteria` contract slot, but no sprint declared any edge-case criteria. This is expected: the meta-eval's deliverables are markdown/JSON config and protocol changes, not the kind of input-handling code where edge cases produce strong signal. The metric becomes meaningful when this harness is applied to a `web-app`, `api-service`, or `rag-system` project.

## Rubric Score Progression

| Dimension (Weight) | S1 | S2 | S3 | S4 | S5 | S6 | S7 | S8 | S9 | S10 |
|--------------------|----|----|----|----|----|----|----|----|----|-----|
| Methodology (30%) | 3 | 3 | 4 | 3 | 5 | 5 | 5 | 5 | 5 | 4 |
| Grading (25%) | 4 | 4 | 4 | 4 | 5 | 5 | 5 | 5 | 5 | 5 |
| Separation (20%) | 5 | 5 | 5 | 4 | 5 | 5 | 5 | 5 | 5 | 5 |
| Context (15%) | 3 | 3 | 3 | 4 | 4 | 4 | 5 | 5 | 5 | 4 |
| Extensibility (10%) | 3 | 3 | 3 | 3 | 5 | 5 | 5 | 5 | 5 | 4 |

**Phase 1 → Phase 2 progression:** Methodology 3→5, Grading 4→5, Separation 5→5 (held), Context 3→5 (peaked at S7-S9), Extensibility 3→5 (peaked at S5-S9). Sprint 10 stepped back from 5 to 4 on Methodology, Context, and Extensibility because Sprint 10 ships protocol-only — edge-case rate aggregation, `verified_via_command` runtime auto-population, and Playwright runtime invocation are deferred to a synthetic verification sprint per the gap-closure plan. Grading and Separation held at 5 because Sprint 10's Adversarial Hygiene rules (no inference from filenames/comments, log-before-score, per-criterion `verified_via_command`) close the last grader-integrity gap end-to-end at the protocol level.

## Trend Analysis

- **First-round pass rate trajectory.** Sprints 1–3: 100%. Sprints 4–5: 91.7%–92.9% (cross-file integration defects). Sprints 6–10: 100% across the board. The Generator's first-round performance recovered fully after Sprint 5's bootstrap-integration failure mode was internalized — Phase 2 sprints touched more files per sprint than Phase 1 (config + agent + skill + conventions + README per gap), yet zero round-1 failures. The contract-negotiation loop did its job: every Phase 2 contract was reviewed for testability before implementation, and Sprint 8's two-round contract negotiation caught three blockers (tasks.json threshold mismatch, multi-line YAML grep, README permutation regex) that would have caused R1 failures.
- **Retry count trajectory.** Sprints 1–3: 1 round each. Sprints 4–5: 2 rounds each. Sprints 6–10: 1 round each. Average dropped from 1.4 (Phase 1) to 1.0 (Phase 2). This is the strongest signal that the harness is converging on first-round capability — the system learned from Sprint 4–5's integration failures and tightened its self-review.
- **Rubric scores improved monotonically through Phase 1 and held at peak through Sprints 6–9.** Sprint 10 stepped back on three dimensions because protocol-only completeness work doesn't add new capabilities — it ships slots and rules awaiting runtime hookup. This is the expected end-of-Phase-2 plateau.
- **Pass^k is high but artificially so** — `trials == 1` means we measured first-attempt success, not statistical consistency. The synthetic verification sprint will produce the first valid multi-trial measurement.

## Common Failure Patterns

Across the entire 10-sprint history, two FAIL events:

1. **Cross-file integration gaps (2 occurrences, Sprints 4 & 5).** Sprint 4 C8 (PostToolUse hook only echoed, didn't update `sprint-state.json`) and Sprint 5 C10 (bootstrap integration described but not referenced from the consuming workflow) were both failures of describing a feature in one file and forgetting to wire it into the file that consumes it. Both retries fixed the integration, not the underlying capability.
2. **Contract negotiation issues (Sprint 8 round 1 NEEDS REVISION).** Three issues caught by the Evaluator before implementation: (a) `tasks.json` count threshold off by 3 (`>= 13` → `>= 16` after counting success+gates), (b) single-line grep against multi-line YAML frontmatter (the `thinking:` field is rendered across two lines), (c) README permutation regex (`(?s).*A.*B.*`) that would silently pass on either ordering.

**No recurring rubric dimension failures.** No criterion required more than one retry to fix. After Sprint 5, the Generator's first-round rate held at 100% across five consecutive Phase 2 sprints despite touching more files per sprint.

**No FAIL criteria in the most recent shipped state** — the latest eval files (`sprint-NN.md` for each sprint) all show PASS. There are no FAIL criteria or grader-disagreement entries to link transcripts for under the Sprint 9 "Transcript Links for FAIL Criteria and Grader Disagreements" protocol. (The Sprint 4 / Sprint 5 round-1 FAILs predated Sprint 9's transcript channel; their `-r1` eval files do not contain transcript trailers.)

## Saturation & Regression Graduation

Across 5 Phase 2 sprints (6–10), several criterion *types* have passed first-round consistently. They are saturated in aggregate, even though each sprint's specific criterion is sprint-scoped:

| Criterion Type | Consecutive First-Round Passes | Status | Recommendation |
|----------------|-------------------------------|--------|----------------|
| `tasks.json` emission with schema check | 5 (S6→S10) | Saturated (mechanical) | Add a generic regression check that any committed sprint contract has a sibling tasks.json with the schema fields. |
| `config.json` field declaration via jq/Python | 5 (S6→S10) | Saturated (mechanical) | Generic regression check that all declared Phase 2 config keys (`trials`, `sandbox.mode`, `taxonomy.emit_tasks_json`, `regression.{enabled,fail_fast}`, `thinking.profile`, `batch.{enabled,min_criteria}`, `transcripts.{capture,retain_days}`, `evaluator_tools.playwright`) remain present. |
| `^## <Heading>` markdown heading existence | 3 (S8→S10) | Saturated (mechanical) | Skip — too narrow to graduate; each sprint's heading is sprint-specific. |
| Append-only gate (no `git diff` on prior `sprint-0[1-N]*` files) | 4 (S7→S10) | Saturated (architectural invariant) | **Graduate as a generic invariant** — every future sprint should preserve all prior committed sprint artifacts. Translate the per-sprint glob into a generic check. |
| Backward-compatibility LLM-judge criterion | 3 (S8→S10) | Saturated (LLM-judge — protocol-only) | Skip graduation — the criterion's specifics change per sprint (which fields are added). |
| Reference-solution presence on highest-weighted LLM-judge | inconsistent (S9 yes, S10 no) | Not saturated | Make this a sprint-contract skill enforcement, not a regression criterion. |

**Why no automatic write to `regression.json` from this run.** The saturated criteria above are sprint-*scoped* (paths, field names, count thresholds change per sprint). The regression suite expects `verification_command` to run verbatim across future sprints; copying Sprint 10's `verification_command` for, say, the `tasks.json` schema check (`jq -e '.sprint == 10 and (.tasks | length) >= 15 ...' .harness/contracts/sprint-10.tasks.json`) would fail in Sprint 11 because the path and count don't apply. Graduating these criteria requires **rewriting them as generic invariants** (e.g., "every committed `sprint-NN.tasks.json` has the schema fields"), which is a meta-eval design task best done as part of the planned synthetic verification sprint, not by an automated saturation-detection write here.

The summary follows the SKILL.md's append-only mandate by **not** writing speculatively to `regression.json`. The recommended next step is the synthetic verification sprint, which will define generic regression invariants and append them under the same audit-trail rules.

## Phase 2 Gap Closure Status

The gap analysis at `.harness/playbook-alignment-2026-04.md` (2026-04-16) identified 10 gaps against Anthropic's eval playbook. All 10 are closed at the protocol level after Sprint 10:

| Gap | Sprint | Status | Runtime hookup |
|-----|--------|--------|----------------|
| 1. Multi-trial execution | 6 | Protocol shipped | Deferred (synthetic verification) |
| 2. Environment sandboxing | 6 | Protocol shipped | Deferred |
| 3. Formal task taxonomy | 6 | **Live** — `tasks.json` emitted every sprint 6–10 | — |
| 4. Capability/regression dual-track | 7 | Protocol shipped (`regression.json` empty) | Deferred — regression abort end-to-end |
| 5. Adaptive thinking config | 8 | **Live** — frontmatter declarations on planner/generator/evaluator/summary | `thinking.profile` runtime dispatch deferred |
| 6. Full transcript capture | 9 | Protocol shipped — Sprint 10 emitted the first transcript trailer with `criteria_audit` | End-to-end transcript file emission deferred |
| 7. Batch API mode | 8 | Protocol shipped | HTTP submission deferred |
| 8. Edge case criteria | 10 | Protocol shipped — contract slot exists | First sprint to declare edge cases is forward |
| 9. Playwright MCP evaluator | 10 | Protocol shipped — `evaluator_tools.playwright: "auto"` | Live invocation deferred |
| 10. Adversarial hygiene | 10 | Protocol shipped — Rules 1–3 + per-criterion `verified_via_command` populated for first time in Sprint 10 eval | Runtime auto-population deferred |

Three of the ten — Gap 3 (tasks.json), Gap 5 (thinking frontmatter), and partially Gap 10 (the Sprint 10 eval populated `criteria_audit` for real) — are running end-to-end. Seven are protocol-only with runtime hookup deferred to a synthetic verification sprint.

## Contract Negotiation Observations

- **Every Phase 2 sprint emitted a `tasks.json`** alongside its markdown contract. The taxonomy handoff is now an automatic artifact of approval, not an add-on.
- **Round-1 contract approval rate improved across Phase 2.** Sprint 6: APPROVED R1. Sprint 7: APPROVED R1. Sprint 8: NEEDS REVISION → APPROVED (3 blockers). Sprint 9: APPROVED R1. Sprint 10: APPROVED R1. Sprint 8's revision was the only Phase 2 contract revision.
- **The four Sprint 8 trap categories are now well-internalized.** Sprints 9 and 10 explicitly addressed them in the contract review prose: tasks.json count threshold, multi-line YAML frontmatter, permutation regexes, pre-existing-content false positives. The Evaluator confirmed all four trap categories were avoided in the Sprint 10 review.
- **One non-blocking gap remains in Sprint 10:** the highest-weighted LLM-judge criterion (Sprint 10 has C10 and C12 tied at 13%) lacked a reference solution. The Evaluator flagged this as advisory, not a blocker. Future contracts should enforce reference-solution-on-highest-LLM-judge as a sprint-contract skill rule.

## Recommendations

1. **Synthetic verification sprint is the next required step.** It would: (a) set `trials = 3` on a representative Phase 2 sprint to produce the first valid pass@k / pass^k measurement; (b) exercise the regression abort path end-to-end by deliberately breaking a graduated criterion; (c) submit a Batch API request against a live `ANTHROPIC_API_KEY`; (d) emit a real `.harness/transcripts/sprint-NN-r1.json` file by routing the Evaluator subagent's tool stream through a serializer; (e) run a Playwright invocation against a small `web-app` test project; (f) audit whether `criteria_audit` `verified_via_command` flags match the actual tool-call ground truth. This closes the runtime hookup gap on Gaps 1, 2, 4, 6, 7, 9, and 10.
2. **Sprint-contract skill should enforce reference-solution on the highest-weighted LLM-judge criterion.** This was non-blocking in Sprints 9 and 10 but flagged by the Evaluator both times. Codifying it as an automatic check in `skills/sprint-contract/SKILL.md` would prevent the recurrence.
3. **Generic regression invariants are the next regression.json write.** The saturated criterion-types listed in Saturation & Regression Graduation are sprint-scoped and not directly graduable. The synthetic verification sprint should rewrite them as generic invariants (e.g., "every committed `sprint-NN.md` contract has a sibling `sprint-NN.tasks.json`," "no previously-committed sprint artifact in `.harness/evals/` or `.harness/contracts/` has been modified in HEAD"), then write those entries to `regression.json` per the append-only protocol.
4. **The Edge Case Pass Rate metric is not exercised by this meta-eval.** Apply this harness to a `web-app`, `api-service`, or `rag-system` project to validate the Edge Case Criteria slot end-to-end. The slot is correct; only the data is missing.
5. **Phase 2 retention window check.** `config.transcripts.retain_days = 30`. Saturation detection requires 3 sprints of history. With sprints running monthly, the default is sufficient; if cadence accelerates, raise to 60+.
6. **Re-run the playbook gap analysis at `.harness/playbook-alignment-2026-04.md`.** The original analysis dated 2026-04-16 identified 10 gaps. All 10 are closed at the protocol level. A re-run after the synthetic verification sprint should show all 10 with **runtime hookup verified** and the alignment scorecard at 5/5 across all areas.

## Tool & Skill Description Improvements

(ACI Self-Optimization — `config.components_enabled.per_sprint_aci_review` is not set in this project's config, so per-skill convention this runs batched here across all evals.)

**Findings from cross-sprint transcript review:**

1. **Sprint-contract skill: enforce reference-solution-on-highest-LLM-judge.** Sprints 9 and 10 both shipped without a reference solution on their highest-weighted LLM-judge criterion. The Evaluator flagged it both times as advisory but non-blocking. The skill description in `skills/sprint-contract/SKILL.md` already says "The highest-weighted LLM-judge criterion **should** have one if it is LLM-judged" — change "should" to "must" and add an automatic checklist item to the contract review process. This codifies a known recurring issue without adding new tooling.

2. **Sprint-contract template: warn against single-line greps on multi-line YAML.** Sprint 8's round-1 NEEDS REVISION cited a multi-line YAML frontmatter grep that would silently pass against an inline literal. The Sprint 9 evaluator confirmed this trap explicitly. The contract template (or the SKILL.md) should add a **deterministic-criterion authoring checklist** explicitly calling out multi-line content traps, permutation regexes, and pre-existing-content false positives. The Evaluator already checks for these — codifying them in the author-facing template would catch them before contract submission.

3. **`harness-summary` skill: pass@k / pass^k validity caveat.** With `trials == 1`, the metric is degenerate. The summary template should auto-render a caveat note when no sprint had `trials > 1`. (Implemented in this summary's "Important caveat" callout — fold the prose into the SKILL.md output template so it appears automatically next time.)

4. **`harness-sprint` skill: `jq` Python fallback.** Sprint 8 and 9 evals both noted `jq` is unavailable on Windows shells and used `python -c "import json; ..."` as a fallback. This is a recurring environmental footgun. The SKILL.md should document the Python fallback explicitly so future evaluators don't re-derive it. (The Sprint 9 contract referenced the fallback in the eval but not in the contract verification commands; codifying the dual form would prevent the recurring footnote.)

5. **No description-level gaps in agent prompts.** The Generator and Evaluator prompts do their jobs across all 10 sprints — both Phase 1 retries fixed real bugs cited by the Evaluator with file paths and line numbers. The Sprint 10 evaluator correctly populated the new `criteria_audit` array on first try without further guidance, demonstrating the Adversarial Hygiene section in `agents/evaluator.md` is self-contained and actionable. No agent description changes recommended.

**Held-out validation.** Reviewed Sprint 4 R1 (PostToolUse hook FAIL) and Sprint 5 R1 (bootstrap integration FAIL) as held-out cases. Recommendations 1–4 above would not have changed those grades — the failures were genuine integration bugs, not skill description ambiguities. Recommendation 1 (must-have reference solution on highest LLM-judge) might have caught Sprint 5's C10 because that criterion was LLM-judge and the implementation defect was visible from the criterion text alone; codifying the requirement increases the probability the contract review catches similar issues earlier. No regression risk from any of the proposed changes.
