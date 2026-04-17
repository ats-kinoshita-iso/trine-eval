# trine-eval v0.1 — Product Specification

## Product Vision

`trine-eval` is a Python evaluation framework that proves functional correctness of LLM applications across three domains — agent trajectories, retrieval-augmented generation, and code — on a single set of composable primitives (Task/Solver/Scorer/Metric/Log). v0.1 ships three end-to-end evals on Anthropic Claude Opus 4.7 (released 2026-04-16, $5/$25 per M tokens), wired to the Batch API and prompt caching from day 1, runnable from a CLI, from `pytest`, or as a CI exit-code gate. The design follows the primitive-convergence thesis: nail sample → solver → scorer → metric → log once, then reuse it everywhere.

Primary sources grounding this spec: Inspect AI (UK AISI) for the Task/Solver/Scorer decomposition and replayable log format; RAGAS for RAG metrics; AgentEvals / τ²-bench / Terminal-Bench 2.0 for trajectory metrics; SWE-bench Verified v2.0.3+ and EvalPlus for code evals; Chen et al. (2021) for pass@k; Anthropic engineering posts for Batch, prompt caching, and the Opus 4.7 `xhigh` thinking tier.

---

## Feature List

### Must-have (P0 — v0.1 correctness gate)

**Core primitives and framework plumbing**
- Task / Dataset / Sample / Solver / Scorer / Metric / EvalLog abstractions with Pydantic typing.
- Decorator-based registry: `@task`, `@solver`, `@scorer`, `@metric`, `@tool`, discoverable via CLI and configurable via YAML.
- Scorer composition: a task may attach multiple named scorers; metrics aggregate separately from scorers (never conflate the two).
- Judge role as first-class: `model_roles={"target": ..., "judge": ...}`; swap Opus judge for Haiku judge with zero code change.
- Replayable log format: binary + JSON, rescorable via `trine-eval score <log>` without re-running the target.
- Async execution with per-run limits: `max_concurrency`, `token_limit`, `time_limit`, `cost_limit`.
- Sandboxed tool execution via Docker (or equivalent) for code and shell evals.
- Pytest plugin: eval tasks can be collected as pytest items; CI exit code is non-zero on regression.

**Anthropic platform integration**
- Anthropic SDK wired with Batch API support and prompt caching from day 1.
- Support Opus 4.7 thinking tiers including the new `xhigh` tier.
- Tokenizer accounting applies the Opus 4.7 1.0–1.35× input-token multiplier when computing `token_limit` and `cost_limit`.

**Agent trajectory eval (B-series)**
- End-state scoring is the primary signal; step-wise scoring is secondary.
- All four trajectory-match modes: strict, unordered, subset, superset.
- Tool-call precision / recall / F1 (set-based) plus sequence-aligned Tool Call Accuracy.
- Per-trajectory step count, unnecessary-call count, and retry count captured in the log.
- Task Completion / Agent Goal Accuracy scorer with reference-based and reference-free variants.
- Benchmark adapters for τ²-bench and Terminal-Bench 2.0.
- `thinking` blocks captured and passed through during tool use with signature verification.

**RAG eval (C-series)**
- RAG triad scorers: Context Relevance, Faithfulness, Answer Relevance.
- RAGAS-compatible wrappers: Faithfulness, Response Relevancy, Context Precision, Context Recall, Factual Correctness.
- Top-k retrieval failure rate reported as a standalone retrieval-only metric.
- Retrieval scoring separated from generation scoring; generation evaluated against gold and against retrieved chunks independently.
- Citation / attribution accuracy scorer.

**Code eval (D-series)**
- Test-execution-based scoring, never patch-match.
- pass@k using Chen et al. unbiased estimator `1 - C(n-c, k) / C(n, k)` with n ≥ k samples.
- Regression-safety gate honoring SWE-bench invariants: FAIL_TO_PASS and PASS_TO_PASS.
- Cheap-to-expensive pre-filter tiers: lint → type-check → AST/semantic diff → run tests.
- Benchmark adapters for SWE-bench Verified (v2.0.3+), Terminal-Bench 2.0, and EvalPlus (HumanEval+ or MBPP+).
- Contamination-aware benchmark selection: LiveCodeBench and/or SWE-bench Pro available as contamination-resistant complements.

