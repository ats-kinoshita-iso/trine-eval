# Sprint 09 Contract: Full Transcript Capture

## What I Will Build

Close Gap 6 (full transcript capture) from the playbook alignment plan: introduce a structured JSON transcript per evaluator run that records sprint/round/trial identifiers, message and tool-call traces, token usage, timing, and a thinking summary, written to `.harness/transcripts/sprint-{NN}-r{R}-t{T}.json` (or `sprint-{NN}-r{R}.json` for single-trial mode). The Evaluator agent emits a structured JSON trailer at the end of its markdown eval file; the harness-sprint workflow extracts that trailer and writes the transcript file. The harness-summary skill links the corresponding transcript path next to every FAIL criterion entry and any grader-disagreement entry so a human auditor can trace the verdict back to the exact tool calls the Evaluator made. Add `config.transcripts.capture` (default `true`) and `config.transcripts.retain_days` (default `30`) to `.harness/config.json`. Document the schema and the file-path convention in `rules/harness-conventions.md`. Like Sprint 8, Sprint 9 ships the protocol and trigger conditions, not a forced runtime hookup — end-to-end trailer extraction against a real evaluator subagent is deferred to a synthetic verification sprint per the gap-closure plan, so a project whose existing config and agent files predate this work experiences no behavior change.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **`.harness/transcripts/` directory and README exist**: The path `.harness/transcripts/` exists as a directory and contains a `README.md` explaining what the directory is for, the file naming convention `sprint-{NN}-r{R}-t{T}.json` (or `sprint-{NN}-r{R}.json` for single-trial), and a pointer to `rules/harness-conventions.md` for the full schema. Verify via `test -d .harness/transcripts && test -f .harness/transcripts/README.md`. [weight: 6%]

2. **config.json declares `transcripts.capture` and `transcripts.retain_days`**: `.harness/config.json` contains a top-level `transcripts` object with keys `capture` (boolean, default `true`) and `retain_days` (integer, default `30`). Verify via `jq -e '.transcripts.capture == true and (.transcripts.retain_days | type == "number") and .transcripts.retain_days == 30' .harness/config.json`. [weight: 7%]

