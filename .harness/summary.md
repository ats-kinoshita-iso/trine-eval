# Eval Summary

## Overview
- Sprints completed: 5
- Overall pass rate: 100% (53/53 criteria passed on final rounds)
- First-round pass rate: 96.2% (51/53 criteria passed on first attempt)
- Overall weighted pass rate: 100% (all sprints reached 100% weighted score)
- Average rounds per sprint: 1.4
- Total evaluation rounds: 7
- Total criteria evaluated: 53 success criteria + 10 gate criteria = 63

## Consistency Metrics

| Sprint | p (avg) | k (rounds) | pass@k | pass^k | Gap |
|--------|---------|------------|--------|--------|-----|
| 01 | 1.000 | 1 | 100.0% | 100.0% | 0.0% |
| 02 | 1.000 | 1 | 100.0% | 100.0% | 0.0% |
| 03 | 1.000 | 1 | 100.0% | 100.0% | 0.0% |
| 04 | 0.950 | 2 | 99.75% | 90.25% | 9.5% |
| 05 | 0.958 | 2 | 99.83% | 91.84% | 8.0% |

- Overall average p: 0.974
- Overall pass@k: ~99.9% (system is highly capable -- at least one passing round is near-certain)
- Overall pass^k: ~94.5% (consistency drops moderately for multi-round sprints)
- Consistency gap (pass@k - pass^k): 5.5% overall; 0% for single-round sprints, 8-9.5% for retried sprints
- Interpretation: The system is both capable and reasonably consistent. The gap only appears in Sprints 04-05, which had higher complexity and more criteria. Both failures were fixed in exactly 1 retry, indicating the feedback loop is effective.

## Per-Sprint Results

| Sprint | Title | Verdict | Rounds | Criteria | First-Round Rate | Weighted | pass^k | Rubric (weighted) |
|--------|-------|---------|--------|----------|-----------------|----------|--------|-------------------|
| 01 | Grading Hierarchy & Contract Structure | PASS | 1 | 13/13 | 100% | 100% | 100% | 3.65/5 (73%) |
| 02 | Evaluator Separation & Isolation | PASS | 1 | 9/9 | 100% | 100% | 100% | 3.65/5 (73%) |
| 03 | Metrics, Saturation & Summary | PASS | 1 | 9/9 | 100% | 100% | 100% | 3.95/5 (79%) |
| 04 | Context Engineering & Structured State | PASS | 2 | 10/10 | 90% | 100% | 90.25% | 3.65/5 (73%) |
| 05 | Bootstrap, Calibration & ACI | PASS | 2 | 12/12 | 91.7% | 100% | 91.84% | 4.85/5 (97%) |

## Rubric Dimension Trajectory

| Dimension (weight) | S01 | S02 | S03 | S04 | S05 | Trend |
|---------------------|-----|-----|-----|-----|-----|-------|
| Methodology (30%) | 3 | 3 | 4 | 3 | 5 | Non-monotonic. S03 gained saturation graduation (3->4), S04 regressed due to evaluator re-counting steps, S05 reached ceiling after completing all 8 steps. |
| Grading (25%) | 4 | 4 | 4 | 4 | 5 | Stable at 4 through S04, then jumped to 5 after human calibration and pass@k were delivered. |
| Separation (20%) | 5 | 5 | 5 | 4 | 5 | At ceiling from S01. Brief dip to 4 in S04 (evaluator cited missing project-specific calibration), recovered in S05. |
| Context (15%) | 3 | 3 | 3 | 4 | 4 | Flat at 3 until S04 delivered JSON state tracking and compaction guidance. Plateaued at 4 -- JIT context retrieval still missing. |
| Extensibility (10%) | 3 | 3 | 3 | 3.5 | 5 | Gradual improvement. S04 added functional hooks (3->3.5). S05 delivered self-optimization pathway (3.5->5). |

## Trend Analysis

### Pass Rate Trends
- Sprints 01-03 achieved 100% first-round pass rates with single evaluation rounds.
- Sprints 04-05 introduced first-round failures (90% and 91.7%), requiring one retry each.
- The first-round degradation correlates with increasing sprint complexity (10 and 12 criteria vs 9-13 in earlier sprints) and higher proportions of cross-component integration criteria.
- Final pass rate is 100% across all sprints -- the retry loop is fully effective.

