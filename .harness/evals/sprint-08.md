# Sprint 08 Evaluation
**Round:** 1

## Summary
- Total criteria: 16 (13 success + 3 Should-NOT gates)
- Passed: 16
- Failed: 0
- Weighted score: 100% (sum of passed-criterion weights)
- Gate criteria: 3/3
- Verdict: **PASS**

## Criteria Results

### 1. planner.md declares adaptive-thinking frontmatter at effort medium
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `grep -q '^thinking:' agents/planner.md && grep -qE 'type:[[:space:]]*adaptive' agents/planner.md && grep -qE 'effort:[[:space:]]*medium' agents/planner.md` → exit 0. The YAML frontmatter in `agents/planner.md` (lines 7-9) contains `thinking:` with `type: adaptive` and `effort: medium`.
**Location:** agents/planner.md:7-9

### 2. generator.md declares adaptive-thinking frontmatter at effort medium
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `grep -q '^thinking:' agents/generator.md && grep -qE 'type:[[:space:]]*adaptive' agents/generator.md && grep -qE 'effort:[[:space:]]*medium' agents/generator.md` → exit 0. Frontmatter declaration at `agents/generator.md:8-10`. Per-mode override documentation for CONTRACT_PROPOSAL/CONTRACT_REVISION at `agents/generator.md:73-81`.
**Location:** agents/generator.md:8-10

### 3. evaluator.md declares adaptive-thinking frontmatter at effort high
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `grep -q '^thinking:' agents/evaluator.md && grep -qE 'type:[[:space:]]*adaptive' agents/evaluator.md && grep -qE 'effort:[[:space:]]*high' agents/evaluator.md` → exit 0. Frontmatter at `agents/evaluator.md:9-11` sets capability-eval baseline to high; body documents `medium` regression and `max` contract-review overrides (lines 79-85).
**Location:** agents/evaluator.md:9-11

### 4. harness-summary SKILL declares adaptive-thinking frontmatter at effort max
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `grep -q '^thinking:' skills/harness-summary/SKILL.md && grep -qE 'type:[[:space:]]*adaptive' skills/harness-summary/SKILL.md && grep -qE 'effort:[[:space:]]*max' skills/harness-summary/SKILL.md` → exit 0. Frontmatter at `skills/harness-summary/SKILL.md:5-7`.
**Location:** skills/harness-summary/SKILL.md:5-7

### 5. config.json schema extended with thinking.profile
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `jq -e '.thinking.profile == "default" or .thinking.profile == "fast" or .thinking.profile == "thorough"' .harness/config.json` → exit 0 (output `true`). `.harness/config.json:29-31` has `"thinking": { "profile": "default" }`.
**Location:** .harness/config.json:29-31

### 6. config.json schema extended with batch fields
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `jq -e '.batch | has("enabled") and has("min_criteria") and (.enabled | type == "boolean") and (.min_criteria | type == "number")' .harness/config.json` → exit 0 (output `true`). `.harness/config.json:32-35` has `"batch": { "enabled": false, "min_criteria": 20 }`.
**Location:** .harness/config.json:32-35

### 7. harness-sprint SKILL contains a Batch API section
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran the full compound check: `grep -qiE '^## .*Batch|^### .*Batch' skills/harness-sprint/SKILL.md && grep -q 'batch.enabled' skills/harness-sprint/SKILL.md && grep -q 'batch.min_criteria' skills/harness-sprint/SKILL.md && grep -q '50%' skills/harness-sprint/SKILL.md && grep -qE '24[- ]hour' skills/harness-sprint/SKILL.md` → exit 0. Section `### 3d. Batch API Mode (optional)` at `skills/harness-sprint/SKILL.md:172`; all five sub-requirements present: batch.enabled (line 174), batch.min_criteria (line 174), guard condition at line 174, submit/poll/map-back at lines 178-181, 50% discount + 24-hour SLA at lines 180/183, synchronous fallback at line 185.
**Location:** skills/harness-sprint/SKILL.md:172-185

### 8. README.md documents the new config knobs
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran the compound grep chain for `thinking.profile`, `default`, `fast`, `thorough`, `batch.enabled`, `batch.min_criteria` → exit 0. README.md contains an "Adaptive Thinking" section at lines 105-121 listing all three profile values and their effort vectors, and a "Batch API" section at lines 123-130 documenting both batch knobs with defaults.
**Location:** README.md:105-130

