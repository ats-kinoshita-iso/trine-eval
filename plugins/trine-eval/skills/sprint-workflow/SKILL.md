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

## Step 1: Contract Negotiation

<!-- Context scope at this step: spec.md, sprints.json, prior contracts/, prior evals/ -->
<!-- Deferred: config.json (resolved in Step 0), progress.md (resolved in Step 0) -->
<!-- Sub-agents receive condensed context summaries — not a file list to discover on their own -->

If `components_enabled.contract_negotiation` is true in config:

### 1a. Generator Proposes Contract

Spawn the Generator subagent with a condensed context summary:
- **Current sprint:** Sprint {NN} — "{sprint title from sprints.json}"
- **Prior sprint outcomes:** Summarize pass/fail status from sprint-state.json (e.g., "Sprint 1 PASS, Sprint 2 PASS")
- **Key constraint reminder:** Weights must sum to 100%; criteria must be deterministic or llm-judge tagged
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

After the Evaluator finishes, read `.harness/evals/sprint-{NN}-r{R}.md` and check the verdict. Copy the file to `.harness/evals/sprint-{NN}.md` so the Generator always has a stable path for the latest eval.

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

3. Report to the user:
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
