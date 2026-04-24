---
paths: .harness/**
---

# Harness Conventions

- Sprint contracts are the source of truth for what "done" means
- JSON files in `.harness/` use 2-space indentation
- Eval results must include specific evidence for every FAIL grade
- Never modify a prior sprint's eval results — they are append-only records
- Communication between agents happens exclusively via files in `.harness/`
- The Evaluator never sees the Generator's reasoning trace

## JSON vs Markdown: When to Use Each

The harness uses two file formats for distinct purposes:

- **JSON** — Machine-readable structured state. Use for: `config.json`, `sprints.json`, `sprint-state.json`. JSON is preferred for structured data because models are less likely to inappropriately modify it during edits. JSON files are the source of truth for sprint status, configuration, and machine-parseable results.
- **Markdown** — Human-readable prose and notes. Use for: `progress.md`, `spec.md`, sprint contracts, eval reports. Markdown is better for session logs, design rationale, and any content that benefits from rich formatting.

Both formats should be kept in sync where they overlap (e.g., sprint status appears in both `sprint-state.json` and `progress.md`). When they conflict, JSON is authoritative for structured state.

## Trial vs Retry

The harness has two independent loops that are easy to confuse — and conflating them produces statistically invalid pass@k / pass^k, because a fixed bug starts looking like evidence of inconsistency.

- **Trial** — A measurement run at **fixed code state**. Trials exist to estimate how reliable the current implementation is. Multiple trials are independent samples of the same agent doing the same task, differing only in trial-time non-determinism (model stochasticity, timing, sandbox entropy). Trials are controlled by `config.trials` (default `1`). Files: `sprint-NN-rR-tT.md`, where `T` is the trial index within round `R`. When `trials == 1`, the `-tT` suffix is omitted and the file is `sprint-NN-rR.md` (Phase 1 backward compatibility).
- **Retry** — A **bug-fix iteration**. Retries exist to let the Generator edit code in response to Evaluator feedback. Code changes between retries; trial counts do not need to. Retries are controlled by `config.max_retries`. Files: the round counter `R` increments with each retry.

Pass@k and pass^k are computed from trial files only (see `skills/harness-summary/SKILL.md`). Retry-round pass rates remain useful as a separate `first-round-pass` / retry-efficiency signal, but they are not a valid consistency metric.

## tasks.json Schema

After contract approval, `.harness/contracts/sprint-NN.md` is accompanied by a sibling `.harness/contracts/sprint-NN.tasks.json`. This is the machine-readable source of record for the sprint's criteria — Sprint 7's regression gate, Sprint 8's Batch API scheduler, Sprint 9's transcripts, and Sprint 10's adversarial hygiene flags all key off it.

Fields:

- `task_id` — Stable id. `s<NN>-c<N>` for scored success criteria, `s<NN>-sn<N>` for Should-NOT gates. Downstream tools reference tasks by this id across trials and sprints, so it must not be renamed after approval.
- `criterion` — Verbatim criterion text copied from the markdown contract. No paraphrasing.
- `grader_type` — `"deterministic"` or `"llm-judge"`.
- `weight` — Integer percentage. Success criteria carry the weights declared in the markdown contract (summing to 100%); gate criteria use `0` because they are not weighted.
- `is_gate` — `true` for Should-NOT gates, `false` otherwise.
- `verification_command` — Runnable shell command for deterministic criteria; `null` for llm-judge.
- `rubric_dimension` — Which rubric dimension this criterion informs. Used for per-dimension summary rollups.

Emission is guarded by `config.taxonomy.emit_tasks_json` (default `true`). See `skills/sprint-contract/SKILL.md` for the full specification and an example.
