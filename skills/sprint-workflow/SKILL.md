---
name: sprint-workflow
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

## Step 1: Contract Negotiation

If `components_enabled.contract_negotiation` is true in config:

### 1a. Generator Proposes Contract

Spawn the Generator subagent:
- Tell it which sprint number and title it's working on
- Tell it to read `.harness/spec.md` and `.harness/sprints.json`
- Tell it to read any prior contracts in `.harness/contracts/` and eval results in `.harness/evals/`
- If `.harness/bootstrap/failure-catalog.json` exists, tell it to read the catalog and incorporate relevant failure cases as sprint criteria (the `success_criteria` field maps directly to contract criteria; include `reference_solution` entries in the contract's Reference Solutions section)
- Tell it to write a draft contract to `.harness/contracts/sprint-{NN}.md` using the sprint-contract template
- Tell it to ONLY write the contract — do NOT implement anything yet

### 1b. Evaluator Reviews Contract

Spawn the Evaluator subagent:
- Tell it to read the draft contract at `.harness/contracts/sprint-{NN}.md`
- Tell it to review for: testability, completeness, and specificity
- Tell it to append its feedback to the contract file under a `## Evaluator Review` section
- If it approves, it writes `**Status: APPROVED**`
- If it wants changes, it writes `**Status: NEEDS REVISION**` with specific feedback

### 1c. Negotiation Loop

Read the contract file. If status is NEEDS REVISION and negotiation round < `contract_negotiation_rounds`:
- Spawn Generator again to revise the contract based on feedback
- Spawn Evaluator again to review the revision
- Repeat until APPROVED or max rounds reached

If max rounds reached without approval, proceed with the latest version and note this in progress.md.

If `contract_negotiation` is disabled, the Generator writes the contract and it's automatically approved.

## Step 2: Implementation

Spawn the Generator subagent:
- Tell it the sprint contract is finalized at `.harness/contracts/sprint-{NN}.md`
- Tell it to implement everything specified in the contract
- Tell it to commit working code with conventional commit format: `feat(sprint-{NN}): <description>`
- Tell it to self-review before declaring done, but NOT to grade itself
- Tell it to read prior eval results if this is a retry round, and fix the specific issues cited

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
- Tell it to write results to `.harness/evals/sprint-{NN}-r{R}.md` where {R} is the current round number (1 for first evaluation, 2 for first retry eval, etc.)
- Tell it which round number this is
- Tell it to grade as PASS or FAIL with specific evidence for each criterion

After the Evaluator finishes, read `.harness/evals/sprint-{NN}-r{R}.md` and check the verdict. Copy the file to `.harness/evals/sprint-{NN}.md` so the Generator always has a stable path for the latest eval.

## Step 4: Retry Loop

If the verdict is FAIL and retry count < `max_retries` from config:

1. Increment retry count
2. Go back to Step 2, but this time tell the Generator:
   - Read the eval results at `.harness/evals/sprint-{NN}.md`
   - Focus on fixing the specific FAIL criteria
   - The Evaluator cited exact file paths and line numbers — address those
   - Commit fixes with: `fix(sprint-{NN}): <what was fixed>`
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
