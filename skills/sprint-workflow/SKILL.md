---
name: sprint-workflow
description: Run one sprint through the contract-build-eval cycle
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, Edit
---

# Sprint Workflow

You are running one sprint through the full Planner-Generator-Evaluator cycle. This skill manages the contract negotiation, build, evaluation, and retry loop for a single sprint.

## Step 0: Determine Which Sprint to Run

1. Read `.harness/config.json` to get configuration
2. Read `.harness/sprints.json` to get the sprint list
3. Read `.harness/progress.md` to determine which sprints have completed
4. If the user specified a sprint number (e.g., `/harness-sprint 3`), use that
5. Otherwise, pick the next incomplete sprint

If all sprints are complete, tell the user and suggest `/harness-summary`.

## Step 1: Contract Negotiation

If `components_enabled.contract_negotiation` is true in config:

### 1a. Generator Proposes Contract

Spawn the Generator subagent:
- Tell it which sprint number and title it's working on
- Tell it to read `.harness/spec.md` and `.harness/sprints.json`
- Tell it to read any prior contracts in `.harness/contracts/` and eval results in `.harness/evals/`
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

Spawn the Evaluator subagent:
- Tell it to read the sprint contract from `.harness/contracts/sprint-{NN}.md`
- Tell it to read `.harness/config.json` to determine the project type and rubric
- Tell it to load and apply the appropriate rubric from the eval-rubric skill
- Tell it to test every criterion in the contract by actually running tests, hitting endpoints, checking files
- Tell it to write results to `.harness/evals/sprint-{NN}.md` in the specified format
- Tell it to grade as PASS or FAIL with specific evidence for each criterion

After the Evaluator finishes, read `.harness/evals/sprint-{NN}.md` and check the verdict.

## Step 4: Retry Loop

If the verdict is FAIL and retry count < `max_retries` from config:

1. Increment retry count
2. Go back to Step 2, but this time tell the Generator:
   - Read the eval results at `.harness/evals/sprint-{NN}.md`
   - Focus on fixing the specific FAIL criteria
   - The Evaluator cited exact file paths and line numbers — address those
   - Commit fixes with: `fix(sprint-{NN}): <what was fixed>`
3. Then go to Step 3 for re-evaluation
4. The Evaluator overwrites `.harness/evals/sprint-{NN}.md` with fresh results

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

2. Git checkpoint:
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

If `.harness/progress.md` indicates a sprint was in-progress when the session ended:
1. Check git log for the latest sprint-related commits
2. Check if a contract exists for the in-progress sprint
3. Check if eval results exist (determines whether we're in build or eval phase)
4. Resume from the appropriate step
