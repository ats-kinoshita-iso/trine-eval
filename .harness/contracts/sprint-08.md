# Sprint 08 Contract: Claude 4.6 Adaptive Thinking and Batch API

## What I Will Build

Close Gap 5 (adaptive thinking) and Gap 7 (Batch API) from the playbook alignment plan. Wire `thinking: { type: adaptive, effort: ... }` frontmatter onto every agent and the analysis-heavy `harness-summary` skill, tuned to role: `medium` for planning and implementation, `high` for capability evaluation, `medium` for regression evaluation (consuming the wiring point Sprint 7 left in `agents/evaluator.md`), and `max` for contract review and summary analysis. Expose a `config.thinking.profile` knob (`"default" | "fast" | "thorough"`) so users can override agent-level effort without editing files. Add a Batch API mode to the evaluation step: when `config.batch.enabled` is true and a sprint's criterion count meets `config.batch.min_criteria`, route eval criterion verifications through Anthropic's Batch API for the documented 50% discount and 24-hour SLA, with per-criterion result shape preserved. Add `batch.enabled` (default `false`) and `batch.min_criteria` (default `20`) to `.harness/config.json`. Update `README.md` to document the new knobs. All new config fields default to current behavior — projects whose `.harness/config.json` lacks `thinking` and `batch` execute exactly as before.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **Planner agent declares adaptive thinking frontmatter at effort `medium`**: `agents/planner.md`'s YAML frontmatter (the block delimited by the first two `---` lines at the top of the file) declares a `thinking` key as a single-line YAML mapping in the form `thinking: { type: adaptive, effort: medium }` (inline format — required so the verification command's single-line grep matches). Verify via `awk 'BEGIN{c=0} /^---$/{c++; if (c==2) exit; next} c==1' agents/planner.md | grep -qE 'thinking:.*type:.*adaptive.*effort:.*medium'`. [weight: 6%]

2. **Generator agent declares adaptive thinking frontmatter at effort `medium`**: `agents/generator.md`'s YAML frontmatter declares a `thinking` key as a single-line YAML mapping in the form `thinking: { type: adaptive, effort: medium }` (inline format; this is the default effort for IMPLEMENTATION mode — per-mode overrides for CONTRACT_PROPOSAL / CONTRACT_REVISION / IMPLEMENTATION are described in the body). Verify via `awk 'BEGIN{c=0} /^---$/{c++; if (c==2) exit; next} c==1' agents/generator.md | grep -qE 'thinking:.*type:.*adaptive.*effort:.*medium'`. [weight: 6%]

3. **Evaluator agent declares adaptive thinking frontmatter at effort `high`**: `agents/evaluator.md`'s YAML frontmatter declares a `thinking` key as a single-line YAML mapping in the form `thinking: { type: adaptive, effort: high }` (inline format; this is the default for capability EVALUATION mode — CONTRACT_REVIEW uses `max` and regression-criterion evaluation uses `medium` per the policy section already in the body). Verify via `awk 'BEGIN{c=0} /^---$/{c++; if (c==2) exit; next} c==1' agents/evaluator.md | grep -qE 'thinking:.*type:.*adaptive.*effort:.*high'`. [weight: 10%]

4. **Evaluator body documents per-mode effort overrides and removes "policy-only" disclaimer**: `agents/evaluator.md`'s "Thinking Effort: Regression vs Capability Evaluation" section explicitly names the three effort levels (`medium`, `high`, `max`) and ties each to a mode (regression eval / capability eval / contract review). The Sprint-7 disclaimer text ("This is a policy-only section until Sprint 8" or "Current agent frontmatter does not yet declare") must be removed or rewritten to reflect that the frontmatter now exists. Verify via `grep -qiE 'medium' agents/evaluator.md && grep -qiE 'high' agents/evaluator.md && grep -qiE 'max' agents/evaluator.md && ! grep -q 'policy-only section until Sprint 8' agents/evaluator.md && ! grep -q 'does not yet declare' agents/evaluator.md`. [weight: 8%]