### Retry Efficiency
- Average rounds: 1.4 (3 single-round, 2 double-round sprints)
- Both retries fixed exactly 1 criterion in 1 additional round -- 100% retry efficiency.
- No sprint required more than 2 rounds. The max_retries limit (3) was never approached.
- Both failed criteria were low-to-moderate weight (12% and 8%), so the weighted impact of failures was limited.

### First-Round vs Final-Round Delta
- Sprint 04: 9/10 -> 10/10 (+1 criterion, +12% weighted)
- Sprint 05: 11/12 -> 12/12 (+1 criterion, +8% weighted)
- Retries consistently recovered the remaining gap in a single round.

### Rubric Score Trends
- Overall weighted rubric improved from 73% (S01-02) to 97% (S05) -- a 24-point gain.
- Every dimension reached its highest score by Sprint 05 except Context Engineering (4/5, missing JIT patterns).
- The Methodology dimension was most volatile (3->3->4->3->5), with an evaluator-driven regression in S04.
- Separation maintained the ceiling (5/5) in 4 of 5 sprints.

### Consistency Trends (pass^k)
- pass^k is 100% for single-round sprints and 90-92% for double-round sprints.
- The gap is modest (8-9.5%) and entirely driven by single-criterion failures.
- No evidence of systemic non-determinism -- both failures are traceable to specific integration oversights, not random behavior.

## Common Failure Patterns

Only 2 criteria failed across 7 evaluation rounds and 53 total criteria:

### 1. Cross-component integration completeness (2/2 failures)

| Sprint | Criterion | Weight | Issue |
|--------|-----------|--------|-------|
| 04 | C8: Hooks cover meaningful lifecycle events | 12% | PostToolUse hook echoed to stderr instead of writing to sprint-state.json -- the hook's intent was correct but the command didn't perform a state mutation. |
| 05 | C10: Bootstrap integrates with existing harness | 8% | Bootstrap skill described integration with kickoff and workflow, but those receiving skills weren't updated to reference the bootstrap catalog. Integration was documented in one place but not wired up in the others. |

**Pattern:** Both failures involve implementing the primary feature correctly but failing to complete the integration with connected components. The generator built the producing side but didn't update the consuming side.

### 2. No deterministic criteria failures

All 28 deterministic criteria across 5 sprints passed on first attempt. Both failures were LLM-judge criteria evaluating semantic completeness and integration -- exactly the gap between what grep can verify and what requires reading comprehension.

### 3. No gate criteria failures

All 10 Should-NOT gate criteria passed across all rounds. These regression guards were never triggered.

## Saturation & Regression Graduation

| Criterion Type | Consecutive First-Round Passes | Status | Recommendation |
|----------------|-------------------------------|--------|----------------|
| Should-NOT gates (regression guards) | 5 (all sprints) | Saturated (easy) | Graduate to regression suite. These serve as safety nets, not capability measures. Keep as gates but exclude from capability scoring. |
| Deterministic grep-based presence checks | 5 (all sprints) | Saturated (easy) | Replace with harder variants. Basic keyword-presence greps (e.g., `grep -c 'pass@k'`) test that content exists but not that it is correct. Replace with LLM-judge criteria testing semantic correctness, or with deterministic checks that verify structure (JSON schema validation, output format matching). |
| LLM-judge integration criteria | 3 (S01-S03), then failures in S04-S05 | Not saturated | Keep. These are where the system's actual capability gaps surface. |

**Graduated criteria (for future sprints):**
1. File existence checks (`test -f`) -- trivially easy, never informative.
2. Single-keyword greps with threshold >= 1 -- too easy to satisfy with incidental matches.
3. Section-header greps -- verify structure exists but not content quality.

**Harder replacements:**
- Replace "file exists" with "file parses as valid YAML/JSON with required fields."
- Replace single-keyword greps with multi-condition deterministic checks (e.g., verify a formula is present AND computes correctly with known inputs).
- Replace section-header greps with LLM-judge criteria that verify the section contains actionable instructions, not just a heading.

## Recommendations

