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

## Step 0.4: Pre-Sprint Governance Gate (b1)

When `config.governance.enabled` is `true` AND `config.governance.review_frequency` is set (any value), check for the sprint prebrief file at `.council/sprint-prebrief/sprint-{NN}.json` (where NN is the sprint number about to run).

If the file is **absent**, emit a WARN message identifying the missing file path:

```
WARN: Council sprint prebrief not found: .council/sprint-prebrief/sprint-{NN}.json
      Proceeding without governance prebrief review.
```

**This gate does NOT block.** It is warn-only — the sprint proceeds regardless of whether the prebrief exists. The WARN is a signal to the governance-enabled operator that the council prebrief step was skipped.

**Backward compatibility:** When `config.governance.enabled` is `false` or the `governance` key is absent from `config.json`, this gate does not fire and no check is performed. A project without a governance config behaves identically to the pre-gate harness-sprint workflow. Governance is **off by default** — trine-eval ships with no `governance` key, so this gate is inert unless a governance layer (e.g. the henkaten-council plugin) is explicitly configured.

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

> **Windows-bash invocation hazard.** Do not invoke `task.verification_command` via `subprocess.run(['bash', '-c', cmd])`. On Windows with WSL installed, Python's PATH resolver picks `wsl bash` (no distros by default) and the command fails silently with a "no installed distributions" message. Use either `subprocess.run(cmd, shell=True)` (cmd.exe; finds `uv` on PATH) or explicit `C:\Program Files\Git\bin\bash.exe`. Surfaced in this project's Sprint 5 setup; workaround validated in Sprint 6 Step 0.5.

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
- Write the draft contract to `.harness/contracts/sprint-{NN}.md` with weighted **Success Criteria** (weights sum to 100%), each criterion tagged `behavioral`, `structural`, or `llm-judge` per the 3-way grader split — with behavioral criteria holding ≥ 60% of total weight unless the Technical Notes justify an exception; plus **Should-NOT** gate criteria, **Reference Solutions** for the highest-weighted LLM-judge criterion, **Out of Scope**, and **Technical Notes**
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

### 1d. After APPROVED — emit `tasks.json`

Per `skills/sprint-contract/SKILL.md` lines 90–132, the Generator (or main thread in minimal mode) writes `.harness/contracts/sprint-{NN}.tasks.json` immediately after the Evaluator writes `**Status: APPROVED**` and before the Generator enters IMPLEMENTATION mode. Emission is guarded by `config.taxonomy.emit_tasks_json` (default `true`). This is a mechanical transcription of the approved markdown contract — schema and field semantics are defined in sprint-contract SKILL. The JSON file is the machine-readable source of record for the Step 0.5 regression gate, batched-eval grouping, and harness-summary's saturation-graduation step. Skipping emission forces downstream synthesis from markdown — every graduated entry in `regression.json` will be flagged `synthesized_from: contract markdown` and the audit chain weakens.

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

### 3d. Batch API Mode (optional)

This subsection applies inside Step 3 — it routes the per-criterion verifications the Evaluator would otherwise perform synchronously through Anthropic's Batch API. It is a **cost optimization, not a latency optimization** — the published Batch API contract trades a 50% discount on input/output tokens for a 24-hour SLA.

**Trigger.** The batch path activates only when **both** of the following are true:

1. `config.batch.enabled == true` (the field is read from `.harness/config.json`; default `false`).
2. The sprint contract's criterion count (success criteria + Should-NOT gates, the same count emitted in `sprint-{NN}.tasks.json`) is greater than or equal to `config.batch.min_criteria` (default `20`).

If either condition is false, the synchronous path documented in Step 3b runs as today. A `.harness/config.json` lacking the `batch` object is equivalent to the default — `enabled: false`, `min_criteria: 20` — and the harness behaves exactly as in Phase 1 with no batch submission attempted.

**Why a threshold.** Batch overhead (request packaging, polling, result mapping) is fixed; the per-criterion savings scale with criterion count. Small sprints stay synchronous so contributors keep tight feedback loops; large suites (≥ `min_criteria`) absorb the overhead and earn the 50% discount on the bulk of their token spend.

**Execution (when the batch path activates).**

1. **Collect.** For each criterion in `.harness/contracts/sprint-{NN}.tasks.json`, build a Batch API request unit: deterministic criteria carry their `verification_command` and a structured "did the command exit 0?" prompt; LLM-judge criteria carry their criterion text plus the rubric dimension. Each unit is keyed by its `task_id` so results map back unambiguously.
2. **Submit.** POST a single batch to Anthropic's `/v1/messages/batches` endpoint. The submission contains every criterion as a custom-id-tagged request inside one batch envelope — N criteria collapse to 1 API call.
3. **Poll.** Wait for the batch to reach a terminal state. The 24-hour SLA is the upper bound; in practice batches typically complete sooner, but the workflow must not assume sub-hour latency. Configure operator-side timeouts to allow the documented 24 hours.
4. **Map back.** Parse the batch response, demultiplex by `custom_id` (= `task_id`), and write each result into its corresponding `## N. Criterion ...` slot in `.harness/evals/sprint-{NN}-r{R}.md` (or `-t{T}.md` for multi-trial). The per-criterion file shape is byte-for-byte identical to the synchronous path — downstream consumers (the regression gate at Step 0.5, the saturation detector in `harness-summary`, the Generator on retry) cannot tell whether batch or synchronous produced the file. **This invariant is critical.** Changing the file shape would cascade into every Sprint 7 / 9 / 10 deliverable.

