# Product Specification: trine-eval v0.1 — Python Library Pivot

## Context

Phase 1 (Sprints 01–05, completed 2026-04-12) upgraded the trine-eval Claude Code plugin into a mature three-agent meta-harness. The `.harness/playbook-alignment-2026-04.md` gap analysis identified 10 remaining gaps against Anthropic's 2025–2026 eval-driven development playbook, and a separate compass requirements document (`Downloads/compass_artifact_wf-6f4b7fb2-ef1b-4fcb-8a01-037702141f31_text_markdown.md`) specified what trine-eval should be **as a product**: a runnable Python eval library modelled on Inspect AI.

Phase 2 pivots: the meta-harness (existing Claude Code plugin) becomes the **build vehicle** for a new Python library (`src/trine_eval/`). The meta-harness itself receives exactly the minimum upgrades needed to produce trustworthy verdicts on the Python build — nothing more.

Full design in `C:\Users\akino\.claude\plans\c-users-akino-downloads-compass-artifac-dapper-muffin.md`.

## Product Vision

Ship trine-eval v0.1 as a Python library that proves functional correctness on one end-to-end benchmark (**SWE-bench Verified**) before any cost-optimisation pass. Surface the same primitives every serious eval framework has rediscovered — sample → solver → scorer → metric → log — specialised to the Anthropic stack with Opus 4.7 as default target, Batch API + prompt caching in v0.1, and self-hosted Langfuse for observability.

## Feature List

### Must-have (v0.1 scope)

1. **Core primitives** (A1–A5, A9) — Pydantic `Sample`/`Score`/`Task`/`EvalLog`; `@task`/`@solver`/`@scorer`/`@metric`/`@tool` decorator registry; `model_roles={target, judge}`; pytest plugin with exit-code gating.
2. **Async runner** (A6, G3) — `max_concurrency`, `token_limit`, `time_limit`, `cost_limit` hard caps; deterministic seeds; pinned model + harness versions.
3. **Replayable log format** (A5, H3–H5) — binary + JSON logs; `trine-eval score --log <path> --scorer <name>` rescores without re-running target.
4. **Docker sandbox** (A7) — per-sample container with `network=none` default, CPU/memory caps, guaranteed teardown.
5. **Anthropic integration** (F1, F2, F3, F6) — `claude-opus-4-7` default; effort tier (`low | medium | high | xhigh | max`); `interleaved-thinking-2025-05-14` beta with unmodified thinking blocks through tool round-trips; tokenizer budgets re-baselined (1.0–1.35× vs. 4.6).
6. **Prompt caching** (G1) — `cache_control` breakpoints on system prompt + tools + golden examples.
7. **Batch API** (G2) — default offline execution path; stacks with caching.
8. **LLM-as-judge** (E1, E2, E5, E6) — CoT rubric + golden answer; binary or small-discrete-label judgments with TPR/TNR (never agreement rate); bootstrap CI on aggregates; three-tier grading (code/model/human).
9. **Observability** (H1, H2, H6) — self-hosted Langfuse via docker-compose; OTel spans on every solver step, tool call, judge invocation; human annotation queue present and empty.
10. **SWE-bench Verified adapter** (D1, D2, D3, D4, D5, D6, F5) — test-execution scoring; unbiased pass@k (`1 − C(n−c,k)/C(n,k)`); `FAIL_TO_PASS` + `PASS_TO_PASS` regression gate; lint → type-check → AST-diff pre-filter; contamination screens disclosed; ±3pp of published Opus 4.7 baseline (87.6%).
11. **Token-efficiency reporting** (G4) — accuracy-per-dollar and success-per-1k-tokens alongside raw accuracy.
12. **Meta-harness prereqs** — Sprint 0 closes GAP 1 (statistical trials), GAP 3 (tasks.json schema), GAP 5 (adaptive thinking), GAP 6 (transcript capture) from playbook-alignment-2026-04.md.

### Deferred to v0.2+

τ²-bench / Terminal-Bench / MCP-Atlas adapters (B6). Entire RAG domain (C1–C7). Trajectory-level judge (B8), cost-per-task (B9). Judge cascade (G5), self-consistency reduction (G6), tool-description compaction (G7). Online production scoring (H7). Task budgets (F7). LangGraph, RAGAS, pgvector, FastAPI. Meta-harness GAPs 2, 4, 7, 8, 9, 10.

## User Interaction Patterns

- Meta-harness workflow unchanged: `/harness-sprint` drives each Phase 2 sprint through contract → build → eval → retry.
- New Python library surface: `uv run trine-eval run <task>`, `uv run trine-eval score --log ...`, `uv run trine-eval report <run>`, `uv run pytest` (via plugin).
- Langfuse UI at `localhost:3000` for trace inspection.

## Technical Constraints

- **Meta-harness** (Phase 2 Sprint 0): still pure markdown/JSON on the Claude Code plugin surface. Agents and skills under `plugins/trine-eval/`.
- **Python library** (Sprints 1–6): Python 3.12+, uv-managed, `src/trine_eval/` layout, strict mypy + ruff.
- Tech stack v0.1: `anthropic`, `pydantic`, `pytest`, `typer`, `opentelemetry`, `langfuse`, `msgpack`, Docker. **No** LangGraph, RAGAS, pgvector, FastAPI in v0.1.
- Platform: Docker Desktop + WSL2 on Windows 11 assumed. Langfuse Cloud free tier is documented SaaS fallback.
- All prior Phase 1 sprint evals remain append-only under `.harness/evals/sprint-0{1..5}*.md`. New sprints write to `.harness/evals/sprint-0{6..12}*.md`-style filenames (sprint number = Phase 2 sprint number + 5, offset to preserve audit continuity) **OR** under a `.harness/evals/phase-02/` subdirectory. Convention decided in Sprint 0.

## Success Criteria (v0.1 ship gate)

Ten verification items from the plan, all green:

1. `uv run pytest` green for core/models/runner/judge/sandbox/benchmarks.
2. `uv run ruff check` and `uv run mypy --strict src` clean.
3. Replayable log: rescore a prior log with a swapped scorer without re-hitting the Anthropic API.
4. Langfuse UI shows traces for every solver step, tool call, judge invocation.
5. Judge calibration passes on 50-item set (TPR + TNR ≥ 1.5).
6. Batch run cost ≤ 55% of streaming; cache-read rate ≥ 85% on system prompt.
7. Docker sandbox leaves zero containers after `pytest` finishes; regression gate rejects a deliberately-regressing fixture patch.
8. SWE-bench Verified 50-instance calibration: pass@1 within 84.6–90.6% (±3pp of 87.6%); harness SHA + model version recorded.
9. `trine-eval report <run>` prints accuracy-per-dollar and success-per-1k-tokens.
10. `/harness-summary` across Phase 2 sprints: pass@k/pass^k computed from **trial** data (not retry data); every failing criterion has a linked transcript.