### 9. sprint-08.tasks.json is emitted
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `jq -e '.sprint == 8 and (.tasks | length) >= 13 and (.tasks | all(has("task_id") and has("grader_type") and has("weight") and has("is_gate")))' .harness/contracts/sprint-08.tasks.json` → exit 0 (output `true`). File contains all 16 tasks (13 scored + 3 gate, confirmed via `jq '.tasks | length'` → 16) with the required schema fields. Gate criteria SN1–SN3 present with `is_gate: true` and `weight: 0`.
**Location:** .harness/contracts/sprint-08.tasks.json

### 10. Per-mode thinking overrides are internally consistent
**Grader:** llm-judge
**Result:** PASS
**Evidence:** Applied the three-part reading test across `agents/planner.md`, `agents/generator.md`, `agents/evaluator.md`, and `skills/harness-summary/SKILL.md`:
(a) **Baselines and rationale** — planner.md:7-9 declares `effort: medium` (frontmatter alone signals routine work; body at line 12 confirms "product strategist" role); generator.md:8-10 declares `medium` with body text at line 75 explicitly labeling it "the IMPLEMENTATION baseline — pragmatic, code-writing work constrained by an already-approved contract"; evaluator.md:9-11 declares `high` with the "Thinking Effort" section at lines 72-85 framing it as "the Evaluator's capability-eval baseline"; harness-summary SKILL.md:5-7 declares `max` (rationale visible in the contract + summary role of "cross-sprint analysis, saturation detection, ACI review" per README.md:113).
(b) **Per-mode overrides** — generator.md:77-79 names CONTRACT_PROPOSAL at `high`, CONTRACT_REVISION at `high`, IMPLEMENTATION at `medium`; evaluator.md:81-83 names CONTRACT_REVIEW at `max`, EVALUATION (capability) at `high`, EVALUATION (regression, Step 0.5) at `medium`.
(c) **Sprint-7 caveat update** — The Sprint-7 "Status: policy-only until Sprint 8" paragraph has been replaced in evaluator.md:79-85 with "**Frontmatter and overrides.** The frontmatter declares `effort: high` as the capability-evaluation baseline. Per-mode overrides …" — the policy-only caveat is gone and the frontmatter wiring is explicit. A reader can explain all three parts directly from the files.
**Location:** agents/planner.md:7-9, agents/generator.md:8-10/73-81, agents/evaluator.md:9-11/72-85, skills/harness-summary/SKILL.md:5-7

### 11. Backward compatibility is explicit and correct
**Grader:** llm-judge
**Result:** PASS
**Evidence:** Three-way convergence verified:
(1) `.harness/config.json:29-35` ships with both objects present (`thinking.profile: "default"` and `batch: { enabled: false, min_criteria: 20 }`), so the harness's own config always works; README.md:121 states "An absent `thinking` object in `config.json` is treated as `profile: \"default\"` — Phase-1 behavior is preserved" and README.md:130 states "An absent `batch` object in `config.json` is treated as `enabled: false` — Phase-1 behavior is preserved."
(2) `skills/harness-sprint/SKILL.md:174` reads `config.batch.enabled` with explicit default `false` and `config.batch.min_criteria` with explicit default `20`; line 183 states "The `batch.enabled: false` default preserves Phase-1 behavior exactly — a project that never sets the flag never goes near the Batch API."
(3) Adaptive-thinking advisory nature — README.md:121 ("Adaptive-thinking frontmatter is advisory: a Claude Code runtime that ignores the `thinking:` key causes agents to run at the model's default, which matches pre-Sprint-8 behavior") and evaluator.md:85 ("A runtime that ignores the `thinking:` key causes the Evaluator to run at the model's default effort — backward-compatible with pre-Sprint-8 behavior"). Each of the three new config fields has a documented "if absent" default that reproduces Phase-1 behavior.
**Location:** README.md:105-130, skills/harness-sprint/SKILL.md:172-185, agents/evaluator.md:85

