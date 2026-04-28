---
name: harness-sprint
description: Run one sprint through the contract-build-eval cycle
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, Edit
disable-model-invocation: true
---

# Sprint Workflow

You are running one sprint through the full Planner-Generator-Evaluator cycle. This skill manages the contract negotiation, build, evaluation, and retry loop for a single sprint.

## Step 0: Determine Which Sprint to Run

1. Read `.harness/config.json` to get configuration
2. Read `.harness/sprint-state.json` for machine-readable sprint status (current sprint, step, results). If it does not exist, fall back to `.harness/progress.md`.
3. Read `.harness/sprints.json` to get the sprint list
4. Read `.harness/progress.md` to determine which sprints have completed (cross-reference with JSON state)
5. If the user specified a sprint number (e.g., `/harness-sprint 3`), use that
6. Otherwise, pick the next incomplete sprint from `sprint-state.json`

If all sprints are complete, tell the user and suggest `/harness-summary`.

## Step 0.5: Regression Gate

Before negotiating any new contract, verify that every previously graduated capability still passes. A regression gate is necessary here — not later — because a new sprint's criteria are independent of prior capabilities: the new eval can grade PASS on fresh work while a graduated capability has silently broken. Running the gate *after* the new sprint's eval would let the system ship a green score even though it regressed, overstating system health in the metrics. Running it *before* contract negotiation means the sprint cannot even begin defining new work until existing capability is verified intact. This is why the gate is `fail_fast` by default, not a warning.

### Guard conditions — when Step 0.5 is a no-op

1. If `.harness/regression/regression.json` does **not** exist, skip this step entirely. This is the Phase 1 path: projects that have never graduated a criterion see no behavior change — there is no file to read, no command to run, no abort to trigger.
2. If `.harness/regression/regression.json` exists but its `tasks` array is empty, skip this step. An empty suite is indistinguishable from no suite.
3. If `config.regression.enabled` is explicitly `false`, skip this step. The operator has disabled the gate on purpose.
4. Otherwise (file exists with a non-empty `tasks` array, and `regression.enabled` is truthy or absent — the auto-default), execute the gate as described below.

### Execution

1. Read `.harness/regression/regression.json`.
2. For each entry in the `tasks` array:
   - Execute `task.verification_command` **verbatim** — do not paraphrase, reconstruct, or substitute variables. The exact string recorded in `regression.json` is what ran when the criterion was graduated; running the same command preserves the audit chain.
   - Record PASS if exit code is `0`, FAIL otherwise. Capture stdout, stderr, and exit code.
3. Write an aggregate results file to `.harness/regression/runs/run-<UTC-ISO8601>.json` with shape:
   ```json
   { "timestamp": "2026-04-24T18:45:00Z", "sprint_about_to_run": 7,
     "results": [
       { "task_id": "s02-c4", "graduated_from_sprint": 5,
         "verification_command": "...", "verdict": "PASS",
         "exit_code": 0, "stdout": "...", "stderr": "..." }
     ] }
   ```
4. If any task's verdict is FAIL:
   - Read `config.regression.fail_fast` (default `true` when absent).
   - If `fail_fast` is true: **abort the sprint**. Print the failing `task_id`s along with their `graduated_from_sprint` origin so the user immediately knows which capability regressed and which sprint graduated it. Do not proceed to Step 1.
   - If `fail_fast` is false: print a warning, note the regression in `progress.md`, and continue to Step 1.
5. If every task passes (or the step was skipped), continue to Step 1.

### Config defaults

- `config.regression.enabled` — default is *auto*: truthy when `regression.json` exists with a non-empty `tasks` array, falsy otherwise. A missing `regression` object in `config.json` is equivalent to `enabled: null` (auto).
- `config.regression.fail_fast` — default `true`. A missing value means abort on any regression failure.

These defaults guarantee that a pre-Phase-2 project with no `regression` object and no `regression.json` file experiences no behavior change.

