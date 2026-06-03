# Eval Summary

_Generated 2026-06-02 (Cycle 3 close). Supersedes the stale 5-sprint summary. Covers the full Sprint 1–13 trine-eval self-upgrade arc._

## Overview
- **Sprints completed:** 13 (Phase 1: S1–6; Phase 1.5: S9; Phase 1.6: S13; Phase 2: S7/8/10/11/12)
- **Overall pass rate:** 145/147 criteria = **98.6%**
- **Overall weighted pass rate:** 12/13 sprints at 100%; Sprint 11 at 76% → arithmetic mean **98.2%**
- **First-round pass rate:** 143/147 = **97.3%** (capability signal — Generator gets it right before retry feedback)
- **Average rounds per sprint:** 15/13 = **1.15** (only S4 and S5 needed a retry; S6–S13 all single-round)
- **Edge Case Pass Rate:** N/A (no sprint declared an `## Edge Case Criteria` section — expected for `eval-harness`, which encodes edge concerns in dimension scoring)
- **Functional Smoke Pass Rate:** N/A (no sprint declared `## Functional Smoke` — no live-API/Docker integration surface in this meta-eval)

## Consistency Metrics

**Trial configuration:** `config.trials` is absent → **single-trial (k=1)** for every sprint. Statistically valid pass@k / pass^k require ≥2 **trials** at a fixed code state; this project has none, so per-sprint consistency collapses to `pass@1 = pass^1 = p` (the final-round pass rate). The two multi-**round** sprints (S4, S5) are reported with the **deprecated** `pass@rounds` / `pass^rounds` formulation (k = retry rounds), which mixes a fixed-bug signal into the consistency estimate and is shown only for continuity with the prior summary.

| Sprint | p (final) | k (rounds) | pass@k | pass^k | Note |
|--------|-----------|------------|--------|--------|------|
| 1 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 2 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 3 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 4 | 0.950 | 2 | 99.75% | 90.25% | _deprecated pass@rounds_ (r1 9/10 → r2 10/10) |
| 5 | 0.958 | 2 | 99.82% | 91.84% | _deprecated pass@rounds_ (r1 11/12 → r2 12/12) |
| 6 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 7 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 8 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 9 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 10 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 11 | 0.818 | 1 | 81.8% | 81.8% | single-round PARTIAL (9/11; J10/J11 FAIL) |
| 12 | 1.000 | 1 | 100.0% | 100.0% | single-trial |
| 13 | 1.000 | 1 | 100.0% | 100.0% | single-trial |

- **Consistency gap (pass@k − pass^k):** 0% for all single-trial sprints (structural — only one trial exists); 9.5% / 8.0% for the deprecated S4 / S5 round-based figures.
- **Interpretation:** The harness is highly capable (12/13 sprints at 100% weighted, first-round rate 97.3%). **True consistency is unmeasured** — no sprint ran ≥2 trials, so the system's run-to-run reliability at a fixed code state has never been quantified. The single PARTIAL (S11) was a *designed* calibration probe, not a reliability failure. **Recommendation:** set `config.trials = 3` for at least one future sprint to obtain a genuine pass^k consistency estimate (see Recommendations).

## Per-Sprint Results

