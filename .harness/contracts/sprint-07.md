# Sprint 07 Contract: Capability/Regression Dual-Track

## What I Will Build

Close Gap 4 (regression gate) from the playbook alignment plan: turn today's prose-only "recommend graduation" behavior in harness-summary into a real regression test suite that blocks new sprints on regression failure. Introduce `.harness/regression/regression.json` as an append-only graduation output whose entries are copied verbatim from `sprint-NN.tasks.json` (Sprint 6's task taxonomy is the source record). Add a Step 0.5 Regression Gate to the sprint workflow that runs every graduated criterion's `verification_command` before contract negotiation — any failure aborts the sprint and records the broken criteria. Add `config.regression.enabled` and `config.regression.fail_fast` with defaults that reproduce Phase 1 behavior when `regression.json` does not exist.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **config.json schema extended with regression fields**: `.harness/config.json` contains a `regression` object with keys `enabled` (boolean) and `fail_fast` (boolean). Values may be literal booleans or `null` (to signal "use default"). Verify via `jq -e '.regression.enabled != null and .regression.fail_fast != null' .harness/config.json || jq -e '.regression | has("enabled") and has("fail_fast")' .harness/config.json`. [weight: 7%]

2. **.harness/regression/ directory and README exist**: The path `.harness/regression/` exists as a directory, contains a `regression.json` file that is valid JSON with a top-level `tasks` array (may be empty on initialization), and contains a `README.md` explaining what the directory is for. Verify via `test -d .harness/regression && jq -e '.tasks | type == "array"' .harness/regression/regression.json && test -f .harness/regression/README.md`. [weight: 7%]

3. **regression.json entries match the tasks.json schema**: Every entry in `.harness/regression/regression.json`'s `tasks` array (when non-empty) contains the fields `task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`, plus one Sprint-7-added field `graduated_from_sprint` (integer). Verify via `jq -e '.tasks | all(has("task_id") and has("criterion") and has("grader_type") and has("weight") and has("is_gate") and has("verification_command") and has("rubric_dimension") and has("graduated_from_sprint"))' .harness/regression/regression.json`. An empty `tasks` array passes vacuously. [weight: 7%]

4. **harness-sprint SKILL contains a Step 0.5 Regression Gate section**: `skills/harness-sprint/SKILL.md` contains a heading whose text matches `Step 0.5` and includes the word `Regression` (case-insensitive). The section must be positioned between Step 0 (Determine Which Sprint to Run) and Step 1 (Contract Negotiation). Verify via `grep -nE '^## Step 0\.5' skills/harness-sprint/SKILL.md | grep -i regression`. [weight: 10%]

5. **Step 0.5 reads regression.json and runs each verification_command**: The Step 0.5 section in `skills/harness-sprint/SKILL.md` explicitly references (a) the path `.harness/regression/regression.json`, (b) iterating the `tasks` array and executing each task's `verification_command`, (c) aborting the sprint when any verification_command fails and `regression.fail_fast` is true, (d) writing a timestamped results file under `.harness/regression/runs/`. Verify via `grep -q 'regression/regression.json' skills/harness-sprint/SKILL.md && grep -q 'verification_command' skills/harness-sprint/SKILL.md && grep -q 'fail_fast' skills/harness-sprint/SKILL.md && grep -q 'regression/runs' skills/harness-sprint/SKILL.md`. [weight: 10%]

6. **harness-summary writes graduated criteria into regression.json**: `skills/harness-summary/SKILL.md` documents that saturated criteria (first-round-pass for 3+ consecutive sprints) are **appended** to `.harness/regression/regression.json` as machine-readable entries, not merely listed as recommendations in the summary markdown. The SKILL must also state that graduation is append-only — existing entries are never removed or rewritten. Verify via `grep -q '\.harness/regression/regression.json' skills/harness-summary/SKILL.md && grep -qiE 'append|graduat' skills/harness-summary/SKILL.md`. [weight: 12%]

7. **evaluator.md notes thinking effort for regression vs capability**: `agents/evaluator.md` contains a note (or section) stating that regression-criterion evaluation uses a lower thinking effort (e.g. `medium` — speed-oriented, since graduated criteria are already calibrated) while fresh capability-criterion evaluation uses a higher effort (`high` or `max` — thoroughness-oriented). This lands the wiring point consumed by Sprint 8. Verify via `grep -qi 'regression' agents/evaluator.md && grep -qiE 'effort|thinking' agents/evaluator.md && grep -qiE 'medium' agents/evaluator.md && grep -qiE 'high|max' agents/evaluator.md`. [weight: 7%]

