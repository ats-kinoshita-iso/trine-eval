# Sprint 08 Contract: Claude 4.6 Adaptive Thinking + Batch API

## What I Will Build

Close Gaps 5 (adaptive-thinking config) and 7 (Batch API) from the playbook alignment plan: land Claude 4.6's `thinking: { type: adaptive, effort: ... }` on every agent and analysis skill, tuned to role (medium for planner/generator baseline, high for evaluator capability passes, max for harness-summary and contract review), and wire an optional Batch API mode into `skills/harness-sprint/SKILL.md` that collects eval criterion verifications into a single submission when a sprint carries ≥ `batch.min_criteria` criteria. Sprint 8 consumes the Sprint-7 policy hook in `agents/evaluator.md` (the "Thinking Effort: Regression vs Capability Evaluation" section) by making it enforceable through frontmatter, and documents per-mode overrides (CONTRACT_PROPOSAL vs IMPLEMENTATION for the Generator; CONTRACT_REVIEW vs EVALUATION vs regression-gate for the Evaluator). Defaults are chosen so a pre-Phase-2 project — no `thinking` or `batch` object in `config.json`, no frontmatter `thinking:` key honored by the runtime — executes exactly as it did in Phase 1.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **planner.md declares adaptive-thinking frontmatter at effort medium**: `agents/planner.md`'s YAML frontmatter contains a `thinking` key with `type: adaptive` and `effort: medium`. Verify via `grep -q '^thinking:' agents/planner.md && grep -qE 'type:[[:space:]]*adaptive' agents/planner.md && grep -qE 'effort:[[:space:]]*medium' agents/planner.md`. [weight: 6%]

2. **generator.md declares adaptive-thinking frontmatter at effort medium**: `agents/generator.md`'s YAML frontmatter contains a `thinking` key with `type: adaptive` and `effort: medium`. This is the IMPLEMENTATION-mode baseline; per-mode overrides for CONTRACT_PROPOSAL and CONTRACT_REVISION are documented in the body. Verify via `grep -q '^thinking:' agents/generator.md && grep -qE 'type:[[:space:]]*adaptive' agents/generator.md && grep -qE 'effort:[[:space:]]*medium' agents/generator.md`. [weight: 7%]

3. **evaluator.md declares adaptive-thinking frontmatter at effort high**: `agents/evaluator.md`'s YAML frontmatter contains a `thinking` key with `type: adaptive` and `effort: high`. `high` is the capability-eval baseline; the body documents `medium` for regression-criterion evaluation (Sprint 7 wiring point) and `max` for CONTRACT_REVIEW. Verify via `grep -q '^thinking:' agents/evaluator.md && grep -qE 'type:[[:space:]]*adaptive' agents/evaluator.md && grep -qE 'effort:[[:space:]]*high' agents/evaluator.md`. [weight: 8%]

4. **harness-summary SKILL declares adaptive-thinking frontmatter at effort max**: `skills/harness-summary/SKILL.md`'s YAML frontmatter contains a `thinking` key with `type: adaptive` and `effort: max`. Summary work is analysis-heavy (cross-sprint trends, saturation, ACI review) and benefits from max effort. Verify via `grep -q '^thinking:' skills/harness-summary/SKILL.md && grep -qE 'type:[[:space:]]*adaptive' skills/harness-summary/SKILL.md && grep -qE 'effort:[[:space:]]*max' skills/harness-summary/SKILL.md`. [weight: 6%]

5. **config.json schema extended with thinking.profile**: `.harness/config.json` contains a `thinking` object with a `profile` key whose value is one of `"default"`, `"fast"`, or `"thorough"` (the default value is `"default"` when the object is present; if the `thinking` object is entirely absent, the harness treats the profile as `"default"`). Verify via `jq -e '.thinking.profile == "default" or .thinking.profile == "fast" or .thinking.profile == "thorough"' .harness/config.json`. [weight: 7%]