### 12. Batch threshold rationale is justified, not just asserted
**Grader:** llm-judge
**Result:** PASS
**Evidence:** The "Why this is opt-in and gated" paragraph at `skills/harness-sprint/SKILL.md:183` explains rather than asserts:
(a) 24-hour SLA unsuitability for iteration — "The Batch API offers a 50% token discount, but only in exchange for the 24-hour SLA" and "the tight contract→build→eval iteration cycle is unaffected" (line 183);
(b) Small-sprint latency-vs-savings tradeoff — "small sprints pay more in latency than they save in tokens, so the default `batch.min_criteria: 20` threshold keeps short feedback loops synchronous" (line 183);
(c) ~20 break-even point — "The break-even is roughly the point at which per-sprint criterion count crosses ~20: below that, submission overhead plus the 24-hour turnaround dominates; above it, the 50% token savings compound enough to justify the latency" (line 183).
A reader comes away understanding the SLA/discount tradeoff, the small-N problem, and why 20 specifically is the threshold.
**Location:** skills/harness-sprint/SKILL.md:183

### 13. thinking.profile override semantics are clear
**Grader:** llm-judge
**Result:** PASS
**Evidence:** README.md:115-121 documents the override semantics per the reference solution: three values listed with their effort vectors across all four agents/skills — `"default"` (each agent uses baseline), `"fast"` (shift one level down, clamped at `medium`; explicit vectors: planner `medium`, generator `medium`, evaluator `medium`, harness-summary `high`), `"thorough"` (shift one level up, clamped at `max`; vectors: planner `high`, generator `high`, evaluator `max`, harness-summary `max`). The vector values match the reference solution table in the contract. Line 121 documents composition: "Per-mode overrides (Generator CONTRACT_PROPOSAL at `high`, Evaluator CONTRACT_REVIEW at `max`, Evaluator regression-gate at `medium`) compose on top of the profile-adjusted baseline." Setting the profile in `config.json` under `thinking.profile` is stated on line 115.
**Location:** README.md:104-121

## Gate (Should-NOT) Results

### SN1. No silent behavior change for pre-Phase-2 configs
**Grader:** llm-judge
**Result:** PASS
**Evidence:** Every new config reference is guarded or defaulted:
- `skills/harness-sprint/SKILL.md:174` reads `config.batch.enabled` with explicit `(default false)` and `config.batch.min_criteria` with explicit `(default 20)`. Execution is gated on "both `batch.enabled` is true AND the sprint contract has at least `batch.min_criteria` criteria"; otherwise "run Step 3b synchronously as before — this is the default path."
- Line 183 states explicitly: "The `batch.enabled: false` default preserves Phase-1 behavior exactly — a project that never sets the flag never goes near the Batch API."
- README.md:121 and README.md:130 independently document that absent `thinking` and `batch` objects are treated as defaults with Phase-1 behavior.
- evaluator.md:85 documents the advisory nature of frontmatter: "A runtime that ignores the `thinking:` key causes the Evaluator to run at the model's default effort — backward-compatible with pre-Sprint-8 behavior."
No unconditional execution path exists for the new config keys. A pre-Phase-2 config with neither object triggers exactly zero of the new behaviors.
**Location:** skills/harness-sprint/SKILL.md:174,183; README.md:121,130; agents/evaluator.md:85

### SN2. No modification of prior sprint artifacts
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `test -z "$(git diff HEAD -- .harness/evals/sprint-0[1-7]* .harness/contracts/sprint-0[1-7]*)"` → exit 0. Empty diff confirms no modifications to sprints 01-07 eval and contract artifacts.

### SN3. Sprint-7 evaluator thinking-effort policy is preserved, not contradicted
**Grader:** llm-judge
**Result:** PASS
**Evidence:** Read the entire "Thinking Effort: Regression vs Capability Evaluation" section at `agents/evaluator.md:72-85`. Each Sprint-7 policy value still appears and is consistent throughout:
- **Regression at `medium`** — line 76 states "Regression-criterion evaluation (lower effort — `medium`)"; line 83 reinforces "EVALUATION (regression, Step 0.5) — `effort: medium`".
- **Capability at `high`** — line 77 states "Use `effort: high` for the capability pass"; line 82 reinforces "EVALUATION (capability) — the frontmatter baseline (`high`)".
- **Contract review at `max`** — line 77 states "`effort: max` when reviewing a *draft* contract"; line 81 reinforces "CONTRACT_REVIEW — `effort: max`".
The frontmatter (`effort: high` at agents/evaluator.md:11) matches the Sprint-7 capability-eval baseline. The "Status: policy-only until Sprint 8" caveat has been updated (git diff HEAD~3 confirms its replacement with the "Frontmatter and overrides" paragraph) — no contradictions introduced. No other section of evaluator.md declares a different effort value for any of these three modes.
**Location:** agents/evaluator.md:9-11, 72-85

