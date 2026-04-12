---
name: harness-kickoff
description: Initialize eval-driven development with Planner-Generator-Evaluator architecture
allowed-tools: Read, Write, Bash, Glob, Grep, Agent, Edit
disable-model-invocation: true
---

# Harness Kickoff

You are initializing the eval-driven development harness. Follow these steps exactly.

## Step 1: Detect Project Type

Check if `.harness/config.json` already exists. If it does, read it and confirm with the user whether to reinitialize or resume.

If no config exists, determine the project type by:
1. Reading any existing `CLAUDE.md`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, or similar project files
2. Looking at existing source code structure
3. If the type is ambiguous, ask the user to choose: `web-app`, `rag-system`, `cli-tool`, or `api-service`

## Step 2: Create .harness/ Directory

Create the following structure:
```
.harness/
├── config.json
├── contracts/
├── evals/
├── progress.md
```

Write `config.json` with detected project type and defaults:
```json
{
  "project_type": "<detected>",
  "rubric": "<matching rubric name>",
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
    "contract_negotiation": true,
    "sprint_decomposition": true,
    "eval_summary": true
  }
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

## Step 3: Invoke the Planner

The user's prompt (the text they provided when invoking `/harness-kickoff`) is the input to the Planner.

Spawn the Planner subagent using the Agent tool:
- subagent_type: use the `planner` agent definition
- Pass the user's prompt as the task
- Tell the Planner to read the project's existing code to understand the stack
- Tell the Planner to write its output to `.harness/spec.md` and `.harness/sprints.json`

After the Planner completes, verify both files exist and are well-formed:
- `spec.md` should have a product vision, feature list, and success criteria
- `sprints.json` should parse as valid JSON with a `sprints` array

## Step 4: Git Checkpoint

If `config.json` has `git_checkpoint: true`:
```bash
git add .harness
git commit -m "harness: initialize spec and sprint plan"
```

## Step 5: Present the Plan

Print:
1. A brief summary of the spec (3-5 sentences)
2. The full sprint plan as a numbered list with titles and complexity
3. Ask the user: "Ready to start Sprint 1? Run `/harness-sprint` to begin, or edit `.harness/sprints.json` to adjust the plan."

## Important Notes

- If the Planner produces an empty or malformed spec, retry once with more specific instructions
- Do NOT proceed to sprint execution — that's the sprint-workflow skill's job
- The `.harness/` directory should be committed to version control so progress survives across sessions