| Sprint | Title | Verdict | Rounds | Pass Rate | Weighted | Rubric (M/G/S/C/E) | Gates | Behavioral % | Edge | Smoke |
|--------|-------|---------|--------|-----------|----------|--------------------|-------|--------------|------|-------|
| 1 | Grading hierarchy & contract structure | PASS | 1 | 13/13 | 100% | 3/4/5/3/3 | 2/2 | — | N/A | N/A |
| 2 | Evaluator separation & isolation | PASS | 1 | 9/9 | 100% | 3/4/5/3/3 | 2/2 | — | N/A | N/A |
| 3 | Metrics, saturation & summary | PASS | 1 | 9/9 | 100% | 4/4/5/3/3 | 2/2 | — | N/A | N/A |
| 4 | Context engineering & structured state | PASS | 2 | 10/10 | 100% | 3/4/4/4/3 | 2/2 | — | N/A | N/A |
| 5 | Bootstrap, calibration & ACI | PASS | 2 | 12/12 | 100% | 5/5/5/4/5 | 2/2 | — | N/A | N/A |
| 6 | JIT context retrieval patterns | PASS | 1 | 11/11 | 100% | 3/4/5/4/3 | 2/2 | — | N/A | N/A |
| 7 | harness-build rubric (Phase 2) | PASS | 1 | 11/11 | 100% | 4/4/5/4/4 | 4/4 | 22% | N/A | N/A |
| 8 | Bootstrap failure catalog (Phase 2) | PASS | 1 | 13/13 | 100% | 4/4/4/4/4 | 6/6 | 66% | N/A | N/A |
| 9 | tasks.json schema port (Phase 1.5) | PASS | 1 | 13/13 | 100% | 4/4/5/4/4 | 5/5 | 63% | N/A | N/A |
| 10 | Planner harness-build mode (Phase 2) | PASS | 1 | 11/11 | 100% | 4/4/5/4/4 | 5/5 | 62% | N/A | N/A |
| 11 | Ephemeral dogfood validation (Phase 2) | **PARTIAL** | 1 | 9/11 | 76% | 3/3/3/4/3 | 5/5 | 62% | N/A | N/A |
| 12 | Positioning & rubric decision guide (Phase 2) | PASS | 1 | 11/11 | 100% | 4/4/4/4/4 | 7/7 | 54%¹ | N/A | N/A |
| 13 | Workflow-step port & governance (Phase 1.6) | PASS | 1 | 13/13 | 100% | 4/4/5/5/4 | 6/6 | 66% | N/A | N/A |

¹ Sprint 12 used the static-artifact carve-out (54% behavioral, below the 60% floor). Behavioral % is 3-way-grader-split data and only exists from Sprint 7 onward (the split methodology was ratified mid-arc, DEC-0007).

**Cross-sprint Edge Case Pass Rate:** N/A · **Cross-sprint Functional Smoke Pass Rate:** N/A

## Trend Analysis

- **Pass rate:** Flat at the ceiling — 12/13 sprints at 100% weighted. The lone dip (S11, 76%) was a deliberately-scoped single-round dogfood probe, not a capability regression.
- **Retry counts decreasing:** Retries occurred only in the early sprints (S4, S5). Every sprint from S6 onward (8 consecutive) passed in a single round — zero retries across the entire Phase 1.5 / Phase 1.6 / Phase 2 body of work.
- **First-round pass rate strong and stable (97.3%):** Only 4 of 147 criteria ever failed a first round (S4-C8, S5-C10, S11-J10, S11-J11). The Generator consistently lands implementations before retry feedback.
- **Friction migrated, then dissolved:** Cycle 1 friction was in implementation (S4/S5 retries); Cycle 2 moved upstream to contract negotiation (S7–S10 each needed an R1→R2 contract revision); Cycle 3 dissolved it — S11/S12/S13 all reached single-round contract APPROVAL, driven by the Evaluator's pre-implementation baseline verification (now being formalized as PROC-001 via DEC-0028).
- **Rubric trajectory:** Ascending then plateauing — Phase 1 climbed toward 5/5 on separation/grading; Phase 2 work plateaued ~4/5 (graded against a Phase-1 yardstick); S13 (Phase 1.6, methodology-native) recovered Context Engineering to 5/5.
- **pass^k trend:** Cannot be assessed — no trial-based data exists (see Consistency Metrics).

## Common Failure Patterns

Only **4 criteria failed across the entire 147-criterion arc** — a very low defect surface. Ranked by significance:

### Sprint 11, Criteria J10 & J11 — FAIL (the dominant unresolved pattern)
**Pattern:** *Synthetic fulfillment* of behavioral criteria. The Generator could not dispatch the Planner subagent into an ephemeral tmp directory, so it authored the expected `spec.md`/`sprints.json` directly. All 9 deterministic criteria PASSed (they test report-document properties), but J10 (evidence standard: synthetic examples disqualified) and J11 (planner-activation unconfirmable) correctly FAILed.
**Rubric dimensions:** `generator_evaluator_separation` (3/5), `methodology_completeness` (3/5).
**Status:** Open — tracked as HK-0006, routed to a future Phase-3 sprint (runtime dispatch observable). This is the only failure pattern that surfaced and remains open.
**Transcript:** `.harness/transcripts/sprint-11-r1.json`

### Sprint 4, Criterion C8 — FAIL (resolved in r2)
**Pattern:** PostToolUse hook only echoed; did not update `sprint-state.json`. Fixed in round 2.
**Dimension:** `context_engineering`. Isolated; did not recur.
_(No transcript — predates Sprint 9 trailer protocol.)_

### Sprint 5, Criterion C10 — FAIL (resolved in r2)
**Pattern:** Bootstrap integration not referenced in kickoff/workflow. Fixed in round 2.
**Dimension:** `extensibility_aci`. Isolated; did not recur.
_(No transcript — predates Sprint 9 trailer protocol.)_

**No recurring failure class.** Each cycle surfaced a distinct, deeper failure class at a different lifecycle phase (Cycle 1 = cross-component integration; Cycle 2 = verification-command quality; Cycle 3 = synthetic fulfillment), indicating the loop keeps finding new edges rather than re-hitting old ones.

## Saturation & Regression Graduation

Saturation detection ran over the S7–S13 window (the sprints with machine-readable `tasks.json`). Four gate criterion-types recurred with first-round PASS across ≥3 consecutive sprints:

| Criterion Type | Verification | Sprints | Status | Action |
|----------------|--------------|---------|--------|--------|
| JIT context-scope annotation preserved (harness-kickoff) | `grep -c '<!-- Context scope at this step:' …/harness-kickoff/SKILL.md` | S7–S12 (6) | Saturated (easy preservation) | **GRADUATED** (s09-sn3 → regression.json, graduated_from_sprint 9) |
| Config core-fields intact | `jq '.project_type==… and .governance.enabled==true' config.json` | S9–S13 (5) | Saturated **but graduation-blocked** | Deferred — see exit-code mismatch below |
| `examples/` directory absent | `test -d "examples"` | S8–S11 (4) | Saturated **but graduation-blocked** | Deferred — inverted polarity |
| Prior contract sprint-07.md unmodified | `git diff HEAD -- …/sprint-07.md` | S10, S11, S13 | **Excluded** — semantics changed | Not graduatable (see below) |

**One criterion graduated** into `.harness/regression/regression.json` (now armed — previously never populated). This unblocks the Step 0.5 regression gate for all future sprints.

### Exit-code-semantics mismatch (critical finding)

The `tasks.json` `verification_command`s were authored for an **Evaluator that reads command output and applies a PASS condition** (count ≥ 6, `== true`, ABSENT). But the Step 0.5 regression runner records **PASS on exit code 0**. These two models diverge for three of the four saturated gates:

- **`grep -c` (JIT gate):** exit 0 iff ≥1 match → **correct polarity** (catches catastrophic deletion; weaker than the contract's `count ≥ 6` but never inverted). ✅ Graduated.
- **`jq '… == true'` without `-e`:** jq exits 0 on any valid JSON regardless of the boolean → **vacuous** under the exit-code model (would never FAIL). ❌ Blocked.
- **`test -d "examples"`:** exit 0 iff `examples/` **exists** (the violation) → **inverted polarity** (would PASS exactly when the bad state occurs). ❌ Blocked.

Because the graduation rule mandates **verbatim** copying (no paraphrase/recompute), the vacuous and inverted gates cannot be safely armed as-is. **Recommendation:** add `-e` to the config `jq` gate and invert the `examples/` gate to `test ! -d "examples"` **at the `tasks.json` source** (a future-sprint contract edit), or extend the regression runner to capture stdout and apply the recorded PASS condition. Until then, these two remain saturation-detected but un-armed.

### Windows-invocation note for the regression runner
The armed JIT gate returns `6` / exit 0 under **git-bash** but spuriously returns exit 1 / empty output under `cmd.exe` (`shell=True` in Python): the single-quotes don't quote and the `<` in `<!--` becomes a redirection operator. The Step 0.5 runner MUST invoke gate commands via git-bash, not `cmd.exe`. This extends the existing "Windows-bash invocation hazard" note in Step 0.5 to cover `grep`/`jq` gates containing single-quotes or `<`/`>` characters.

### `git diff` gate excluded
The `git diff HEAD -- sprint-07.md` gate is **not** graduatable: its semantics flipped at S13. In S10/S11 it asserted "empty diff (unmodified)"; in S13 the SN2 carve-out *deliberately* modified sprint-07.md, so the S13 gate (s13-sn3) asserts "renumbering-only diff." Same command string, different PASS condition — not a stable regression target.

## Recommendations

1. **Run ≥2 trials on a future sprint** (`config.trials = 3`) to obtain the first genuine pass^k consistency estimate. The entire arc has measured capability (first-round rate) but never run-to-run consistency at a fixed code state.
2. **Fix the two blocked regression gates at the source** (add `jq -e`; invert `test -d` → `test ! -d`) so the config-fields and `examples/`-absence gates can graduate. Pair with a regression-runner that uses git-bash and (ideally) captures stdout to apply output-based PASS conditions, decoupling regression gates from raw exit codes.
3. **Close HK-0006 (synthetic fulfillment)** in a Phase-3 sprint with a non-fakeable runtime dispatch observable (`subagent_dispatch.jsonl`, proof-of-dispatch criterion, or spec SC9b amendment). This is the only open failure class and the natural seed for continued work. _(A task has been spawned for this.)_
4. **Strengthen behavioral-coverage discipline** via the now-ratified PROC-002 amendment (DEC-0028): the mandatory `Coverage Justification` heading and codified carve-out permission test guard against the S12-style sub-floor breach recurring un-gated.
5. **No harness component should be disabled.** All enabled components (planner, contract_negotiation, sprint_decomposition, eval_summary) contributed; the 97.3% first-round rate and single-PARTIAL record indicate the full pipeline is performing.

## Tool & Skill Description Improvements

`config.components_enabled.per_sprint_aci_review` is absent (not enabled), so this is a **single batched review** across all evals. Consolidated findings:

1. **Verification-command authoring vs. exit-code consumption (systemic).** The most valuable cross-sprint insight: `tasks.json` `verification_command`s are written for an output-reading Evaluator but are consumed verbatim by an exit-code-only regression runner. The `sprint-contract` SKILL should advise contract authors that any criterion intended for eventual regression graduation must have **correct exit-code polarity** — prefer `grep -q` / `test ! -d` / `jq -e` forms whose exit code alone encodes the PASS condition. This single guidance change would let all four saturated gates graduate cleanly. _(Recommendation recorded here; not auto-applied — it is a `sprint-contract` SKILL edit that belongs in a future sprint's scope, not a summary-time mutation.)_
2. **Step 0.5 Windows-bash hazard scope.** The hazard note in `sprint-workflow` Step 0.5 should explicitly call out that `grep`/`jq` gate strings containing single-quotes or `<`/`>` must run under git-bash, not `cmd.exe shell=True` — the failure is silent (exit 1 / empty output), masquerading as a regression. _(Recorded; future-sprint edit.)_
3. **No tool-description defects found in the eval transcripts themselves.** The two emitted transcripts (S11, S13) show the Evaluator interpreting criteria as intended; no tool call failed due to ambiguous tool/skill wording. The S11 J10/J11 FAILs were correct verdicts, not misinterpretations.

_Held-out validation: re-reading the S7, S8, S10 evals (not used to derive the above) confirms the exit-code-polarity recommendation would not have changed any of their verdicts (the Evaluator read output correctly in every case) — it only affects downstream regression graduation, where it is strictly an improvement. No regressions introduced._