5. **harness-summary skill declares adaptive thinking at effort `max`**: `skills/harness-summary/SKILL.md`'s YAML frontmatter (the block delimited by the first two `---` lines) declares a `thinking` key as a single-line YAML mapping in the form `thinking: { type: adaptive, effort: max }` (inline format; analysis-heavy). Verify via `awk 'BEGIN{c=0} /^---$/{c++; if (c==2) exit; next} c==1' skills/harness-summary/SKILL.md | grep -qE 'thinking:.*type:.*adaptive.*effort:.*max'`. [weight: 6%]

6. **config.json declares `thinking.profile` field**: `.harness/config.json` contains a top-level `thinking` object with a `profile` key whose value is one of the strings `"default"`, `"fast"`, or `"thorough"`. The default value is `"default"` (matches today's behavior). Verify via `jq -e '.thinking.profile | IN("default","fast","thorough")' .harness/config.json`. [weight: 6%]

7. **config.json declares `batch.enabled` and `batch.min_criteria` fields**: `.harness/config.json` contains a top-level `batch` object with keys `enabled` (boolean, default `false`) and `min_criteria` (integer, default `20`). Verify via `jq -e '.batch.enabled == false and (.batch.min_criteria | type == "number") and .batch.min_criteria == 20' .harness/config.json`. [weight: 6%]

8. **harness-sprint SKILL contains a Batch API section in Step 3**: `skills/harness-sprint/SKILL.md` contains a section (heading or labeled subsection inside Step 3 Evaluation) titled with the words "Batch API" (case-insensitive). The section must explicitly reference `config.batch.enabled`, `config.batch.min_criteria`, the trigger rule (enabled AND criterion count meets `min_criteria`), and the documented 50% discount and 24-hour SLA. Verify via `grep -qiE 'batch.api' skills/harness-sprint/SKILL.md && grep -q 'batch.enabled' skills/harness-sprint/SKILL.md && grep -q 'batch.min_criteria' skills/harness-sprint/SKILL.md && grep -qiE '50%|fifty percent' skills/harness-sprint/SKILL.md && grep -qiE '24.hour|twenty.four' skills/harness-sprint/SKILL.md`. [weight: 10%]

9. **README documents new config knobs**: `README.md` documents both the `thinking.profile` config knob (each of its three valid values appears verbatim somewhere in the file — they may be on separate lines, e.g. as bullets) and the `batch.enabled` / `batch.min_criteria` config knobs (with the discount/SLA tradeoff). Verify via `grep -q 'thinking.profile' README.md && grep -q '"default"' README.md && grep -q '"fast"' README.md && grep -q '"thorough"' README.md && grep -q 'batch.enabled' README.md && grep -q 'batch.min_criteria' README.md`. [weight: 5%]

10. **sprint-08.tasks.json is emitted**: A file `.harness/contracts/sprint-08.tasks.json` exists, is valid JSON, has a top-level `sprint: 8` field and a `tasks` array with one entry per criterion in this contract — 13 success criteria + 3 Should-NOT gates = **16 entries** — each with the Sprint-6 schema fields `task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`. Verify via `jq -e '.sprint == 8 and (.tasks | length) >= 16 and (.tasks | all(has("task_id") and has("grader_type") and has("weight") and has("is_gate")))' .harness/contracts/sprint-08.tasks.json`. [weight: 6%]

### LLM-as-judge (requires reading comprehension)

11. **Backward compatibility is explicit and correct**: The updated `README.md`, `skills/harness-sprint/SKILL.md`, and the agent files together must make it unambiguous that a project whose `.harness/config.json` predates Phase 2 (no `thinking` object, no `batch` object) experiences no behavior change: the agent frontmatter declares effort levels but those declarations do not gate execution, the `thinking.profile` default `"default"` reproduces today's behavior, and `batch.enabled: false` (the default) means evaluations remain synchronous. A reader should be able to identify, for each new config field, the default value and the sentence that confirms it preserves Phase-1 behavior. [weight: 12%]

12. **Per-role thinking effort rationale is justified, not just asserted**: The documentation (across the agent files and `agents/evaluator.md`'s "Thinking Effort" section) should explain *why* each role gets the effort level it does — not merely state the value. A reader should come away understanding that planner/generator use `medium` because routine planning and implementation do not benefit from deep reasoning relative to its cost; the evaluator capability mode uses `high` because new criteria are open-ended and the "talk yourself out of it" bias warrants thoroughness; contract review and summary analysis use `max` because a missed hole in either propagates across the whole sprint or all sprints; and regression-criterion evaluation uses `medium` because graduated criteria are pre-calibrated and the gate runs before every sprint, so speed matters. [weight: 10%]

13. **Batch API trigger condition, payoff, and result shape are well-defined**: The `skills/harness-sprint/SKILL.md` Batch API section must (a) state the precise trigger — the batch path activates only when `config.batch.enabled == true` AND the sprint's criterion count is greater than or equal to `config.batch.min_criteria`, otherwise the synchronous path runs; (b) document the payoff — Anthropic's Batch API offers a 50% discount on input/output tokens at the cost of a 24-hour SLA; (c) state that per-criterion result shape (the `## N. Criterion ...` blocks in `sprint-NN-rR.md`) is preserved when batched, so downstream consumers (regression gate, harness-summary) cannot tell whether a batch or synchronous path produced the file. [weight: 9%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **No silent behavior change for pre-Phase-2 configs**: A project whose `.harness/config.json` lacks the `thinking` object and the `batch` object must run the harness identically to Phase 1: agent effort defaults to whatever the runtime would do without frontmatter (no override applied), no batch submission is attempted, and the evaluator runs every criterion synchronously as today. Verify by reading the updated workflow and agent files — every new behavior tied to `thinking.profile` or `batch.enabled` must be explicitly guarded on a config lookup with a default that matches Phase 1.

2. **No modification of prior sprint artifacts**: `.harness/evals/sprint-0[1-7]*` and `.harness/contracts/sprint-0[1-7]*` must be unchanged from HEAD at the start of this sprint (append-only rule from `rules/harness-conventions.md`). Verify via `test -z "$(git diff HEAD -- .harness/evals/sprint-0[1-7]* .harness/contracts/sprint-0[1-7]*)"`.

3. **No invented Batch API semantics that contradict Anthropic's published contract**: The Batch API section must not claim discount or SLA values that diverge from Anthropic's documented Batch API behavior (50% discount, 24-hour SLA). It must also not assert that batched calls return results faster than synchronous calls — the tradeoff is cost for latency. Verify by reading the Batch API section: if the prose contradicts the documented 50%/24-hour values or claims a latency improvement, this gate fails.

## Reference Solutions

**Criterion 1 (Planner thinking frontmatter) — example of the added frontmatter line:**

```yaml
---
name: planner
description: Expands user prompts into product specifications with sprint decomposition
model: sonnet
maxTurns: 15
tools: Read, Write, Glob, Grep
thinking: { type: adaptive, effort: medium }
---
```

**Criterion 3 (Evaluator thinking frontmatter) — example of the added frontmatter line:**

```yaml
---
name: evaluator
description: Adversarial QA agent that tests sprint deliverables against contracts
model: sonnet
maxTurns: 30
tools: Read, Glob, Grep, Bash
context: fork
skills: eval-rubric
thinking: { type: adaptive, effort: high }
---
```

The capability-eval default (`high`) is what the frontmatter declares. The body's "Thinking Effort: Regression vs Capability Evaluation" section already documents that CONTRACT_REVIEW mode uses `max` and regression-criterion evaluation uses `medium` — Sprint 8 only adds the literal frontmatter at `high` and revises the body to remove the "policy-only" disclaimer, since the wiring is now in place.

**Criterion 6 & 7 (config.json fields) — example of the added config sections:**

```json
{
  "project_type": "eval-harness",
  "rubric": "eval-harness",
  "max_retries": 3,
  "...": "...",
  "thinking": {
    "profile": "default"
  },
  "batch": {
    "enabled": false,
    "min_criteria": 20
  }
}
```

**Criterion 8 (harness-sprint Batch API section) — example of the added subsection inside Step 3 Evaluation:**

```markdown
### 3d. Batch API Mode (optional)

Read `config.batch.enabled` (default `false`) and `config.batch.min_criteria` (default `20`).
The batch path activates only when `config.batch.enabled == true` AND the sprint contract's
criterion count (success criteria + Should-NOT gates) is greater than or equal to
`config.batch.min_criteria`. Otherwise the synchronous evaluation path in Step 3b runs as today.

When the batch path activates:

1. Collect every criterion's verification request (the deterministic command or the LLM-judge
   prompt) into a single Anthropic Batch API submission against `/v1/messages/batches`.
2. Poll the batch until completion. Anthropic's documented Batch API offers a 50% discount on
   input/output tokens with a 24-hour SLA — batch is a cost optimization, not a latency
   optimization.
3. Map each batch result back onto its criterion's slot in `sprint-NN-rR.md` so the per-criterion
   `## N. Criterion ...` shape is preserved. Downstream consumers (the regression gate, the
   summary, the saturation detector) read the same file format whether batch or synchronous
   produced it.

Backward compatibility: `batch.enabled: false` (the default) means evaluation runs synchronously
as in Phase 1. A `.harness/config.json` lacking the `batch` object is equivalent to the
default — no batch submission is attempted.
```

**Criterion 11 (backward compatibility) — example of the README sentence pattern:**

```markdown
### Configuration knobs (Phase 2)

- `thinking.profile` — one of `"default"`, `"fast"`, `"thorough"`. Default: `"default"`,
  which preserves Phase-1 behavior (no override applied to agent frontmatter).
- `batch.enabled` — boolean. Default: `false`. When `true` and a sprint has at least
  `batch.min_criteria` criteria, eval verifications are submitted as a single Anthropic
  Batch API call (50% discount, 24-hour SLA). With the default `false`, evaluations run
  synchronously as in Phase 1.
- `batch.min_criteria` — integer. Default: `20`. Sprints with fewer criteria stay synchronous
  even when `batch.enabled` is `true` — the batch overhead is only worth it on large suites.
```

## Out of Scope

- Actually issuing a real Batch API HTTP request against `/v1/messages/batches` from inside this sprint's own evaluation. The plumbing and documentation ship here; end-to-end batch submission verification is deferred to a synthetic follow-up sprint per the gap-closure-plan Verification item 3 (the meta-eval after Sprint 10).
- Implementing a runtime that reads the `thinking` frontmatter and applies it programmatically when spawning agents. The frontmatter is declared as policy/configuration that Claude Code (or a future custom orchestrator) consumes; the harness's deliverable is the declaration, not the dispatcher.
- Wiring `thinking.profile` overrides into a translator that rewrites individual agent frontmatter at runtime. The knob's default `"default"` is the only path that must work in this sprint; `"fast"` and `"thorough"` are reserved values whose dispatch logic lands in a future sprint or out-of-band tooling.
- Updating Sprint 1–7 contracts retroactively to add `thinking` frontmatter. The frontmatter and config knob apply going forward; existing contracts and evals are append-only artifacts.
- Transcript JSON trailer emission (Sprint 9) and Playwright / edge-case / adversarial hygiene (Sprint 10).
- Modifying the regression suite invocation in Step 0.5 to use `effort: medium`. Sprint 7 already documents the policy in `agents/evaluator.md`'s "Thinking Effort" section; Sprint 8 only adds the literal frontmatter and removes the "policy-only" disclaimer. The dispatching of `medium` to the regression-eval invocation is a runtime concern, not a declaration concern.

## Technical Notes

- **The `thinking` frontmatter declarations are policy, not orchestration.** Whether or not Claude Code's current agent runtime honors a `thinking` frontmatter field, the declarations make the per-role effort policy machine-readable in a single place. A future change to the runtime — or an out-of-band wrapper that pre-processes agent files — can read these declarations directly.
- **Per-mode overrides for the Evaluator stay in the body, not the frontmatter.** YAML frontmatter cannot express "max for CONTRACT_REVIEW, high for capability EVALUATION, medium for regression EVALUATION" without overloading the schema. The frontmatter declares the most common case (`high` for capability eval) and the body's existing "Thinking Effort" section enumerates the overrides. Sprint 7 already wrote that section as policy-only; Sprint 8 promotes it to a "live" section by adding the frontmatter and removing the disclaimer text.
- **Batch API is a pure cost optimization, not a latency optimization.** The 24-hour SLA means batch evaluations may take up to a day to complete. The criterion count threshold (`min_criteria: 20`) exists because batch overhead is only worth absorbing on large suites — small sprints stay synchronous so contributors keep tight feedback loops.
- **Per-criterion result shape preservation is critical.** The regression gate (Step 0.5), the saturation detector in `harness-summary`, and the future transcript correlator all read `sprint-NN-rR.md` with a fixed `## N. Criterion ...` shape. Whether the underlying API call was batch or synchronous is invisible to those consumers — and must remain invisible — because changing the file shape would cascade across every Sprint 7–10 deliverable.
- **`thinking.profile` is reserved for future override behavior.** This sprint introduces the field with a default that preserves today's behavior; the `"fast"` and `"thorough"` values are documented as reserved, with their override logic landing in a follow-up. Reserving the values now means a future sprint can wire them up without a config schema migration.
- **Forward wiring to Sprint 9**: the transcript trailer Sprint 9 will emit can include the actual `thinking_summary` field (already noted in the gap-closure plan's Sprint 9 schema). The frontmatter declarations from this sprint are what would be referenced when constructing that trailer.

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/sprint-08.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — both Success Criteria and Should-NOT gates — with stable `task_id`s, `grader_type`, `weight`, `is_gate`, `verification_command`, and `rubric_dimension`. Downstream sprints (regression gate, transcript capture, adversarial hygiene) consume that JSON; this markdown contract remains the human-readable source of truth. See `skills/sprint-contract/SKILL.md` for the schema.

## Evaluator Review

**Status: NEEDS REVISION**

### Feedback

**Criterion 10 — tasks.json threshold is wrong (must fix)**

The verification command uses `(.tasks | length) >= 13`, but the contract has 13 success criteria + 3 Should-NOT gates = 16 total entries. A Generator that emits only the 13 success criteria without any gate entries would pass this check. The threshold must be `>= 16` (or `>= 13 + 3`) to actually require the Should-NOT entries to be present. Sprint 07's equivalent criterion used `>= 12` matching its 12 success + 3 gates = 15 total, and a `length >= 12` threshold there also had the same gap — but this sprint is the one to fix it. Change the verification command to:
```
jq -e '.sprint == 8 and (.tasks | length) >= 16 and (.tasks | all(has("task_id") and has("grader_type") and has("weight") and has("is_gate")))' .harness/contracts/sprint-08.tasks.json
```

**Criteria 1, 2, 3, 5 — inline-only awk+grep fails on multi-line YAML (must fix or constrain)**

All four frontmatter criteria use `grep -qE 'thinking:.*type:.*adaptive.*effort:.*medium'` (or `...effort:.*high'` / `...effort:.*max'`). This pattern requires all three fields (`thinking`, `type`, `effort`) to appear on a single line. If the Generator writes multi-line block YAML:

```yaml
thinking:
  type: adaptive
  effort: medium
```

the awk output will contain three separate lines, and the single-line grep will not match any of them — producing a false FAIL on valid frontmatter. The reference solutions show inline format (`thinking: { type: adaptive, effort: medium }`), so the intent is inline. Fix by one of two approaches:

- Option A (preferred): tighten the criterion text to mandate inline format ("…declared as a single-line YAML mapping `thinking: { type: adaptive, effort: medium }`"), so the grep is correct for all valid implementations.
- Option B: replace the single-line grep with two separate greps that work on multi-line output: `grep -q 'type: adaptive' && grep -q 'effort: medium'` (applied to the awk output saved to a variable or temp file).

Without this fix, a correct multi-line implementation falsely fails, and an incorrect single-line implementation with the wrong effort level could appear to pass if the pattern is weakened.

**Criterion 9 — README permutation regex requires three values on the same line (should fix)**

`grep -qE 'default.*fast.*thorough|fast.*thorough.*default|...'` requires all three values to appear on the same line in README. The reference solution shows them as a bullet list where each value is on its own line. If the Generator follows that reference solution exactly, the grep will FAIL even though the documentation is correct. Fix by replacing the permutation grep with three independent existence checks:
```
grep -q 'thinking.profile' README.md && grep -q '"default"' README.md && grep -q '"fast"' README.md && grep -q '"thorough"' README.md && grep -q 'batch.enabled' README.md && grep -q 'batch.min_criteria' README.md
```
This verifies that all three valid values and both batch fields are present in README, without requiring them to be on the same line.

**SN3 — grader type mismatch (minor)**

SN3 says "Verify by reading the Batch API section" — this is an LLM-judge check, not a deterministic one. The contract does not tag it. The same issue was noted in the Sprint 07 Evaluator Review for that sprint's SN3. The `sprint-08.tasks.json` entry for SN3 should carry `grader_type: "llm-judge"` to be consistent with Sprint 06/07 precedent and with the sprint-contract SKILL's field semantics.

**Criterion 8 — regex dot is unescaped (minor, not a blocker)**

`grep -qiE 'batch.api'` and `grep -q 'batch.enabled'` use `.` which matches any character, not just a literal period. "batch_api" or "batch_enabled" would also match. In practice this is benign (the file will use the correct field names), but for rigor `batch\.` or the literal-string flag `-F` should be used. Similarly `grep -qiE '24.hour'` matches "24-hour", "24 hour", "24_hour", etc. — intentional flexibility here is acceptable since the reference solution uses a hyphen and the .` is effectively a wildcard for the separator.

### Missing Criteria

None. Every file in the gap-closure-plan's Sprint 8 section maps to at least one criterion:

- `agents/planner.md` → Criterion 1
- `agents/generator.md` → Criterion 2
- `agents/evaluator.md` frontmatter → Criterion 3
- `agents/evaluator.md` body disclaimer removal → Criterion 4
- `skills/harness-summary/SKILL.md` frontmatter → Criterion 5
- `.harness/config.json` thinking.profile → Criterion 6
- `.harness/config.json` batch fields → Criterion 7
- `skills/harness-sprint/SKILL.md` Batch API section → Criterion 8
- `README.md` → Criterion 9
- `sprint-08.tasks.json` emission → Criterion 10
- Backward compatibility (README + skills + agents) → Criterion 11
- Per-role rationale (agent files + evaluator.md body) → Criterion 12
- Batch API trigger/payoff/result shape → Criterion 13

### Approved Criteria

4, 5, 6, 7, 11, 12, 13 — approved as-is.

SN1 — approved: LLM-judge gate with clear Phase-1 guard semantics; matches spec.md backward-compat requirement.
SN2 — approved: deterministic git-diff check; same pattern as prior sprint SN2 gates.
SN3 — approved in substance, but should be tagged `grader_type: "llm-judge"` in tasks.json (non-blocking for contract approval; Generator must act on this when emitting the JSON).

Criteria 1, 2, 3 — approved in substance pending the inline-YAML fix noted above (either constrain the implementation format in the criterion text or use a multi-line-safe grep).
Criterion 8 — approved in substance; unescaped `.` is benign in this context.
Criterion 9 — needs the permutation-regex fix before the evaluation command is reliable.
Criterion 10 — blocked: threshold must be raised from `>= 13` to `>= 16` before this criterion can verify gate inclusion.

### Contract Quality Notes

**Weight sum:** 6+6+10+8+6+6+6+10+5+6+12+10+9 = 100%. Verified correct.

**Weight distribution:** Healthy. Largest criterion is 11 (backward compatibility, 12%), which correctly reflects the sprint's must-not-break-existing-projects obligation. No single criterion dominates. The two Batch API body criteria (8 at 10% and 13 at 9%) and the evaluator frontmatter criterion (3 at 10%) collectively carry the heaviest load — appropriate for the sprint's core deliverables.

**Reference solution coverage:** Present for Criteria 1, 3, 6+7 (config), 8 (Batch API section), and 11 (backward compat README). Criterion 12 (per-role rationale, 10%, LLM-judge) lacks a reference solution — adding one would reduce inter-evaluator disagreement, but given that the rationale is fully described in the Technical Notes and the existing "Thinking Effort" section text, it is not required to approve.

**Scope discipline:** Out-of-Scope correctly defers end-to-end Batch API HTTP calls, `thinking.profile` dispatch logic, retroactive Sprint 1–7 frontmatter, transcript capture, and Playwright hygiene. No scope creep visible.

**Backward-compat alignment:** Criteria 6, 7, 11, SN1, and Technical Notes all converge on the same rule — absent `thinking` and `batch` objects reproduce Phase-1 behavior. Consistent four-way coverage.

**Criterion 3 effort split is sensible:** Frontmatter at `high` (the modal capability-eval case) with body overrides for `max` (contract review) and `medium` (regression eval) is the right design. The frontmatter cannot express per-mode branching; body prose is the correct place for the override table. No change needed.

## Evaluator Review — Round 2

**Status: APPROVED**

### Round 1 Issues — Resolution

- **Blocker 1 (Criterion 10 threshold):** Resolved. Criterion 10 verification command now uses `(.tasks | length) >= 16` and the criterion text explicitly states "13 success criteria + 3 Should-NOT gates = **16 entries**". A Generator that emits only the 13 success criteria without gate entries will now correctly fail this check.

- **Blocker 2 (Criteria 1, 2, 3, 5 inline-format mandate):** Resolved. All four criteria now contain explicit inline-format language: "declared as a single-line YAML mapping in the form `thinking: { type: adaptive, effort: ... }` (inline format — required so the verification command's single-line grep matches)" (or equivalent wording). The awk+grep verification is now correct for all valid implementations because the criterion text constrains the implementation to the form the grep expects.

- **Blocker 3 (Criterion 9 permutation regex):** Resolved. The permutation regex is completely replaced with six independent existence checks: `grep -q 'thinking.profile' README.md && grep -q '"default"' README.md && grep -q '"fast"' README.md && grep -q '"thorough"' README.md && grep -q 'batch.enabled' README.md && grep -q 'batch.min_criteria' README.md`. These checks work correctly when values appear on separate bullet lines, matching the reference solution format.

### Remaining Concerns

None introduced by the revision. The two pre-existing minor issues from round 1 are unchanged and remain non-blocking:

- Unescaped `.` in `batch.api`, `batch.enabled`, `batch.min_criteria`, and `24.hour` grep patterns in Criterion 8 (benign in practice — the file will use the correct field names).
- `grep -q '"default"'` in Criterion 9 is slightly over-broad (matches any `"default"` in README), but a README following the reference solution will satisfy the check and a README lacking the value will correctly fail.
- SN3 `grader_type: "llm-judge"` tagging is a Generator responsibility when emitting `sprint-08.tasks.json`, not a contract text issue.

### Final Verdict

All three round-1 blockers are cleanly resolved with no new issues introduced; the contract is well-formed, weight-balanced (100%), and every criterion is independently testable with a grader type that matches its verification method.
