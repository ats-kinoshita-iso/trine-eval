# trine-eval

A modular three-agent eval-driven development harness for Claude Code. Implements Anthropic's Planner-Generator-Evaluator architecture as a portable, rubric-swappable plugin.

## How It Works

Three agents collaborate through files on disk — no shared context:

1. **Planner** — Expands a short user prompt into a product spec with sprint decomposition
2. **Generator** — Implements one sprint at a time, negotiating testable success criteria before writing code
3. **Evaluator** — Adversarially tests each sprint against its contract, grading PASS/FAIL with specific evidence

The agents communicate exclusively through files in a `.harness/` directory. Each sprint follows a contract→build→eval→retry cycle.

## Installation

Copy or clone this repository into your Claude Code plugins directory, or install from a target project:

```bash
# From your project directory
claude /plugin install /path/to/eval-harness
```

## Usage

### 1. Initialize the Harness

```
/harness-kickoff Build a task management API with user authentication and team workspaces
```

This will:
- Detect your project type (or ask you to choose)
- Create the `.harness/` directory with configuration
- Run the Planner to produce a spec and sprint plan
- Present the plan for your review

### 2. Run Sprints

```
/harness-sprint
```

Runs the next incomplete sprint through the full cycle:
- Generator proposes a sprint contract with testable success criteria
- Evaluator reviews the contract for testability and completeness
- Generator implements the sprint
- Evaluator tests against the contract
- If failures: Generator fixes, Evaluator re-tests (up to 3 rounds)

To target a specific sprint:
```
/harness-sprint 3
```

### 3. View Progress

```
/harness-summary
```

Generates a cross-sprint analysis with pass rates, trends, failure patterns, and recommendations.

## Project Types and Rubrics

The harness ships with four rubrics. Set the project type during kickoff or in `.harness/config.json`:

| Type | Rubric | Key Dimensions |
|------|--------|----------------|
| `web-app` | web-app | Functionality, Visual Design, Code Quality, Robustness |
| `rag-system` | rag-system | Retrieval Quality, Answer Faithfulness, System Robustness, Architecture |
| `cli-tool` | cli-tool | Functionality, Usability, Error Handling, Code Quality |
| `api-service` | api-service | Correctness, Robustness, API Design, Code Quality |

## Configuration

`.harness/config.json` controls harness behavior:

```json
{
  "project_type": "web-app",
  "rubric": "web-app",
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

### Disabling Components

The `components_enabled` section lets you simplify the harness as models improve. For example, disabling `contract_negotiation` skips the Evaluator's contract review — the Generator's proposed criteria are accepted directly.

### Phase 2 Configuration Knobs

These optional fields extend `.harness/config.json` with backward-compatible defaults. A config that omits them runs exactly as in Phase 1.

- **`thinking.profile`** — one of `"default"`, `"fast"`, or `"thorough"`. Default: `"default"`, which preserves Phase-1 behavior (no override applied to agent-level adaptive-thinking effort declared in agent frontmatter). The `"fast"` and `"thorough"` values are reserved for a future override dispatcher; the default is the only path that mutates today's behavior, and it does not. Each role's effort level is declared in the agent's own frontmatter (`agents/planner.md`, `agents/generator.md`, `agents/evaluator.md`, and the `harness-summary` skill) — `medium` for routine planning and implementation, `high` for capability evaluation, and `max` for contract review and cross-sprint summary analysis.

- **`batch.enabled`** — boolean. Default: `false`. When `true` and a sprint has at least `batch.min_criteria` criteria, eval verifications are submitted as a single Anthropic Batch API call (50% discount on input/output tokens, 24-hour SLA). Batch is a cost optimization, not a latency optimization. With the default `false`, evaluations run synchronously as in Phase 1.

- **`batch.min_criteria`** — integer. Default: `20`. Sprints with fewer criteria stay synchronous even when `batch.enabled` is `true` — the batch overhead is only worth absorbing on large suites. The criterion count compared against this threshold is the same count emitted in `sprint-{NN}.tasks.json` (success criteria + Should-NOT gates).

- **`regression.enabled`** / **`regression.fail_fast`** — see `rules/harness-conventions.md`. The defaults are auto (truthy iff `regression.json` has a non-empty `tasks` array) and `true` (abort on regression failure). Pre-Phase-2 projects whose `.harness/config.json` lacks the `regression` object see no behavior change.

- **`trials`** / **`sandbox.mode`** / **`taxonomy.emit_tasks_json`** — see Sprint 6 documentation. Defaults `1`, `"none"`, `true` reproduce Phase-1 behavior.

- **`evaluator_tools.playwright`** — string. Default `"auto"`. Reserved values: `"auto"` (Playwright MCP enabled when `project_type == "web-app"`, disabled otherwise — recommended default), `"never"` (disable unconditionally — used when running a `web-app` project without Playwright installed; the Evaluator falls back to `curl` and routes Visual Design findings to human review), `"always"` (enable regardless of project type — for explicit testing of the Playwright path). Backward compatibility: a config that lacks the `evaluator_tools` object hits `"auto"`, which combined with any non-`web-app` project type resolves to "Playwright disabled" — exactly Phase-1 behavior.

## Adding Custom Rubrics

1. Create a new file in `skills/eval-rubric/rubrics/your-type.md`
2. Follow the structure of existing rubrics:
   - Define quality dimensions with percentage weights (must total 100%)
   - For each dimension, provide a 1-5 scoring table with specific descriptions
   - Define hard thresholds (minimum scores that cause automatic failure)
   - List testing tools appropriate for the domain
3. Set `"rubric": "your-type"` in `.harness/config.json`

## Directory Structure

```
eval-harness/                     # Plugin root
├── .claude-plugin/plugin.json    # Plugin manifest
├── skills/
│   ├── harness-kickoff/          # Entry point: init + planning
│   ├── harness-sprint/           # Per-sprint contract→build→eval loop
│   ├── eval-rubric/              # Rubric loader + domain rubrics
│   ├── sprint-contract/          # Contract template + negotiation protocol
│   └── harness-summary/          # Cross-sprint analysis
├── agents/
│   ├── planner.md                # Product strategist
│   ├── generator.md              # Senior engineer
│   └── evaluator.md              # Adversarial QA
├── hooks/hooks.json              # Session lifecycle hooks
└── rules/harness-conventions.md  # Conventions for .harness/ files
```

When running in a target project:

```
your-project/
├── .harness/                     # Created by harness-kickoff
│   ├── config.json               # Project type, rubric, thresholds
│   ├── spec.md                   # Planner output
│   ├── sprints.json              # Sprint decomposition
│   ├── contracts/sprint-NN.md    # Negotiated sprint contracts
│   ├── evals/sprint-NN.md        # Evaluation results per sprint
│   ├── progress.md               # Session-resumable progress log
│   └── summary.md                # Cross-sprint summary
```

## Design Principles

- **Files, not shared memory.** Agents communicate via `.harness/` files. This creates an audit trail and survives session interruptions.
- **Grade outcomes, not paths.** The Evaluator checks what was produced, not how.
- **Specific evidence required.** Every FAIL must cite file paths, line numbers, and error messages.
- **Complexity decreases over time.** Components can be individually disabled as models improve.
- **Rubrics are the parameterization point.** Change the rubric to change the project type — orchestration stays the same.
