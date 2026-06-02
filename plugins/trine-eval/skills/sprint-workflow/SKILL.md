---
name: sprint-workflow
description: Run one sprint through the contract-build-eval cycle
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, Edit
disable-model-invocation: true
---

# Sprint Workflow

You are running one sprint through the full Planner-Generator-Evaluator cycle. This skill manages the contract negotiation, build, evaluation, and retry loop for a single sprint.

## Step 0: Determine Which Sprint to Run

<!-- Context scope at this step: sprint-state.json (machine state), sprints.json (sprint list) -->
<!-- Deferred: spec.md, contracts/, evals/ — not needed until Step 1+ -->
<!-- Lazy reads: config.json (only if you need harness settings), progress.md (only if sprint-state.json absent) -->

1. Read `.harness/sprint-state.json` for machine-readable sprint status (current sprint, step, results). If it does not exist, fall back to `.harness/progress.md`.
2. Read `.harness/sprints.json` to get the sprint list
3. Read `.harness/config.json` to get configuration (defer this if sprint-state.json already tells you everything you need)
4. Read `.harness/progress.md` only if you need human-readable session notes to disambiguate state
5. If the user specified a sprint number (e.g., `/harness-sprint 3`), use that
6. Otherwise, pick the next incomplete sprint from `sprint-state.json`

Do NOT read spec.md, contracts/, or evals/ at this step — those are only needed later.

If all sprints are complete, tell the user and suggest `/harness-summary`.

### Pre-Sprint Governance Warn-Only Gate (b1)

When `config.governance.enabled` is `true` AND `config.governance.review_frequency` is set (any value), check for the sprint prebrief file at `.council/sprint-prebrief/sprint-{NN}.json` (where NN is the sprint number about to run).

If the file is **absent**, emit a WARN message identifying the missing file path:

```
WARN: Council sprint prebrief not found: .council/sprint-prebrief/sprint-{NN}.json
      Proceeding without governance prebrief review.
```

**This gate does NOT block.** It is warn-only — the sprint proceeds regardless of whether the prebrief exists. The WARN is a signal to the governance-enabled operator that the council prebrief step was skipped.

**Backward compatibility:** When `config.governance.enabled` is `false` or the `governance` key is absent from `config.json`, this gate does not fire and no check is performed. A project without a governance config behaves identically to the pre-gate sprint-workflow.

## Step 0.5: Regression Gate

Before negotiating any new contract, verify that every previously graduated capability still
passes. A regression gate is necessary here — not later — because a new sprint's criteria are
independent of prior capabilities: the new eval can grade PASS on fresh work while a graduated
capability has silently broken. Running the gate *before* contract negotiation means the sprint
cannot even begin defining new work until existing capability is verified intact. This is why
the gate is `fail_fast` by default, not a warning.

### Guard conditions — when Step 0.5 is a no-op

1. If `.harness/regression/regression.json` does **not** exist, skip this step entirely. This
   is the Phase 1 path: projects that have never graduated a criterion see no behavior change —
   there is no file to read, no command to run, no abort to trigger.
2. If `.harness/regression/regression.json` exists but its `tasks` array is empty, skip this
   step. An empty suite is indistinguishable from no suite.
3. If `config.regression.enabled` is explicitly `false`, skip this step. The operator has
   disabled the gate on purpose.
4. Otherwise (file exists with a non-empty `tasks` array, and `regression.enabled` is truthy
   or absent — the auto-default), execute the gate as described below.

### Execution

1. Read `.harness/regression/regression.json`.
2. For each entry in the `tasks` array:
   - Execute `task.verification_command` **verbatim** — do not paraphrase, reconstruct,
     or substitute variables. The exact string recorded in `regression.json` is what ran
     when the criterion was graduated; running the same command preserves the audit chain.
   - Record PASS if exit code is `0`, FAIL otherwise. Capture stdout, stderr, and exit code.

> **Windows-bash invocation hazard.** Do not invoke `task.verification_command` via
> `subprocess.run(['bash', '-c', cmd])`. On Windows with WSL installed, Python's PATH resolver
> picks `wsl bash` (no distros by default) and the command fails silently with a "no installed
> distributions" message. Use either `subprocess.run(cmd, shell=True)` (cmd.exe; finds tools on
> PATH) or explicit `C:\Program Files\Git\bin\bash.exe`. Surfaced in this project's Sprint 5
> setup; workaround validated in Sprint 6 Step 0.5.

