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

### Adaptive Thinking

Claude 4.6 supports adaptive thinking with an `effort` parameter. Each agent declares a baseline in its frontmatter, tuned to role:

| Agent / Skill | Baseline Effort | Rationale |
|---|---|---|
| `planner` | `medium` | Product spec expansion; routine work |
| `generator` | `medium` | Implementation; raised to `high` for CONTRACT_PROPOSAL and CONTRACT_REVISION |
| `evaluator` | `high` | Capability-eval baseline; raised to `max` for CONTRACT_REVIEW, lowered to `medium` for regression-criterion evaluation |
| `harness-summary` | `max` | Cross-sprint analysis, saturation detection, ACI review |

Override the whole harness's quality/cost tradeoff with a single knob, `config.thinking.profile`:

- `"default"` (default) — each agent uses its frontmatter baseline.
- `"fast"` — shift every baseline one level down, clamped at `medium`: planner `medium`, generator `medium`, evaluator `medium`, harness-summary `high`.
- `"thorough"` — shift every baseline one level up, clamped at `max`: planner `high`, generator `high`, evaluator `max`, harness-summary `max`.

Per-mode overrides (Generator CONTRACT_PROPOSAL at `high`, Evaluator CONTRACT_REVIEW at `max`, Evaluator regression-gate at `medium`) compose on top of the profile-adjusted baseline. An absent `thinking` object in `config.json` is treated as `profile: "default"` — Phase-1 behavior is preserved. Adaptive-thinking frontmatter is advisory: a Claude Code runtime that ignores the `thinking:` key causes agents to run at the model's default, which matches pre-Sprint-8 behavior.

### Batch API

For large eval suites, the Evaluator can route per-criterion verification commands through Anthropic's [Batch API](https://docs.anthropic.com/en/docs/build-with-claude/batch-processing), which offers a 50% token discount in exchange for a 24-hour SLA:

- `config.batch.enabled` (default `false`) — turn on batch mode.
- `config.batch.min_criteria` (default `20`) — threshold below which batch is not worth the latency; sprints with fewer criteria stay synchronous regardless of `enabled`.

Batch is strictly opt-in: the 24-hour SLA makes it unsuitable for tight contract→build→eval iteration cycles. It is intended for large regression suites, synthetic verification sprints, or cross-sprint summary generation where per-call savings compound. An absent `batch` object in `config.json` is treated as `enabled: false` — Phase-1 behavior is preserved. If a batch call fails (submission error, SLA timeout, malformed result), the harness falls back to synchronous evaluation and notes the failure in `progress.md`; no criterion is silently dropped.

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
