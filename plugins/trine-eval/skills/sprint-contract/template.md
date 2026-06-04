# Sprint {NN} Contract: {Title}

## What I Will Build
{2-3 sentences describing the deliverable at a high level}

## Success Criteria
Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `behavioral` (execution-verified), `structural` (artifact-inspected), or `llm-judge` (reading-comprehension).
Weights must sum to 100% across all success criteria.

**Behavioral coverage:** Behavioral criteria must hold **≥ 60% of total weight**. If a sprint genuinely has no behavioral surface (e.g., it produces only static documentation or a config schema with no runtime), state the reason explicitly in `## Technical Notes` so the Evaluator can verify the exception during CONTRACT_REVIEW.

**Converting structural criteria to behavioral.** A structural criterion proves a string exists in a file. A behavioral criterion proves the feature works when invoked. Prefer behavioral wherever the artifact can be run:

| Structural (weak) | Behavioral (strong) |
|---|---|
| `grep -c '"event":' hooks/hooks.json >= 3` | Trigger the SessionStart hook with a stubbed event and verify `sprint-state.json` `last_updated` changed within 5s of the trigger |
| `grep -ci 'feature_list\|sprint-state' skills/harness-kickoff/SKILL.md >= 1` | Run `/harness-kickoff` against a fresh fixture spec; assert `.harness/sprint-state.json` is created and conforms to the documented schema |
| `grep -c 'def evaluate' src/eval.py >= 1` | Invoke `evaluate(sample_input)` and assert the returned `EvalResult` has `passed=True` for the canonical positive case and `passed=False` for the canonical negative case |

### Behavioral (execution-verified)
Verified by *running* the artifact (invoking a skill, triggering a hook, executing the built binary, calling the library function) and observing the output, state change, or side effect. The "How to verify" must specify the command(s) to run AND the observable result to check.

1. {Criterion}: {Command(s) to run, then observable result to check} [weight: N%]
2. {Criterion}: {Command(s) to run, then observable result to check} [weight: N%]

### Structural (artifact-inspected)
Verified by inspecting an artifact at rest (grep, jq, schema check, file existence, frontmatter field). Use for cheap pre-flight checks that gate a behavioral criterion, or for genuinely static artifacts (config schemas, documentation presence).

3. {Criterion}: {How to verify — specific command, URL, or check} [weight: N%]

### LLM-as-judge (reading-comprehension)
Subjective quality assessment that no command can capture.

4. {Criterion}: {What to check and what constitutes PASS} [weight: N%]
5. {Criterion}: {What to check and what constitutes PASS} [weight: N%]

## Should-NOT Criteria
Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. {Behavior that should not happen}: {How to verify absence}

## Edge Case Criteria
Optional. Edge case criteria are a third class of criterion, distinct from the 100%-weighted Success Criteria above and from the Should-NOT gates. They test behavior on ambiguous, boundary, or adversarial inputs (empty inputs, very large inputs, concurrent requests, malformed payloads, queries with no matches) and are tracked separately as an **edge-case pass rate** metric in `harness-summary` — they do NOT carry weights and do NOT count toward the weighted total. Omit this section entirely when not applicable; including it is most valuable for `web-app`, `api-service`, and `rag-system` rubrics. See `skills/sprint-contract/SKILL.md` for the rationale (why separate, why optional, why per-rubric guidance).

1. {Edge-case behavior to test}: {What to check and what constitutes PASS}

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
