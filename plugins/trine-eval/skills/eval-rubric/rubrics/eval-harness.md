# Eval Harness Evaluation Rubric

Rubric for evaluating eval-driven development harnesses against Anthropic's published methodology (January–March 2026 guidance).

## Dimensions and Weights

### Methodology Completeness (20%)

| Score | Description |
|-------|-------------|
| 5 | All 8 steps implemented: (0) early bootstrapping from real failures, (1) manual-to-automated conversion, (2) unambiguous tasks with reference solutions, (3) balanced positive/negative test sets, (4) isolated environments, (5) grader hierarchy code→LLM→human, (6) transcript review for grader quality, (7) saturation graduation. |
| 4 | 6-7 of the 8 steps above are implemented. Missing steps are acknowledged with clear extension points. Typical at this level: steps 0-5 implemented, steps 6-7 (transcript review, saturation) deferred with documented plans. |
| 3 | 4-5 of the 8 steps above are implemented. Core loop (contract→build→eval→retry) works. Typical at this level: steps 2-5 (reference solutions, negative tests, isolation, grader hierarchy) implemented; steps 0-1 (bootstrapping, manual-to-automated) and 6-7 (transcript review, saturation) are missing. |
| 2 | Only the core loop exists. No bootstrapping, no negative tests, no saturation tracking. |
| 1 | Partial implementation. Eval loop is incomplete or broken. |

**Note on weight change (Sprint 07).** Methodology Completeness dropped from 30% to 20%; the recovered 10% was promoted to the new `Functional Integration Coverage` dimension (defined below). Previously, "isolated environments" and "balanced positive/negative test sets" were implicit Methodology 5/5 requirements; the new dimension makes the functional/architectural distinction explicit and gives it standalone scoring pressure.

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

### Functional Integration Coverage (10%)

This dimension scores by **bucket distribution** of the verification evidence, not by mock-vs-live alone. See `rules/harness-conventions.md` → "Three Buckets of Verification" for the canonical definitions. Briefly:

- **Bucket 1 — structural / presence.** `grep -q "X" file.md`, `assert key in dict`, `[ -f path ]`. Verifies plumbing exists. Does NOT verify behavior.
- **Bucket 2 — behavioral with mocks.** Code does what it should given stubbed dependencies. Asserts on observable outcomes (return values, exit codes, raised exceptions, written files). Example: `test_caps.py` asserts `cap_hit == "token_limit"` fires when the limit is exceeded.
- **Bucket 3 — behavioral against real systems.** Code AND the dependency behave correctly together. Real Docker, real Anthropic API, real judge subagent. Catches integration drift.

| Score | Description |
|-------|-------------|
| 5 | Bucket 3 coverage parity with bucket 2 across every feature. Live + recorded-fixture modes both wired (CI runs fixtures, on-demand runs live). Bucket-3 failures gate the sprint. Bucket 1 is reserved for genuinely-plumbing-only criteria; the contract makes the bucket of each criterion explicit. |
| 4 | Bucket 2 is comprehensive (every behavioral criterion has a behavioral test, mocked or otherwise). Bucket 3 covers most major external integrations. Live API or recorded fixtures wired with automated budget enforcement. |
| 3 | Bucket 2 is the default for behavioral work — most contract criteria assert outcomes, not just presence. At least one bucket-3 test exists (real local Docker, subagent-driven judge correctness, or recorded fixture). |
| 2 | Substantial bucket-2 coverage exists for the deliverable code (most code-side tests assert outcomes given mocks). Contract criteria are still bucket-1-heavy. Bucket 3 is empty. *(This is Phase 2's honest score: the Python library has ~80% bucket-2 coverage, but the eval-harness's own contract criteria are 90% bucket 1 and no bucket-3 tests exist.)* |
| 1 | Only bucket 1: structural/presence tests. The code or AI is never exercised behaviorally — verifications check that files exist, regex patterns match, and JSON keys are present, but nothing asserts an outcome. A deliverable could ship at 100% PASS while being non-functional. |

**Why bucket distribution matters.** A sprint that verifies "the new feature's source file exists and contains the function name" (bucket 1) can pass at 100% while the function returns wrong values. A sprint that verifies "calling the new function with input X returns output Y" (bucket 2) catches that. A sprint that verifies "running the new function against the real downstream system produces the documented behavior" (bucket 3) catches integration drift the mocked test can't. Each bucket exists to catch a different failure mode; collapsing them into a single weighted score hides the asymmetry.

**Hard threshold for this dimension** (see "Hard Thresholds" below): the grace window for bucket-3 absence stays in place for three sprints after Sprint 07; bucket-1-only sprints (score 1/5) block from the start. The harness should never grade a sprint as PASS when no test actually exercises the deliverable's behavior.

## Hard Thresholds

- **Methodology Completeness below 3/5 blocks.** The core eval loop must function.
- **Grading Architecture below 2/5 blocks.** Evaluations must produce structured, evidence-based results.
- **Generator-Evaluator Separation below 3/5 blocks.** Self-evaluation defeats the purpose.
- **Functional Integration Coverage at 1/5 blocks immediately.** A sprint whose verification is entirely bucket-1 (presence checks, no behavioral assertions) cannot pass — the harness should never grade as PASS when no test exercises the deliverable's behavior. This applies from Sprint 07 onward; pre-Sprint-07 sprints are grandfathered.
- **Functional Integration Coverage below 3/5 is advisory-only for the first 3 sprints after Sprint 07 lands; blocks at <3/5 thereafter.** The grace window lets the harness ramp bucket-3 (real-system) coverage without gating sprints that legitimately have nothing to exercise against external systems (pure-internal refactor sprints). Bucket 2 is achievable for nearly every sprint.

## Testing Methods

- **File structure verification:** Check that all required files exist with correct schemas
- **Instruction review:** Read agent/skill markdown for completeness against playbook requirements
- **Schema validation:** Parse JSON files and verify required fields
- **Workflow tracing:** Walk through each skill's steps and verify they reference correct paths
- **Gap counting:** Count playbook requirements implemented vs. missing
- **Cross-reference:** Verify rubric dimensions map to playbook sections
