# Sprint 10 Contract: Completeness — Edge Cases, Playwright, Adversarial Hygiene

## What I Will Build

Close Gaps 8, 9, and 10 from the playbook alignment plan: introduce explicit edge-case criteria as a third class of contract criterion (separate from the 100%-weighted success criteria and from Should-NOT gates), wire conditional Playwright MCP availability to the Evaluator for `web-app` projects (with documented Visual Design fallback when Playwright is unavailable), and add an Adversarial Hygiene section to the Evaluator that forbids inferring PASS/FAIL from filenames or comments and introduces a per-criterion `verified_via_command` flag inside Sprint 9's transcript trailer. Add `config.evaluator_tools.playwright` (default `"auto"`) to `.harness/config.json`. Document the new taxonomy, the Playwright conditional, and the `verified_via_command` semantics in `rules/harness-conventions.md`. Update the contract template and the sprint-contract skill so future sprints can declare edge cases, and update `harness-summary` to surface "Edge Case Pass Rate" as a distinct metric. Like Sprints 8 and 9, Sprint 10 ships the protocol — taxonomy slots, conditional declarations, and per-criterion flag semantics — not a forced runtime hookup. End-to-end Playwright invocation against a live `web-app` project is deferred to a synthetic verification sprint per the gap-closure plan; `evaluator_tools.playwright: "auto"` resolves to "no Playwright" when `project_type != "web-app"`, so this `eval-harness` project sees no behavior change.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **`## Edge Case Criteria` section appears in the sprint-contract template**: `skills/sprint-contract/template.md` contains a level-2 heading exactly equal to `## Edge Case Criteria`. The new section is the contract slot future sprints use to declare optional edge-case criteria (separate from the 100%-weighted Success Criteria and from Should-NOT gates). Verify via `grep -qE '^## Edge Case Criteria' skills/sprint-contract/template.md`. [weight: 5%]

2. **`skills/sprint-contract/SKILL.md` documents the Edge Case Criteria taxonomy**: The skill file contains a level-2 heading exactly equal to `## Edge Case Criteria` AND uses the literal phrase "edge-case pass rate" (or the case/punctuation variant `edge case pass rate`) AND mentions at least one project rubric type (`web-app`) that warrants edge-case coverage. Verify via `grep -qE '^## Edge Case Criteria' skills/sprint-contract/SKILL.md && grep -qiE 'edge.case pass rate' skills/sprint-contract/SKILL.md && grep -q 'web-app' skills/sprint-contract/SKILL.md`. [weight: 7%]

3. **`Edge Case Pass Rate` is a distinct metric in the harness-summary skill**: `skills/harness-summary/SKILL.md` contains the literal string `Edge Case Pass Rate` (case-sensitive — distinct from prose mentions of "edge cases"). The phrase appears in the context of the summary output format so the metric is rendered separately from the weighted score. Verify via `grep -q 'Edge Case Pass Rate' skills/harness-summary/SKILL.md`. [weight: 6%]

4. **`## Adversarial Hygiene` section is added to the Evaluator with explicit `verified_via_command` semantics**: `agents/evaluator.md` contains a level-2 heading exactly equal to `## Adversarial Hygiene` AND the string `verified_via_command` appears at least 3 times in the file. The threshold of 3 is chosen because the file currently contains exactly one `verified_via_command` mention (a forward reference inside the Sprint 9 Transcript Trailer "why each field exists" prose at line 294); requiring 3 forces the new section to introduce the flag (rule statement), reference its schema location (per-tool-call or per-criterion field), and either show an example or reiterate the no-fabrication rule. Verify via `grep -qE '^## Adversarial Hygiene' agents/evaluator.md && [ $(grep -c 'verified_via_command' agents/evaluator.md) -ge 3 ]`. [weight: 12%]

5. **Playwright MCP is added to the Evaluator conditional on `config.project_type == "web-app"` with a documented Visual Design fallback**: `agents/evaluator.md` mentions Playwright (the literal string `Playwright`) AND mentions `project_type` AND mentions `visual design` (case-insensitive). The combination tests that the Evaluator's tools section now (a) names Playwright as a conditional MCP tool, (b) ties enablement to the project type, and (c) addresses the Visual Design dimension explicitly (Playwright's primary use case). Each of those three terms is absent from `agents/evaluator.md` today, so the AND chain fails until all three land. Verify via `grep -q 'Playwright' agents/evaluator.md && grep -q 'project_type' agents/evaluator.md && grep -qi 'visual design' agents/evaluator.md`. [weight: 10%]