## Step 1: Contract Negotiation

If `components_enabled.contract_negotiation` is true in config:

### 1a. Propose Contract

The contract (`.harness/contracts/sprint-{NN}.md`) gets drafted using the sprint-contract template either by the Generator subagent or by the main thread, depending on `components_enabled.generator_subagent`. The output file format and downstream consumers are identical in both branches.

**If `components_enabled.generator_subagent` is true** (standard mode): spawn the Generator subagent in `CONTRACT_PROPOSAL` mode.
- Tell it which sprint number and title it's working on
- Tell it to read `.harness/spec.md` and `.harness/sprints.json`
- Tell it to read any prior contracts in `.harness/contracts/` and eval results in `.harness/evals/`
- If `.harness/bootstrap/failure-catalog.json` exists, tell it to read the catalog and incorporate relevant failure cases as sprint criteria (the `success_criteria` field maps directly to contract criteria; include `reference_solution` entries in the contract's Reference Solutions section)
- Tell it to write a draft contract to `.harness/contracts/sprint-{NN}.md` using the sprint-contract template
- Tell it to ONLY write the contract — do NOT implement anything yet

**If `components_enabled.generator_subagent` is false** (minimal mode): draft the contract in the main thread following `agents/generator.md` CONTRACT_PROPOSAL mode rules.
- Read `.harness/spec.md`, `.harness/sprints.json`, the current sprint number and title, any prior contracts in `.harness/contracts/`, and prior eval results in `.harness/evals/`
- Read the sprint-contract template at `skills/sprint-contract/template.md` and follow it
- If `.harness/bootstrap/failure-catalog.json` exists, read it and fold relevant failures into the contract
- Write the draft contract to `.harness/contracts/sprint-{NN}.md` with weighted **Success Criteria** split into `Deterministic` and `LLM-as-judge` groups (weights sum to 100%), **Should-NOT** gate criteria, **Reference Solutions** for the highest-weighted LLM-judge criterion, **Out of Scope**, and **Technical Notes**
- Do not implement anything in this step — only produce the contract

### 1b. Evaluator Reviews Contract

Spawn the Evaluator subagent (this happens in both modes — the Evaluator always runs forked):
- Tell it to read the draft contract at `.harness/contracts/sprint-{NN}.md`
- Tell it to review for: testability, completeness, and specificity
- Tell it to append its feedback to the contract file under a `## Evaluator Review` section
- If it approves, it writes `**Status: APPROVED**`
- If it wants changes, it writes `**Status: NEEDS REVISION**` with specific feedback

### 1c. Negotiation Loop

Read the contract file. If status is NEEDS REVISION and negotiation round < `contract_negotiation_rounds`:
- Revise the contract based on feedback — in standard mode, spawn Generator in `CONTRACT_REVISION` mode; in minimal mode, revise the contract in the main thread following the Evaluator's feedback line by line, editing `.harness/contracts/sprint-{NN}.md` directly
- Spawn Evaluator again to review the revision (always forked, both modes)
- Repeat until APPROVED or max rounds reached

If max rounds reached without approval, proceed with the latest version and note this in progress.md.

If `contract_negotiation` is disabled, whoever drafted the contract (Generator or main thread) writes it once and it's automatically approved.

## Step 2: Implementation

**If `components_enabled.generator_subagent` is true** (standard mode): spawn the Generator subagent in `IMPLEMENTATION` mode.
- Tell it the sprint contract is finalized at `.harness/contracts/sprint-{NN}.md`
- Tell it to implement everything specified in the contract
- Tell it to commit working code with conventional commit format: `feat(sprint-{NN}): <description>`
- Tell it to self-review before declaring done, but NOT to grade itself
- Tell it to read prior eval results if this is a retry round, and fix the specific issues cited

**If `components_enabled.generator_subagent` is false** (minimal mode): implement in the main thread following `agents/generator.md` IMPLEMENTATION mode rules.
- Read the finalized contract at `.harness/contracts/sprint-{NN}.md`
- Read prior eval results in `.harness/evals/sprint-{NN}.md` if this is a retry round — the Evaluator cited exact file paths and line numbers; fix those specific issues
- Plan the implementation approach, then implement, committing after each meaningful unit of work using `feat(sprint-{NN}): <description>` (or `fix(sprint-{NN}): <what was fixed>` on retry rounds)
- If a design decision affects future sprints, note it in the contract file under `## Technical Notes`
- Self-review against the contract's success criteria before proceeding to evaluation, but do not grade your own work — that is the Evaluator's job. Verify completeness only (criteria addressed, code compiles/runs, no obvious bugs, commits clean).

## Step 3: Evaluation

### 3a. Pre-Evaluation Clean State Check

Before spawning the evaluator, verify the environment is in a clean state for a fair evaluation:

1. **Check for leftover artifacts:** If prior evaluation rounds ran (retry scenario), ensure no temporary files, test outputs, or cached state from those rounds could influence the new evaluation. For projects with build artifacts, consider whether a clean build is needed.
2. **Verify fresh process state:** If the sprint involves running servers or services, ensure they are restarted fresh rather than reusing state from the generator's development session.
3. **Git state check:** Run `git status` to confirm all implementation changes are committed. Uncommitted changes suggest incomplete work.

If the environment cannot be verified clean, note this in progress.md and inform the user before proceeding.

### 3b. Spawn Evaluator

Spawn the Evaluator subagent:
- Tell it to read the sprint contract from `.harness/contracts/sprint-{NN}.md`
- Tell it to read `.harness/config.json` to determine the project type and rubric
- Tell it to load and apply the appropriate rubric from the eval-rubric skill
- Tell it to test every criterion in the contract by actually running tests, hitting endpoints, checking files
- Tell it to write results to `.harness/evals/sprint-{NN}-r{R}.md` where {R} is the current round number (1 for first evaluation, 2 for first retry eval, etc.) — or, when `trials > 1`, to `.harness/evals/sprint-{NN}-r{R}-t{T}.md` (see Step 3c below)
- Tell it which round number this is and, if applicable, which trial number
- Tell it to grade as PASS or FAIL with specific evidence for each criterion

See Step 3c for how many times to spawn the Evaluator (once vs. once per trial) and for the file-copy logic to `.harness/evals/sprint-{NN}.md`.

### 3c. Trial Loop vs Retry Loop (statistical foundation)

**Read `config.trials` (default `1` if absent).** This controls the **trial loop**, which is independent of the retry loop in Step 4.

**Distinction — critical for pass@k / pass^k validity:**

| Loop | Purpose | File naming | Code state |
|------|---------|-------------|------------|
| Retry loop (Step 4) | Bug-fix after FAIL: Generator edits code and re-evaluates | `sprint-NN-rR.md` with next round number | Code changes between rounds |
| Trial loop (this step) | Measurement: independent trials at fixed code state | `sprint-NN-rR-tT.md` with trial suffix | Code is frozen; only trial-time non-determinism varies |

Trials measure the probability of the current code passing; retries measure whether the Generator can fix a bug. Collapsing them double-counts a fixed bug as evidence of inconsistency, so pass@k and pass^k are only statistically valid when computed from trial files (`-tT`), not round files (`-rR`).

**Behavior by `trials` value:**

- **If `trials == 1` (default, backward-compatible):** write exactly one eval file to `.harness/evals/sprint-{NN}-r{R}.md`. Do NOT emit a `-t1` variant. This is the current Phase 1 behavior — unchanged.
- **If `trials > 1`:** for each trial `T` in `1..trials`:
  1. Reset to a clean git state: stash any working-copy changes, check out the sprint head commit, and ensure `git status` is clean. Restore the stash after the trial finishes.
  2. Apply the Pre-eval Sandbox Setup from `agents/evaluator.md` (based on `config.sandbox.mode`).
  3. Spawn the Evaluator, passing it round `R` and trial `T`, and have it write to `.harness/evals/sprint-{NN}-r{R}-t{T}.md`.
  4. Do NOT copy trial files over the `sprint-{NN}.md` latest-copy path until the trial loop completes. After all trials finish, copy the result of trial 1 (by convention) to `sprint-{NN}.md` so the retry loop has a stable reference.

The retry loop in Step 4 is unchanged: a FAIL verdict (aggregated across trials when `trials > 1`) triggers a new round `R+1`, and the trial loop repeats at the new code state.

After the Evaluator finishes, read the appropriate file (`sprint-{NN}-r{R}.md` for single-trial or the trial files for multi-trial) and check the verdict. Copy the latest eval to `.harness/evals/sprint-{NN}.md` so the Generator always has a stable path for the latest eval.

## Step 4: Retry Loop

If the verdict is FAIL and retry count < `max_retries` from config:

1. Increment retry count
2. Go back to Step 2 with the same `components_enabled.generator_subagent` branch that was used initially. In standard mode, tell the Generator to:
   - Read the eval results at `.harness/evals/sprint-{NN}.md`
   - Focus on fixing the specific FAIL criteria
   - The Evaluator cited exact file paths and line numbers — address those
   - Commit fixes with: `fix(sprint-{NN}): <what was fixed>`
   In minimal mode, the main thread reads the eval results and applies the same fixes itself.
3. Then go to Step 3 for re-evaluation
4. The Evaluator writes fresh results to `.harness/evals/sprint-{NN}-r{R}.md` (next round number), then the workflow copies it to `.harness/evals/sprint-{NN}.md`

If max retries exhausted with failures remaining, note this in progress.md and inform the user.

## Step 5: Sprint Completion

Once the sprint passes (or max retries exhausted):

1. Update `.harness/progress.md`:
   ```markdown
   ## Sprint {NN}: {Title}
   - Status: PASS | PARTIAL | FAIL
   - Rounds: {number of eval rounds}
   - Passed criteria: X/Y
   - Date: {current date}
   ```

2. Update `.harness/sprint-state.json` — update the sprint entry with final status, rounds, criteria passed/total, and weighted score. Advance `current_sprint` to the next sprint number. Update `last_updated` timestamp.

3. Git checkpoint:
   ```bash
   git add .harness
   git commit -m "harness: complete sprint {NN} evaluation"
   ```

3. Report to the user:
   - Sprint outcome (PASS/PARTIAL/FAIL)
   - How many rounds it took
   - Key findings from the eval
   - Suggest `/harness-sprint` for the next sprint or `/harness-summary` for a report

## Session Resumption

When resuming a harness session after interruption or context compaction:

1. **Read `.harness/sprint-state.json`** first — it provides the machine-readable current state:
   - `current_sprint` tells you which sprint was active
   - Each sprint's `status` tells you whether it completed
   - If the current sprint has no entry or status is `"in_progress"`, it was interrupted
2. **Cross-reference with git log** — check for sprint-related commits to understand what was implemented
3. **Check for partial evaluation rounds** — look in `.harness/evals/` for `sprint-{NN}-r{R}.md` files. If a round file exists but `sprint-state.json` does not reflect its results, the evaluation completed but the state was not updated
4. **Determine the exact resumption point** within the sprint:
   - No contract file → resume at Step 1 (Contract Negotiation)
   - Contract exists but no eval results → resume at Step 2 (Implementation) or Step 3 (Evaluation)
   - Eval results exist with FAIL verdict and retries remaining → resume at Step 4 (Retry Loop)
   - Eval results exist with PASS → resume at Step 5 (Sprint Completion)
5. **Read `.harness/progress.md`** for human-readable session notes that may provide additional context about what was happening when the session ended

If `sprint-state.json` does not exist (pre-Sprint-4 harness), fall back to the legacy method: read `progress.md` and git log only.
