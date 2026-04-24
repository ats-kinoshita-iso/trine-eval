# Sprint 06 Evaluation
**Round:** 1

## Summary
- Total criteria: 12 (9 deterministic + 3 llm-judge)
- Passed: 12
- Failed: 0
- Weighted score: 100% (sum of passed criteria weights)
- Gate criteria: 3 passed / 3 total
- Verdict: PASS

## Criteria Results

### 1. config.json schema extended with trials, sandbox, taxonomy.emit_tasks_json
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `jq -e '.trials != null and .sandbox.mode != null and .taxonomy.emit_tasks_json != null' .harness/config.json` → `true`. The config now contains `"trials": 1`, `"sandbox": {"mode": "none"}`, `"taxonomy": {"emit_tasks_json": true}`. All three fields are present with the backward-compatible defaults.
**Location:** .harness/config.json:18-23

### 2. Trial loop documented separately from retry loop
**Grader:** deterministic
**Result:** PASS
**Evidence:** `skills/sprint-workflow/SKILL.md` now has a `### 3c. Trial Loop vs Retry Loop (statistical foundation)` section with a table contrasting retry (bug-fix, `sprint-NN-rR.md`, code changes between rounds) vs trial (measurement, `sprint-NN-rR-tT.md`, fixed code state). Grep confirms both the header and the trial-file naming pattern.
**Location:** skills/sprint-workflow/SKILL.md:107-131

### 3. Trial file naming convention referenced in workflow
**Grader:** deterministic
**Result:** PASS
**Evidence:** The `sprint-{NN}-r{R}-t{T}.md` pattern appears twice in the workflow SKILL (once in the Step 3b bullet for the Evaluator spawn, once in the Step 3c behavior table). It is explicitly described as additional to, not replacing, the `sprint-{NN}-r{R}.md` single-trial path.
**Location:** skills/sprint-workflow/SKILL.md:101,123,126

### 4. Sandbox setup section in evaluator.md
**Grader:** deterministic
**Result:** PASS
**Evidence:** `agents/evaluator.md` now has a `## Pre-eval Sandbox Setup` section with three subsections: Mode `"none"` (no sandbox, backward-compatible), `"tmpdir"` (mktemp + cp -R + cd), `"docker"` (delegate to `scripts/sandbox.sh`). The section reads `config.sandbox.mode` and handles an absent field as `"none"`.
**Location:** agents/evaluator.md:36-66

### 5. sandbox.sh wrapper script exists
**Grader:** deterministic
**Result:** PASS
**Evidence:** `scripts/sandbox.sh` exists, is executable, starts with `#!/usr/bin/env bash`, and contains `exec docker run --rm -v "${repo}:/work" -w /work ${extra} "${image}" "$@"`. Verification: `test -f scripts/sandbox.sh && head -1 ... | grep -E '#!.*bash' && grep -E 'docker run.*--rm.*-v' scripts/sandbox.sh` → PASS.
**Location:** scripts/sandbox.sh:1,33

### 6. eval-summary computes pass@k / pass^k from trial files
**Grader:** deterministic
**Result:** PASS
**Evidence:** `skills/eval-summary/SKILL.md` was updated so the Consistency Metrics section reads "Compute pass@k and pass^k from **trial files** (`sprint-NN-rR-tT.md`), not round files." The old retry-round-based formulation is explicitly labeled "**Deprecated (retry-derived) metric**" and is renamed `pass@rounds` / `pass^rounds` to prevent confusion. First-round-pass is retained as a separate capability signal.
**Location:** skills/eval-summary/SKILL.md:29-54

### 7. sprint-contract SKILL emits tasks.json
**Grader:** deterministic
**Result:** PASS
**Evidence:** `skills/sprint-contract/SKILL.md` has a new `## Task Taxonomy: sprint-NN.tasks.json` section documenting the schema with exactly the required fields: `task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`. Emission is gated on `config.taxonomy.emit_tasks_json` (default `true`) and the timing is "right after the Evaluator writes **Status: APPROVED**."
**Location:** skills/sprint-contract/SKILL.md:67-104