8. **harness-conventions.md documents the regression.json schema**: `rules/harness-conventions.md` contains a section describing `regression.json` — its role (append-only graduation output), its schema (the same fields as `tasks.json` plus `graduated_from_sprint`), and the gate semantics (Step 0.5 runs every entry before contract negotiation; failure aborts the sprint when `fail_fast` is true). Verify via `grep -q 'regression.json' rules/harness-conventions.md && grep -q 'graduated_from_sprint' rules/harness-conventions.md && grep -qi 'append-only\|append only' rules/harness-conventions.md`. [weight: 8%]

9. **sprint-07.tasks.json is emitted**: A file `.harness/contracts/sprint-07.tasks.json` exists, is valid JSON, has a top-level `sprint: 7` field and a `tasks` array with one entry per criterion in this contract (including gate criteria with `is_gate: true, weight: 0`). Each entry has the Sprint 6 schema fields. Verify via `jq -e '.sprint == 7 and (.tasks | length) >= 12 and (.tasks | all(has("task_id") and has("grader_type") and has("weight") and has("is_gate")))' .harness/contracts/sprint-07.tasks.json`. [weight: 7%]

### LLM-as-judge (requires reading comprehension)

10. **Backward compatibility is explicit and correct**: The updated `skills/harness-sprint/SKILL.md` Step 0.5 section, when read by a reasonable reader, makes it unambiguous that a project whose `.harness/regression/regression.json` does not exist — or whose `tasks` array is empty — experiences no behavior change from Phase 1: no regression command is run, no abort condition is triggered, and the sprint proceeds directly to Step 1. The config knobs `regression.enabled` and `regression.fail_fast` must each have a documented default (either stated default value or an "if absent" clause) such that a `config.json` lacking the `regression` object produces Phase-1 behavior. [weight: 10%]

11. **Regression graduation semantics are clear**: A reader of the updated `skills/harness-summary/SKILL.md` saturation section should be able to explain: (a) the exact graduation trigger (first-round-pass for 3+ consecutive sprints), (b) which fields from `tasks.json` are copied into `regression.json` and which fields are added (`graduated_from_sprint`), (c) why graduation is append-only — so the regression suite only grows and historical coverage cannot be lost by a buggy summary run. [weight: 6%]

12. **Fail-fast rationale is justified, not just asserted**: The `skills/harness-sprint/SKILL.md` Step 0.5 section should explain (not merely state) why regression failure must abort before contract negotiation, rather than continuing as a warning. A reader should come away understanding that running a new sprint while a graduated capability is broken produces misleading eval scores — the sprint may pass its own new criteria while the system has regressed on prior capability — and that the sprint's metrics would therefore overstate system health. [weight: 5%]