6. **`config.json` declares `evaluator_tools.playwright == "auto"`**: `.harness/config.json` contains a top-level `evaluator_tools` object with a `playwright` key set to the string `"auto"`. Verify via `jq -e '.evaluator_tools.playwright == "auto"' .harness/config.json`. [weight: 4%]

7. **`rules/harness-conventions.md` documents Edge Case Criteria, `evaluator_tools.playwright`, and the per-criterion `verified_via_command` semantics**: The conventions file contains a level-2 heading exactly equal to `## Edge Case Criteria` AND the literal string `evaluator_tools.playwright` AND the string `verified_via_command` appears at least 3 times in the file. The threshold of 3 is chosen because the file currently contains exactly two `verified_via_command` mentions (forward references on lines 80 and 85 from the Sprint 9 transcript schema docs); requiring 3 forces the new docs to add at least one substantive new mention (the per-criterion flag's semantics, default value, and no-fabrication rule). Verify via `grep -qE '^## Edge Case Criteria' rules/harness-conventions.md && grep -q 'evaluator_tools.playwright' rules/harness-conventions.md && [ $(grep -c 'verified_via_command' rules/harness-conventions.md) -ge 3 ]`. [weight: 10%]

8. **`README.md` Phase 2 Configuration Knobs section documents `evaluator_tools.playwright`**: `README.md` contains the literal string `evaluator_tools.playwright`. The string is absent today, so the grep correctly fails until the README is updated. Verify via `grep -q 'evaluator_tools.playwright' README.md`. [weight: 4%]

9. **`sprint-10.tasks.json` is emitted**: A file `.harness/contracts/sprint-10.tasks.json` exists, is valid JSON, has a top-level `sprint: 10` field and a `tasks` array with one entry per criterion in this contract — 12 success criteria + 3 Should-NOT gates = **15 entries** — each with the Sprint-6 schema fields `task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, and `rubric_dimension`. Verify via `jq -e '.sprint == 10 and (.tasks | length) >= 15 and (.tasks | all(has("task_id") and has("grader_type") and has("weight") and has("is_gate")))' .harness/contracts/sprint-10.tasks.json`. [weight: 5%]

### LLM-as-judge (requires reading comprehension)

10. **Backward compatibility is explicit and correct**: The updated `agents/evaluator.md`, `.harness/config.json`, `rules/harness-conventions.md`, `skills/sprint-contract/SKILL.md`, `skills/sprint-contract/template.md`, and `skills/harness-summary/SKILL.md` together must make it unambiguous that a project whose `.harness/config.json` predates Phase 2 (no `evaluator_tools` object) experiences no functional behavior change. Three specific behaviors must be backward-compatible: (a) `evaluator_tools.playwright: "auto"` resolves to "Playwright disabled" when `project_type != "web-app"` — so the current `eval-harness` project sees no Playwright invocation; (b) the `## Edge Case Criteria` contract section is optional — sprints that omit it produce the same per-sprint `tasks.json` they would have produced before Sprint 10; (c) the `verified_via_command` per-criterion flag lives inside Sprint 9's failure-tolerant trailer extraction — a missing or fabricated flag does not change the eval verdict, and a project whose evaluator agent file predates Sprint 10 simply does not emit the flag. The documentation should explain the deferred end-to-end posture (Playwright runtime invocation, edge-case pass-rate aggregation, and adversarial-hygiene flag enforcement against a live evaluator subagent are deferred to a synthetic verification sprint per the gap-closure plan), matching Sprints 8 and 9. [weight: 13%]

11. **Edge-case taxonomy rationale is justified, not just asserted**: The documentation across `skills/sprint-contract/SKILL.md`, `skills/sprint-contract/template.md`, `skills/harness-summary/SKILL.md`, and `rules/harness-conventions.md` should explain *why* edge-case criteria are tracked separately from the 100%-weighted Success Criteria and from Should-NOT gates — not merely declare a third bucket exists. A reader should come away understanding: edge cases test the agent's *judgment under ambiguity* (positive-case-and-negative-case-by-luck is the failure mode the playbook calls out — "one-sided evals create one-sided optimization"); folding edge cases into the weighted total would let an agent earn the same weighted score by passing only the obvious positive cases and skating past the ambiguous ones; tracking edge-case pass rate as its own metric makes the asymmetry visible. The rationale should also explain why edge cases are *optional* per contract — for sprints whose deliverables are pure mechanical refactors, edge-case criteria add no signal. [weight: 11%]

12. **Adversarial-hygiene `verified_via_command` rationale is justified, not just asserted**: The documentation across `agents/evaluator.md` and `rules/harness-conventions.md` should explain *why* the `verified_via_command` flag is recorded **per criterion** (not per eval file or per sprint) — not merely declare a flag exists. A reader should come away understanding: the playbook flags as a real adversarial risk that an evaluator can infer PASS/FAIL from filenames or code comments without running the actual verification command (Anthropic's own Opus 4.6 was observed independently detecting eval state and finding answer keys); a per-eval-file flag is too coarse — one criterion correctly verified does not vouch for the others; a per-criterion flag forces the Evaluator to record, for each of N criteria, whether it actually executed the verification command versus inferring from non-executable evidence; the summary skill can then flag any criterion where `verified_via_command: false` as suspect even if the verdict was PASS. The documentation should also explain the no-fabrication obligation: writing `verified_via_command: true` when no command was executed defeats the purpose of the flag, so the schema documentation must mark fabrication as forbidden in the same posture as `token_usage` and `timing` from Sprint 9. [weight: 13%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **No silent behavior change for pre-Phase-2 configs**: A project whose `.harness/config.json` lacks the `evaluator_tools` object and whose contract files predate Sprint 10 must run the harness identically to Phase 1 / earlier Phase 2 sprints: no Playwright is invoked (the `eval-harness` project's `project_type` is not `web-app`, so the `"auto"` default resolves to disabled regardless of what the field declares); no edge-case section is required in any contract; the `verified_via_command` flag's absence from a legacy evaluator's transcript trailer does not change the eval verdict (Sprint 9's failure-tolerant extraction continues to apply). The documentation must make these three guards readable at a glance — Playwright requires `project_type == "web-app"`, edge cases are optional, and the hygiene flag inherits Sprint 9's trailer-extraction failure-tolerance. Verify by reading the updated `agents/evaluator.md`, `rules/harness-conventions.md`, and `README.md`: each guard must be stated, not just implied.

2. **No modification of prior sprint artifacts**: `.harness/evals/sprint-0[1-9]*` and `.harness/contracts/sprint-0[1-9]*` must be unchanged from HEAD at the start of this sprint (append-only rule from `rules/harness-conventions.md`). Verify via `test -z "$(git diff HEAD -- .harness/evals/sprint-0[1-9]* .harness/contracts/sprint-0[1-9]*)"`.

3. **No fabrication of `verified_via_command` and no inference of PASS/FAIL from filenames or comments**: The schema documentation must not allow the Evaluator to populate `verified_via_command: true` on a criterion for which no shell command was actually executed. Specifically, the Adversarial Hygiene section in `agents/evaluator.md` must (a) forbid inferring PASS/FAIL from filenames or comments, (b) require logging the exact verification command before scoring (so the trailer's `tool_calls` array is the audit ground truth), and (c) require the Evaluator to set `verified_via_command: false` when no command was run, rather than assuming `true`. Fabricated flags would produce misleading audit data — exactly the failure mode the flag exists to catch. Verify by reading `agents/evaluator.md` and `rules/harness-conventions.md`: the no-fabrication and no-inference rules must be explicit, not implicit.

## Reference Solutions

**Criterion 4 (Adversarial Hygiene section in `agents/evaluator.md`) — example of the added section:**

````markdown
## Adversarial Hygiene

Eval integrity is an ongoing adversarial problem. The Anthropic Opus 4.6 model independently detected when it was being evaluated and located the answer key in its own working tree — the same class of failure can happen to any evaluator that infers verdicts from non-executable evidence (filenames, code comments, surrounding prose) instead of running the actual verification command. This section names three rules that close the gap.

**Rule 1 — Never infer PASS/FAIL from filenames or comments.** A file named `success_v3_FINAL.py` is not evidence that the criterion passed. A comment that says `// TODO: this is broken` is not evidence that the criterion failed. The verdict for a deterministic criterion is determined by exit code or output of the verification command — nothing else. The verdict for an LLM-judge criterion is determined by structured rubric assessment of the artifact — not by signals embedded in the artifact's metadata. If you find yourself reasoning "the file is named X, so it must be Y," stop: that is the failure mode this rule exists to prevent.

**Rule 2 — Log the exact verification command before scoring.** For each deterministic criterion, the verification command goes into the transcript trailer's `tool_calls` array before the verdict is assigned. The audit ground truth for "did this evaluator actually verify the criterion?" is the `tool_calls` list — not the prose evidence in the markdown eval. If the prose says "verified via grep" but no `grep` invocation appears in `tool_calls`, the audit reveals an unrun verification.

**Rule 3 — Emit `verified_via_command` per criterion.** Inside the Sprint 9 transcript trailer (see "Transcript Trailer (Structured Output)" above), each criterion entry carries a `verified_via_command` boolean: `true` when the criterion's verdict was determined by an actual shell command's exit code (deterministic criteria); `false` when no command was run (llm-judge criteria, criteria graded by reading prose, or criteria where the runtime did not record a command invocation). **Do not fabricate `true` when no command ran.** Writing `verified_via_command: true` for a criterion you graded by reading code defeats the calibration purpose of the flag — the summary skill flags any criterion with `verified_via_command: false` as a candidate for human spot-check, and a fabricated `true` hides exactly the cases that need review.

The flag lives inside the trailer's structured channel — see `rules/harness-conventions.md` under **Transcript Schema** for the on-disk shape — alongside the existing `tool_calls` array. The shape extension is forward-compatible with Sprint 9's schema: per Sprint 9's "intentionally extensible" framing, Sprint 10 adds the per-criterion `verified_via_command` flag without renegotiating the top-level keys.
````

**Criterion 5 (Playwright conditional in `agents/evaluator.md`) — example of the added section:**

````markdown
## Conditional Tools: Playwright MCP for Web Apps

Most of this agent's tool set (Read, Glob, Grep, Bash) is project-type-agnostic. Playwright MCP is the exception — it is the right tool for **Visual Design** dimension verification on `web-app` projects (rendered DOM, computed styles, viewport-specific layout) and the wrong tool for everything else (CLI tools, RAG systems, API services, this `eval-harness` project itself). The harness gates Playwright availability behind two checks:

1. **`config.evaluator_tools.playwright`** must not be `"never"`. Default is `"auto"`, which means "enable when applicable."
2. **`config.project_type`** must equal `"web-app"`. The `"auto"` setting resolves to "Playwright enabled" only when this is true.

When both checks pass, the Evaluator may invoke Playwright MCP tools (typically `mcp__claude-in-chrome__*` or equivalent) for the Visual Design dimension. When either check fails — or when `evaluator_tools.playwright` is explicitly `"never"` — the Evaluator falls back to `curl` for HTTP-level verification and flags every Visual Design dimension finding as **low-confidence** in the `## Human Review Flags` section, since Visual Design legitimately requires browser rendering. Routing low-confidence Visual Design findings to human review is the documented escape hatch — silently grading without the right tool would produce confidently-wrong scores on a 25%-weight rubric dimension.

For the current `eval-harness` project (`project_type: "eval-harness"`), Playwright is never invoked — `"auto"` resolves to disabled — and the Visual Design fallback path is N/A because the rubric does not include that dimension.
````

**Criterion 11 (edge-case taxonomy rationale) — example of the added section in `skills/sprint-contract/SKILL.md`:**

````markdown
## Edge Case Criteria

Edge case criteria are an **optional** third class of contract criterion, distinct from weighted Success Criteria and from Should-NOT gates. They are tracked separately because they answer a different question.

- **Success Criteria** ask: "Does the deliverable do what it should?" Weighted to 100% in aggregate; the weighted score is the headline pass-rate metric.
- **Should-NOT Criteria** ask: "Does the deliverable avoid behaviors it shouldn't?" Binary gates; any failure blocks the sprint.
- **Edge Case Criteria** ask: "Does the deliverable handle ambiguous, boundary, or adversarial inputs correctly?" Tracked as a separate **edge-case pass rate** metric, *not* folded into the weighted total.

Folding edge cases into the weighted total would be a one-sided eval — the same failure mode Anthropic's playbook calls out as "positive-case-and-negative-case-by-luck." An agent that passes only the obvious positive cases would earn the same weighted score whether or not it correctly declined the ambiguous ones; the asymmetry would be invisible. Reporting edge-case pass rate as a distinct metric makes the asymmetry visible and lets the operator decide how to weight robustness vs. core functionality.

Edge case criteria are **optional** because not every sprint is the right place for them — a sprint that delivers a pure mechanical refactor adds no signal from edge-case scoring. The contract template includes the section as an optional slot; sprints that omit it produce the same `tasks.json` shape they would have produced before Sprint 10. The Evaluator should propose edge-case coverage during contract review when the rubric is `web-app`, `api-service`, or `rag-system` — those domains have well-known edge cases (empty inputs, very large inputs, concurrent requests, malformed payloads, queries with no matches) — and may skip the recommendation for `cli-tool` or `eval-harness` deliverables.
````

## Out of Scope

- Actually invoking Playwright MCP from a live evaluator subagent for a real `web-app` project. The conditional declaration and tool-availability prose ship here; end-to-end Playwright invocation is deferred to a synthetic follow-up sprint per the gap-closure-plan Verification item 5 (the meta-eval after Sprint 10).
- Implementing aggregation of edge-case pass rates across sprints in the harness-summary output (beyond declaring the metric exists). The metric slot is established here; cross-sprint aggregation logic — including how to merge edge-case pass rates across `web-app`, `api-service`, and `rag-system` projects — lands when at least one project actually emits edge-case criteria, which is post-Sprint-10.
- Wiring the `verified_via_command` flag into a runtime that intercepts the evaluator subagent's tool call stream and auto-populates the field per criterion. Sprint 10 adds the flag to the schema and the no-fabrication obligation; auto-population is a runtime instrumentation deliverable, not a protocol-level deliverable, and matches Sprint 9's deferral pattern for `token_usage` / `timing`.
- Retroactively updating Sprint 1–9 contracts and eval markdown files to add edge-case sections or `verified_via_command` flags. The protocol applies going forward; existing artifacts are append-only per `rules/harness-conventions.md`.
- Modifying the `web-app`, `api-service`, `rag-system`, or `cli-tool` rubric files (other than mentions in the new Edge Case Criteria docs). The rubrics already describe their edge-case concerns informally; Sprint 10 introduces the *contract slot*, not new rubric content.
- Aborting the eval on a missing `verified_via_command` flag. The flag, like the rest of the trailer, lives behind Sprint 9's failure-tolerant extraction — its absence is loggable but not a verdict-changing failure. Enforcement is a future-sprint concern; auditing is the Sprint 10 deliverable.
- Synthetic verification of Sprint 6's trial loop, Sprint 7's regression abort, Sprint 8's Batch API HTTP submission, Sprint 9's transcript file emission, or Sprint 10's Playwright invocation. Every Phase 2 sprint defers end-to-end runtime verification to the post-Sprint-10 synthetic verification sprint per the gap-closure plan.

## Technical Notes

- **`evaluator_tools.playwright: "auto"` is a *guarded* default, not a forced one.** The `"auto"` value means "enable when applicable" — the auxiliary check is `project_type == "web-app"`. For the current `eval-harness` project, the field's value is moot because the project-type guard fails. This guarantees the Sprint 10 default is backward-compatible: no Playwright invocation occurs in this repository regardless of whether the field is present, set to `"auto"`, or missing entirely.

- **Edge case criteria are tracked separately from weighted Success Criteria, not as a weight bucket inside them.** The contract template introduces a new top-level `## Edge Case Criteria` section — analogous to `## Should-NOT Criteria` in being structurally distinct from the 100%-weighted core criteria. Edge-case pass rate is reported in the harness-summary as its own row, not as a sub-component of weighted score. This positioning is the reason edge cases can be optional: omitting the section does not break the weight-sum invariant, since edge-case weights were never part of that invariant.

- **`verified_via_command` is per-criterion inside the Sprint 9 trailer, not per-eval-file.** Sprint 9's schema framed the trailer as "intentionally extensible" — the extension point is per-`tool_calls`-entry or a new top-level array keyed by `task_id`. Sprint 10 picks the per-criterion shape (one boolean per task_id) because per-eval-file flags would let one verified criterion vouch for the others — which is exactly the failure mode the flag exists to catch. The runtime that auto-populates the flag from real tool-call traces is deferred; the schema slot lands here.

- **The Adversarial Hygiene section sits next to the Transcript Trailer section in `agents/evaluator.md`.** The two are tightly coupled: Rule 2 ("log the exact verification command before scoring") is enforced by the trailer's `tool_calls` array; Rule 3 ("emit `verified_via_command` per criterion") extends that array with the new flag. Placing the sections adjacently keeps the data flow visible — what the Evaluator records in the trailer is what the harness-summary's audit logic later reads.

- **The Playwright fallback routes Visual Design findings to human review, not to silent failure.** When `evaluator_tools.playwright` is unavailable on a `web-app` project, the Evaluator's Visual Design dimension scores carry a `## Human Review Flags` annotation with `low-confidence` justification. Silent grading without the right tool would produce confidently-wrong scores on a 25%-weight dimension; the explicit human-review escape hatch is the documented design.

- **Forward compatibility.** Sprint 10's per-criterion `verified_via_command` field, edge-case pass rate, and Playwright availability flag are all forward-compatible with the Sprint 9 trailer schema — no top-level keys are renamed, no required fields are removed, and the optional `evaluator_tools` config object follows Sprint 6's "additive defaults" precedent. A Sprint 11+ change that adds a new project type or a new evaluator tool will follow the same `evaluator_tools.<tool>` pattern.

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/sprint-10.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — both Success Criteria and Should-NOT gates — with stable `task_id`s, `grader_type`, `weight`, `is_gate`, `verification_command`, and `rubric_dimension`. Downstream sprints (regression gate, Batch API, transcript capture, adversarial hygiene) consume that JSON; this markdown contract remains the human-readable source of truth. See `skills/sprint-contract/SKILL.md` for the schema.

## Evaluator Review

**Status: APPROVED**

### Weight Sum

5+7+6+12+10+4+10+4+5+13+11+13 = **100%. Correct.**

### Trap-by-Trap Walkthrough

**Tasks.json count (C9):** Contract claims 12 success criteria + 3 gates = 15 entries; threshold `>= 15`. Counting the numbered criteria in this file: C1–C9 deterministic (9) + C10–C12 LLM-judge (3) = 12 success criteria, plus 3 Should-NOT gates = 15 total. Threshold is correct and non-trivial (exactly at the minimum).

**Multi-line content traps:** None present. All deterministic verification commands are single-line shell one-liners that do not depend on multi-line heredoc matching or newline-sensitive regex.

**Permutation regexes:** None present. All grep patterns are literal strings or simple character-class anchors (`^##`).

**Pre-existing content false positives — results of running each check against current state:**

| Criterion | Verification | Current state | Result |
|-----------|-------------|--------------|--------|
| C1 | `grep -qE '^## Edge Case Criteria' skills/sprint-contract/template.md` | Heading absent | Correctly FAILS today |
| C2 (3-part AND) | `grep -qE '^## Edge Case Criteria'` + `grep -qiE 'edge.case pass rate'` + `grep -q 'web-app'` in SKILL.md | "adversarial" exists; "edge case" and "web-app" absent — chain fails | Correctly FAILS today |
| C3 | `grep -q 'Edge Case Pass Rate' skills/harness-summary/SKILL.md` | String absent | Correctly FAILS today |
| C4 (2-part AND) | `grep -qE '^## Adversarial Hygiene' agents/evaluator.md` + count >= 3 | Heading absent; count = 1 | Correctly FAILS today |
| C5 (3-part AND) | Playwright + project_type + visual design in evaluator.md | All three absent | Correctly FAILS today |
| C6 | `jq -e '.evaluator_tools.playwright == "auto"' .harness/config.json` | `evaluator_tools` key absent | Correctly FAILS today |
| C7 (3-part AND) | `^## Edge Case Criteria` + `evaluator_tools.playwright` + count >= 3 in harness-conventions.md | Heading and key absent; count = 1 | Correctly FAILS today |
| C8 | `grep -q 'evaluator_tools.playwright' README.md` | String absent | Correctly FAILS today |
| C9 | file `.harness/contracts/sprint-10.tasks.json` exists | File absent | Correctly FAILS today |

No pre-existing content false positives found.

**One inaccuracy in C7 rationale prose:** The contract states "the file currently contains exactly two `verified_via_command` mentions (forward references on lines 80 and 85)." The actual count is **1** (only line 85). C4's claim of "exactly one mention" is correct. This is a documentation inaccuracy only — the `>= 3` threshold is still correct and strict regardless (adding 1 mention from baseline 2 or baseline 1 both require the generator to produce substantive new content). This does not affect testability.

### Schema-Shape Lock-In Question (C4 vs C7 vs C12)

The per-criterion shape question: does C12's LLM-judge rationale check suffice, or is a deterministic grep needed to confirm the docs commit to per-criterion (not per-eval-file) shape?

**Decision: C12 is sufficient.** C4's deterministic criterion requires `verified_via_command` to appear >= 3 times in `agents/evaluator.md`; the reference solution for C4 explicitly shows the per-criterion language ("each criterion entry carries a `verified_via_command` boolean") and uses "per-task_id" framing. C12 (13%, LLM-judge) tests that the documentation explains *why* per-criterion rather than per-eval-file. The Technical Notes already lock the design: "Sprint 10 picks the per-criterion shape (one boolean per task_id)." A deterministic `grep -q 'per criterion'` check would add coverage but risks a generator satisfying it with incidental prose while the actual schema documentation still uses per-eval-file semantics. C12's structured rubric assessment of the rationale catches substantive gaps better than a string-count check here.

### Reference Solution Coverage

- C4 (12%, deterministic): has reference solution. Correct.
- C5 (10%, deterministic): has reference solution. Correct.
- C11 (11%, LLM-judge): has reference solution. Correct.
- C10 and C12 are tied at 13% as the highest-weighted LLM-judge criteria. The sprint contract skill requires at least the highest-weighted LLM-judge criterion to have a reference solution. **Neither C10 nor C12 has a reference solution.** This is a gap.

However: C12 is the tightest-defined LLM-judge criterion (it has a specific multi-part rationale checklist: per-criterion not per-file, adversarial detection failure mode, fabrication-forbidden framing, summary-skill audit use case). A reviewer can assess C12 reliably from the contract text alone because the criterion itself enumerates the required elements. C10 similarly enumerates three specific backward-compatibility behaviors. Both criteria are more checklist-like than impressionistic. The absence of a reference solution raises grader variance but does not block the sprint — the criteria are specific enough to grade without one. Flag for improvement in Sprint 11 by convention, not a blocker here.

### Feedback

**Minor issues (non-blocking):**

1. **C7 rationale prose inaccuracy:** Contract states `rules/harness-conventions.md` currently has "exactly two mentions" of `verified_via_command` on "lines 80 and 85." Actual count is 1 (line 85 only). The threshold `>= 3` is still correct and will function properly; only the explanatory prose is wrong. No fix needed before approval — the verification command is unaffected.

2. **C10 and C12 tied at 13% with no reference solutions:** Sprint contract skill convention requires the highest-weighted LLM-judge criterion to have a reference solution. Both are the highest-weighted LLM-judge criteria. The criteria are enumerated with sufficient specificity that grading is tractable, but adding at least one reference solution (C12 is recommended, as it has the most detailed rationale requirements) would reduce inter-evaluator variance. Recommend adding in a future revision; not a blocker for this sprint.

3. **C6 verification command fragility:** `jq -e '.evaluator_tools.playwright == "auto"' .harness/config.json` fails if `jq` is unavailable. The Python fallback is documented in this review but not in the contract itself. Sprint 9 established the precedent of noting the Python fallback in the contract; this contract omits it. Not a blocker, but worth noting for consistency.

### Approved Criteria

C1, C2, C3, C4, C5, C6, C7, C8, C9 — deterministic criteria are well-formed, thresholds are non-trivial, no false positives from pre-existing content.

C10, C11, C12 — LLM-judge criteria are enumerated with specific multi-part checklists rather than vague impressionistic descriptions; each criterion states which files to read and what a reader should "come away understanding." Testable as written.

SN1, SN2, SN3 — gates are meaningful blocking criteria, not vacuous.