**LLM-as-judge protocol**
- Default judge protocol: rubric + golden answer + CoT evaluation steps, returns `{score, reason}`.
- Binary or small-discrete labels preferred; report TPR/TNR (never bare agreement rate).
- Pairwise judging with position-swap debiasing.

**Stack constraint**
- Python + `uv` + LangGraph + Anthropic SDK + RAGAS + self-hosted Langfuse + Postgres/pgvector + FastAPI.

### Should-have (P1 — optimization; scheduled for last 1–2 sprints)

- Output cache keyed on `(prompt, model, params)` for model-call deduplication.
- Trajectory-level LLM-as-judge with a `GraphTrajectory` input schema.
- Cost-per-task and steps-vs-optimal reported as first-class secondary metrics.
- Noise Sensitivity metric for RAG distractor robustness.
- Long-context-vs-RAG A/B harness.
- Aider polyglot benchmark adapter.
- Cascade judges (cheap Haiku first-pass → Opus on disagreement).
- Sampling-count reduction heuristics for pass@k convergence.
- Prompt-compaction optimization pass for cached prefixes.

### Nice-to-have (deferred past v0.1)

- Web UI for log inspection (Langfuse handles this externally for v0.1).
- Non-Anthropic model providers beyond what's needed for judge/target role swaps.
- Distributed execution across worker nodes.
- Contamination auditing tooling beyond benchmark selection.

---

## User Interaction Patterns

**CLI** (primary surface)
- `trine-eval run <task.yaml>` — execute a task, emit an EvalLog.
- `trine-eval score <log>` — rescore an existing log without calling the target model.
- `trine-eval list` — enumerate registered `@task`, `@solver`, `@scorer`, `@metric`, `@tool`.
- `trine-eval view <log>` — pretty-print log contents (samples, scores, metrics, trajectories).
- All CLI invocations accept `--model-roles target=<model> judge=<model>`, `--max-concurrency`, `--token-limit`, `--cost-limit`, `--batch` (Anthropic Batch API).

**YAML task definition** — declarative composition of dataset + solver + scorers + metrics + model_roles + limits.

**Pytest integration** — `pytest tests/evals/` collects eval tasks as pytest items; CI treats eval failure as a test failure (non-zero exit).

**Python API** — `from trine_eval import task, solver, scorer, metric, tool, eval; eval(my_task, model_roles={...})` for programmatic use.

---

## Technical Constraints

- **Language/runtime:** Python 3.11+, package-managed with `uv`.
- **Required dependencies:** LangGraph, Anthropic Python SDK, RAGAS, self-hosted Langfuse, Postgres with pgvector, FastAPI.
- **Sandboxing:** Docker (or equivalent OCI runtime) for code and shell tool execution.
- **Log format:** replayable, binary + JSON side-by-side; rescoring must not require target-model calls.
- **Anthropic integration:** Batch API and prompt caching wired from the first sprint that instantiates any model call; Opus 4.7 `xhigh` thinking tier supported; tokenizer accounting reflects the 1.0–1.35× Opus 4.7 input-token change.
- **Scorer/metric separation:** scorers return named per-sample scores; metrics aggregate across samples. Code must not blur the boundary.
- **Determinism:** judge-based scorers must log the judge model, rubric, seed (if any), and raw judge output so rescoring is reproducible.
- **Append-only evals:** per harness conventions, eval artifacts written by this framework must be append-only.

---

## Success Criteria

Every criterion below is pass/fail and verifiable by an automated evaluator (CLI invocation, file inspection, or test execution). Criteria are grouped by the subsystem they validate.

### S1. Primitives, registry, and log

1. `trine-eval list` enumerates at least one registered `@task`, `@solver`, `@scorer`, `@metric`, and `@tool` from the shipped examples.
2. Running `trine-eval run examples/trivial.yaml` produces an EvalLog file containing: task name, samples (input, target, output), scores (named), metrics (named, aggregated), model_roles, limits, and timestamps.
3. `trine-eval score <log>` rescorés the log without issuing any target-model API calls, verified by network-call count or SDK-mocked assertion.
4. Pydantic validation rejects an EvalLog missing any required field (automated test asserts `ValidationError`).
5. Scorers and metrics are separate objects; a test asserts that a scorer instance has no `aggregate()` method and a metric instance has no per-sample `score()` method.