13. **Regression is positioned as the output of saturation, not a parallel system**: The documentation (across `skills/harness-summary/SKILL.md` and `rules/harness-conventions.md`) should make clear that `regression.json` is the downstream product of the existing saturation detection logic — not a new hand-curated list — and that the Sprint 6 `tasks.json` schema is the direct source of record. A reader should understand that there is one pipeline: sprint contracts → tasks.json → saturation detection → regression.json → Step 0.5 gate. [weight: 4%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **No silent behavior change for pre-Phase-2 configs**: A project whose `.harness/config.json` lacks the `regression` object and whose repository has no `.harness/regression/regression.json` file must run the harness identically to Phase 1: no Step 0.5 execution, no abort, no regression runs directory created. Verify by reading the updated workflow SKILL and confirming every new action in Step 0.5 is explicitly guarded on either the `regression.json` file existing or `config.regression.enabled` being truthy — never unconditionally executed.

2. **No modification of prior sprint artifacts**: `.harness/evals/sprint-0[1-6]*` and `.harness/contracts/sprint-0[1-6]*` must be unchanged from HEAD at the start of this sprint (append-only rule from `rules/harness-conventions.md`). Verify via `git diff HEAD -- .harness/evals/sprint-0[1-6]* .harness/contracts/sprint-0[1-6]*` producing empty diff.

3. **No ad-hoc regression commands — only tasks.json verification commands execute**: The Step 0.5 regression gate must not invent or paraphrase verification commands. It must run, verbatim, the `verification_command` string recorded on each task in `regression.json`. This preserves the audit chain (a graduated criterion's PASS evidence in the regression suite matches the evidence that justified graduation). Verify by reading `skills/harness-sprint/SKILL.md` Step 0.5 — the command execution step must reference `task.verification_command` (or equivalent) as the exact source, not a reconstructed command.

## Reference Solutions

**Criterion 6 (harness-summary writes into regression.json) — example of the added logic:**

```markdown
### Saturation & Regression Graduation

When a criterion passes in the first evaluation round across 3 or more consecutive
sprints, append it to `.harness/regression/regression.json` by copying its entry
from the producing sprint's `tasks.json` and adding `graduated_from_sprint: <NN>`.
Graduation is append-only: existing entries are never removed or rewritten.
```

**Criterion 4 & 5 (Step 0.5 Regression Gate) — example of the added workflow section:**

```markdown
## Step 0.5: Regression Gate

Before proposing a new sprint contract, run the graduated regression suite so a
regression is never masked by a green eval on the new sprint's criteria.

1. If `.harness/regression/regression.json` does not exist, skip this step entirely
   (Phase 1 behavior).
2. If `config.regression.enabled` is explicitly `false`, skip this step.
3. Otherwise, for each entry in `regression.json`'s `tasks` array:
   a. Execute `task.verification_command` verbatim (do not paraphrase or reconstruct).
   b. Record PASS (exit 0) or FAIL (non-zero exit) plus stdout/stderr.
4. Write aggregate results to `.harness/regression/runs/run-<UTC-ISO8601>.json`.
5. If any regression task failed AND `config.regression.fail_fast` is true
   (default `true`), abort the sprint. Print the failing `task_id`s and their
   `graduated_from_sprint` origin so the user knows which capability regressed.
```

**Criterion 3 (regression.json schema) — example of a well-formed entry:**

```json
{
  "tasks": [
    {
      "task_id": "s02-c4",
      "criterion": "Evaluator agent enforces environment isolation between trial runs",
      "grader_type": "deterministic",
      "weight": 10,
      "is_gate": false,
      "verification_command": "grep -q 'Environment Isolation' agents/evaluator.md",
      "rubric_dimension": "generator_evaluator_separation",
      "graduated_from_sprint": 5
    }
  ]
}
```

## Out of Scope

- Actually triggering a regression abort against a real broken capability in this sprint's own evaluation. The plumbing and documentation ship here; end-to-end regression-abort verification happens on a synthetic follow-up sprint per the gap-closure-plan Verification item 2.
- Populating `regression.json` with historical Sprint 1–6 saturated criteria retroactively. Graduation applies going forward — Sprint 7 initializes the file with an empty `tasks` array, and Sprint 8+ evaluator runs produce the first real graduations through harness-summary.
- The adaptive-thinking frontmatter on agents (Sprint 8). Sprint 7 only notes in `evaluator.md` that regression evaluation *should* run at `medium` effort and capability evaluation at `high`/`max` — the actual frontmatter declarations land in Sprint 8.
- Batch API wiring for regression runs (Sprint 8), transcript capture of regression runs (Sprint 9), Playwright invocation (Sprint 10).

## Technical Notes

- **Regression gate runs before contract negotiation, not after.** Running after the eval would let a broken capability slip through the current sprint's evaluation — the new sprint's criteria would grade PASS on fresh work while a graduated capability silently regressed. Running before contract negotiation means the sprint cannot even begin negotiating new criteria until existing capability is verified intact.
- **The `graduated_from_sprint` field** is Sprint 7's only schema addition on top of `tasks.json`. It preserves the audit trail: readers of `regression.json` can trace any entry back to the sprint whose eval first demonstrated saturation.
- **Append-only graduation** is intentional. If a buggy summary run rewrote `regression.json`, historical regression coverage would be lost. Operators who want to retire a regression criterion do so by editing the file by hand, outside the harness — the harness never removes entries programmatically.
- **Config defaults**: when the `regression` object is absent from `.harness/config.json`, treat `enabled` as "auto" (true iff `regression.json` exists with a non-empty `tasks` array) and `fail_fast` as `true`. These defaults reproduce Phase 1 behavior for projects that never graduate a criterion.
- **Forward wiring to Sprint 8**: the `evaluator.md` note establishing that regression uses `effort: medium` while capability uses `effort: high`/`max` is the exact hook Sprint 8 will consume when it adds the `thinking` frontmatter. Keeping the policy text here — rather than waiting for Sprint 8 — means the two sprints can land in either order.

## Evaluator Review

**Status: APPROVED**

### Feedback

The contract is testable, specific, and weight-valid. Deterministic criteria all cite concrete grep/jq commands with patterns that match the reference-solution examples; LLM-judge criteria (10–13) anchor on identifiable claims a reader must be able to extract from the docs. Schema changes extend Sprint 6's `tasks.json` without renaming any field — only `graduated_from_sprint` is added, which matches the gap-closure plan.

Non-blocking notes the Generator should keep in mind during implementation:

- **Criterion 1 fallback logic is internally consistent but worth understanding:** the verification command accepts both explicit booleans and a `regression` object with null values. However, if the harness's own `.harness/config.json` were to omit the `regression` object entirely, both branches fail. This is fine because Sprint 7 is updating the harness's config to include the object — but it means the Generator must actually add the `regression` key to `.harness/config.json`, not rely on the "absent = defaults" path that Criterion 10 / SN1 cover for external pre-Phase-2 projects. The two coexist: the harness config must declare the object; external configs that lack it must still run. Make sure both hold.
- **Criterion 4 grep is strict about header placement:** `grep -nE '^## Step 0\.5' | grep -i regression` requires "regression" on the same line as the `## Step 0.5` header. Use a heading like `## Step 0.5: Regression Gate` (exactly as in the reference solution) — a heading that only says `## Step 0.5` with the word "Regression" on a following line would false-negative.
- **Criterion 7 is satisfiable with a single short paragraph** (it only greps for `regression`, `effort|thinking`, `medium`, `high|max`). That is appropriate scope for Sprint 7 — the real frontmatter lands in Sprint 8 — but be explicit in the prose that the values are policy-only until Sprint 8 wires them, so a future evaluator reading the note does not expect to find frontmatter yet.
- **Criterion 8 grep `'append-only\|append only'`** relies on GNU grep's BRE alternation. All current harness environments use GNU grep, so acceptable. No change required.
- **SN3 ("no ad-hoc regression commands")** is a documentation-reading check — the criterion states "Verify by reading `skills/harness-sprint/SKILL.md` Step 0.5 — the command execution step must reference `task.verification_command`". This is effectively an llm-judge gate even though the contract does not tag it as such. The tasks.json emission for Sprint 7 should mark SN3 as `grader_type: "llm-judge"` (consistent with Sprint 6's SN1/SN2 precedent).

### Missing Criteria

None. Every file-to-modify line in the gap-closure plan's Sprint 7 section maps to at least one criterion:

- `.harness/regression/` dir + `regression.json` + `README.md` → Criterion 2
- `regression.json` schema → Criterion 3
- `skills/harness-summary/SKILL.md` graduation writer → Criterion 6
- `skills/harness-sprint/SKILL.md` Step 0.5 → Criteria 4, 5
- `.harness/config.json` regression fields → Criterion 1
- `agents/evaluator.md` effort note → Criterion 7

Bonus coverage beyond the plan (`rules/harness-conventions.md` schema documentation via Criterion 8, and `sprint-07.tasks.json` emission via Criterion 9) is correct scope and inherited directly from the Sprint 6 taxonomy protocol.

### Approved Criteria

1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 — all approved. Should-NOT gates SN1, SN2, SN3 all testable and defensible.

### Contract Quality Notes

- **Weight distribution:** 7+7+7+10+10+12+7+8+7+10+6+5+4 = 100%. Verified. The highest single weight (12% on Criterion 6) correctly sits on the graduation writer — the mechanism that converts saturation detection into a real regression suite, which is the sprint's raison d'être. No single criterion dominates.
- **Reference solutions:** present for the three highest-stakes criteria (3 schema, 4/5 workflow, 6 graduation writer). The workflow Step 0.5 example includes both the guard conditions (skip if file absent, skip if `regression.enabled == false`) and the abort logic — this gives a round-2 evaluator zero ambiguity on what constitutes a complete Step 0.5 implementation.
- **Scope boundaries:** Out-of-Scope correctly defers adaptive-thinking frontmatter (Sprint 8), transcript capture (Sprint 9), Playwright / edge-case (Sprint 10), retroactive historical graduation, and end-to-end regression-abort verification (synthetic follow-up per gap-closure-plan Verification item 2). No scope creep.
- **Backward-compat alignment:** Criterion 10, SN1, and Technical Notes' "Config defaults" paragraph all converge on the same rule — missing `regression` object + missing `regression.json` → Phase-1 behavior. This matches `spec.md`'s Phase 2 technical constraint that pre-Phase-2 configs "must continue to execute exactly as it did before."
- **Append-only semantics:** explicitly stated in Criterion 6, Criterion 11, Criterion 8 (schema documentation), and Technical Notes — four-way consistency, which is what a would-be-destructive operation like "rewrite regression.json" deserves. Good.