3. Write an aggregate results file to `.harness/regression/runs/run-<UTC-ISO8601>.json` with
   shape:
   ```json
   { "timestamp": "2026-06-02T18:45:00Z", "sprint_about_to_run": 13,
     "results": [
       { "task_id": "s07-c1", "graduated_from_sprint": 7,
         "verification_command": "...", "verdict": "PASS",
         "exit_code": 0, "stdout": "...", "stderr": "" }
     ] }
   ```
4. If any task's verdict is FAIL:
   - Read `config.regression.fail_fast` (default `true` when absent).
   - If `fail_fast` is true: **abort the sprint**. Print the failing `task_id`s along with
     their `graduated_from_sprint` origin so the user immediately knows which capability
     regressed and which sprint graduated it. Do not proceed to Step 1.
   - If `fail_fast` is false: print a warning, note the regression in `progress.md`, and
     continue to Step 1.
5. If every task passes (or the step was skipped), continue to Step 1.

### Config defaults

- `config.regression.enabled` — default is *auto*: truthy when `regression.json` exists with
  a non-empty `tasks` array, falsy otherwise. A missing `regression` object in `config.json`
  is equivalent to `enabled: null` (auto).
- `config.regression.fail_fast` — default `true`. A missing value means abort on any
  regression failure.

These defaults guarantee that a pre-Phase-2 project with no `regression` object and no
`regression.json` file experiences no behavior change.

## Step 1: Contract Negotiation

<!-- Context scope at this step: spec.md, sprints.json, prior contracts/, prior evals/ -->
<!-- Deferred: config.json (resolved in Step 0), progress.md (resolved in Step 0) -->
<!-- Sub-agents receive condensed context summaries — not a file list to discover on their own -->

If `components_enabled.contract_negotiation` is true in config:

### 1a. Generator Proposes Contract