### S2. Async execution and limits

6. A task configured with `max_concurrency=4` never has more than 4 in-flight target calls (verified by instrumented mock).
7. A task exceeding `token_limit`, `time_limit`, or `cost_limit` halts and emits a log with `status="limit_exceeded"` and the triggering limit named.
8. Pytest plugin: `pytest tests/evals/test_trivial.py` exits 0 when the task passes its threshold and exits non-zero when it does not.

### S3. Anthropic integration

9. An eval run with `--batch` dispatches requests via the Anthropic Batch API (verified by SDK call or recorded request URL).
10. Prompt caching is active on at least one solver in the shipped examples (verified by cache-read tokens reported in the EvalLog or by the Anthropic API response fields).
11. `thinking_effort="xhigh"` is an accepted parameter and is propagated to the Anthropic request payload.
12. Token accounting multiplies input tokens by the configured Opus 4.7 multiplier (a test sets multiplier=1.35 and asserts `accounted_tokens == round(raw_tokens * 1.35)`).
13. Swapping `model_roles.judge` from Opus to Haiku requires zero source-code changes (verified by running the same YAML with both judges and diffing code = empty).

### S4. Agent trajectory eval

14. All four trajectory match modes (strict, unordered, subset, superset) exist as named scorers and produce distinct scores on a crafted fixture where the four modes disagree.
15. Tool-call precision, recall, F1, and sequence-aligned Tool Call Accuracy are computed and logged per sample.
16. Step count, unnecessary-call count, and retry count appear in the per-sample log record.
17. Task Completion scorer has both reference-based and reference-free variants, selectable by config; both run to completion on a fixture.
18. τ²-bench and Terminal-Bench 2.0 adapters each load at least one sample from their upstream dataset format without modification.
19. A solver using tools preserves `thinking` blocks with signatures across turns; a test asserts the signature is present and verifiable in the outbound request.

### S5. RAG eval

20. The RAG triad scorers (Context Relevance, Faithfulness, Answer Relevance) all produce scores on a shipped RAG fixture.
21. RAGAS-compatible wrappers exist for Faithfulness, Response Relevancy, Context Precision, Context Recall, and Factual Correctness, each callable via the registry and producing numeric scores.
22. Top-k retrieval failure rate is reported as a standalone retrieval-only metric independent of any generation scorer.
23. Generation is scored twice — once against gold chunks, once against retrieved chunks — and both scores appear separately in the log.
24. Citation / attribution accuracy scorer produces a numeric score on a fixture with known citation ground truth.

### S6. Code eval

25. A code task runs candidate solutions inside a Docker sandbox; a test asserts the sandbox is invoked and host FS is not written.
26. pass@k is computed using the Chen et al. unbiased estimator; a unit test asserts `pass_at_k(n=10, c=3, k=5)` matches the closed-form value.
27. SWE-bench FAIL_TO_PASS and PASS_TO_PASS gating: a candidate that breaks PASS_TO_PASS receives a failing sprint-level regression score even if FAIL_TO_PASS tests pass.
28. Cheap-tier pre-filter runs in order lint → type-check → AST/semantic diff → tests; a test asserts test execution is skipped when an earlier tier fails.
29. SWE-bench Verified (v2.0.3+), Terminal-Bench 2.0, and EvalPlus (HumanEval+ or MBPP+) adapters each load at least one sample without modification.
30. A contamination-resistant benchmark (LiveCodeBench or SWE-bench Pro) adapter loads at least one sample.

### S7. LLM-as-judge

31. The default judge protocol accepts `(rubric, golden_answer, cot_steps)` and returns `{score, reason}` (schema validated).
32. A judge scorer using binary labels reports TPR and TNR computed against a labeled fixture; bare agreement rate is not reported as the primary metric.
33. Pairwise judging runs each comparison twice with positions swapped and reports a debiased score; a test asserts position-swap is invoked.

### S8. End-to-end gate

34. Three end-to-end evals ship and pass on their own fixtures: one agent-trajectory eval, one RAG eval, one code eval. Each is runnable via `trine-eval run <task.yaml>` and via `pytest`.
35. Each end-to-end eval emits a complete, replayable EvalLog; rescoring each log via `trine-eval score` reproduces the original scores bit-for-bit (or within a documented judge-nondeterminism tolerance when judge model is stochastic).
