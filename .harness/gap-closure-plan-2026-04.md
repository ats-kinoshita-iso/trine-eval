# Close the 10 Playbook Gaps in trine-eval

## Context

The gap analysis at `.harness/playbook-alignment-2026-04.md` (dated 2026-04-16) scores trine-eval against Anthropic's Jan–Mar 2026 eval playbook. It finds the harness strong on methodology (three-agent pattern, grading hierarchy, contract-first, saturation tracking) but weak on execution infrastructure: statistical trial isolation, Claude 4.6 API features, and formal evaluation suite primitives. Most critically, pass@k and pass^k are computed from retry rounds rather than clean independent trials, so the current consistency metrics are not statistically valid — an agent that is 60% consistent can report 100%.

The user has asked for full coverage of all 10 gaps, implemented by dogfooding through the harness (new Sprints 6–10, matching the gap-analysis priority roadmap A–E), with new config fields defaulting to current behavior so existing `.harness/config.json` files keep working.

## Approach

Add five new sprints to `.harness/sprints.json` and extend `.harness/spec.md` with a "Phase 2: Playbook Alignment" feature block. Then run `/harness-sprint 6` … `/harness-sprint 10` — each sprint negotiates its own contract, implements the changes to the harness files, and produces an eval result. The harness evaluates itself (`project_type: eval-harness`, `rubric: eval-harness` already configured).

Each sprint's changes edit the agents, skills, templates, hooks, and config schema in place. Backward compatibility is preserved: every new config field has a default that reproduces current behavior (`trials: 1`, `sandbox.mode: "none"`, `thinking.effort: null`, `batch: false`, `transcripts.capture: false`).

## Sprint Plan

### Sprint 6 (Gap A — Gaps 1, 2, 3): Statistical Foundation

**Goal:** Make pass@k / pass^k meaningful by adding real multi-trial execution, optional sandboxing, and a discrete task taxonomy.

**Files to modify:**
- `.harness/config.json` — add `trials` (default `1`), `sandbox` (`{mode: "none" | "tmpdir" | "docker"}`, default `"none"`), `taxonomy.emit_tasks_json` (default `true`)
- `skills/sprint-workflow/SKILL.md` — split retry loop (bug-fix) from **trial loop** (measurement). New Step 3c: if `trials > 1`, for each trial reset to a clean git state (stash working copy → checkout sprint head → run eval → restore) and write `.harness/evals/sprint-{NN}-r{R}-t{T}.md`
- `agents/evaluator.md` — add Pre-eval Sandbox Setup section: if `sandbox.mode == "tmpdir"` copy working tree to tmpdir and `cd` there; if `"docker"` delegate to `scripts/sandbox.sh` (new, thin wrapper around `docker run --rm -v`)
- `skills/eval-summary/SKILL.md` — compute pass@k / pass^k from **trial** files (`-t{T}`), not round files. Keep first-round-pass as a separate metric. Mark retry-derived metrics as deprecated in summary output
- `skills/sprint-contract/SKILL.md` + `skills/sprint-contract/template.md` — after contract approval, emit sibling `.harness/contracts/sprint-{NN}.tasks.json` with one entry per criterion (`task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`). This is the Gap 3 formal taxonomy
- `rules/harness-conventions.md` — document trial vs. retry distinction and the `tasks.json` schema

**Reuse:** existing round-file naming (`sprint-NN-rR.md`) extends to `-tT`; existing weighted-score computation in eval-summary; existing `.harness/sprint-state.json` for tracking trial progress.

**Key should-NOT gate:** If `trials == 1`, harness must behave identically to today (no behavior change for existing projects).

### Sprint 7 (Gap B — Gap 4): Capability / Regression Dual-Track

**Goal:** Turn the current *recommendation* to graduate saturated criteria into an enforced regression gate.

**Files to modify:**
- Create `.harness/regression/` directory, with `regression.json` (array of graduated task entries copied from `sprint-NN.tasks.json`) and `README.md`
- `skills/eval-summary/SKILL.md` — when a criterion passes first-round for 3+ consecutive sprints, append its entry to `regression.json` (not just recommend in prose)
- `skills/sprint-workflow/SKILL.md` — add **Step 0.5: Regression Gate**. Before new-sprint contract proposal, run every criterion in `regression.json` via its `verification_command`. If any fail, abort sprint with loud error listing the broken regression criteria. Write results to `.harness/regression/runs/run-{timestamp}.json`
- `.harness/config.json` — add `regression.enabled` (default `true` when `regression.json` exists), `regression.fail_fast` (default `true`)
- `agents/evaluator.md` — add explicit note: regression criteria use `effort: medium` (speed) vs capability criteria which use `high`/`max` (thoroughness) — lands the wiring point for Sprint 8

