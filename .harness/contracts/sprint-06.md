# Sprint 06 Contract: Statistical Foundation (Trials, Sandbox, Tasks.json)

## What I Will Build

Close Gap A (gaps 1, 2, 3) from the playbook alignment doc: make pass@k and pass^k statistically meaningful by separating the retry loop (bug-fix) from the trial loop (measurement), adding an optional sandbox layer so each trial runs from clean state, and emitting a machine-readable `sprint-NN.tasks.json` alongside the markdown contract so downstream sprints (regression gate, batch API, transcripts) have a formal task taxonomy to build on. All new `.harness/config.json` fields default to current behavior — `trials: 1`, `sandbox.mode: "none"`, `taxonomy.emit_tasks_json: true` — so existing projects execute unchanged.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **config.json schema extended**: `.harness/config.json` contains keys `trials` (integer, default 1), `sandbox` (object with `mode` enum `"none" | "tmpdir" | "docker"`, default `"none"`), and `taxonomy.emit_tasks_json` (boolean, default `true`). Verify via `jq '.trials, .sandbox.mode, .taxonomy.emit_tasks_json' .harness/config.json` returning non-null values. [weight: 8%]

2. **Trial loop documented separately from retry loop**: `skills/sprint-workflow/SKILL.md` contains a Step 3c (or equivalently labeled new section) distinguishing **trial** (measurement, clean state per trial, `-tT` suffix) from **retry** (bug-fix, next round number, `-rR` suffix). Verify via `grep -n "trial" skills/sprint-workflow/SKILL.md` showing the distinction and trial-file naming `sprint-NN-rR-tT.md`. [weight: 12%]

3. **Trial file naming convention referenced in workflow**: `skills/sprint-workflow/SKILL.md` references the `sprint-{NN}-r{R}-t{T}.md` path for trial eval files in addition to (not replacing) the `sprint-{NN}-r{R}.md` single-trial path used when `trials == 1`. Verify via grep for the `-t{T}` pattern. [weight: 7%]

4. **Sandbox setup section in evaluator.md**: `agents/evaluator.md` contains a `## Pre-eval Sandbox Setup` (or equivalently titled) section describing behavior for each `sandbox.mode`: `"none"` (current behavior), `"tmpdir"` (copy working tree to tmpdir and cd), `"docker"` (delegate to `scripts/sandbox.sh`). Verify by grepping evaluator.md for `sandbox.mode`, `tmpdir`, and `docker`. [weight: 10%]

5. **sandbox.sh wrapper script exists**: A `scripts/sandbox.sh` file exists, is a plain shell script (`#!/usr/bin/env bash` or `#!/bin/bash`), and contains a `docker run --rm` invocation with a volume mount. Verify via `test -f scripts/sandbox.sh && head -1 scripts/sandbox.sh | grep -E '#!.*bash' && grep -E 'docker run.*--rm.*-v' scripts/sandbox.sh`. [weight: 8%]

6. **eval-summary computes pass@k / pass^k from trial files**: `skills/eval-summary/SKILL.md` states that pass@k and pass^k are computed from trial files (`-tT`), not round files (`-rR`), and marks the prior round-based metric as deprecated. First-round-pass is kept as a separate metric. Verify by grepping for `trial` in the pass@k / pass^k section and for a "deprecated" or equivalent marker on retry-derived metrics. [weight: 10%]

7. **sprint-contract SKILL emits tasks.json**: `skills/sprint-contract/SKILL.md` documents that after contract approval a sibling `.harness/contracts/sprint-{NN}.tasks.json` is emitted with one entry per criterion, fields: `task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`. Verify via grep for these exact field names. [weight: 10%]

8. **sprint-contract template has tasks.json handoff note**: `skills/sprint-contract/template.md` references the sibling `tasks.json` emission as part of the contract protocol (so the Generator and Evaluator both know it is produced). Verify via grep for `tasks.json` in the template. [weight: 5%]

9. **harness-conventions documents trial vs retry and tasks.json schema**: `rules/harness-conventions.md` contains a section (1) distinguishing trial (clean-state, measurement) from retry (bug-fix, new round) and (2) documenting the `tasks.json` schema fields. Verify via grep for both `trial` / `retry` and the `task_id`, `grader_type`, `is_gate` fields. [weight: 8%]

### LLM-as-judge (requires reading comprehension)

10. **Backward compatibility is explicit**: The workflow SKILL documents that `trials == 1` reproduces current behavior — single eval file named `sprint-NN-rR.md`, no sandbox setup, no trial-suffix — and the sandbox section in evaluator.md documents that `sandbox.mode == "none"` reproduces current behavior. An evaluator reading the updated files should conclude that an existing project without any of the new config fields will run identically to Phase 1. [weight: 12%]

11. **Trial isolation rationale is clear**: A reader of the updated `agents/evaluator.md` sandbox section should be able to explain *why* trial isolation matters for pass@k/pass^k validity (without cross-trial leakage, consistency metrics are artificially inflated). The section should reference the gap-analysis insight directly or through paraphrase, not just describe the mechanics. [weight: 5%]