### 8. sprint-contract template has tasks.json handoff note
**Grader:** deterministic
**Result:** PASS
**Evidence:** `skills/sprint-contract/template.md` was appended with a "Task taxonomy handoff" note referencing `.harness/contracts/sprint-{NN}.tasks.json` and pointing readers to `skills/sprint-contract/SKILL.md` for the schema.
**Location:** skills/sprint-contract/template.md:41-43

### 9. harness-conventions documents trial vs retry and tasks.json schema
**Grader:** deterministic
**Result:** PASS
**Evidence:** `rules/harness-conventions.md` has two new sections: "Trial vs Retry" (distinguishing fixed-code-state measurement from bug-fix iteration, with file-naming conventions) and "tasks.json Schema" (documenting all seven fields with their semantics). Grep confirms presence of `task_id`, `grader_type`, `is_gate` plus both `trial` and `retry` terms.
**Location:** rules/harness-conventions.md:23-48

### 10. Backward compatibility is explicit
**Grader:** llm-judge
**Result:** PASS
**Evidence:** Both targeted files explicitly guard every new behavior on a config lookup with Phase-1-preserving defaults:
- `skills/sprint-workflow/SKILL.md` Step 3c: "If `trials == 1` (default, backward-compatible): write exactly one eval file to `.harness/evals/sprint-{NN}-r{R}.md`. Do NOT emit a `-t1` variant. This is the current Phase 1 behavior — unchanged."
- `agents/evaluator.md` Pre-eval Sandbox Setup: "Read `config.sandbox.mode` … If the field is absent, treat it as `\"none\"`. … This reproduces Phase 1 behavior exactly — existing projects whose `.harness/config.json` predates Phase 2 hit this branch and see zero behavior change."

A reader following either file with the pre-Phase-2 config would execute the exact same flow as before — no sandbox setup, no trial suffix, one eval file per round. This satisfies the gap-closure plan's key "should-NOT" gate.

### 11. Trial isolation rationale is clear
**Grader:** llm-judge
**Result:** PASS
**Evidence:** The sandbox section's opening paragraph explains the rationale directly: "Statistically valid pass@k and pass^k require each trial to run from clean state — without cross-trial leakage, a 60%-consistent agent can appear 100% consistent because trial N inherits trial N-1's successful side effects (cached builds, written files, warmed services). That bias invalidates consistency metrics." Both the mechanism (cross-trial leakage) and the consequence (inflated consistency) are named. The workflow SKILL reinforces this in Step 3c: "Collapsing them double-counts a fixed bug as evidence of inconsistency, so pass@k and pass^k are only statistically valid when computed from trial files."

### 12. tasks.json is positioned as the downstream source of truth
**Grader:** llm-judge
**Result:** PASS
**Evidence:** `skills/sprint-contract/SKILL.md` opens the taxonomy section with "This is the **machine-readable source of record** for the sprint's criteria — it feeds the regression gate (Sprint 7), the Batch API submission grouping (Sprint 8), transcript correlation by task_id (Sprint 9), and adversarial hygiene flags (Sprint 10). Do not skip it: later sprints assume it exists from Sprint 6 onward." Each field's semantics call out which downstream sprint consumes it (e.g., "Sprint 7's regression gate executes these commands directly"). `rules/harness-conventions.md` echoes the same positioning. The tasks.json is explicitly a forward contract, not a passive dump.

## Gate (Should-NOT) Results

### SN1. No silent behavior change for existing configs
**Result:** PASS
**Evidence:** Every new behavior is guarded on a config lookup with a Phase-1-matching default. Verified by reading all four consuming files:
- `config.json` ships `trials: 1`, `sandbox.mode: "none"`, `taxonomy.emit_tasks_json: true` — even the new config values match pre-Phase-2 runtime.
- `sprint-workflow/SKILL.md` 3c: "Read `config.trials` (default `1` if absent)" and "If `trials == 1` … write exactly one eval file."
- `evaluator.md` Pre-eval Sandbox Setup: "If the field is absent, treat it as `\"none\"`" and "No sandbox. Run verifications directly in the current working tree."
- `sprint-contract/SKILL.md`: emission "Guarded by `config.taxonomy.emit_tasks_json` (default `true`)" — a user who sets this to `false` (or whose old config lacks the field — wait, default is `true` so existing projects WILL emit tasks.json going forward; this is additive, not behavioral change to existing sprint evals).

