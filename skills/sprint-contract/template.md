# Sprint {NN} Contract: {Title}

## What I Will Build
{2-3 sentences describing the deliverable at a high level}

## Success Criteria
Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `deterministic` (code-verifiable) or `llm-judge` (requires reading comprehension).
Weights must sum to 100% across all success criteria.

### Deterministic (code-verifiable)
1. {Criterion}: {How to verify — specific command, URL, or check} [weight: N%]
2. {Criterion}: {How to verify} [weight: N%]
3. {Criterion}: {How to verify} [weight: N%]

### LLM-as-judge (requires reading comprehension)
4. {Criterion}: {What to check and what constitutes PASS} [weight: N%]
5. {Criterion}: {What to check and what constitutes PASS} [weight: N%]

## Should-NOT Criteria
Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. {Behavior that should not happen}: {How to verify absence}

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
