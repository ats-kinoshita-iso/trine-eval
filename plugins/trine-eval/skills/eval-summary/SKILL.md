---
name: eval-summary
description: Cross-sprint analysis showing pass rates, consistency metrics, trends, and failure patterns
allowed-tools: Read, Glob, Grep
---

# Eval Summary

Generate a cross-sprint evaluation summary by analyzing all completed sprint evaluations.

## How to Generate

1. Read `.harness/config.json` for project context
2. Read `.harness/progress.md` for sprint completion status
3. Read all files in `.harness/evals/` to collect evaluation results. Files named `sprint-NN-rR.md` contain per-round data; files named `sprint-NN.md` contain the final round's results only.
4. Read all files in `.harness/contracts/` to understand what was promised vs delivered

## What to Compute

### Pass Rate
- Overall: (total passed criteria) / (total criteria) across all sprints
- Per-sprint: pass rate for each individual sprint
- Weighted pass rate: sum of passed criteria weights / 100% per sprint (if contracts use weighted criteria)

### Consistency Metrics

**pass@k** — The probability of at least one success in k attempts:
```
pass@k = 1 - (1 - p)^k
```
where p is the per-trial pass rate (passed criteria / total criteria for a single evaluation round) and k is the number of evaluation rounds for that sprint.

Use pass@k when one success is sufficient — e.g., a code generation tool where the user picks the best output from multiple runs. High pass@k with low pass^k indicates the system can succeed but does so inconsistently.

**pass^k** — The probability that all k trials succeed:
```
pass^k = p^k
```

Use pass^k when consistency is essential — e.g., a customer-facing agent where every interaction must succeed. At a 75% per-trial pass rate, pass^3 drops to approximately 42%.

**How to compute from eval data:**
1. For each sprint, collect the per-round pass rates from all `sprint-NN-rR.md` files
2. Compute p as the average per-round pass rate across rounds
3. k = number of evaluation rounds for that sprint
4. Report both pass@k and pass^k per sprint and overall

These metrics reveal whether the system is reliable (high pass^k) or merely capable (high pass@k but low pass^k). A large gap between pass@k and pass^k signals non-determinism that needs investigation.

### Trend Analysis
- Is the pass rate improving or degrading across sprints?
- Are retry counts increasing or decreasing?
- Is the first-round pass rate improving? (This indicates the Generator is learning from prior eval feedback)
- Is pass^k improving? (This indicates the system is becoming more consistent, not just more capable)

### Failure Patterns
- Which rubric dimensions fail most often?
- Are the same types of issues recurring? (e.g., always failing on error handling, always failing on responsive design)
- Which criteria required the most retries?

### Retry Efficiency
- Average rounds per sprint (count `sprint-NN-r*.md` files per sprint)
- Cost trajectory: are later rounds cheaper than earlier ones? Compare criteria fail counts across rounds within each sprint. (If not improving, feedback specificity may need improvement)
- First-round vs final-round delta: how many criteria were fixed by retries?

### Saturation & Regression Graduation

A criterion is **saturated** when it passes on the first evaluation round across 3 or more consecutive sprints. Saturated criteria track regressions but provide no improvement signal.

**Identifying saturated criteria:**
1. For each criterion type that appears across sprints, check whether it passed in round 1 of every sprint
2. If it has passed on first attempt for 3+ consecutive sprints, flag it as saturated

**Action for saturated criteria:** Flag them for graduation to a regression test suite. The sprint contract should replace graduated criteria with harder variants that push the agent's capabilities. Include specific recommendations for harder replacements.

**Distinguishing easy from well-implemented:** A criterion that is inherently trivial (e.g., "file exists") saturates because it is easy — it should be graduated without replacement. A criterion that was previously hard but now consistently passes saturates because the implementation improved — replace it with a harder variant targeting the same capability. Check the criterion's history: if it ever failed in prior sprints, it represents genuine capability growth. If it has never failed across any sprint, it may be too easy.

### Recommendations
- Based on patterns, what should the next sprint focus on?
- Are there systemic issues that rubric changes could address?
- Should any harness components be disabled based on performance? (per the `components_enabled` config)
- Which criteria should be graduated from capability eval to regression suite?
- Where is the largest gap between pass@k and pass^k? (indicates where to invest in consistency)

## Output Format

Write the summary to `.harness/summary.md`:

```markdown
# Eval Summary

## Overview
- Sprints completed: X
- Overall pass rate: Y%
- Overall weighted pass rate: W%
- Average rounds per sprint: Z

## Consistency Metrics
| Sprint | p (avg) | k (rounds) | pass@k | pass^k |
|--------|---------|------------|--------|--------|
| 1      | 0.85    | 2          | 97.8%  | 72.3%  |

- Overall pass@k: {value}
- Overall pass^k: {value}
- Consistency gap (pass@k - pass^k): {value} — {interpretation}

## Per-Sprint Results
| Sprint | Title | Verdict | Rounds | Pass Rate | Weighted | pass^k |
|--------|-------|---------|--------|-----------|----------|--------|
| 1      | ...   | PASS    | 2      | 85%       | 87%      | 72%    |

## Trend Analysis
{Description of trends including consistency trends}

## Common Failure Patterns
{Ranked list of recurring issues}

## Saturation & Regression Graduation
| Criterion Type | Consecutive First-Round Passes | Status | Recommendation |
|---------------|-------------------------------|--------|----------------|
| File exists   | 5                             | Saturated (easy) | Graduate without replacement |
| Error handling| 3                             | Saturated (improved) | Replace with concurrency edge cases |

## Recommendations
{Actionable suggestions for next sprints, including consistency improvements and graduation actions}

## Tool & Skill Description Improvements
{ACI self-optimization recommendations from eval transcript analysis — see below}
```

Also print the summary to the user for immediate review.

## ACI Self-Optimization from Eval Transcripts

After generating the summary, review eval transcripts to identify improvements to tool and skill descriptions. This implements the playbook's guidance that "tool design is an eval target itself" and that agents optimizing tool descriptions can produce improvements "beyond expert human-written implementations."

### Extract Feedback from Eval Transcripts

Read through eval reports (`.harness/evals/sprint-NN-rR.md`) looking for:

1. **Tool calls that failed or produced unexpected results** — the tool description may have been ambiguous or missing critical context
2. **Criteria where the grader type was wrong** — a criterion tagged `deterministic` that required LLM judgment (or vice versa) suggests the verification method in the contract was misspecified
3. **Evaluator misinterpretations** — where the evaluator tested something different from what the criterion intended, often because the skill/agent description was unclear
4. **Recurring failures across sprints** — the same type of failure appearing in multiple sprints may indicate a systemic description gap rather than an implementation issue

### Improvement Process

For each identified issue:

1. **Locate the relevant tool/skill description** — the agent markdown file, skill SKILL.md, or rubric that was involved
2. **Propose a description change** — make the description more specific, add context that was missing, or clarify ambiguous language. Follow ACI best practices: 3-4 sentences per tool description, meaningful names, explicit context about specialized terminology
3. **Apply the change** to the markdown file
4. **Document the change** in the summary under "Tool & Skill Description Improvements" with the rationale

### Validation Against Held-Out Cases

To ensure improvements actually help rather than introducing new problems:

1. **Identify held-out eval cases** — select 2-3 prior sprint evals that were NOT used to derive the description changes
2. **Re-evaluate mentally** — would the updated descriptions have changed any grades in those held-out cases? Would they have prevented any misinterpretations?
3. **Check for regressions** — could the new wording cause false positives or false negatives on cases that previously graded correctly?

Only apply changes that improve held-out cases without causing regressions.
