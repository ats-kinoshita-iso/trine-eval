---
name: harness-kickoff
description: Initialize eval-driven development with Planner-Generator-Evaluator architecture
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, Edit
disable-model-invocation: true
---

# Harness Kickoff

You are initializing the eval-driven development harness. Follow these steps exactly.

## Step 0: Parse Mode Argument

The user may pass `--mode minimal` (or `--mode standard`, the default) in `$ARGUMENTS`. Parse it out of the prompt before treating the remainder as the product description.

- `standard` (default): runs the full Planner-Generator-Evaluator harness. All `components_enabled` flags default to `true`.
- `minimal`: collapses the Planner and Generator into main-thread drafting for roughly 25–40% token savings per sprint. The Evaluator subagent still runs forked — this preserves Generator-Evaluator separation, which is the playbook's core independence guarantee. Contract negotiation still runs (the Evaluator's contract review is the cheapest high-leverage gate).

Remember the parsed mode; it drives config defaults in Step 2 and the Planner gate in Step 3.

## Step 1: Detect Project Type

<!-- Context scope at this step: .harness/config.json (existence check only), project manifest files -->
<!-- Deferred: spec.md, sprints.json, progress.md — do not exist yet; do not attempt to read them -->
<!-- Only read project files necessary to determine project type — not the entire codebase -->

Check if `.harness/config.json` already exists. If it does, read it and confirm with the user whether to reinitialize or resume.

If no config exists, determine the project type by:
1. Reading only the necessary project manifest files: `CLAUDE.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar
2. Looking at existing source code structure (read only top-level files — defer deep reads)
3. If the type is ambiguous, ask the user to choose: `web-app`, `rag-system`, `cli-tool`, `api-service`, `eval-harness`, or `harness-build` (for agent runtime harnesses evaluated against the playbook stages). For harness-adjacent projects: choose `eval-harness` (meta layer — grading the eval methodology itself) when the primary deliverable is the eval infrastructure such as contract format, grader hierarchy, or sprint workflow; choose `harness-build` (runtime layer — grading the agent control plane) when the primary deliverable is the agentic loop, tool registry, sandboxing, or governance. See `plugins/trine-eval/skills/eval-rubric/rubrics/README.md` for the full decision guide.

## Step 2: Create .harness/ Directory

<!-- Context scope at this step: no file reads needed — write-only step -->
<!-- Deferred: bootstrap/failure-catalog.json until Step 2b; Planner output until Step 3 -->
<!-- Do not read harness files that will be created in this step -->

Create the following structure:
```
.harness/
├── config.json
├── sprint-state.json
├── contracts/
├── evals/
├── progress.md
```

Write `config.json` with detected project type and defaults.

Use the following project_type → rubric mapping to fill the `"rubric"` field:
- `web-app` → `"rubric": "web-app"`
- `rag-system` → `"rubric": "rag-system"`
- `cli-tool` → `"rubric": "cli-tool"`
- `api-service` → `"rubric": "api-service"`
- `eval-harness` → `"rubric": "eval-harness"`
- `harness-build` → `"rubric": "harness-build"`

The `mode` field and the four `components_enabled` flags (`generator_subagent`, `per_sprint_aci_review`, `calibration_writes`, plus the existing `planner`) together determine which parts of the harness run as subagents versus in the main thread.

For `--mode standard` (default), all `components_enabled` flags are `true`:
```json
{
  "mode": "standard",
  "project_type": "<detected>",
  "rubric": "<matching rubric name — see routing table above>",
  "max_retries": 3,
  "pass_threshold": {
    "per_dimension_minimum": 2,
    "critical_dimensions": ["functionality"],
    "critical_minimum": 3
  },
  "contract_negotiation_rounds": 2,
  "git_checkpoint": true,
  "components_enabled": {
    "planner": true,
    "generator_subagent": true,
    "contract_negotiation": true,
    "sprint_decomposition": true,
    "per_sprint_aci_review": true,
    "calibration_writes": true,
    "eval_summary": true
  }
}
```

For `--mode minimal`, set `mode: "minimal"` and flip `planner`, `generator_subagent`, `per_sprint_aci_review`, and `calibration_writes` to `false`. Leave `contract_negotiation`, `sprint_decomposition`, and `eval_summary` as `true` — contract negotiation is the cheapest high-leverage gate and should stay on even in minimal mode.

Initialize `sprint-state.json` with machine-readable state:
```json
{
  "current_sprint": 1,
  "sprints": [],
  "last_updated": "<ISO 8601 timestamp>"
}
```

As sprints complete, each entry in `sprints` will be populated:
```json
{
  "number": 1,
  "title": "Sprint title from sprints.json",
  "status": "pass",
  "rounds": 2,
  "criteria_passed": 8,
  "criteria_total": 10,
  "weighted_score": 85
}
```

Initialize `progress.md`:
```markdown
# Harness Progress Log