6. **config.json schema extended with batch fields**: `.harness/config.json` contains a `batch` object with keys `enabled` (boolean) and `min_criteria` (integer). Defaults: `enabled: false` and `min_criteria: 20`. Verify via `jq -e '.batch | has("enabled") and has("min_criteria") and (.enabled | type == "boolean") and (.min_criteria | type == "number")' .harness/config.json`. [weight: 8%]

7. **harness-sprint SKILL contains a Batch API section**: `skills/harness-sprint/SKILL.md` contains a section headed with something matching `Batch` (e.g., `## Batch API Mode` or a subsection under Step 3). The section must reference (a) the config keys `batch.enabled` and `batch.min_criteria`, (b) the guard condition "batch.enabled is true AND criteria count ≥ batch.min_criteria", (c) the submit/poll/map-back workflow (collect per-criterion verifications into a single Batch API submission, poll until complete, map results back onto per-criterion eval entries), (d) the 50% token discount and 24-hour SLA from Anthropic's Batch API docs, and (e) the synchronous fallback when the guard does not hold or when the batch call fails. Verify via `grep -qiE '^## .*Batch|^### .*Batch' skills/harness-sprint/SKILL.md && grep -q 'batch.enabled' skills/harness-sprint/SKILL.md && grep -q 'batch.min_criteria' skills/harness-sprint/SKILL.md && grep -q '50%' skills/harness-sprint/SKILL.md && grep -qE '24[- ]hour' skills/harness-sprint/SKILL.md`. [weight: 14%]

8. **README.md documents the new config knobs**: `README.md` contains documentation for `thinking.profile` (mentioning the three values `default` / `fast` / `thorough`), `batch.enabled`, and `batch.min_criteria`. Verify via `grep -q 'thinking.profile' README.md && grep -q 'default' README.md && grep -q 'fast' README.md && grep -q 'thorough' README.md && grep -q 'batch.enabled' README.md && grep -q 'batch.min_criteria' README.md`. [weight: 5%]

9. **sprint-08.tasks.json is emitted**: A file `.harness/contracts/sprint-08.tasks.json` exists, is valid JSON, has a top-level `sprint: 8` field and a `tasks` array with one entry per criterion in this contract (including gate criteria with `is_gate: true, weight: 0`). Each entry has the Sprint 6 schema fields (`task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`). Verify via `jq -e '.sprint == 8 and (.tasks | length) >= 13 and (.tasks | all(has("task_id") and has("grader_type") and has("weight") and has("is_gate")))' .harness/contracts/sprint-08.tasks.json`. [weight: 6%]

### LLM-as-judge (requires reading comprehension)

10. **Per-mode thinking overrides are internally consistent**: A reader of `agents/planner.md`, `agents/generator.md`, `agents/evaluator.md`, and `skills/harness-summary/SKILL.md` should be able to explain (a) the frontmatter baseline effort for each agent/skill and why (planner/generator: `medium` for routine work; evaluator: `high` for fresh capability evaluation; harness-summary: `max` for cross-sprint analysis); (b) the per-mode overrides described in each agent's body — Generator CONTRACT_PROPOSAL/REVISION invokes higher effort than IMPLEMENTATION; Evaluator CONTRACT_REVIEW at `max`, capability EVALUATION at `high`, regression-criterion evaluation at `medium`; (c) that the Sprint-7 "Thinking Effort: Regression vs Capability Evaluation" policy in `agents/evaluator.md` is now wired through the frontmatter plus per-mode documentation — the Sprint-7 "Status: policy-only until Sprint 8" caveat is updated to reflect that the frontmatter is now present and the policy is enforceable via per-mode overrides. [weight: 11%]

11. **Backward compatibility is explicit and correct**: The updates to `agents/*.md`, `skills/harness-summary/SKILL.md`, `skills/harness-sprint/SKILL.md`, and `.harness/config.json` make it unambiguous that a pre-Phase-2 project — `config.json` with no `thinking` object and no `batch` object, plus a Claude Code runtime that may or may not honor `thinking:` frontmatter — executes exactly as it did in Phase 1: no batch submission attempted, no errors from missing config keys, every agent spawn proceeds with pre-Sprint-8 semantics. Each new config field (`thinking.profile`, `batch.enabled`, `batch.min_criteria`) must have a documented default (explicit default value or an "if absent" clause) such that a `.harness/config.json` lacking the corresponding object produces Phase-1 behavior. A reader should also understand that adaptive-thinking frontmatter is advisory — if a runtime ignores the key, agents still run with the prior model-default behavior. [weight: 10%]