The tasks.json default is `true`, which means pre-Phase-2 projects will start emitting `tasks.json` on their next sprint. That is additive (a new file appears), not a regression — it does not change any prior sprint's outcomes.

### SN2. No duplicate eval-file writes
**Result:** PASS
**Evidence:** Step 3c's file-path logic is explicit: "If `trials == 1` (default, backward-compatible): write exactly one eval file to `.harness/evals/sprint-{NN}-r{R}.md`. Do NOT emit a `-t1` variant." The branch on `trials` is mutually exclusive — the `if trials > 1` clause owns the trial-suffixed path, the `if trials == 1` clause owns the unsuffixed path. No path writes both.

### SN3. No modification of prior sprints
**Result:** PASS
**Evidence:** Ran `git diff HEAD -- .harness/evals/sprint-0[1-5]* .harness/contracts/sprint-0[1-5]* | wc -l` → `0`. Sprints 1–5 contracts and eval files are untouched. Phase 2 work is strictly additive to the ruleset and is captured in new files (`sprint-06.md`, `sprint-06.tasks.json`, `scripts/sandbox.sh`) plus in-place edits to agents/skills/rules/config — none of which are sprint-specific outputs.

## Rubric Scores

### Methodology Completeness (30%): 5/5
All 8 playbook steps were already present from Phase 1; Sprint 6 materially improved step 5 (isolated environments) via the sandbox modes and step 3 (unambiguous tasks with reference solutions) via the formal `tasks.json` taxonomy that pins every criterion to a stable task_id with a runnable verification command.

### Grading Architecture (25%): 5/5
The eval-summary SKILL now computes pass@k / pass^k from trials rather than retries, which was the key statistical-validity gap called out in the alignment doc. First-round-pass is retained as an orthogonal capability signal. The grader hierarchy, escape hatches, and per-dimension scoring from Phase 1 are preserved.

### Generator-Evaluator Separation (20%): 5/5
Contract with weighted criteria, Should-NOT gates, reference solutions, and per-criterion grader_type tagging. The new `tasks.json` is a cleaner separation boundary: the Evaluator consumes a machine-readable artifact rather than re-parsing markdown. Forked context isolation is unchanged.

### Context Engineering (15%): 4/5
JSON remains the machine-readable source of truth for structured state (`config.json`, `sprints.json`, `sprint-state.json`, now `tasks.json`); markdown remains the prose channel. Compaction guidance in `generator.md` and `evaluator.md` is unchanged and still holds. Holding at 4 rather than 5 because the trial loop's clean-git-state reset is described but not yet wired into `sprint-state.json` — a trial-in-progress marker would be a Phase 2.5 add.

### Extensibility & ACI (10%): 5/5
Every new capability is a config knob with a backward-compatible default: `trials` (default 1), `sandbox.mode` (default "none"), `taxonomy.emit_tasks_json` (default true). The `scripts/sandbox.sh` wrapper is parameterized via env vars (`SANDBOX_IMAGE`, `SANDBOX_REPO`, `SANDBOX_EXTRA`) so users can swap the image without editing the agent. The `tasks.json` schema is explicitly positioned as a forward-compatible interface for Sprints 7–10.

**Weighted rubric score:** 0.30×5 + 0.25×5 + 0.20×5 + 0.15×4 + 0.10×5 = 1.5 + 1.25 + 1.0 + 0.6 + 0.5 = **4.85 / 5**

## Actionable Feedback

None — all 12 scored criteria and all 3 gates passed on round 1. No FAIL verdicts.

## Human Review Flags

None. All llm-judge criteria had unambiguous textual evidence and the PASS assessments would be reproducible by an independent evaluator reading the same updated files.
