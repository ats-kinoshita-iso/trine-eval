# trine-eval v0.1 — Product Specification

## Product Vision

`trine-eval` is a Python evaluation framework that proves functional correctness of LLM applications across three domains — agent trajectories, retrieval-augmented generation, and code — on a single set of composable primitives (Task/Solver/Scorer/Metric/Log). v0.1 ships three end-to-end evals on Anthropic Claude Opus 4.7 (released 2026-04-16), wired to the Batch API and prompt caching from day 1, so that a team can run reproducible, regression-gated evals from the CLI, `pytest`, or CI. The design follows the primitive-convergence thesis: nail sample → solver → scorer → metric → log once and reuse it everywhere.

## Priority Legend

- **P0** — baseline correctness, must ship in v0.1
- **P1** — cost/token optimization, may land in the final 1–2 sprints

## Must-Have Features (P0)

### Core primitives and runtime
- **F-A1** Inspect-AI-style decomposition: `Task`, `Dataset`, `Sample`, `Solver`, `Scorer`, `Metric`, `EvalLog` as typed Pydantic objects (ref: [Inspect AI](https://inspect.aisi.org.uk/)).
- **F-A2** Decorator registry (`@task`, `@solver`, `@scorer`, `@metric`, `@tool`) with YAML-driven run configs and a CLI that enumerates registered objects.
- **F-A3** Scorer composition — a task may carry a list of scorers; each returns one or more named `Score`s; `Metric`s aggregate independently (no conflation between scorer and metric).
- **F-A4** `model_roles` abstraction with at minimum `target` and `judge` roles; swapping judge model requires no code change.
- **F-A5** Replayable log format: binary+JSON `EvalLog` written per run, plus an `inspect score`-equivalent CLI subcommand that re-runs scorers against a prior log without re-calling the target model.
- **F-A6** Async execution with per-run limits: `max_concurrency`, `token_limit`, `time_limit`, `cost_limit`. A run exceeding any limit aborts cleanly and flags the log.
- **F-A7** Sandboxed tool execution for code/shell evals (Docker sandbox or equivalent isolation boundary).
- **F-A9** Pytest plugin: tasks discoverable as test items; non-zero exit when success criteria regress — usable as a CI gate.

### Anthropic platform integration
- **F-P1** Anthropic SDK client wired for both streaming and Batch API submission; caller chooses per run.
- **F-P2** Prompt-caching annotations on system prompt, tool definitions, and long retrieved contexts by default; cache-hit stats written to the log.
- **F-P3** Opus 4.7 support including `xhigh` thinking effort tier exposed as a config parameter; `thinking` blocks preserved across tool-use turns with signature verification (ref: [Anthropic extended thinking](https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking)).
- **F-P4** Tokenizer accounting uses Opus 4.7's updated tokenizer (1.0–1.35× input-token ratio vs. prior models) when enforcing `token_limit` / `cost_limit`; mis-accounting is a bug, not a rounding issue.
- **F-P5** Judge role swap-compatibility: Opus rubric judge and Haiku cheap judge yield the same scorer API; switching is a config change.

### Judge protocol
- **F-E1** Default judge protocol: rubric + golden answer + CoT evaluation steps, returning `{score, reason}`.
- **F-E2** Binary or small-discrete (≤5) label output is the default; judges report TPR/TNR against a calibration set, not raw agreement rate.
- **F-E3** Pairwise judge mode with automatic position-swap debiasing; the harness runs both orders and reports only debiased outcomes.

### Agent trajectory eval
- **F-B1** End-state scoring as the primary trajectory signal.
- **F-B2** All four trajectory-match modes: `strict`, `unordered`, `subset`, `superset` (ref: [AgentEvals](https://github.com/langchain-ai/agentevals)).
- **F-B3** Set-based tool-call precision/recall/F1 **and** sequence-aligned Tool Call Accuracy.
- **F-B4** Trajectory metadata in every log: step count, unnecessary-call count, retry count.
- **F-B5** Task Completion / Agent Goal Accuracy with both reference-based and reference-free variants.
- **F-B6** Benchmark adapters for τ²-bench and Terminal-Bench 2.0 (the trajectories Anthropic reports against for Opus 4.7).
- **F-B7** `thinking`-block pass-through during tool use, preserving signatures across assistant turns.

### RAG eval
- **F-C1** RAG triad scorers: Context Relevance, Faithfulness, Answer Relevance.
- **F-C2** RAGAS-compatible wrappers: Faithfulness, Response Relevancy, Context Precision, Context Recall, Factual Correctness (ref: [RAGAS](https://docs.ragas.io/)).
- **F-C3** Top-k retrieval failure rate as a standalone retrieval-only metric.
- **F-C4** Retrieval and generation scored separately; generation evaluated against both gold-context and retrieved-context variants of the same sample.
- **F-C5** Citation / attribution accuracy scorer that verifies every cited span is actually in the retrieved context.

### Code eval
- **F-D1** Test-execution-based scoring (not patch-match).
- **F-D2** pass@k using Chen et al. unbiased estimator `1 - C(n-c,k)/C(n,k)` with `n ≥ k` samples (ref: [HumanEval paper](https://arxiv.org/abs/2107.03374)).
- **F-D3** Regression-safety gate combining `FAIL_TO_PASS` and `PASS_TO_PASS` sets (SWE-bench invariant).
- **F-D4** Tiered pre-filter: lint → type-check → AST/semantic diff → run tests; cheap checks short-circuit expensive ones.
- **F-D5** Adapters for SWE-bench Verified (v2.0.3+), Terminal-Bench 2.0, and EvalPlus (HumanEval+ or MBPP+).
- **F-D6** Contamination-aware benchmark pairing: each primary benchmark ships with a contamination-resistant complement (LiveCodeBench and/or SWE-bench Pro).

## Should-Have Features (P1)

- **F-A10** Model-output cache keyed on `(prompt, model, params)` with disk backing; cache hits must be observable in the log.
- **F-B8** Trajectory-level LLM-as-judge with the `GraphTrajectory` input schema.
- **F-B9** Cost-per-task and steps-vs-optimal as first-class secondary metrics in every trajectory log.
- **F-C6** Noise Sensitivity metric for distractor robustness.
- **F-C7** Long-context vs. RAG A/B harness (same question answered from full-document context and from retrieved chunks, scores compared side-by-side).
- **F-D7** Aider polyglot benchmark adapter.

## Nice-to-Have Features

- Langfuse (self-hosted) tracing integration and FastAPI viewer for run logs.
- Postgres/pgvector-backed dataset store for RAG corpora.
- Cascade judge (cheap judge for easy cases, Opus only for disagreements).
- Prompt-compaction utilities for long trajectories.

## User Interaction Patterns

### CLI
- `trine-eval list [--tasks|--solvers|--scorers|--metrics]` — enumerate registered objects.
- `trine-eval run <task> [--solver ...] [--model ...] [--judge ...] [--batch] [--config run.yaml]` — execute an eval, write an `EvalLog`.
- `trine-eval score <log-path> [--scorer ...]` — re-score a prior log without re-running the target.
- `trine-eval view <log-path>` — render human-readable summary of a log.

### Python / YAML
- Authors write `@task` functions returning a `Task(dataset=..., solver=..., scorer=[...])`.
- Runs can be configured entirely in YAML (`task`, `model_roles`, `limits`, `sandbox`).

### Pytest / CI
- `pytest` discovers tasks; each task becomes a test item.
- Non-zero exit on regression allows direct use as a CI gate.

## Technical Constraints

- **Language / packaging:** Python ≥ 3.11, managed with `uv`.
- **Core dependencies:** `anthropic` SDK, `pydantic`, `langgraph`, `ragas`, `langfuse` (self-hosted), `fastapi` (viewer), Postgres + `pgvector`, Docker (sandbox), `pytest`.
- **Methodology constraints:** primitive convergence — all three domain evals reuse the same Task/Solver/Scorer/Metric/Log surface; no domain-specific forks of these types.
- **Harness constraints:** this product is implemented via the trine-eval three-agent harness (Planner → Generator → Evaluator). Sprint contracts in `.harness/contracts/` are the source of truth for done-ness.
- **Anthropic-specific:** Opus 4.7 pricing at $5 / $25 per M in/out tokens; tokenizer is 1.0–1.35× vs. prior models; `xhigh` effort tier exists between `high` and `max`; `thinking` signatures must be preserved across tool-use turns.

## Success Criteria

Each criterion is pass/fail and automatable.

1. **Primitives exist and are typed** — `Task`, `Sample`, `Solver`, `Scorer`, `Metric`, `EvalLog` are importable Pydantic models; instantiating each with invalid fields raises `ValidationError`.
2. **Decorator registry is complete** — `@task`, `@solver`, `@scorer`, `@metric`, `@tool` register objects retrievable via `trine-eval list`; an undecorated function is NOT discoverable.
3. **CLI `run` produces a log** — `trine-eval run <toy_task> --model claude-opus-4-7` writes an `EvalLog` file on disk containing samples, per-sample scores, and aggregated metrics.
4. **CLI `score` replays without calling target** — `trine-eval score <log>` with a network shim that errors on target-model calls succeeds and updates scores in-place (or writes a sibling file).
5. **Run limits enforced** — a run configured with `token_limit=100` on a task that would consume ≥1000 tokens aborts before completion and flags the log with `limit_exceeded=true`.
6. **Async concurrency** — `max_concurrency=N` is observable: a run with N=5 over 20 samples issues at most 5 in-flight target calls at any instant (verified via mock client timing).
7. **Sandboxed tool execution** — a malicious tool call that writes `/tmp/escape` inside the sandbox is NOT visible on the host filesystem after the run.
8. **Batch API path** — `trine-eval run <task> --batch` submits via Anthropic Message Batches and produces an identical `EvalLog` shape to the streaming path; the log records `batch_id`.
9. **Prompt caching observable** — a two-sample run with a shared 2k-token system prompt reports `cache_read_input_tokens > 0` on sample 2.
10. **Opus 4.7 `xhigh` tier reachable** — a run with `thinking.effort=xhigh` sends the correct request param and records thinking blocks (with signatures) in the log.
11. **Tokenizer accounting** — `token_limit` enforcement uses the Opus 4.7 tokenizer count, not a legacy estimate; a unit test asserts the counted value for a fixed prompt equals the SDK's reported `input_tokens` within ±1.
12. **Judge role swap** — the same scorer API produces scores with `judge=claude-opus-4-7` and `judge=claude-haiku-4-5` via config flip only; the test asserts both runs succeed and produce `Score` objects of the same schema.
13. **Judge protocol** — the default rubric judge returns `{score, reason}` with a binary or ≤5-discrete label; a free-form Likert response fails schema validation.
14. **Pairwise debiasing** — pairwise judge runs both A-vs-B and B-vs-A orders and reports only the debiased winner; single-order invocation is disallowed by the API.
15. **Trajectory match modes** — `strict`, `unordered`, `subset`, `superset` each yield deterministic pass/fail on a hand-crafted trajectory fixture with predictable results.
16. **Tool-call F1** — set-based precision/recall/F1 match values computed by hand on a 3-call vs. 4-call fixture (e.g., P=2/3, R=2/4, F1=0.571).
17. **Trajectory metadata logged** — every trajectory `EvalLog` includes `step_count`, `unnecessary_call_count`, `retry_count`.
18. **τ²-bench and Terminal-Bench adapters** — each adapter loads ≥10 samples from the upstream release and runs end-to-end against a stub solver.
19. **`thinking` pass-through** — a multi-turn tool-use trajectory preserves `thinking` block signatures across turns; a corrupted signature produces a documented error.
20. **RAG triad scorers** — Context Relevance, Faithfulness, Answer Relevance each produce a score on a fixture with a known-good and known-bad sample; known-good > known-bad.
21. **RAGAS wrappers round-trip** — Faithfulness, Response Relevancy, Context Precision, Context Recall, Factual Correctness each return scores on a fixture sample; output schemas validate.
22. **Retrieval-only metric** — top-k retrieval failure rate is computed standalone from a retrieval log without invoking a generator.
23. **Dual-context generation scoring** — for one RAG sample, the harness runs generation twice (gold context, retrieved context) and logs both scores.
24. **Citation accuracy** — a response citing a span absent from retrieved context is scored FAIL by the citation scorer; a correctly cited span is scored PASS.
25. **Code pass@k** — for `n=10, c=3, k=1` the estimator returns 0.3 ±1e-9; for `n=10, c=10, k=5` returns 1.0.
26. **SWE-bench regression gate** — a patch that makes `FAIL_TO_PASS` tests pass but breaks any `PASS_TO_PASS` test is scored FAIL by the gate scorer.
27. **Tiered pre-filter short-circuits** — a solution that fails lint never reaches test execution; the log records which tier rejected it.
28. **Code benchmark adapters** — SWE-bench Verified (≥v2.0.3), Terminal-Bench 2.0, and EvalPlus (HumanEval+ or MBPP+) each load ≥5 samples and execute end-to-end on a stub solver.
29. **Contamination-resistant complement** — configuration exposes a paired benchmark (LiveCodeBench or SWE-bench Pro) for at least one primary code benchmark; running the pair emits both scores.
30. **Pytest plugin exit code** — a task with a regressed criterion causes `pytest` to exit non-zero; a passing task exits zero.
31. **Three end-to-end evals runnable from one command each** — `trine-eval run trajectory.demo`, `trine-eval run rag.demo`, `trine-eval run code.demo` each complete and write a non-empty log.
