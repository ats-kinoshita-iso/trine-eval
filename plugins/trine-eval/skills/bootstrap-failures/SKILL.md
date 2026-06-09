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
      "grader_type": "behavioral | structural | llm-judge"
    }
  ]
}
```

### Conversion guidelines:

1. **Write a clear problem statement** — describe the failure as observed, not the suspected cause
2. **Define unambiguous success criteria** — use the same standard as sprint contract criteria (action, expected result, verification method)
3. **Include a reference solution** if the fix is known — this calibrates the grader
4. **Tag with rubric dimension** — map each failure to the quality dimension it tests (functionality, robustness, etc.)
5. **Assign grader type** — `behavioral` if the criterion is verified by invoking the artifact and observing the result (preferred); `structural` if it is verified by inspecting an artifact at rest (grep, jq, schema check); `llm-judge` if it requires reading comprehension or subjective assessment. Default to behavioral whenever the artifact can be executed.
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

## Templates by Rubric

The `templates/by-rubric/` subdirectory contains pre-seeded failure catalogs derived from
rubric playbook traps. Each file is named after the rubric it targets (e.g.,
`templates/by-rubric/harness-build.json`) and contains a `failures` array following the
same schema as `.harness/bootstrap/failure-catalog.json`.

### Purpose

Per-rubric templates provide a curated starting point for projects graded by a specific rubric.
Rather than starting from zero failure cases, a harness-build project can begin with 12–15
trap-derived entries that cover all rubric dimensions — including the three UNCONDITIONAL gate
dimensions (Control Plane & Agentic Loop, Tool Registry & Sandboxing, Governance & Human Oversight)
that carry the highest risk weight and cause automatic sprint FAIL if absent.

### Kickoff Merge Procedure

When `/harness-kickoff` runs for a project and a matching per-rubric template exists, the
merge is triggered during Step 2b (failure catalog seeding). The procedure is:

1. **Identify the rubric.** Read the project type from the kickoff context (e.g., `harness-build`).
2. **Locate the template.** Look up `templates/by-rubric/<rubric-name>.json` within the
   bootstrap-failures skill directory. For a harness-build project, this is
   `templates/by-rubric/harness-build.json`.
3. **Read the template.** Load the `failures` array from the template file.
4. **Check for an existing project catalog.** Read `.harness/bootstrap/failure-catalog.json`
   if it exists. If no project catalog exists yet, proceed to step 6.
5. **Collect existing IDs.** Build a set of all `id` values already present in the project catalog.
6. **Additive merge by id.** For each entry in the template's `failures` array: if the entry's
   `id` is not already in the existing-ID set, append the entry to the project catalog. Entries
   whose `id` is already present are skipped and not overwritten.
7. **Write the merged catalog.** Write the updated `failures` array back to
   `.harness/bootstrap/failure-catalog.json`. If no project catalog existed, this write creates
   the file with the template entries as the initial catalog.

**Additive-merge-by-id rule:** per-rubric template entries do not overwrite user-authored entries.
Any entry with an `id` already present in the project catalog is skipped. This ensures the merge
is idempotent — running kickoff a second time on the same project does not duplicate entries or
overwrite changes the practitioner made to the catalog after the initial seeding.

### Available Templates

- `by-rubric/harness-build.json` — 12–15 playbook-trap-derived entries for agent runtime harnesses,
  covering all 7 harness-build rubric dimensions with at least 2 entries each for the three gate
  dimensions.

## Running the Bootstrap

To bootstrap a project's eval suite:

1. Create `.harness/bootstrap/` directory
2. Gather failure cases from the sources above
3. Write each as an entry in `failure-catalog.json` following the schema
4. Run `/harness-kickoff` — the planner will incorporate the catalog
5. During sprints, the generator references catalog entries when proposing criteria

The bootstrap is a one-time seeding operation, but the catalog should be updated as new production failures are discovered. It is a living document, not a snapshot.