## Rubric Scores

### Methodology Completeness (30%): 5/5
Sprint 8 closes two methodology gaps identified in the Phase 2 spec: Gap 5 (adaptive-thinking configuration, effort levels tuned to agent role) and Gap 7 (Batch API mode for large eval suites). Every agent and the summary skill now carry an `adaptive` thinking declaration tuned to the playbook's effort policy (`medium` for routine work, `high` for capability eval, `max` for summary analysis and contract review). The Batch API protocol at `skills/harness-sprint/SKILL.md:172-185` covers all 5 sub-requirements from Criterion 7's contract (config keys, guard condition, submit/poll/map-back, 50%/24-hour docs reference, synchronous fallback) and additionally preserves the "no silent criterion drop" invariant on fallback (line 185). Reference solutions from the contract are followed literally in the implementation. The Sprint-7 policy hook is consumed through the frontmatter + per-mode documentation path without contradiction, making the policy enforceable where it was previously policy-only.

### Grading Architecture (25%): 5/5
The code→LLM→human hierarchy is preserved. The Batch API protocol explicitly restricts itself to deterministic `verification_command` tasks and falls back to synchronous evaluation for LLM-judge criteria (line 181) — the hierarchy invariant is not weakened by the optimization. Evaluator per-mode effort (capability `high`, regression `medium`, contract review `max`) directly instruments reasoning depth into grader type, sharpening the architecture. `tasks.json` continues to serve as the source of record for verification commands — the Batch protocol at line 178 reads `.harness/contracts/sprint-{NN}.tasks.json` and collects items by task_id, preserving the audit chain. Fallback on batch failure is documented with explicit "Never silently drop criteria" invariant (line 185), which strengthens the architecture's commitment to evidence-based grading.

### Generator-Evaluator Separation (20%): 5/5
Forked-context isolation for the Evaluator remains intact (`context: fork` still present at `agents/evaluator.md:7`). Per-mode differentiation (capability/regression/contract-review) tightens the Evaluator's independent calibratability: the capability pass runs at `high` (deeper investigation); the regression pass runs at `medium` (fast pass/fail on pre-calibrated commands); the contract-review pass runs at `max` (thorough gap-finding). Generator-side symmetry: CONTRACT_PROPOSAL and CONTRACT_REVISION invoke higher effort than IMPLEMENTATION, matching the Evaluator's CONTRACT_REVIEW elevation. SN3's three-way reinforcement (frontmatter + body + explicit should-NOT) against cross-sprint policy drift is the appropriate defense for a policy hook.

### Context Engineering (15%): 5/5
JSON-for-state / markdown-for-prose discipline maintained: `.harness/config.json` extended with two new objects (`thinking`, `batch`) both using JSON; prose documentation in markdown (README.md, SKILL.md bodies). The `thinking.profile` knob is a single-value switch that operators can tune without editing frontmatter across four files — classic ACI simplification. `config.thinking.profile` composition on per-mode overrides is documented at README.md:121 as "compose on top of the profile-adjusted baseline", making the composition semantics explicit. The harness-summary skill itself being at `effort: max` improves cross-sprint analysis fidelity — directly relevant to the Context Engineering dimension.

### Extensibility & ACI (10%): 5/5
The two new config objects (`thinking.profile`, `batch`) are additive with documented defaults that reproduce Phase-1 behavior (README.md:121,130). A future per-agent override (`thinking.per_agent.evaluator = "max"`) is pre-announced as an extension point (sprint contract's Technical Notes). The Batch API path is CLI-flag-free (contract explicitly chose config-gating over `--batch` flag to match the existing skill architecture), reducing surface-area drift. Tool descriptions follow ACI best practices: frontmatter `name`/`description` fields present, effort levels semantically named (`medium`/`high`/`max` rather than opaque numeric values).

## Human Review Flags
None. All criteria passed with strong, reproducible evidence.