3. **harness-sprint SKILL adds a Transcript Capture section in Step 3**: `skills/harness-sprint/SKILL.md` contains a section (heading or labeled subsection inside Step 3 Evaluation) that uses the word "Transcript" or "Transcripts" (case-insensitive) and explicitly references (a) `config.transcripts.capture`, (b) the file path under `.harness/transcripts/`, (c) the trailer extraction step (workflow reads the evaluator's markdown eval, extracts the JSON trailer, writes it to the transcript file). Verify via `grep -qi 'transcript' skills/harness-sprint/SKILL.md && grep -q 'transcripts.capture' skills/harness-sprint/SKILL.md && grep -qE '\.harness/transcripts/' skills/harness-sprint/SKILL.md && grep -qi 'trailer' skills/harness-sprint/SKILL.md`. [weight: 11%]

4. **evaluator.md adds a Transcript Trailer instruction**: `agents/evaluator.md` contains a section (or subsection) instructing the evaluator to emit a structured JSON trailer at the end of its markdown eval file, distinct from the existing "Transcript Review" section (which is about reviewing markdown evals for grader-quality patterns — the trailer is the new structured-data channel). The new section must use the word "trailer" (case-insensitive) and reference at least three required schema field names by literal name: `messages`, `tool_calls`, `token_usage`, `timing`, `thinking_summary`. Verify via `grep -qi 'trailer' agents/evaluator.md && grep -q 'thinking_summary' agents/evaluator.md && grep -q 'tool_calls' agents/evaluator.md && grep -q 'token_usage' agents/evaluator.md`. [weight: 10%]

5. **harness-conventions.md documents the Transcript schema with all required fields**: `rules/harness-conventions.md` contains a section about the structured JSON transcript that includes (a) the file-path convention beginning with `.harness/transcripts/`, (b) the `transcripts.capture` and `transcripts.retain_days` config knobs, and (c) every required schema field name in JSON-quoted form: `"sprint"`, `"round"`, `"trial"`, `"messages"`, `"tool_calls"`, `"token_usage"`, `"timing"`, `"thinking_summary"`. Verify via `grep -qi 'transcript' rules/harness-conventions.md && grep -q 'transcripts.capture' rules/harness-conventions.md && grep -q 'transcripts.retain_days' rules/harness-conventions.md && grep -qE '\.harness/transcripts/' rules/harness-conventions.md && grep -q '"sprint"' rules/harness-conventions.md && grep -q '"round"' rules/harness-conventions.md && grep -q '"trial"' rules/harness-conventions.md && grep -q '"messages"' rules/harness-conventions.md && grep -q '"tool_calls"' rules/harness-conventions.md && grep -q '"token_usage"' rules/harness-conventions.md && grep -q '"timing"' rules/harness-conventions.md && grep -q '"thinking_summary"' rules/harness-conventions.md`. [weight: 12%]

6. **harness-summary SKILL references transcript paths in its summary output**: `skills/harness-summary/SKILL.md` documents that the cross-sprint summary output links the corresponding transcript path for FAIL criterion entries and grader-disagreement entries. The skill must reference the literal path prefix `.harness/transcripts/` and use the word "transcript" (case-insensitive) in the linking context. Verify via `grep -qE '\.harness/transcripts/' skills/harness-summary/SKILL.md && grep -qi 'transcript' skills/harness-summary/SKILL.md`. [weight: 9%]

7. **sprint-09.tasks.json is emitted**: A file `.harness/contracts/sprint-09.tasks.json` exists, is valid JSON, has a top-level `sprint: 9` field and a `tasks` array with one entry per criterion in this contract — 11 success criteria + 3 Should-NOT gates = **14 entries** — each with the Sprint-6 schema fields `task_id`, `criterion`, `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`. Verify via `jq -e '.sprint == 9 and (.tasks | length) >= 14 and (.tasks | all(has("task_id") and has("grader_type") and has("weight") and has("is_gate")))' .harness/contracts/sprint-09.tasks.json`. [weight: 6%]

### LLM-as-judge (requires reading comprehension)

8. **Backward compatibility is explicit and correct**: The updated `skills/harness-sprint/SKILL.md`, `agents/evaluator.md`, and `rules/harness-conventions.md` together must make it unambiguous that a project whose `.harness/config.json` predates Phase 2 (no `transcripts` object) and whose evaluator agent file predates Sprint 9 experiences no functional behavior change. The `transcripts.capture: true` default describes Phase-2 declared intent for fresh installs that pick up the updated agent file; for legacy projects, no transcript file is forced to exist on disk because the legacy evaluator does not emit a trailer for the workflow to extract. A reader should be able to identify, for each new config field, the default value and the sentence(s) that explain the protocol-vs-dispatcher posture: end-to-end transcript writing against a live evaluator subagent is deferred to a synthetic verification sprint per the gap-closure plan, matching Sprint 8's posture for `thinking.profile`. [weight: 13%]

9. **Schema field rationale is justified, not just asserted**: The documentation across `rules/harness-conventions.md` and `agents/evaluator.md` should explain *why* each schema field is captured — not merely list the field names. A reader should come away understanding: `messages` exists because reading the actual model output is the only way to verify a grader's reasoning chain; `tool_calls` exists because adversarial-hygiene checks (Sprint 10's `verified_via_command` flag) need to confirm a verification command actually ran; `token_usage` exists because cost regressions are otherwise invisible; `timing` exists because slow evals are themselves a quality signal; `thinking_summary` exists because the adaptive-thinking declaration from Sprint 8 produces internal reasoning that is otherwise lost when only the markdown eval is preserved. [weight: 8%]

10. **FAIL/disagreement linkage rationale is justified**: The `skills/harness-summary/SKILL.md` transcript-linking section should explain *why* transcripts are linked specifically for FAIL criteria and grader disagreements — and not for every PASS entry. A reader should come away understanding that PASS verdicts on deterministic criteria are usually self-explanatory (the verification command exited 0), while FAILs and disagreements are the points where a human auditor most needs to read what the evaluator actually did — what tools it called, what evidence it weighed, and where its conclusion came from. The link is a calibration audit trail, not summary boilerplate. [weight: 8%]