**Backward compatibility.** With `config.batch.enabled == false` (the default), Step 3d is a no-op — the synchronous Step 3b path runs as in Phase 1. With `config.batch.enabled == true` but a small sprint (criterion count < `config.batch.min_criteria`), the batch path is *not* activated and Step 3b still runs synchronously. A project whose `.harness/config.json` lacks the `batch` object hits the default-false branch and sees zero behavior change.

**What this section does not promise.** It does not promise faster turnaround than synchronous calls — the tradeoff is cost for latency, not the reverse. It does not promise that the batch API request is wired up against a live `ANTHROPIC_API_KEY` in this sprint; the harness ships the protocol and the trigger conditions, while end-to-end batch submission against the live endpoint is verified post-Sprint-10 per the gap-closure plan.

### 3e. Transcript Capture (optional)

This subsection runs after the Evaluator's markdown eval lands. It extracts a structured JSON trailer from the evaluator's eval file and writes a sibling transcript file to `.harness/transcripts/`. The structured channel is the audit-grade record the harness-summary skill links from FAIL criteria and grader-disagreement entries — see `skills/harness-summary/SKILL.md`. The schema lives in `rules/harness-conventions.md` under the **Transcript Schema** section.

**Trigger.** Read `config.transcripts.capture` from `.harness/config.json` (default `true` when the `transcripts` object is present; absent means the legacy/Phase-1 default applies, see Backward compatibility below). If `config.transcripts.capture` is explicitly `false`, skip this step entirely. Otherwise proceed.

**Why a markdown trailer, not a runtime hook.** Sprint 9 ships the protocol — the Evaluator emits the structured payload at the end of its existing markdown eval, and the workflow extracts it. This avoids requiring runtime instrumentation of the evaluator subagent's message stream while still producing a machine-readable transcript file. End-to-end transcript writing against a live evaluator subagent is deferred to a synthetic verification sprint per the gap-closure plan, matching Sprint 8's posture for `thinking.profile`.

**Trailer extraction protocol.** Two independent implementers must produce equivalent transcript files from the same evaluator markdown eval, so the protocol is precise:

1. **Locate the trailer.** Read the markdown eval file just produced by the Evaluator (`.harness/evals/sprint-{NN}-r{R}-t{T}.md` for multi-trial, or `.harness/evals/sprint-{NN}-r{R}.md` for single-trial). Find the last `## Transcript Trailer` heading in the file. The body of that section is a fenced ` ```json ` code block containing the structured JSON payload the Evaluator produced. The Evaluator's instruction for emitting this block lives in `agents/evaluator.md`.
2. **Parse the trailer.** Extract the JSON between the fences and parse it. If the `## Transcript Trailer` section is missing, the fence is malformed, the JSON does not parse, or required top-level fields are absent, **skip the rest of this step** — do NOT fail the eval and do NOT fabricate a transcript. The eval verdict is unaffected; transcripts are an audit artifact, not a grading input. This failure-tolerant posture matches the regression gate's stance from Sprint 7.
3. **Write the transcript.** Write the parsed JSON verbatim to `.harness/transcripts/sprint-{NN}-r{R}-t{T}.json` (multi-trial) or `.harness/transcripts/sprint-{NN}-r{R}.json` (single-trial mode). The file naming mirrors the markdown eval naming so transcript-to-eval pairing is unambiguous.

**Backward compatibility.** A project whose `.harness/config.json` lacks the `transcripts` object and whose `agents/evaluator.md` predates Sprint 9 experiences no functional behavior change: the legacy evaluator does not emit a `## Transcript Trailer` section, so step 2 above falls into the failure-tolerant branch and no transcript file is written. The `config.transcripts.capture: true` default applies to fresh installs that picked up the updated agent file; for legacy projects, the no-op fallback preserves Phase-1 disk state. When `config.transcripts.capture` is explicitly `false`, this entire step is skipped and no extraction is attempted.

**What this section does not promise.** It does not promise that runtime-instrumented fields (`token_usage`, `timing`) are populated with real values — those fields are nullable and best-effort, per `rules/harness-conventions.md`. It does not promise retention enforcement; the `transcripts.retain_days` knob is a documented policy and cleanup runs out-of-band. It does not promise that every Evaluator implementation will emit a parseable trailer — the protocol's failure-tolerance is the design choice, not a bug.

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

