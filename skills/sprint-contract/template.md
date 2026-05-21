# Sprint {NN} Contract: {Title}

## What I Will Build
{2-3 sentences describing the deliverable at a high level}

## Success Criteria
Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `deterministic` (code-verifiable) or `llm-judge` (requires reading comprehension).
Weights must sum to 100% across all success criteria.

**Bucket discipline (mandatory).** Every criterion belongs to one of three buckets defined in [`rules/harness-conventions.md`](rules/harness-conventions.md) → "Three Buckets of Verification". Briefly:

- **Bucket 1 — structural / presence.** `grep -q "X" file.md`, `assert key in dict`, `[ -f path ]`. Verifies plumbing. Acceptable only for pure-plumbing deliverables (config keys, conventions, documentation that must exist verbatim).
- **Bucket 2 — behavioral with mocks.** Asserts on observable outcomes — return values, exit codes, raised exceptions, written files — given stubbed dependencies. *This is the default bucket for nearly every behavioral deliverable.* For harness-side deliverables (skill prose, agent instructions), bucket 2 is achieved via subagent-driven verification (spawn a real subagent, assert on its output — no separate API key needed).
- **Bucket 3 — behavioral against real systems.** Real Docker, real Anthropic API, real subagent integration. Catches integration drift the mocked test can't.

Tag each criterion's bucket inline (e.g., `[weight: N%, bucket: 2]`). A sprint that's 100% bucket 1 cannot pass — the `Functional Integration Coverage` rubric dimension blocks at 1/5. See the rubric for the full bucket → score mapping. The Authoring Checklist's "bucket discipline trap" (Trap #6 in `skills/sprint-contract/SKILL.md`) walks through how to re-author a bucket-1 criterion as bucket 2.

### Deterministic (code-verifiable)
1. {Criterion}: {How to verify — specific command, URL, or check} [weight: N%, bucket: 2]
2. {Criterion}: {How to verify} [weight: N%, bucket: 2]
3. {Plumbing-only criterion}: {presence check} [weight: N%, bucket: 1]

### LLM-as-judge (requires reading comprehension)
4. {Criterion}: {What to check and what constitutes PASS} [weight: N%, bucket: 2]
5. {Criterion}: {What to check and what constitutes PASS} [weight: N%, bucket: 2]

## Should-NOT Criteria
Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. {Behavior that should not happen}: {How to verify absence}

## Edge Case Criteria
Optional. Edge case criteria are a third class of criterion, distinct from the 100%-weighted Success Criteria above and from the Should-NOT gates. They test behavior on ambiguous, boundary, or adversarial inputs (empty inputs, very large inputs, concurrent requests, malformed payloads, queries with no matches) and are tracked separately as an **edge-case pass rate** metric in `harness-summary` — they do NOT carry weights and do NOT count toward the weighted total. Omit this section entirely when not applicable; including it is most valuable for `web-app`, `api-service`, and `rag-system` rubrics. See `skills/sprint-contract/SKILL.md` for the rationale (why separate, why optional, why per-rubric guidance).

1. {Edge-case behavior to test}: {What to check and what constitutes PASS}

## Functional Smoke
Optional. Functional Smoke criteria are a fourth class of criterion, complementary to the architectural mocked tests in Success Criteria. They exercise the deliverable against **real external systems** (live Anthropic API, real Docker, real filesystem, real judge model) to validate that code which passes the mocked tests also functions end-to-end. They are tracked separately as a **functional smoke pass rate** metric in `harness-summary` and inform the `Functional Integration Coverage` rubric dimension; they do NOT carry weights and do NOT count toward the 100% weighted total. Omit this section entirely when no live check fits the sprint (pure-refactor or documentation sprints commonly omit it).

Each entry should declare:
- **Criterion** — what behavior the smoke test validates end-to-end.
- **Real system** — Anthropic API / Docker / filesystem / judge model / etc.
- **Env-var gate** — `TRINE_EVAL_LIVE_API=1` (Anthropic), `TRINE_EVAL_LIVE_DOCKER=1` (Docker), etc. CI default skips when unset.
- **Measured signal** — the observable that distinguishes "code works against the real system" from "code returns the right shape" (e.g., second-call `cache_read_input_tokens > 0`; container exits 0 *and* leaves no leftover container per `docker ps`).
- **Cost reference** — for paid systems, the per-run cost in USD. Combined sprint cost must stay under the `functional_smoke.budget_usd` cap in `.harness/config.json` (currently $1.00/sprint).

Example:
1. {Caching produces real cache hit}: Anthropic API, gate `TRINE_EVAL_LIVE_API=1`, signal `response.usage.cache_read_input_tokens > 0` on second call, cost ~$0.02.

## Reference Solutions
Optional. Provide known-working outputs for criteria where grader calibration is valuable.
Especially useful for LLM-as-judge criteria to reduce inter-judge disagreement.

**Criterion {N}:**
```
{Example of a correct output or expected state}
```

## Out of Scope
{Explicitly list things that might be assumed but are NOT included in this sprint}

## Technical Notes
{Design decisions, constraints, or dependencies relevant to evaluation}

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/sprint-{NN}.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — both Success Criteria and Should-NOT gates — with stable `task_id`s, `grader_type`, `weight`, `is_gate`, `verification_command`, and `rubric_dimension`. Downstream sprints (regression gate, Batch API, transcript capture, adversarial hygiene) consume that JSON; this markdown contract remains the human-readable source of truth. See `skills/sprint-contract/SKILL.md` for the schema.