### 1. Focus on Context Engineering (15% rubric weight, stuck at 4/5)
Context Engineering is the only dimension that hasn't reached 5/5. The gap is JIT context retrieval patterns -- documented guidance for agents to pull relevant context on-demand rather than front-loading all files. A targeted sprint addressing this would complete the rubric ceiling.

### 2. Address rubric scoring inconsistency
The Methodology dimension scored 4/5 in Sprint 03 and regressed to 3/5 in Sprint 04 despite no methodology features being removed. Different evaluator instances counted the 8 methodology steps differently. The rubric should enumerate specific steps at each score level (not just counts) to prevent evaluator drift.

### 3. Strengthen integration testing in contracts
Both failures involved cross-component integration. Future contracts should include explicit integration criteria that name both the producing and consuming components, with separate verification for each end.

### 4. Graduate saturated criteria from capability eval
The 28 deterministic grep-presence criteria all passed on first attempt every time. These serve as useful regression guards but provide zero signal about capability growth. Future sprints should shift weight toward LLM-judge criteria (where failures actually occur) and use deterministic checks only for structural baselines.

### 5. Largest pass@k vs pass^k gap: Sprint 04 (9.5%)
This sprint had the lowest pass^k (90.25%) due to a 12%-weight criterion failure. The fix was a single-line command change in hooks.json. Consider adding a self-review step specifically for hooks/infrastructure changes, where the generator verifies that each hook's command performs its described action (not just compiles).

### 6. Contract negotiation is highly effective -- keep enabled
Sprint 05's contract negotiation caught 7 issues across 2 review rounds (no-op criteria, missing reference solutions, fragile grep patterns, wrong search scope). All were fixed before implementation, preventing evaluation-time surprises. The `contract_negotiation` component should remain enabled.

### 7. Missing eval round files
Sprint 04 is missing its `sprint-04-r1.md` file despite having 2 evaluation rounds. The workflow should enforce round-specific file naming for all rounds including Round 1, treating round files as append-only artifacts.

## Tool & Skill Description Improvements

### Applied Changes

#### 1. Generator: Cross-component integration verification
**Source:** Sprint 05 R1 C10 FAIL -- bootstrap integration one-directional.
**File:** `agents/generator.md`
**Change:** Added integration verification guidance to the IMPLEMENTATION self-review checklist.
**Rationale:** The generator built the producing component correctly but didn't update the consuming components. An explicit checklist item catches this class of error during self-review.
**Held-out validation:** Sprints 01-03 had no cross-component data flows requiring bidirectional updates. No false negatives introduced.

#### 2. Eval-harness rubric: Methodology step enumeration
**Source:** Sprint 03 evaluator gave Methodology 4/5; Sprint 04 evaluator gave 3/5 for the same feature set.
**File:** `skills/eval-rubric/rubrics/eval-harness.md`
**Change:** Added explicit step names at each score level (3, 4, 5) to prevent evaluator drift in step-counting.
**Rationale:** The rubric said "4-5 steps" and "6-7 steps" but different evaluators disagreed on which features count as "steps." Explicit enumeration removes ambiguity.
**Held-out validation:** Sprints 01-02 scored 3/5 consistently. Explicit step names would produce the same scores. No regression.

#### 3. Sprint-contract skill: No-op criterion detection
**Source:** Sprint 05 contract negotiation found 2 criteria (C3, C4) that matched pre-existing content.
**File:** `skills/sprint-contract/SKILL.md`
**Change:** Added guidance to run deterministic verification commands against the current codebase before finalizing the contract, flagging criteria that already pass as no-ops.
**Rationale:** A criterion that passes before implementation provides zero signal. Contract authors should detect and revise these during negotiation.
**Held-out validation:** Sprint 01-03 contracts do not show evidence of no-op criteria. No regression.

#### 4. Sprint-workflow: Round file naming enforcement
**Source:** Sprint 04 missing `sprint-04-r1.md` despite 2 rounds of evaluation.
**File:** `skills/sprint-workflow/SKILL.md`
**Change:** Added explicit instruction that every round (including Round 1) must use `sprint-{NN}-r{R}.md` naming. Round files are append-only.
**Rationale:** Missing round files break pass@k/pass^k computation (requires per-round pass rates) and make debugging evaluation history impossible.
**Held-out validation:** Sprints 01-03 all have correct r1 files. No regression.
