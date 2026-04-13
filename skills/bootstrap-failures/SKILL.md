---
name: bootstrap-failures
description: Import real failure cases from bug reports, incidents, and manual tests to seed the eval suite
allowed-tools: Read, Write, Glob, Grep
---

# Bootstrap from Real Failures

Seed the eval suite with real failure cases instead of starting from scratch. This implements Steps 0 and 1 of Anthropic's eval methodology: "Start early with 20-50 real failure cases" and "Start with what you already test manually."

## Why Bootstrap?

Synthetic test cases miss the failure modes that matter most. Real failures — drawn from production incidents, bug reports, and manual QA — represent the actual distribution of problems your system encounters. Starting with these gives the eval suite immediate relevance and catches the issues users care about.

## Sources of Real Failures

Gather failure cases from these sources, prioritized by user impact:

1. **Bug reports** from issue trackers (GitHub Issues, Linear, Jira) — each closed bug becomes a test case, with the fix serving as the reference solution
2. **Manual test notes** — QA team's manual checklists and exploratory test results, converted to automated criteria with specific pass/fail thresholds
3. **Production incidents** — post-mortem documents provide high-impact failure scenarios with real-world context and severity data
4. **Support tickets** — user-reported issues reveal edge cases that developers didn't anticipate, often with exact reproduction steps
5. **Code review comments** — recurring review feedback indicates patterns the eval suite should check for

## Conversion Process

For each failure case, create an eval task entry in `.harness/bootstrap/failure-catalog.json`:

```json
{
  "failures": [
    {
      "id": "F001",
      "source": "bug-report",
      "source_ref": "GH-123",
      "title": "Short description of the failure",
      "problem": "What went wrong — the observed behavior",
      "expected": "What should have happened — the correct behavior",
      "success_criteria": "Specific, unambiguous criterion for verifying the fix",
      "reference_solution": "Optional: known-working output or approach",
      "rubric_dimension": "Which rubric dimension this maps to",
      "severity": "critical | high | medium | low",
      "grader_type": "deterministic | llm-judge"
    }
  ]
}
```

### Conversion guidelines:

1. **Write a clear problem statement** — describe the failure as observed, not the suspected cause
2. **Define unambiguous success criteria** — use the same standard as sprint contract criteria (action, expected result, verification method)
3. **Include a reference solution** if the fix is known — this calibrates the grader
4. **Tag with rubric dimension** — map each failure to the quality dimension it tests (functionality, robustness, etc.)
5. **Assign grader type** — deterministic if the criterion can be verified by running a command; llm-judge if it requires reading comprehension
6. **Prioritize by severity** — critical and high-severity failures should become sprint criteria before medium and low

## Target Volume

Start with **20-50 real failure cases**. This is sufficient for early development, where each system change produces large, noticeable effects. As the system matures, grow the catalog organically from ongoing production feedback.

A **0% pass rate across many trials almost always signals a broken task, not an incapable agent** — if nothing passes, review the task definitions before concluding the system is broken.

## Integration with the Harness

The failure catalog feeds into the existing harness workflow at two points:

### 1. During Kickoff (`.harness/` initialization)

When `/harness-kickoff` runs, if `.harness/bootstrap/failure-catalog.json` exists:
- Read the catalog and group failures by rubric dimension
- Use failure patterns to inform the Planner's sprint decomposition — sprints should prioritize addressing high-severity failures
- Failures tagged as `critical` should appear as sprint criteria in the first sprint

### 2. During Contract Negotiation

When the Generator proposes sprint contracts:
- Reference the failure catalog for relevant test cases
- Convert catalog entries into contract criteria (the `success_criteria` field maps directly)
- Include the `reference_solution` from the catalog in the contract's Reference Solutions section

### Data Flow

```
Real failures (bugs, incidents, tickets)
    ↓ bootstrap skill (manual import)
.harness/bootstrap/failure-catalog.json
    ↓ kickoff reads catalog
.harness/spec.md (informed by failure patterns)
    ↓ planner decomposes sprints
.harness/sprints.json (prioritized by severity)
    ↓ generator reads catalog during contract proposal
.harness/contracts/sprint-NN.md (criteria from real failures)
    ↓ evaluator tests criteria
.harness/evals/sprint-NN-rR.md (real failure cases as eval tasks)
```

## Running the Bootstrap

To bootstrap a project's eval suite:

1. Create `.harness/bootstrap/` directory
2. Gather failure cases from the sources above
3. Write each as an entry in `failure-catalog.json` following the schema
4. Run `/harness-kickoff` — the planner will incorporate the catalog
5. During sprints, the generator references catalog entries when proposing criteria

The bootstrap is a one-time seeding operation, but the catalog should be updated as new production failures are discovered. It is a living document, not a snapshot.