12. **Batch threshold rationale is justified, not just asserted**: The Batch section in `skills/harness-sprint/SKILL.md` should explain (not merely state) why `batch.enabled: false` is the default and why `batch.min_criteria: 20` is the threshold below which the harness stays synchronous. A reader should come away understanding that (a) the 24-hour Batch API SLA makes batch unsuitable for tight contract→build→eval iteration cycles, which is why it is opt-in rather than default, (b) small sprints do not benefit from batching because submission overhead plus latency exceeds the per-call token savings, and (c) the 50% discount compounds only when the per-sprint criterion count crosses a break-even point around ~20 criteria, which is why that value is the default threshold. [weight: 6%]

13. **thinking.profile override semantics are clear**: A reader of the documentation (`README.md`, `rules/harness-conventions.md`, or the agent files) should be able to explain how `config.thinking.profile` overrides per-agent frontmatter effort: the three values `default` / `fast` / `thorough` map to consistent effort vectors across the four agents and skills (`default` = per-agent baseline; `fast` = shift every baseline one level down, clamped at `medium`; `thorough` = shift every baseline one level up, clamped at `max`). The documentation should also describe how a user sets `thinking.profile` in `config.json` without editing individual agent frontmatter, and how per-mode overrides (Generator CONTRACT_PROPOSAL, Evaluator CONTRACT_REVIEW and regression-gate invocations) compose on top of the profile-adjusted baseline. [weight: 6%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **No silent behavior change for pre-Phase-2 configs**: A project whose `.harness/config.json` lacks both the `thinking` object and the `batch` object must run the harness identically to Phase 1 — no batch submission attempted, no errors from missing config keys, every agent spawn proceeds with pre-Sprint-8 semantics (effort level enforced only to the extent the runtime honors the new frontmatter; absent runtime honor, behavior is unchanged). Verify by reading the updated `.harness/config.json`, the updated agent files, and `skills/harness-sprint/SKILL.md` Batch section — every reference to a new config key must be explicitly guarded on its presence or have a documented default that reproduces Phase-1 behavior.

2. **No modification of prior sprint artifacts**: `.harness/evals/sprint-0[1-7]*` and `.harness/contracts/sprint-0[1-7]*` must be unchanged from HEAD at the start of this sprint (append-only rule from `rules/harness-conventions.md`). Verify via `test -z "$(git diff HEAD -- .harness/evals/sprint-0[1-7]* .harness/contracts/sprint-0[1-7]*)"`.

3. **Sprint-7 evaluator thinking-effort policy is preserved, not contradicted**: The Sprint-7 policy in `agents/evaluator.md`'s "Thinking Effort: Regression vs Capability Evaluation" section — regression-criterion evaluation at `medium`, capability-criterion evaluation at `high`, contract review at `max` — must remain consistent with the Sprint-8 frontmatter and body. The frontmatter baseline (`effort: high`) must match the capability-eval policy; any per-mode override documented in the body must match the Sprint-7 policy (medium for regression, max for contract review). Verify by reading `agents/evaluator.md` and confirming that no Sprint-8 edit introduces effort values that contradict the Sprint-7 policy paragraph.

## Reference Solutions

**Criterion 3 & 10 (evaluator frontmatter + per-mode overrides) — example frontmatter and body note:**

```yaml
---
name: evaluator
description: Adversarial QA agent that tests sprint deliverables against contracts
model: sonnet
maxTurns: 30
tools: Read, Glob, Grep, Bash
context: fork
skills: eval-rubric
thinking:
  type: adaptive
  effort: high
---
```

Body paragraph (appended to the existing "Thinking Effort: Regression vs Capability Evaluation" section, replacing the "Status: policy-only until Sprint 8" caveat):

```markdown
**Frontmatter and overrides.** The frontmatter above declares `effort: high`
as the capability-evaluation baseline. Per-mode overrides:

- **CONTRACT_REVIEW** — invoke at `effort: max`. A draft contract's gaps
  propagate into the whole sprint, so the Evaluator reads it with the
  maximum reasoning budget.
- **EVALUATION (capability)** — use the frontmatter baseline (`high`).
- **EVALUATION (regression, Step 0.5)** — drop to `effort: medium`. Regression
  criteria are pre-calibrated verbatim commands; speed matters more than
  re-investigation, because the gate runs before every sprint.

The harness-sprint skill sets the override when it spawns the Evaluator
in each mode; the frontmatter provides the fallback if no override is
passed.
```

**Criterion 7 (harness-sprint Batch section) — example of the added subsection under Step 3:**

```markdown
### 3d. Batch API Mode (optional)

Read `config.batch.enabled` (default `false`) and `config.batch.min_criteria`
(default `20`). If both `batch.enabled` is true AND the sprint contract has
at least `batch.min_criteria` criteria, route the capability-eval
verification step through Anthropic's Batch API instead of the per-criterion
synchronous calls in Step 3b. Otherwise, run Step 3b synchronously as before.

**Protocol:**

1. Read `.harness/contracts/sprint-{NN}.tasks.json`. For every task with a
   non-null `verification_command`, collect one batch request item:
   `{task_id, verification_command, grader_type, rubric_dimension}`.
2. Submit the collected items as a single Batch API request. Record the
   batch id to `.harness/progress.md`.
3. Poll the batch until status is `ended`. Batch jobs carry a 24-hour SLA
   (the hard upper bound on when results return); in practice most jobs
   complete faster, but do not design the retry loop around sub-hour
   turnaround.
4. When the batch completes, map each result entry back to its `task_id`
   and write the per-criterion PASS/FAIL evidence into
   `.harness/evals/sprint-{NN}-r{R}.md` using the same format as the
   synchronous path. LLM-judge criteria fall back to the synchronous path —
   batch is only used for deterministic verification commands.

**Why this is opt-in and gated.** The 50% token discount is only worth the
24-hour SLA on large eval suites where per-call savings compound. Small
sprints (fewer than `batch.min_criteria` criteria) pay more in latency
than they save in tokens, so the default threshold keeps short feedback
loops synchronous. The `batch.enabled: false` default preserves Phase-1
behavior exactly — a project that never sets the flag never goes near the
Batch API.

**Fallback.** If the Batch API call fails for any reason (submission error,
timeout beyond 24 hours, malformed result), fall back to synchronous Step 3b
and note the failure in `.harness/progress.md`. Never silently drop criteria.
```

**Criterion 13 (thinking.profile mapping) — example of the documentation:**

```markdown
### thinking.profile

Override per-agent frontmatter effort without editing agents. Values:

- `"default"` (default) — each agent uses its frontmatter baseline: planner `medium`,
  generator `medium`, evaluator `high`, harness-summary `max`.
- `"fast"` — shift every baseline one level down, clamped at `medium`: planner
  `medium`, generator `medium`, evaluator `medium`, harness-summary `high`.
- `"thorough"` — shift every baseline one level up, clamped at `max`: planner
  `high`, generator `high`, evaluator `max`, harness-summary `max`.

Set in `.harness/config.json` under `thinking.profile`. The harness applies
the profile at agent-spawn time; per-mode overrides (Generator
CONTRACT_PROPOSAL, Evaluator CONTRACT_REVIEW and regression-gate
invocations) compose on top of the profile-adjusted baseline.
```

## Out of Scope

- **Runtime enforcement of adaptive-thinking frontmatter.** Sprint 8 declares the frontmatter; whether a particular Claude Code runtime honors `thinking:` on plugin agents is outside this sprint. If the runtime ignores the key, agents continue to run at the model's default — i.e., exactly as Phase 1.
- **Actually submitting a live Batch API request.** This sprint ships the protocol documentation, config knobs, and guard conditions. End-to-end Batch API submission verification happens on a synthetic follow-up sprint per the gap-closure-plan Verification item 3.
- **Retroactive thinking-profile application to prior sprint transcripts.** The profile applies to agent spawns going forward. Prior sprints' eval reports were produced at pre-Sprint-8 defaults and are not re-run.
- **Batch API wiring for Step 0.5 regression runs.** Step 0.5 runs graduated criteria synchronously by default. Routing regression verifications through Batch API is a potential follow-up — the `tasks.json` schema already carries `verification_command` so the data channel is ready, but this sprint does not add the regression-gate batch path.
- **Transcript capture integration (Sprint 9) and adversarial hygiene (Sprint 10).** Sprint 8 may reference these but does not implement them.

## Technical Notes

- **Sprint-7 hook consumed.** `agents/evaluator.md` carries a Sprint-7 policy paragraph ("Thinking Effort: Regression vs Capability Evaluation") that explicitly names Sprint 8 as the consumer of its policy. Sprint 8 adds the frontmatter `thinking: { type: adaptive, effort: high }` as the capability-eval baseline and documents the per-mode overrides (medium for regression, max for contract review). The Sprint-7 paragraph's "Status: policy-only until Sprint 8" caveat must be updated to reflect that the frontmatter is now present and per-mode overrides are the enforcement mechanism.
- **Frontmatter syntax.** YAML frontmatter supports both nested and inline forms; the deterministic grep checks accept either, matching the lines `type: adaptive` and `effort: <value>` independently of indentation. The `thinking:` line at column 0 is required in both forms (the inline form writes `thinking: { type: adaptive, effort: medium }` on one line; the nested form puts the subkeys on indented lines).
- **thinking.profile as a single knob.** The spec calls for `thinking.profile` rather than per-agent effort overrides in `config.json` to keep the common case simple: operators tune the whole harness's quality/cost tradeoff with one value. Advanced per-agent overrides can be added later (e.g., `thinking.per_agent.evaluator = "max"`) without breaking the profile knob.
- **Batch API threshold rationale.** `batch.min_criteria: 20` is chosen so that most Phase 2 sprints (typically 10–15 criteria) stay synchronous — batch is an optimization for large regression suites and cross-sprint summary generation, not per-sprint capability evaluation. The 24-hour SLA makes batch strictly worse for small N where token savings do not compensate for wall-clock latency.
- **Forward wiring.** Sprint 9 (transcript capture) reads the Evaluator's structured trailer; landing adaptive-thinking in Sprint 8 means the thinking-summary channel is available when Sprint 9 arrives. Sprint 10 (adversarial hygiene) uses the `verified_via_command` flag on each criterion; the batch path must preserve the flag when mapping results back.
- **Fail-safe on batch failures.** When the Batch API submission or polling fails, the harness falls back to the synchronous path rather than dropping or re-submitting silently. This preserves the primary invariant: every criterion must have a recorded PASS/FAIL with evidence before the sprint can complete.

## Evaluator Review

**Status: APPROVED**

### Feedback

The contract is testable, specific, and weight-valid (6+7+8+6+7+8+14+5+6+11+10+6+6 = 100, verified). Deterministic criteria cite concrete grep/jq commands; LLM-judge criteria (10–13) anchor on identifiable claims a reader can extract from the docs. Reference solutions cover the three highest-stakes areas (evaluator frontmatter + overrides, harness-sprint Batch section, thinking.profile mapping). The Sprint-7 hook is consumed correctly without contradiction: Criterion 3 puts evaluator.md frontmatter at `effort: high` (the Sprint-7 capability-eval baseline) and documents `medium`/`max` overrides that match the Sprint-7 policy paragraph verbatim.

Non-blocking notes the Generator should keep in mind during implementation:

- **Criterion 1/2/3/4 grep anchoring is loose.** The verification commands do not anchor `type: adaptive` / `effort: <value>` to the YAML frontmatter region (no `---...---` boundary check). A file whose body contains prose like "use `type: adaptive`" without the actual frontmatter declaration would false-pass. This mirrors the Sprint-7 Criterion 7 pattern that was explicitly approved with the same characteristic, so the check is consistent with prior sprints — but implementers should ensure the frontmatter is actually present and not rely solely on the grep passing. The reference solution (Criterion 3) shows the intended frontmatter shape; follow it literally.
- **Criterion 7 Batch-section grep is thorough but case-sensitive on lowercase keys.** `grep -q 'batch.enabled'` uses literal-dot matching — `.` matches any character, so `batch-enabled`, `batchXenabled`, etc. would also match. Acceptable because no such false-positive would realistically appear, but tight-match could be `grep -q 'batch\.enabled'` if stricter anchoring is desired. Not a blocker.
- **Criterion 8 (README grep) is weak by construction.** The check greps for the words `default`, `fast`, `thorough` independently anywhere in README.md. These are common English words that could appear in unrelated sections ("fast feedback loops", "default behavior"). Anchoring them under the `thinking.profile` documentation would be stricter, but the inclusion of `thinking.profile` + `batch.enabled` + `batch.min_criteria` in the same check provides enough structural evidence that the section exists. Keep the profile-values near the `thinking.profile` heading in the README so a reader spot-check matches the grep result.
- **CLI `--batch` flag vs config-only gating.** The gap-closure plan mentions "Add `--batch` flag" to `skills/harness-sprint/SKILL.md`, but the contract consolidates on pure config-gated behavior (`batch.enabled` + `batch.min_criteria`) with no CLI flag. This is a scope simplification, not a coverage gap — the substance (Batch API mode, submit/poll/map-back, fallback) is fully covered by Criterion 7 and the reference solution. The CLI flag is a surface detail that `harness-sprint` does not currently use elsewhere (it has no CLI-flag parsing today), so omitting it is consistent with the existing skill architecture. Note this in implementation so a future reader of the plan does not expect the flag.
- **Should-NOT Criterion 1 is documentation-style (llm-judge gate).** SN1 is verified "by reading the updated `.harness/config.json`, the updated agent files, and `skills/harness-sprint/SKILL.md`" — it is a reading-comprehension check, not a runnable command. The tasks.json emission should mark SN1 as `grader_type: "llm-judge"` (consistent with Sprint 6 SN1 and Sprint 7 SN1 precedent).
- **Should-NOT Criterion 3 is documentation-style (llm-judge gate).** Same as above — SN3 is verified "by reading `agents/evaluator.md`." Mark as `grader_type: "llm-judge"` in tasks.json.
- **Criterion 13 override composition.** The criterion asserts that `fast` shifts one level down "clamped at medium" and `thorough` shifts one level up "clamped at max." Applying the reference solution's vectors to the four agents: planner medium→medium under `fast` (clamp hit), generator medium→medium under `fast` (clamp hit), evaluator high→medium under `fast` (shifts down), harness-summary max→high under `fast` (shifts down). And under `thorough`: planner medium→high, generator medium→high, evaluator high→max, harness-summary max→max (clamp hit). The reference-solution table in the contract body matches this. Be sure the documentation body's table exactly reproduces the reference to avoid inter-document drift.
- **tasks.json length threshold:** Criterion 9 requires `(.tasks | length) >= 13`. With 13 success criteria + 3 Should-NOT gates, the file should contain 16 tasks total. The `>= 13` floor passes whether the emitter includes gates or not, so a bug where gates are dropped would silently pass this check. Consider emitting all 16 entries per the template's explicit "one entry per criterion in this contract (including gate criteria)" rule — the reference solution contract language already requires it, and the Sprint 6 / Sprint 7 precedent emits gates.

### Missing Criteria

None. Every file-to-modify line in the gap-closure plan's Sprint 8 section maps to at least one criterion:

- `agents/planner.md` frontmatter → Criterion 1
- `agents/generator.md` frontmatter + per-mode documentation → Criterion 2, referenced in Criterion 10
- `agents/evaluator.md` frontmatter + per-mode documentation → Criterion 3, Criterion 10, SN3
- `skills/harness-summary/SKILL.md` frontmatter → Criterion 4
- `.harness/config.json` `thinking.profile` → Criterion 5
- `.harness/config.json` `batch.enabled`, `batch.min_criteria` → Criterion 6
- `skills/harness-sprint/SKILL.md` Batch API section → Criterion 7, Criterion 12
- `README.md` new config knobs → Criterion 8, Criterion 13
- `.harness/contracts/sprint-08.tasks.json` emission → Criterion 9

The Sprint-7 hook consumption (from `agents/evaluator.md` "Thinking Effort: Regression vs Capability Evaluation") is explicitly covered by Criterion 3, Criterion 10, and SN3 — three-way reinforcement against drift.

### Approved Criteria

1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13 — all approved. Should-NOT gates SN1, SN2, SN3 all testable and defensible.

### Contract Quality Notes

- **Weight distribution:** 6+7+8+6+7+8+14+5+6+11+10+6+6 = 100%. Verified. The highest single weight (14% on Criterion 7, the harness-sprint Batch API section) correctly sits on the sprint's largest deliverable — the Batch API protocol documentation with five substantive sub-requirements (config-key reference, guard condition, submit/poll/map-back workflow, 50%/24-hour docs reference, synchronous fallback). No single criterion exceeds 15%; the weight ceiling prescribed by `skills/sprint-contract/SKILL.md` (~20% unless core deliverable) is respected. Methodology-completeness dimension carries ~36% (Criteria 1, 2, 3, 4, 7 effort-level items — well-proportioned for an agent-frontmatter sprint), extensibility dimension ~30% (Criteria 5, 6, 8, 11, 13 — config/docs surface), grading-architecture dimension ~14%, and generator-evaluator-separation ~20% via the Sprint-7 hook consumption.
- **Reference solutions:** present for Criterion 3 & 10 (evaluator frontmatter + body note), Criterion 7 (harness-sprint Batch subsection), and Criterion 13 (thinking.profile mapping table). The highest-weighted LLM-judge criterion (Criterion 10 at 11%) has a reference solution — the evaluator frontmatter block and the updated body paragraph replacing the Sprint-7 "policy-only" caveat. This pins the expected output pattern so a round-2 evaluator has zero ambiguity on what constitutes a complete per-mode override documentation.
- **Scope boundaries:** Out-of-Scope correctly defers runtime enforcement, live Batch API submission verification, retroactive application to prior sprints, Step 0.5 regression-gate Batch wiring, and Sprint 9/10 touchpoints. The contract explicitly acknowledges that adaptive-thinking frontmatter is advisory (if runtime ignores the key, Phase-1 behavior is preserved) — this matches spec.md's Phase 2 technical constraint language and is the same risk-acknowledgment pattern Sprint 6 used for its `trials > 1` paths.
- **Backward-compat alignment:** Criterion 11, SN1, and the Technical Notes' "thinking.profile as a single knob" paragraph converge on the same rule — missing `thinking` object + missing `batch` object + runtime that may or may not honor frontmatter → Phase-1 behavior. This matches `.harness/spec.md` Phase 2 technical constraint: "An existing config file that predates Phase 2 must continue to execute exactly as it did before."
- **Append-only semantics:** SN2 (no modification of prior sprint artifacts) correctly extends to `.harness/evals/sprint-0[1-7]*` and `.harness/contracts/sprint-0[1-7]*`, matching the Sprint-7 SN2 pattern extended one sprint forward.
- **Sprint-7 hook consistency:** The Sprint-7 policy in `agents/evaluator.md`'s "Thinking Effort" section names Sprint 8 as its consumer. Sprint 8's Criterion 3 places the frontmatter at `effort: high` (Sprint-7's capability-eval baseline); the body text documents `medium` for regression (Sprint-7's speed-oriented policy) and `max` for contract review (Sprint-7's thoroughness policy). SN3 gates against any contradiction. Three-way enforcement — frontmatter + body documentation + explicit should-NOT — is the right level of defense for a cross-sprint policy hook.