Spawn the Generator subagent with a condensed context summary:
- **Current sprint:** Sprint {NN} — "{sprint title from sprints.json}"
- **Prior sprint outcomes:** Summarize pass/fail status from sprint-state.json (e.g., "Sprint 1 PASS, Sprint 2 PASS")
- **Key constraint reminder:** Weights must sum to 100%; each criterion must be tagged `behavioral`, `structural`, or `llm-judge`; behavioral criteria must hold ≥ 60% of total weight (or the contract's Technical Notes must justify the exception)
- Tell it to read `.harness/spec.md` for the full product vision
- Tell it to read `.harness/sprints.json` for its sprint's specific scope
- Tell it to read prior contracts in `.harness/contracts/` (only those needed for calibration, not all of them)
- Tell it to read prior eval results in `.harness/evals/` only if this sprint builds on prior outcomes
- If `.harness/bootstrap/failure-catalog.json` exists, tell it to read the catalog and incorporate relevant failure cases as sprint criteria (the `success_criteria` field maps directly to contract criteria; include `reference_solution` entries in the contract's Reference Solutions section)
- Tell it to write a draft contract to `.harness/contracts/sprint-{NN}.md` using the sprint-contract template
- Tell it to ONLY write the contract — do NOT implement anything yet
<!-- Condensed context above reduces Generator cold-start overhead — it gets key facts inline, not just file paths to discover -->

### 1b. Evaluator Reviews Contract

Spawn the Evaluator subagent with a condensed context summary:
- **Task:** Review draft contract for Sprint {NN} at `.harness/contracts/sprint-{NN}.md`
- **Sprint context:** Brief description of what this sprint builds (e.g., "Metrics sprint — adds pass@k tracking")
- **Prior baseline:** Note which prior sprints are approved and do not need re-evaluation
- **What to read:** Only the draft contract at the path above — not the full `.harness/` directory
- Tell it to review for: testability, completeness, and specificity
- Tell it to append its feedback to the contract file under a `## Evaluator Review` section
- If it approves, it writes `**Status: APPROVED**`
- If it wants changes, it writes `**Status: NEEDS REVISION**` with specific feedback
<!-- Condensed context above replaces the need for Evaluator to read spec.md, all prior contracts, all evals -->
<!-- Sub-agent gets what it needs to act, not a list of files to discover context from -->
<!-- This reduces sub-agent cold-start overhead and prevents unnecessary context consumption -->

### 1c. Negotiation Loop

Read the contract file. If status is NEEDS REVISION and negotiation round < `contract_negotiation_rounds`:
- Spawn Generator again to revise the contract based on feedback
- Spawn Evaluator again to review the revision
- Repeat until APPROVED or max rounds reached

If max rounds reached without approval, proceed with the latest version and note this in progress.md.

If `contract_negotiation` is disabled, the Generator writes the contract and it's automatically approved.

### 1d. After APPROVED — emit `tasks.json`

**Trigger:** Immediately after the Evaluator writes `**Status: APPROVED**` and before the
Generator enters IMPLEMENTATION mode.

**Config guard:** Guarded by `config.taxonomy.emit_tasks_json` (default `true`). If this is
explicitly `false`, skip this step. Otherwise proceed.

**What to emit:** Write `.harness/contracts/sprint-{NN}.tasks.json` — the machine-readable
source of record for the sprint's criteria. Schema and field semantics are defined in
`skills/sprint-contract/SKILL.md` (Task Taxonomy section). The JSON file feeds:
- The regression gate at Step 0.5
- Batched-eval grouping in Step 3d
- The harness-summary saturation-graduation step

**Consequence of skipping:** Downstream synthesis must fall back to parsing the markdown
contract — every graduated entry in `regression.json` will be flagged
`synthesized_from: contract markdown` and the audit chain weakens.

**features.json advancement (DEC-0019):** When `emit_tasks_json` runs, also advance
`.harness/features.json` by appending any new sprint features from
`sprints.json[sprint].features`. The merge is **additive by feature slug**: for each feature
id listed in the sprint's `features` array, append it to `.harness/features.json` only if an
entry with that id does not already exist. **Do not overwrite existing entries.** This closes
the recurring SG drift pattern where `features.json` fell behind the sprint completion state.
If `.harness/features.json` does not exist, create it with the new features as the initial
content.

## Step 2: Implementation

<!-- Context scope at this step: contracts/sprint-{NN}.md only (finalized contract) -->
<!-- Deferred: evals/ (only if retry round), source files (read on-demand during implementation) -->
<!-- Per-step context retrieval: Generator reads only the contract to start; other reads are deferred -->

Spawn the Generator subagent with a condensed context summary:
- **Task:** Implement Sprint {NN} — "{sprint title}"
- **Contract location:** `.harness/contracts/sprint-{NN}.md` (finalized and approved)
- **Retry round:** Yes/No — if Yes, also read `.harness/evals/sprint-{NN}.md` for specific FAIL criteria to fix
- **Prior sprint outcomes (for context):** Brief summary (e.g., "Sprint 1-2 passed, no regressions expected")
<!-- Condensed context summary prevents Generator from re-reading all prior history unnecessarily -->
- Tell it the sprint contract is finalized at `.harness/contracts/sprint-{NN}.md`
- Tell it to implement everything specified in the contract
- Tell it to commit working code with conventional commit format: `feat(sprint-{NN}): <description>`
- Tell it to self-review before declaring done, but NOT to grade itself
- Tell it to read prior eval results only if this is a retry round, and fix the specific issues cited

## Step 3: Evaluation

<!-- Context scope at Step 3: contracts/sprint-{NN}.md, config.json, rubric file (deferred until 3b) -->
<!-- Deferred: evals/ from prior sprints (not needed), progress.md (not needed for evaluation) -->

### 3a. Pre-Evaluation Clean State Check

Before spawning the evaluator, verify the environment is in a clean state for a fair evaluation:

1. **Check for leftover artifacts:** If prior evaluation rounds ran (retry scenario), ensure no temporary files, test outputs, or cached state from those rounds could influence the new evaluation. For projects with build artifacts, consider whether a clean build is needed.
2. **Verify fresh process state:** If the sprint involves running servers or services, ensure they are restarted fresh rather than reusing state from the generator's development session.
3. **Git state check:** Run `git status` to confirm all implementation changes are committed. Uncommitted changes suggest incomplete work.

If the environment cannot be verified clean, note this in progress.md and inform the user before proceeding.

### 3b. Spawn Evaluator

Spawn the Evaluator subagent with a condensed context summary:
- **Task:** Evaluate Sprint {NN} — "{sprint title}" at round {R}
- **Contract location:** `.harness/contracts/sprint-{NN}.md`
- **Project type:** {project_type from config.json} — rubric: {rubric name}
- **Round:** {R} (1 = initial, 2+ = retry); if retry, prior round results are at `.harness/evals/sprint-{NN}-r{prev_R}.md`
- **Output location:** Write results to `.harness/evals/sprint-{NN}-r{R}.md`
<!-- Condensed context above means Evaluator does not need to read all of .harness/ to begin -->
<!-- Evaluator pulls additional context on-demand: reads contract first, rubric only when scoring, evals only if retry -->
- Tell it to read the sprint contract from `.harness/contracts/sprint-{NN}.md`
- Tell it to read `.harness/config.json` to determine the project type and rubric (may already know from condensed context)
- Tell it to load and apply the appropriate rubric from the eval-rubric skill
- Tell it to test every criterion in the contract by actually running tests, hitting endpoints, checking files
- Tell it to write results to `.harness/evals/sprint-{NN}-r{R}.md` where {R} is the current round number (1 for first evaluation, 2 for first retry eval, etc.). **IMPORTANT:** Always use the `r{R}` naming convention for every round, including Round 1. Never write directly to `sprint-{NN}.md` — always write to the round-specific file first, then copy. Round files are append-only and must never be deleted (they are needed for pass@k/pass^k computation).
- Tell it which round number this is
- Tell it to grade as PASS or FAIL with specific evidence for each criterion

See Step 3c for how many times to spawn the Evaluator (once vs. once per trial) and for the file-copy logic to `.harness/evals/sprint-{NN}.md`.

### 3c. Trial Loop vs Retry Loop (statistical foundation)

**Read `config.trials` (default `1` if absent).** This controls the **trial loop**, which is
independent of the retry loop in Step 4.

**Distinction — critical for pass@k / pass^k validity:**

| Loop | Purpose | File naming | Code state |
|------|---------|-------------|------------|
| Retry loop (Step 4) | Bug-fix after FAIL: Generator edits code and re-evaluates | `sprint-NN-rR.md` with next round number | Code changes between rounds |
| Trial loop (this step) | Measurement: independent trials at fixed code state | `sprint-NN-rR-tT.md` with trial suffix | Code is frozen; only trial-time non-determinism varies |

Trials measure the probability of the current code passing; retries measure whether the
Generator can fix a bug. Collapsing them double-counts a fixed bug as evidence of
inconsistency, so pass@k and pass^k are only statistically valid when computed from trial
files (`-tT`), not round files (`-rR`).

**Behavior by `trials` value:**

- **If `trials == 1` (default, backward-compatible):** write exactly one eval file to
  `.harness/evals/sprint-{NN}-r{R}.md`. Do NOT emit a `-t1` variant. This is the current
  Phase 1 behavior — unchanged.
- **If `trials > 1`:** for each trial `T` in `1..trials`:
  1. Reset to a clean git state: stash any working-copy changes, check out the sprint head
     commit, and ensure `git status` is clean. Restore the stash after the trial finishes.
  2. Apply the Pre-eval Sandbox Setup from `agents/evaluator.md` (based on
     `config.sandbox.mode`).
  3. Spawn the Evaluator, passing it round `R` and trial `T`, and have it write to
     `.harness/evals/sprint-{NN}-r{R}-t{T}.md`.
  4. Do NOT copy trial files over the `sprint-{NN}.md` latest-copy path until the trial loop
     completes. After all trials finish, copy the result of trial 1 (by convention) to
     `sprint-{NN}.md` so the retry loop has a stable reference.

The retry loop in Step 4 is unchanged: a FAIL verdict (aggregated across trials when
`trials > 1`) triggers a new round `R+1`, and the trial loop repeats at the new code state.

After the Evaluator finishes, read the appropriate file (`sprint-{NN}-r{R}.md` for
single-trial or the trial files for multi-trial) and check the verdict. Copy the latest eval
to `.harness/evals/sprint-{NN}.md` so the Generator always has a stable path for the latest eval.

### 3d. Batch API Mode (optional)

This subsection applies inside Step 3 — it routes the per-criterion verifications the
Evaluator would otherwise perform synchronously through Anthropic's Batch API. It is a
**cost optimization, not a latency optimization** — the published Batch API contract trades a
50% discount on input/output tokens for a 24-hour SLA.

**Trigger.** The batch path activates only when **both** of the following are true:

1. `config.batch.enabled == true` (the field is read from `.harness/config.json`; default
   `false`).
2. The sprint contract's criterion count (success criteria + Should-NOT gates, the same count
   emitted in `sprint-{NN}.tasks.json`) is greater than or equal to `config.batch.min_criteria`
   (default `20`).

If either condition is false, the synchronous path documented in Step 3b runs as today. A
`.harness/config.json` lacking the `batch` object is equivalent to the default —
`enabled: false`, `min_criteria: 20` — and the harness behaves exactly as in Phase 1 with
no batch submission attempted.

**Why a threshold.** Batch overhead (request packaging, polling, result mapping) is fixed;
the per-criterion savings scale with criterion count. Small sprints stay synchronous so
contributors keep tight feedback loops; large suites (>= `min_criteria`) absorb the overhead
and earn the 50% discount on the bulk of their token spend.

**Execution (when the batch path activates).**

1. **Collect.** For each criterion in `.harness/contracts/sprint-{NN}.tasks.json`, build a
   Batch API request unit: deterministic criteria carry their `verification_command` and a
   structured "did the command exit 0?" prompt; LLM-judge criteria carry their criterion text
   plus the rubric dimension. Each unit is keyed by its `task_id` so results map back
   unambiguously.
2. **Submit.** POST a single batch to Anthropic's `/v1/messages/batches` endpoint. The
   submission contains every criterion as a custom-id-tagged request inside one batch
   envelope — N criteria collapse to 1 API call.
3. **Poll.** Wait for the batch to reach a terminal state. The 24-hour SLA is the upper
   bound; in practice batches typically complete sooner, but the workflow must not assume
   sub-hour latency.
4. **Map back.** Parse the batch response, demultiplex by `custom_id` (= `task_id`), and
   write each result into its corresponding slot in `.harness/evals/sprint-{NN}-r{R}.md`
   (or `-t{T}.md` for multi-trial). **The per-criterion file shape is byte-for-byte identical
   to the synchronous path** — downstream consumers (the regression gate at Step 0.5, the
   saturation detector in `harness-summary`, the Generator on retry) cannot tell whether
   batch or synchronous produced the file. This invariant is critical: changing the file shape
   would cascade into every deliverable that keys off the eval file format.

**Backward compatibility.** With `config.batch.enabled == false` (the default), Step 3d is a
no-op — the synchronous Step 3b path runs as in Phase 1. A project whose `.harness/config.json`
lacks the `batch` object hits the default-false branch and sees zero behavior change.

### 3e. Transcript Capture (optional)

This subsection runs after the Evaluator's markdown eval lands. It extracts a structured JSON
trailer from the evaluator's eval file and writes a sibling transcript file to
`.harness/transcripts/`. The structured channel is the audit-grade record that
`harness-summary` links from FAIL criteria and grader-disagreement entries.

**Trigger.** Read `config.transcripts.capture` from `.harness/config.json` (default `true`
when the `transcripts` object is present; absent means the legacy/Phase-1 default applies).
If `config.transcripts.capture` is explicitly `false`, skip this step entirely.

**Trailer extraction protocol.** Two independent implementers must produce equivalent
transcript files from the same evaluator markdown eval, so the protocol is precise:

1. **Locate the trailer.** Read the markdown eval file just produced by the Evaluator
   (`.harness/evals/sprint-{NN}-r{R}-t{T}.md` for multi-trial, or
   `.harness/evals/sprint-{NN}-r{R}.md` for single-trial). Find the last
   `## Transcript Trailer` heading in the file. The body of that section is a fenced
   ` ```json ` code block containing the structured JSON payload the Evaluator produced.
2. **Parse the trailer.** Extract the JSON between the fences and parse it. If the
   `## Transcript Trailer` section is missing, the fence is malformed, the JSON does not
   parse, or required top-level fields are absent, **skip the rest of this step** — do NOT
   fail the eval and do NOT fabricate a transcript. The eval verdict is unaffected;
   transcripts are an audit artifact, not a grading input. This failure-tolerant posture
   matches the regression gate's stance from Sprint 7.
3. **Write the transcript.** Write the parsed JSON verbatim to
   `.harness/transcripts/sprint-{NN}-r{R}-t{T}.json` (multi-trial) or
   `.harness/transcripts/sprint-{NN}-r{R}.json` (single-trial mode). The file naming mirrors
   the markdown eval naming so transcript-to-eval pairing is unambiguous.

**Backward compatibility.** A project whose `.harness/config.json` lacks the `transcripts`
object and whose `agents/evaluator.md` predates Sprint 9 experiences no functional behavior
change: the legacy evaluator does not emit a `## Transcript Trailer` section, so step 2 above
falls into the failure-tolerant branch and no transcript file is written. When
`config.transcripts.capture` is explicitly `false`, this entire step is skipped.

## Step 4: Retry Loop

<!-- Context scope at this step: evals/sprint-{NN}.md (latest eval), contracts/sprint-{NN}.md (contract) -->
<!-- Deferred: spec.md, other sprint files — not needed for a targeted retry -->

If the verdict is FAIL and retry count < `max_retries` from config:

1. Increment retry count
2. Go back to Step 2, but this time tell the Generator:
   - Read the eval results at `.harness/evals/sprint-{NN}.md` (defer this read until retry is confirmed)
   - Focus on fixing the specific FAIL criteria
   - The Evaluator cited exact file paths and line numbers — address those
   - Commit fixes with: `fix(sprint-{NN}): <what was fixed>`
3. Then go to Step 3 for re-evaluation
4. The Evaluator writes fresh results to `.harness/evals/sprint-{NN}-r{R}.md` (next round number), then the workflow copies it to `.harness/evals/sprint-{NN}.md`

If max retries exhausted with failures remaining, note this in progress.md and inform the user.

## Step 5: Sprint Completion

<!-- Context scope at this step: sprint-state.json (to update), progress.md (to update) -->
<!-- Deferred: spec.md, rubric, source files — not needed at completion step -->

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

4. **Post-Sprint Governance Auto-Trigger Gate (b2).** When `config.governance.enabled` is
   `true` AND `config.governance.review_frequency == "every-sprint"`, invoke
   `/henkaten-council:council-autorun` for the just-completed sprint as the final action of
   this step — **after** updating `progress.md`, `sprint-state.json`, and the git checkpoint
   (steps 1–3 above), but **before** reporting to the user (step 5 below).

   If `council-autorun` returns an andon halt or autonomy-floor breach, surface that result
   to the user **before** offering the next sprint. Do not proceed to offer the next sprint
   until the user acknowledges the andon-stop outcome.

   **Backward compatibility:** When `config.governance.enabled` is `false` or the `governance`
   key is absent from `config.json`, this gate does not fire. A project without a governance
   config behaves identically to the pre-gate sprint-workflow.

5. Report to the user:
   - Sprint outcome (PASS/PARTIAL/FAIL)
   - How many rounds it took
   - Key findings from the eval
   - Suggest `/harness-sprint` for the next sprint or `/harness-summary` for a report

## Lazy Loading: Deferrable Context Reads

Context retrieval in this workflow is pull-based and just-in-time. Read each file at the step where its contents first influence a decision — do not front-load all harness files at session start.

The following reads can be deferred until the step that actually needs them:

| Read | Default eager timing | Deferral condition | Deferred until |
|------|---------------------|-------------------|----------------|
| `.harness/spec.md` | Step 0 | Generator already knows sprint title/scope from `sprints.json` | Step 1a (contract proposal only) |
| Prior contracts in `.harness/contracts/` | Step 1a | Only needed if calibrating against prior contract style | Step 1a, only what is necessary |
| Prior eval results in `.harness/evals/` | Step 1a | Only needed for retry rounds or if sprint builds on prior outcomes | Step 4 (retry), or Step 1a only if needed |
| Rubric file from eval-rubric skill | Step 3a | Not needed until the Evaluator begins scoring | Step 3b |
| `.harness/progress.md` | Step 0 | Only needed if `sprint-state.json` is absent or ambiguous | Fallback read only |
| `.harness/config.json` | Step 0 | Only needed if harness settings affect the step's logic | Step 0, but can skip if state is already clear |

**Cost of eager loading:** Reading all harness files at session start consumes thousands of tokens of context window before the agent has done any useful work. In long sessions spanning many sprints, this front-loading accelerates context compaction and causes earlier information loss — reducing the agent's ability to track decisions made earlier in the session.

**Lazy loading rule:** Read a file at the step where its contents first influence a decision. If a file is needed in two steps, read it at the first step only and rely on context for the second step. If context has compacted, re-read only the minimal set required to resume.

**Per-step context scope summary:**
- Step 0: `sprint-state.json`, `sprints.json` (minimal — just enough to pick the sprint)
- Step 1: `spec.md`, `sprints.json`, targeted prior contracts/evals (only necessary for calibration)
- Step 2: `contracts/sprint-{NN}.md` (finalized contract only; source files pulled on-demand)
- Step 3: `contracts/sprint-{NN}.md`, `config.json`, rubric (deferred until 3b scoring begins)
- Step 4: `evals/sprint-{NN}.md` (latest eval), `contracts/sprint-{NN}.md` (deferred until retry confirmed)
- Step 5: `sprint-state.json`, `progress.md` (update only; no new reads needed)

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

The Evaluator subagent runs forked (`context: fork` in `agents/evaluator.md`) and writes its
eval markdown directly via the `Write` tool. This is the **default and preferred** path —
forked context preserves Generator/Evaluator separation, which is one of the harness's core
invariants.

**When the fallback applies.** If the Evaluator subagent fails to write the eval file due to
a **tool limitation** (e.g., the agent's `tools:` frontmatter does not include `Write`, the
agent's environment cannot execute a long heredoc reliably, or the subagent dispatch itself
fails for infrastructure reasons), the main thread may transcribe the eval markdown into
`.harness/evals/sprint-{NN}-r{R}.md` so the sprint can complete. This is an **escape valve,
not a feature** — every fallback invocation is a regression in Generator/Evaluator separation
that must be flagged.

**How to flag a fallback eval.** When the main thread writes the eval, it must add a
`## Process Note` section near the top of the eval file explicitly disclosing:
- That the eval was authored by the main-thread orchestrator, not a forked Evaluator subagent
- The reason for the fallback (cite the specific tool limitation or dispatch failure)
- Which deterministic verification commands were run verbatim from the contract (so the audit
  chain is preserved even though the authorship is degraded)

**Rubric impact.** A sprint whose eval was written via fallback typically scores 3/5 on the
`generator_evaluator_separation` rubric dimension instead of 5/5, regardless of the underlying
technical correctness of the verifications.

### thinking.profile

`config.thinking.profile` is a per-installation knob that selects how the harness translates
the agent-frontmatter `thinking: { type: adaptive, effort: ... }` declarations into the
runtime API parameters Anthropic's API expects. The reserved values are intentionally small.

**Reserved values and their runtime translations:**

- `"default"` → standard adaptive thinking. Each agent's frontmatter `effort: medium|high|max`
  maps to a budget consistent with the model's adaptive defaults. No override is applied at
  the orchestrator layer. This is the value the harness ships with.
- `"fast"` → no extended thinking. The orchestrator strips `thinking` from outgoing API
  requests regardless of the agent's frontmatter declaration. Trades accuracy for latency and
  cost; appropriate for CI smoke checks or operator iterations on contract drafting.
- `"thorough"` → high-budget extended thinking. The orchestrator forces a high `budget_tokens`
  setting on every thinking-enabled message, overriding the per-agent `effort` to its highest
  tier. Trades latency and cost for the highest reasoning quality available; appropriate for
  adversarial evaluation rounds or complex contract review.
