---
name: eval-summary
description: Cross-sprint analysis showing pass rates, trends, and failure patterns
allowed-tools: Read, Glob, Grep
---

# Eval Summary

Generate a cross-sprint evaluation summary by analyzing all completed sprint evaluations.

## How to Generate

1. Read `.harness/config.json` for project context
2. Read `.harness/progress.md` for sprint completion status
3. Read all files in `.harness/evals/` to collect evaluation results
4. Read all files in `.harness/contracts/` to understand what was promised vs delivered

## What to Compute

### Pass Rate
- Overall: (total passed criteria) / (total criteria) across all sprints
- Per-sprint: pass rate for each individual sprint

### Trend Analysis
- Is the pass rate improving or degrading across sprints?
- Are retry counts increasing or decreasing?
- Is the first-round pass rate improving? (This indicates the Generator is learning from prior eval feedback)

### Failure Patterns
- Which rubric dimensions fail most often?
- Are the same types of issues recurring? (e.g., always failing on error handling, always failing on responsive design)
- Which criteria required the most retries?

### Retry Efficiency
- Average rounds per sprint
- Cost trajectory: are later rounds cheaper than earlier ones? (If not, feedback specificity may need improvement)

### Saturated Criteria
- Criteria that pass on first attempt across all sprints — candidates for graduation to a regression test suite

### Recommendations
- Based on patterns, what should the next sprint focus on?
- Are there systemic issues that rubric changes could address?
- Should any harness components be disabled based on performance? (per the `components_enabled` config)

## Output Format

Write the summary to `.harness/summary.md`:

```markdown
# Eval Summary

## Overview
- Sprints completed: X
- Overall pass rate: Y%
- Average rounds per sprint: Z

## Per-Sprint Results
| Sprint | Title | Verdict | Rounds | Pass Rate |
|--------|-------|---------|--------|-----------|
| 1      | ...   | PASS    | 2      | 85%       |

## Trend Analysis
{Description of trends}

## Common Failure Patterns
{Ranked list of recurring issues}

## Recommendations
{Actionable suggestions for next sprints}
```

Also print the summary to the user for immediate review.