## Initialized
- Date: <current date>
- Project type: <type>
- Rubric: <rubric>
```

## Step 2b: Load Bootstrap Failure Catalog (if exists)

<!-- Context scope at this step: bootstrap/failure-catalog.json (deferred read — only if it exists) -->
<!-- Lazy read: only pull this file if it is present; do not attempt to read it otherwise -->

If `.harness/bootstrap/failure-catalog.json` exists, read it and pass the failure data to the Planner:
- Group failures by rubric dimension to inform sprint decomposition
- Failures tagged `critical` severity should appear as criteria in the first sprint
- The catalog provides real-world failure cases that the Planner should prioritize over synthetic test ideas

If the catalog does not exist, skip this step. The bootstrap is optional — the harness works without it.

## Step 3: Produce Spec and Sprint Plan

<!-- Context scope at this step: user prompt (already in context), failure catalog summary if loaded in Step 2b -->
<!-- Deferred: spec.md and sprints.json do not exist yet; Planner will create them -->
<!-- Only pass the minimal set of context to Planner: user prompt + failure catalog summary (if any) -->

The user's prompt (the text they provided when invoking `/harness-kickoff`, minus any `--mode` argument) is the product description. Produce `.harness/spec.md` and `.harness/sprints.json` — which route depends on `components_enabled.planner` in the config you just wrote.

### 3a. Planner subagent (when `components_enabled.planner` is true — standard mode)

Spawn the Planner subagent using the Agent tool:
- subagent_type: use the `planner` agent definition
- Pass the user's prompt as the task
- If a failure catalog was loaded in Step 2b, pass its summary to the Planner as additional context
- Tell the Planner to read the project's existing code to understand the stack
- Tell the Planner to write its output to `.harness/spec.md` and `.harness/sprints.json`

### 3b. Main-thread planning (when `components_enabled.planner` is false — minimal mode)

Do not spawn the Planner subagent. Instead, draft the spec and sprint plan directly in the main thread, producing the same two artifacts (`.harness/spec.md` and `.harness/sprints.json`) in the same format — only the author changes, not the file shape or downstream consumers.

1. Read the project's existing code (CLAUDE.md, package.json, pyproject.toml, Cargo.toml, go.mod, and the source tree) to understand the stack. Don't re-specify things that already exist.
2. If a failure catalog was loaded in Step 2b, fold its failure cases into the success criteria.
3. Write `.harness/spec.md` with the sections defined in `agents/planner.md`: **Product Vision** (2–3 sentences), **Feature List** grouped Must/Should/Nice-to-have, **User Interaction Patterns**, **Technical Constraints** drawn from the detected stack, and **Success Criteria** (testable, unambiguous pass/fail).
4. Write `.harness/sprints.json` matching the planner schema: `{"sprints": [{"number", "title", "features", "estimated_complexity": "low"|"medium"|"high", "dependencies": [sprint numbers]}]}`. Aim for 3–8 sprints, ordered so each builds on the last, each completable in one context window.
5. Stay at the product level — do not specify function signatures, database schemas, or route structures. That is still the Generator's (or main-thread implementation's) concern, not the planner's.

### 3c. Verify Artifacts

After either path, verify both files exist and are well-formed:
- `spec.md` should have a product vision, feature list, and success criteria
- `sprints.json` should parse as valid JSON with a `sprints` array

## Step 4: Git Checkpoint

<!-- Context scope at this step: no new file reads needed — git operations only -->
<!-- Deferred: nothing; this step uses no context retrieval -->

If `config.json` has `git_checkpoint: true`:
```bash
git add .harness
git commit -m "harness: initialize spec and sprint plan"
```

## Step 5: Present the Plan

<!-- Context scope at this step: spec.md, sprints.json (just created by Planner) — deferred until now -->
<!-- Read spec.md and sprints.json only at this step to compose the summary for the user -->
<!-- Do not re-read project manifest files — they were only needed in Step 1 -->

Print:
1. A brief summary of the spec (3-5 sentences)
2. The full sprint plan as a numbered list with titles and complexity
3. Ask the user: "Ready to start Sprint 1? Run `/harness-sprint` to begin, or edit `.harness/sprints.json` to adjust the plan."

## Important Notes

- If the Planner produces an empty or malformed spec, retry once with more specific instructions
- Do NOT proceed to sprint execution — that's the harness-sprint skill's job
- The `.harness/` directory should be committed to version control so progress survives across sessions

## Context Retrieval Principles

This kickoff skill uses just-in-time (JIT) context retrieval: each step reads only the minimal set of files needed at that point. Context reads are deferred to the step that actually requires them rather than front-loaded at session start.

**Deferrable reads in this skill:**
- Project source files: read only enough to determine project type (Step 1), then deferred
- `bootstrap/failure-catalog.json`: deferred until Step 2b, and only if it exists (lazy read)
- `spec.md` and `sprints.json`: deferred until Step 5 when the Planner has already written them

Reading all available files at Step 1 would waste context window on content that is not yet needed — for example, reading spec.md before the Planner has even written it would fail, and reading the entire project codebase to detect project type is unnecessary when manifest files suffice.
