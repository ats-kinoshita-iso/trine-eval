# Eval Harness Evaluation Rubric

Rubric for evaluating eval-driven development harnesses against Anthropic's published methodology (January–March 2026 guidance).

## Dimensions and Weights

### Methodology Completeness (30%)

| Score | Description |
|-------|-------------|
| 5 | All 8 steps of Anthropic's eval methodology are implemented: early bootstrapping from real failures, manual-to-automated conversion, unambiguous tasks with reference solutions, balanced positive/negative test sets, isolated environments, grader hierarchy, transcript review, saturation graduation. |
| 4 | 6-7 steps implemented. Missing steps are acknowledged with clear extension points. |
| 3 | 4-5 steps implemented. Core loop (contract→build→eval→retry) works but bootstrap, balance, and graduation are missing. |
| 2 | Only the core loop exists. No bootstrapping, no negative tests, no saturation tracking. |
| 1 | Partial implementation. Eval loop is incomplete or broken. |

### Grading Architecture (25%)

| Score | Description |
|-------|-------------|
| 5 | Explicit code→LLM→human grader hierarchy. Deterministic checks run first, LLM-as-judge handles subjective dimensions with isolated per-dimension scoring, structured rubrics with thinking-then-scoring, escape hatches. Human calibration mechanism exists. Pass@k and pass^k metrics available. |
| 4 | Grader hierarchy documented and encouraged. Per-dimension scoring works. LLM grading has rubrics. Missing one of: human calibration, pass@k, or escape hatches. |
| 3 | Evaluator uses rubrics and per-dimension scoring but doesn't enforce code-first grading. No pass@k metrics. No human calibration pathway. |
| 2 | Single-pass evaluation with no grader type distinction. Rubrics exist but scoring is ad-hoc. |
| 1 | No structured grading. Evaluator produces free-form opinions. |

### Generator-Evaluator Separation (20%)

| Score | Description |
|-------|-------------|
| 5 | Evaluator runs in forked context with no access to generator reasoning. Contract negotiation happens before implementation. Sprint contracts include weighted criteria, negative test cases, and reference solutions. The evaluator is independently calibratable with few-shot examples. |
| 4 | Forked context and contract negotiation in place. Contracts are specific and testable. Missing one of: weighted criteria, negative tests, or reference solutions. Calibration examples exist but are static. |
| 3 | Separation exists (forked context). Contracts have testable criteria but are flat (no weights, no negative cases). Calibration examples present but minimal. |
| 2 | Separation is instructional only (no technical enforcement). Contracts are vague. |
| 1 | No separation. Generator self-evaluates. |

### Context Engineering (15%)

| Score | Description |
|-------|-------------|
| 5 | Structured JSON note-taking for state that must survive compaction. Progress log distinguishes prose (markdown) from structured data (JSON). Compaction guidance for long sessions. Sub-agent isolation with condensed summaries. JIT context retrieval patterns documented. |
| 4 | Progress logging works. JSON used for structured data. Sub-agent isolation in place. Missing compaction guidance or JIT patterns. |
| 3 | Markdown-only progress logging. Sub-agent isolation exists. No compaction strategy. |
| 2 | Minimal progress tracking. No structured data format discipline. |
| 1 | No progress tracking. Context management is ad-hoc. |

### Extensibility & ACI (10%)

| Score | Description |
|-------|-------------|
| 5 | Custom rubrics supported with clear template. Hooks cover key lifecycle events (session start, pre-eval, post-eval, file changes). Plugin manifest accurate. Tool descriptions follow ACI best practices (3-4 sentences, semantic names, concise responses). Self-optimization pathway exists. |
| 4 | Custom rubrics work. Multiple hooks in place. Manifest accurate. Tool descriptions adequate. |
| 3 | Custom rubrics supported. Minimal hooks. Minor manifest issues. |
| 2 | Rubric system exists but is hard to extend. No hooks beyond basics. |
| 1 | Monolithic. No extension points. |

## Hard Thresholds

- **Methodology Completeness below 3/5 blocks.** The core eval loop must function.
- **Grading Architecture below 2/5 blocks.** Evaluations must produce structured, evidence-based results.
- **Generator-Evaluator Separation below 3/5 blocks.** Self-evaluation defeats the purpose.

## Testing Methods

- **File structure verification:** Check that all required files exist with correct schemas
- **Instruction review:** Read agent/skill markdown for completeness against playbook requirements
- **Schema validation:** Parse JSON files and verify required fields
- **Workflow tracing:** Walk through each skill's steps and verify they reference correct paths
- **Gap counting:** Count playbook requirements implemented vs. missing
- **Cross-reference:** Verify rubric dimensions map to playbook sections