> **Windows encoding hazard for `sprint-state.json` and `progress.md`.** Write JSON / markdown files containing UTF-8 superscripts (`²`, `³`), em-dashes, or other non-ASCII via `Path(...).write_text(content, encoding='utf-8')`. Bash heredocs on Windows + Git Bash produce mojibake (`²` becomes `Â²`). Multiple sprints in this project's run required the Python workaround when their progress entries contained `σ²` or similar.

4. **Post-Sprint Governance Auto-Trigger Gate (b2).** When `config.governance.enabled` is
   `true` AND `config.governance.review_frequency == "every-sprint"`, invoke
   `/henkaten-council:council-autorun` for the just-completed sprint as the final action of
   this step — **after** updating `progress.md`, `sprint-state.json`, and the git checkpoint
   (steps 1–3 above), but **before** reporting to the user (step 5 below).

   If `council-autorun` returns an andon halt or autonomy-floor breach, surface that result
   to the user **before** offering the next sprint. Do not proceed to offer the next sprint
   until the user acknowledges the andon-stop outcome.

   **Backward compatibility:** When `config.governance.enabled` is `false` or the `governance`
   key is absent from `config.json`, this gate does not fire. Governance is **off by default**;
   a project without a governance config behaves identically to the pre-gate harness-sprint
   workflow.

5. Report to the user:
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

## Operational Notes

### Evaluator Fallback

The Evaluator subagent runs forked (`context: fork` in `agents/evaluator.md`) and writes its eval markdown directly via the `Write` tool. This is the **default and preferred** path — forked context preserves Generator/Evaluator separation, which is one of the harness's core invariants.

**When the fallback applies.** If the Evaluator subagent fails to write the eval file due to a **tool limitation** (e.g., the agent's `tools:` frontmatter does not include `Write`, the agent's environment cannot execute a long heredoc reliably, or the subagent dispatch itself fails for infrastructure reasons), the main thread may transcribe the eval markdown into `.harness/evals/sprint-{NN}-r{R}.md` so the sprint can complete. This is an **escape valve, not a feature** — every fallback invocation is a regression in Generator/Evaluator separation that must be flagged.

**How to flag a fallback eval.** When the main thread writes the eval, it must add a `## Process Note` section near the top of the eval file explicitly disclosing:
- That the eval was authored by the main-thread orchestrator, not a forked Evaluator subagent
- The reason for the fallback (cite the specific tool limitation or dispatch failure)
- Which deterministic verification commands were run verbatim from the contract (so the audit chain is preserved even though the authorship is degraded)

**Why this matters.** The Sprint 11 round-1 eval was written via this fallback because the Evaluator's `tools:` line did not include `Write`. Sprint 12 closed the underlying tool limitation by adding `Write` to the agent's frontmatter, so the fallback should not fire under normal operation from Sprint 12 onward. The eval-summary skill and rubric `generator_evaluator_separation` dimension penalize fallback eval rounds — a sprint whose eval was written via fallback typically scores 3/5 on that dimension instead of 5/5, regardless of the underlying technical correctness of the verifications.

### thinking.profile

`config.thinking.profile` (added in Sprint 8) is a per-installation knob that selects how the harness translates the agent-frontmatter `thinking: { type: adaptive, effort: ... }` declarations into the runtime API parameters Anthropic's API expects. The reserved values are intentionally small.

**Reserved values and their runtime translation.**

- `"default"` → standard adaptive thinking. Each agent's frontmatter `effort: medium|high|max` maps to a budget consistent with the model's adaptive defaults. No override is applied at the orchestrator layer. This is the value the harness ships with.
- `"fast"` → no extended thinking. The orchestrator strips `thinking` from outgoing API requests regardless of the agent's frontmatter declaration. Trades accuracy for latency and cost; appropriate for CI smoke checks or operator iterations on contract drafting.
- `"thorough"` → high-budget extended thinking. The orchestrator forces a high `budget_tokens` setting on every thinking-enabled message, overriding the per-agent `effort` to its highest tier. Trades latency and cost for the highest reasoning quality available; appropriate for adversarial evaluation rounds or complex contract review.

**Documentation-only in Sprint 12.** The Sprint 12 deliverable for `thinking.profile` is the translation table above — a documentation criterion. The orchestrator-side wire-up that actually consumes `config.thinking.profile` and rewrites outgoing `thinking: {...}` parameters runs in the Claude Code runtime and is exercised end-to-end only when the harness drives a live API call through the new dispatcher. Sprint 12 ships the protocol and the values; the runtime hookup is observable when a downstream sprint or applied-harness use case exercises the live pipeline. The protocol-vs-runtime split here matches Sprint 8's posture for Batch API and Sprint 9's posture for transcript emission.