**Reuse:** the Sprint 6 `tasks.json` schema is the source record for graduation; graduation logic already exists in `skills/eval-summary/SKILL.md` — just swap the output from prose recommendation to writing into `regression.json`.

### Sprint 8 (Gap C — Gaps 5, 7): Claude 4.6 Adaptive Thinking + Batch API

**Goal:** Expose Claude 4.6 quality/cost levers; cut eval cost on large suites.

**Files to modify:**
- `agents/planner.md` — add frontmatter `thinking: { type: adaptive, effort: medium }`
- `agents/generator.md` — add frontmatter `thinking: { type: adaptive, effort: medium }` for implementation; document per-mode overrides
- `agents/evaluator.md` — add frontmatter `thinking: { type: adaptive, effort: high }` for capability evals; `medium` when invoked on regression criteria (Sprint 7 wiring point); `max` for contract review
- `skills/eval-summary/SKILL.md` — add `thinking: { type: adaptive, effort: max }` (analysis-heavy)
- `.harness/config.json` — add `thinking.profile` (`"default" | "fast" | "thorough"`, default `"default"`) so users can override without editing agents
- `skills/sprint-workflow/SKILL.md` — add `--batch` flag. When set, collect all eval criterion verifications into a single Batch API submission, poll, and map results back onto the per-criterion result file. Document the 50% discount and 24-hour SLA
- `.harness/config.json` — add `batch.enabled` (default `false`), `batch.min_criteria` (default `20`, so tiny sprints stay synchronous)
- `README.md` — document the new config knobs

**Reuse:** existing subagent spawn points in `sprint-workflow`; no new agent types needed — thinking config lives on existing agents.

### Sprint 9 (Gap D — Gap 6): Full Transcript Capture

**Goal:** Make evaluator calibration data-driven by recording the full message array, tool calls, and token usage per trial.

**Files to modify:**
- Create `.harness/transcripts/` directory
- `skills/sprint-workflow/SKILL.md` — after each Evaluator spawn, serialize the subagent transcript to `.harness/transcripts/sprint-{NN}-r{R}-t{T}.json` with shape:
  ```json
  { "sprint": 6, "round": 1, "trial": 1,
    "messages": [...], "tool_calls": [...],
    "token_usage": {"input": ..., "output": ..., "cache_hit": ...},
    "timing": {"ttft_ms": ..., "total_ms": ...},
    "thinking_summary": "..." }
  ```
- `agents/evaluator.md` — add instruction: at end of run, emit structured JSON trailer (machine-readable) in addition to current markdown eval file; sprint-workflow reads the trailer to assemble the transcript file
- `skills/eval-summary/SKILL.md` — when reporting a FAIL criterion or grader disagreement, link the transcript file path in the summary output so humans can audit which tools the Evaluator actually called
- `.harness/config.json` — add `transcripts.capture` (default `true`), `transcripts.retain_days` (default `30`, with a note that summary graduation needs at least 3 sprints of history)
- `rules/harness-conventions.md` — document transcript schema

**Reuse:** Evaluator already produces narrative evidence; this sprint adds the structured channel alongside, not replacing markdown evals.

### Sprint 10 (Gap E — Gaps 8, 9, 10): Completeness

**Goal:** Balanced problem sets, browser-based UI eval, basic adversarial hygiene.

**Files to modify:**
- `skills/sprint-contract/template.md` — add optional `## Edge Case Criteria` section, tracked separately from deterministic/LLM-judge criteria. Weights do not count toward the 100% total; edge-case pass rate is a distinct metric
- `skills/sprint-contract/SKILL.md` — update negotiation rules to require Evaluator to check for edge-case coverage when the rubric is `web-app`, `api-service`, or `rag-system`
- `skills/eval-summary/SKILL.md` — add "Edge Case Pass Rate" to the summary, separate from weighted score
- `agents/evaluator.md` — add Playwright MCP to available tools **conditional on** `config.project_type == "web-app"`; fall back to curl for other project types. Document in the evaluator that Visual Design dimension in `web-app` rubric requires Playwright if available, otherwise flag Visual Design findings as low-confidence and route to human review
- `.harness/config.json` — add `evaluator_tools.playwright` (default `"auto"` = enable when `project_type: web-app`)
- `agents/evaluator.md` — add **Adversarial Hygiene** section: (a) never infer PASS/FAIL from filenames or code comments; (b) before scoring, log the exact verification command executed; (c) in the structured trailer (Sprint 9), include a `verified_via_command: true/false` flag per criterion; the summary skill flags criteria where this is false as suspect

**Reuse:** Sprint 9 transcript trailer is the data channel for adversarial hygiene flags; rubric files already describe testing tools — just conditionally surface Playwright.

## Bootstrap Step (Before Running Sprint 6)

Before running any sprints, two files need additive edits so the harness knows about Sprints 6–10:

1. **`.harness/sprints.json`** — append five entries:
   ```json
   {"number": 6, "title": "Statistical foundation (trials, sandbox, tasks.json)",
    "features": ["multi-trial-execution", "environment-sandboxing", "formal-task-taxonomy"],
    "estimated_complexity": "high", "dependencies": [1,2,3,4,5]},
   {"number": 7, "title": "Capability/regression dual-track",
    "features": ["regression-suite", "regression-gate"],
    "estimated_complexity": "medium", "dependencies": [6]},
   {"number": 8, "title": "Claude 4.6 adaptive thinking and Batch API",
    "features": ["adaptive-thinking-config", "batch-api-mode"],
    "estimated_complexity": "medium", "dependencies": [6]},
   {"number": 9, "title": "Full transcript capture",
    "features": ["structured-transcripts", "grader-disagreement-links"],
    "estimated_complexity": "medium", "dependencies": [6]},
   {"number": 10, "title": "Completeness — edge cases, Playwright, integrity",
    "features": ["edge-case-criteria", "playwright-mcp-evaluator", "adversarial-hygiene"],
    "estimated_complexity": "high", "dependencies": [6,8,9]}
   ```
2. **`.harness/spec.md`** — append a **Phase 2: Playbook Alignment** section listing the 10 gap-closing features as Must-have (Gaps 1–6) and Should-have (Gaps 7–10), with Technical Constraints updated to note the new optional config fields and their defaults.

These are the only edits that happen outside the sprint loop — everything else flows through `/harness-sprint N`.

## Critical Files Reference

| Concern | File |
|---|---|
| Retry vs trial loop | `skills/sprint-workflow/SKILL.md` |
| Trial sandbox wiring | `agents/evaluator.md`, new `scripts/sandbox.sh` |
| Task taxonomy emission | `skills/sprint-contract/SKILL.md` (writes `.tasks.json`) |
| Pass@k/pass^k from trials | `skills/eval-summary/SKILL.md` |
| Regression gate | `skills/sprint-workflow/SKILL.md` Step 0.5 |
| Graduation writer | `skills/eval-summary/SKILL.md` |
| Adaptive thinking config | `agents/*.md` frontmatter |
| Batch API flag | `skills/sprint-workflow/SKILL.md`, `config.json` |
| Transcript serialization | `skills/sprint-workflow/SKILL.md`, `agents/evaluator.md` |
| Edge-case section | `skills/sprint-contract/template.md` |
| Playwright conditional | `agents/evaluator.md`, `config.json` |
| Adversarial hygiene flags | `agents/evaluator.md`, transcript trailer |
| Backward-compat defaults | `.harness/config.json`, `skills/harness-kickoff/SKILL.md` |

## Verification

After each sprint the harness evaluates itself against the `eval-harness` rubric. Beyond that, end-to-end verification:

1. **Sprint 6 trial loop** — Set `trials: 3` on a synthetic non-deterministic sprint (coin-flip criterion). Confirm `.harness/evals/sprint-X-r1-t1.md`, `-t2.md`, `-t3.md` exist with independent results. Confirm `skills/eval-summary` reports pass@3 ≈ 1−(1−0.5)³ ≈ 0.875 and pass^3 ≈ 0.125. With `trials: 1` (default), confirm no behavior change vs. today.
2. **Sprint 7 regression gate** — Manually break a file that a graduated criterion depends on. Run `/harness-sprint`. Confirm abort with "regression failed" error before contract negotiation begins.
3. **Sprint 8 thinking + batch** — Inspect a sprint transcript; confirm `thinking` blocks present. Set `batch.enabled: true` on a ≥20-criterion sprint; confirm a single Batch API call replaces N synchronous calls and eval results still land in `.harness/evals/`.
4. **Sprint 9 transcripts** — After any eval, confirm `.harness/transcripts/sprint-N-r1-t1.json` exists with `messages`, `tool_calls`, `token_usage`. Confirm summary.md links the transcript for any FAIL criterion.
5. **Sprint 10 completeness** — In a web-app test project, add a Visual Design criterion with an Edge Case entry; confirm Evaluator invokes Playwright, edge-case result reported separately from weighted score, and transcript trailer carries `verified_via_command: true` for every criterion.
6. **Meta-eval** — Run `/harness-summary` after Sprint 10. The `eval-harness` rubric should score ≥4 on all five dimensions (Methodology, Grading, Separation, Context Engineering, Extensibility/ACI), and the playbook alignment scorecard in the gap-analysis doc should show no remaining **Missing** rows.
7. **Backward compatibility** — On an existing project whose `.harness/config.json` predates this work (no `trials`, `sandbox`, `thinking`, `batch`, `transcripts` fields), run `/harness-sprint`. Confirm it executes exactly as before — one trial, no sandbox, no thinking config, synchronous calls, no transcript files.