12. **tasks.json is positioned as the downstream source of truth**: `skills/sprint-contract/SKILL.md` or `rules/harness-conventions.md` makes clear that `tasks.json` is the machine-readable source of record that later sprints (regression gate in Sprint 7, batch API in Sprint 8, transcripts in Sprint 9) will consume — not just a passive dump. [weight: 5%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **No silent behavior change for existing configs**: Running the updated harness with the current `.harness/config.json` (no `trials`, no `sandbox`, no `taxonomy` fields) must not produce trial-suffixed files, must not invoke any sandbox setup, and must not refuse to start due to missing fields. Verify by reading the updated workflow and evaluator files — they must explicitly guard every new behavior on a config lookup with a default that matches Phase 1.

2. **No duplicate eval-file writes**: When `trials == 1`, the workflow must write exactly one eval file per round (`sprint-NN-rR.md`), not two (not both `sprint-NN-rR.md` and `sprint-NN-rR-t1.md`). Verify by reading the workflow SKILL's file-path logic.

3. **No modification of prior sprints**: `.harness/evals/sprint-01*.md` through `.harness/evals/sprint-05*.md` and `.harness/contracts/sprint-0{1..5}.md` must be unchanged (append-only rule from `rules/harness-conventions.md`). Verify via `git diff HEAD -- .harness/evals/sprint-0[1-5]* .harness/contracts/sprint-0[1-5]*` showing no changes.

## Reference Solutions

**Criterion 7 (tasks.json emission):** Example of a well-formed `sprint-NN.tasks.json` entry:
```json
{
  "tasks": [
    {
      "task_id": "s06-c1",
      "criterion": "config.json schema extended with trials, sandbox, taxonomy.emit_tasks_json",
      "grader_type": "deterministic",
      "weight": 8,
      "is_gate": false,
      "verification_command": "jq -e '.trials and .sandbox.mode and .taxonomy.emit_tasks_json' .harness/config.json",
      "rubric_dimension": "methodology_completeness"
    },
    {
      "task_id": "s06-sn1",
      "criterion": "No silent behavior change for existing configs",
      "grader_type": "llm-judge",
      "weight": 0,
      "is_gate": true,
      "verification_command": null,
      "rubric_dimension": "generator_evaluator_separation"
    }
  ]
}
```

The `tasks.json` is emitted as a sibling of `sprint-NN.md` in `.harness/contracts/`. Gate (Should-NOT) criteria have `weight: 0` and `is_gate: true`. Deterministic criteria provide a runnable `verification_command`; LLM-judge criteria set it to `null`.

**Criterion 10 (backward compatibility):** Example of the config lookup guard in workflow SKILL:
```
Read trials from config; default 1 if absent.
If trials == 1: write eval to sprint-NN-rR.md (current behavior).
If trials >  1: for T in 1..trials, write eval to sprint-NN-rR-tT.md.
```

## Out of Scope

- Actually executing multiple trials or docker sandboxes during this sprint's own evaluation — this sprint only ships the plumbing and documentation. End-to-end verification of the trial loop will happen on a synthetic sprint (per the gap-closure-plan Verification section item 1).
- Writing the regression gate itself (that is Sprint 7).
- Wiring adaptive thinking config into agents (Sprint 8).
- Transcript JSON trailer emission (Sprint 9).
- Updating existing sprint-01 through sprint-05 contracts to emit retroactive `tasks.json` files — `tasks.json` emission applies going forward from Sprint 6.

## Technical Notes

- **Trial vs retry distinction is the core conceptual unlock** of this sprint. Today the harness collapses them: a retry round is both a bug-fix *and* the measurement for pass^k, which double-counts the retry as evidence of inconsistency when it is actually evidence of a fixed bug. After this sprint, pass^k measures capability consistency at a fixed code state (trials of the same commit) while retry counts remain an orthogonal debug-effort signal.
- **Sandbox modes are layered**: `"none"` keeps current behavior; `"tmpdir"` is a cheap POSIX-only copy-and-cd (no container runtime needed); `"docker"` delegates to `scripts/sandbox.sh` so users can extend the wrapper without editing the evaluator agent.
- **`tasks.json` is the forward handoff** to Sprints 7 (regression), 8 (batch API — a batch submission groups by `verification_command`), 9 (transcripts key off `task_id`), and 10 (adversarial hygiene flags a criterion by `task_id`). The fields were chosen to satisfy all four consumers.
- File naming extends rather than replaces: `sprint-NN-rR.md` remains valid when `trials == 1`; trials add a `-tT` suffix. This keeps the existing `sprint-NN.md` latest-copy contract stable for the Generator retry loop.

## Evaluator Review

**Status: APPROVED**

### Feedback

The contract is testable, specific, and weighted proportionally. Deterministic criteria all name grep/jq commands or exact file paths; LLM-judge criteria carry clear PASS definitions ("a reader should conclude X", "a reader should be able to explain Y"). Weight sum verified: 8+12+7+10+8+10+10+5+8+12+5+5 = 100%.

Two notes the Generator should act on during implementation (not blockers):

- **Criterion 5 verification is strict about `docker run` text**: the sandbox.sh wrapper should include `docker run --rm -v` literally so the grep pattern matches. If the implementation uses environment-variable indirection (`$DOCKER_CMD`), rewrite the script to inline `docker run --rm -v` at least once, or soften the check.
- **Criterion 7's field list is a fixed schema**: the tasks.json entries must use exactly those field names (`task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`) because Sprints 7–10 consume them. Do not rename.

### Missing Criteria

None. The three gap-areas (trials, sandbox, tasks.json) each have deterministic coverage plus LLM-judge coverage of the rationale.

### Approved Criteria

1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12 — all approved. Should-NOT gates SN1, SN2, SN3 all testable and defensible.

### Contract Quality Notes

- Weight concentration is healthy: largest criterion is 12%, no single criterion dominates.
- Reference solution for Criterion 7 is strong — it pins the schema so a round 2 evaluator would have zero ambiguity.
- Out-of-scope section correctly defers end-to-end trial execution to a synthetic verification sprint rather than trying to dogfood trial-mode inside its own evaluation.