11. **Trailer extraction protocol is well-defined**: The `skills/harness-sprint/SKILL.md` Transcript Capture section should describe the trailer extraction protocol precisely enough that two independent implementers would produce equivalent file contents from the same evaluator markdown eval. A reader should understand: the Evaluator emits a delimited JSON block (e.g., a fenced ` ```json ` code block under a section heading) at the end of its markdown eval file; the workflow reads that block, parses it, and writes it verbatim to `.harness/transcripts/sprint-{NN}-r{R}-t{T}.json`; if the trailer is missing or malformed JSON, the workflow proceeds without writing a transcript file rather than failing the eval. [weight: 10%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **No silent behavior change for pre-Phase-2 configs**: A project whose `.harness/config.json` lacks the `transcripts` object and whose agent files predate Sprint 9 must run the harness identically to Phase 1: no transcript files are forced to exist, no errors are raised when an evaluator subagent does not emit a trailer, and no preexisting workflow steps change semantics. The `transcripts.capture: true` default applies to projects that pick up the updated agent files (and therefore start emitting trailers); for legacy installs, the workflow's Transcript Capture step is a no-op when no trailer is present in the evaluator's markdown eval. Verify by reading the updated workflow and conventions — every transcript-write action must be guarded on a successfully extracted trailer, never unconditionally executed.

2. **No modification of prior sprint artifacts**: `.harness/evals/sprint-0[1-8]*` and `.harness/contracts/sprint-0[1-8]*` must be unchanged from HEAD at the start of this sprint (append-only rule from `rules/harness-conventions.md`). Verify via `test -z "$(git diff HEAD -- .harness/evals/sprint-0[1-8]* .harness/contracts/sprint-0[1-8]*)"`.

3. **No fabrication of fields the evaluator cannot actually compute**: The schema documentation must not require the Evaluator to populate every field with high-fidelity values. Specifically, runtime-instrumentation-dependent fields (`token_usage.input`, `token_usage.output`, `token_usage.cache_hit`, `timing.ttft_ms`, `timing.total_ms`) must be documented as runtime-supplied or best-effort with `null` allowed when the agent runtime does not expose them. The Evaluator must be explicitly told not to invent or estimate values it cannot observe — fabricated token counts or timing metrics would produce misleading audit data and contradict the calibration purpose of transcript capture. Verify by reading `agents/evaluator.md` and `rules/harness-conventions.md`: the runtime-dependent fields must be marked nullable / best-effort, not asserted as required-and-known.

## Reference Solutions

**Criterion 4 (Evaluator Transcript Trailer instruction) — example of the added section in `agents/evaluator.md`:**

````markdown
## Transcript Trailer (Structured Output)

In addition to your markdown eval at `.harness/evals/sprint-{NN}-r{R}-t{T}.md` (or
`-r{R}.md` when `config.trials == 1`), emit a structured JSON trailer at the end of
that same file under a final `## Transcript Trailer` heading, as a fenced JSON code
block. The trailer is the source data for `.harness/transcripts/sprint-{NN}-r{R}-t{T}.json`:
the harness-sprint workflow reads your markdown file, extracts the trailer block,
parses it as JSON, and writes it to the transcripts directory.

This is distinct from the "Transcript Review" section above — Transcript Review is
about reading prior markdown evals to spot grader-quality issues; the Transcript
Trailer is the new structured-data channel that makes evaluator behavior auditable
across runs.

Required schema (top-level keys):
- `"sprint"` — integer, the sprint number you graded.
- `"round"` — integer, round 1 for the initial eval, R+1 for retry round R.
- `"trial"` — integer, 1 for single-trial mode, otherwise the 1..config.trials index.
- `"messages"` — array of `{role, content}` objects summarizing the message exchange
  during your evaluation. May be a high-level summary if the full message array is
  not directly available to you.
- `"tool_calls"` — array of `{name, arguments_summary, result_summary}` objects, one
  per tool call you made during the eval. You know what tools you called — list them.
- `"token_usage"` — object with integer keys `"input"`, `"output"`, `"cache_hit"`.
  These are runtime-supplied; if your runtime does not expose them, write `null` for
  each. Do not guess.
- `"timing"` — object with integer keys `"ttft_ms"`, `"total_ms"`. Runtime-supplied
  per the same rule as `token_usage` — use `null` when unknown.
- `"thinking_summary"` — string. Your one-paragraph summary of how you reasoned
  about this evaluation overall. Sprint 8's adaptive-thinking declaration means your
  internal reasoning is otherwise lost; this field captures the audit trail.

Example trailer (note runtime-supplied fields set to null when unknown):

```json
{
  "sprint": 9,
  "round": 1,
  "trial": 1,
  "messages": [{"role": "user", "content": "Read the contract and grade each criterion."}],
  "tool_calls": [
    {"name": "Bash", "arguments_summary": "test -d .harness/transcripts", "result_summary": "exit 0"},
    {"name": "Bash", "arguments_summary": "jq -e ... config.json", "result_summary": "exit 0"}
  ],
  "token_usage": {"input": null, "output": null, "cache_hit": null},
  "timing": {"ttft_ms": null, "total_ms": null},
  "thinking_summary": "Tested every deterministic criterion via grep/jq, then read the prose for LLM-judge criteria. The backward-compat criterion was the closest call — verified by..."
}
```

Do not fabricate values for runtime-instrumented fields. Empty arrays and `null` are
preferred over guessed numbers; the calibration value of transcripts depends on
their fidelity.
````

**Criterion 8 (backward compatibility) — example of the README/SKILL sentence pattern:**

```markdown
A project whose `.harness/config.json` lacks the `transcripts` object and whose
evaluator agent file predates Sprint 9 experiences no functional behavior change.
Sprint 9 ships the protocol — agent declarations for trailer emission and workflow
prose for trailer extraction — but end-to-end transcript writing against a live
evaluator subagent is deferred to a synthetic verification sprint per the
gap-closure plan, matching Sprint 8's posture for `thinking.profile`. The
`transcripts.capture: true` default describes Phase-2 declared intent for fresh
installs that pick up the updated agent file; for legacy projects, no transcript
file is forced to exist on disk because the legacy evaluator does not emit a
trailer for the workflow to extract.
```

**Criterion 11 (trailer extraction protocol) — example of the harness-sprint Step 3e prose:**

```markdown
### 3e. Transcript Capture (optional)

Read `config.transcripts.capture` (default `true`). When truthy, after the
Evaluator's markdown eval file is written, the workflow extracts a structured
JSON trailer from the eval file and writes it to a sibling transcript file:

1. **Locate the trailer.** Read the markdown eval (`.harness/evals/sprint-{NN}-r{R}-t{T}.md`
   or the single-trial `.harness/evals/sprint-{NN}-r{R}.md`). Find the last
   `## Transcript Trailer` (or equivalent) heading; the body of that section is a
   fenced ` ```json ` code block.
2. **Parse the trailer.** Extract the JSON between the fences. If the section is
   missing, the fence is malformed, or the JSON does not parse, skip the rest of
   this step — do NOT fail the eval.
3. **Write the transcript.** Write the parsed JSON verbatim to
   `.harness/transcripts/sprint-{NN}-r{R}-t{T}.json` (or `sprint-{NN}-r{R}.json`
   for single-trial mode). The file is the transcript record consumed by
   harness-summary and any future audit tooling.

Backward compatibility: when `config.transcripts.capture` is `false`, this step
is skipped entirely. When the field is absent (legacy config), the default is
`true` per Phase-2 intent — but the no-op fallback in step 2 means a legacy
evaluator that does not emit a trailer produces no transcript file, preserving
Phase-1 disk state.
```

## Out of Scope

- Actually running an end-to-end eval that produces a real `.harness/transcripts/sprint-09-r1.json` file in this sprint. The protocol and the schema ship here; end-to-end transcript-file emission against a live evaluator subagent is deferred to a synthetic follow-up sprint per the gap-closure-plan Verification item 4 (the meta-eval after Sprint 10).
- Implementing a runtime that programmatically intercepts the evaluator's message stream and serializes it. The trailer is emitted by the evaluator and extracted by the workflow from the markdown eval file — this is a protocol-level deliverable, not a runtime instrumentation deliverable.
- Retention enforcement (deleting transcript files older than `transcripts.retain_days`). The knob is documented as policy; the actual cleanup runs out-of-band or in a future sprint.
- Linking transcripts from PASS criteria — the FAIL/disagreement linkage in Criterion 10 is the deliberate scope, since PASS deterministic criteria are typically self-explanatory.
- Updating Sprint 1–8 contracts and eval markdown files retroactively to add transcript pointers. The protocol applies going forward; existing eval markdown files are append-only.
- Playwright MCP integration, edge-case criteria, and adversarial hygiene flags (Sprint 10).
- Wiring `thinking.profile` runtime dispatch from Sprint 8 to populate `thinking_summary` automatically. The schema declares the field; the Evaluator's prose summary fills it for now.

## Technical Notes

- **The transcript trailer is a markdown-embedded JSON block, not a separate runtime channel.** The Evaluator emits its eval as a markdown file ending with a fenced JSON code block under a `## Transcript Trailer` (or equivalent) heading. The workflow extracts that block and writes it to `.harness/transcripts/`. This avoids requiring runtime instrumentation while still producing a machine-readable transcript record.
- **Runtime-dependent fields are explicitly nullable.** `token_usage` and `timing` depend on runtime instrumentation that the evaluator agent typically cannot observe directly. The schema marks those fields as nullable/best-effort; the Evaluator emits `null` rather than fabricating values. A future runtime hookup can populate them faithfully without a schema migration.
- **The trailer extraction is failure-tolerant.** If the Evaluator's markdown eval lacks a trailer, or the trailer is malformed JSON, the workflow proceeds without writing a transcript file. The eval verdict is unaffected — transcripts are an audit artifact, not a grading input. This matches Sprint 7's append-only and fail-tolerant posture for regression entries.
- **Linking from FAIL/disagreement entries is the calibration design choice.** PASS deterministic criteria self-explain (the verification command's exit code is the answer); FAIL and disagreement entries are where a human auditor needs to read what the evaluator actually did. Linking only those entries keeps the summary readable while preserving audit access where it matters.
- **The schema is intentionally extensible.** Sprint 7 added a single `graduated_from_sprint` audit field to a copied schema; Sprint 9 follows the same posture — define the trailer's existence and core fields, leave room for forward-compatible additions. Sprint 10's adversarial hygiene flags (`verified_via_command`) will live in this same JSON trailer at a per-criterion level without renegotiating the top-level schema.
- **Forward wiring to Sprint 10**: Sprint 10's `verified_via_command` per-criterion flag will appear inside the trailer as either an extension to `tool_calls` entries or a new top-level array. Sprint 9 only needs to establish the trailer; the per-criterion adversarial flag lands in Sprint 10.

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/sprint-09.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — both Success Criteria and Should-NOT gates — with stable `task_id`s, `grader_type`, `weight`, `is_gate`, `verification_command`, and `rubric_dimension`. Downstream sprints (regression gate, Batch API, Playwright, adversarial hygiene) consume that JSON; this markdown contract remains the human-readable source of truth. See `skills/sprint-contract/SKILL.md` for the schema.

## Evaluator Review

**Status: APPROVED**

### Feedback

The contract is testable, specific, and well-constructed. All deterministic criteria use grep/jq commands that were verified against the current state of each target file — no false positives were found for the pre-Sprint-9 codebase, and each verification command correctly fails until the Generator adds the required content.

**Confirmed traps from Sprint 7/8 reviews — all addressed:**

1. **tasks.json threshold** — C7 correctly states "11 success criteria + 3 Should-NOT gates = **14 entries**" and uses `(.tasks | length) >= 14`. Math verified: 7 deterministic + 4 LLM-judge = 11 success; 3 gates; 14 total. The threshold matches exactly, avoiding the Sprint 08 round-1 blocker.

2. **Single-line grep on multi-line content** — No frontmatter greps in this sprint. The keyword greps (C3, C4, C5, C6) are file-wide searches, not YAML-structure searches, so multi-line content is irrelevant. No trap.

3. **Permutation regexes on docs** — Not used. All greps are independent existence checks. No trap.

4. **Pre-existing content creating false positives** — Checked against every target file:
   - `grep -qi 'trailer' agents/evaluator.md` → NOT FOUND today (no false positive for C4). The existing "Transcript Review" section does not contain the word "trailer".
   - `grep -qi 'transcript' skills/harness-sprint/SKILL.md` → NOT FOUND today (no false positive for C3).
   - Criterion 6 (`grep -qi 'transcript' skills/harness-summary/SKILL.md`): the word "transcript" DOES appear today at lines 154 and 161 (ACI Self-Optimization section). However, Criterion 6's AND-chain requires BOTH that grep AND `grep -qE '\.harness/transcripts/' skills/harness-summary/SKILL.md` — and the path grep correctly fails today. The AND logic means no false positive in the combined verification.
   - Criterion 5 (`grep -qi 'transcript' rules/harness-conventions.md`): the word "transcripts" appears today at line 34 (tasks.json schema description). Same AND-chain protection applies — `grep -q 'transcripts.capture'` fails on the current file, so the combined verification correctly fails pre-Sprint-9.

**SN1 and SN3 grader-type tagging (minor, non-blocking):**

SN1 ("Verify by reading the updated workflow and conventions") and SN3 ("Verify by reading `agents/evaluator.md` and `rules/harness-conventions.md`") are LLM-judge checks, not deterministic ones. The contract does not tag Should-NOT criteria with an explicit grader type in the markdown prose (consistent with prior sprint contracts), but the Generator must assign `grader_type: "llm-judge"` to these entries in `sprint-09.tasks.json`. SN2 ("test -z...") is deterministic. This was flagged as minor in Sprint 08's round-1 review for the same pattern — non-blocking for contract approval, but the Generator must act on it when emitting the JSON file.

**One observation on Criterion 5 (part 1 redundancy):**

The first grep in C5's chain (`grep -qi 'transcript' rules/harness-conventions.md`) already passes on the current file, making it a non-gate against the pre-Sprint-9 state. The real work is done by the remaining 11 greps. This is not a defect — the combined AND chain correctly fails today — but future contract reviewers should know that part 1 of C5's chain adds no additional signal beyond what the other parts already enforce.

**Criterion 4 field coverage:**

C4 requires the new section to reference "at least three" of the five named schema fields and verifies three (`thinking_summary`, `tool_calls`, `token_usage`). `messages` and `timing` are not independently grep-checked. This is intentional and acceptable: the reference solution includes all five, and the "at least three" language explicitly allows flexibility. No change needed.

### Missing Criteria

None. Every file listed in the gap-closure-plan Sprint 9 "Files to modify" section maps to at least one criterion:

- `.harness/transcripts/` directory → C1
- `.harness/config.json` (`transcripts.capture`, `transcripts.retain_days`) → C2
- `skills/harness-sprint/SKILL.md` (Transcript Capture section, trailer extraction) → C3
- `agents/evaluator.md` (Transcript Trailer instruction) → C4
- `rules/harness-conventions.md` (schema documentation) → C5
- `skills/harness-summary/SKILL.md` (FAIL/disagreement linkage) → C6
- `sprint-09.tasks.json` emission → C7
- Behavioral quality (backward compat, rationale, protocol precision) → C8–C11

### Approved Criteria

All criteria approved. Specifically:

- **C1** — straightforward file-existence check; clean.
- **C2** — jq-based config validation; `transcripts` key is absent from current `config.json`, so no false positive risk.
- **C3** — four-part AND chain; all four greps correctly fail on the current `harness-sprint/SKILL.md`; no false positive.
- **C4** — four-part AND chain; `trailer` is absent from current `evaluator.md`; the distinction from the existing "Transcript Review" section is made explicit in the criterion prose and reference solution.
- **C5** — twelve-part AND chain; eleven of the twelve greps correctly fail on the current `harness-conventions.md`; comprehensive schema field coverage.
- **C6** — two-part AND chain; the path grep correctly fails today; sufficient to gate the required new content.
- **C7** — count threshold matches 11+3=14; uses `>= 14` correctly.
- **C8** — highest-weighted LLM-judge (13%); has reference solution; backward-compat posture mirrors Sprint 8's approach to `thinking.profile`.
- **C9**, **C10** — rationale criteria; anchored to specific causal claims a reader must be able to identify; testable by reading comprehension.
- **C11** — trailer extraction protocol; reference solution provides precise enough spec that two implementers would converge; malformed-JSON fallback is explicit.
- **SN1** — LLM-judge gate; backward-compat guard semantics clearly stated.
- **SN2** — deterministic git-diff check; `sprint-0[1-8]*` correctly covers prior sprints 01–08 without catching the current sprint-09.
- **SN3** — LLM-judge gate; nullable fields and no-fabrication obligation are well-specified.

**Weight sum:** 6+7+11+10+12+9+6+13+8+8+10 = **100%** — verified correct.

**Reference solution coverage:** C4 (deterministic, 10%), C8 (LLM-judge, 13% — highest weighted), and C11 (LLM-judge, 10%) all have reference solutions. C9 and C10 (both 8% LLM-judge) do not, but C8's reference solution is the required one per the evaluator contract-review rules.
