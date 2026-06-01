---
name: sprint-contract
description: Template and protocol for Generator-Evaluator sprint contract negotiation
allowed-tools: Read, Write
---

# Sprint Contract

This skill provides the contract template and negotiation protocol for Generator-Evaluator agreement on sprint success criteria.

## Negotiation Protocol

1. **Generator proposes first** — Writes a draft contract using the template below
2. **Evaluator reviews** — Checks each criterion for:
   - **Testability:** Can this be verified automatically? (If it requires human judgment, it needs rewording)
   - **Completeness:** Are there obvious features in the sprint scope that have no criterion?
   - **Specificity:** Would two independent evaluators agree on pass/fail for this criterion?
3. **Revision rounds** — Max rounds configured in `.harness/config.json` (`contract_negotiation_rounds`, default 2)
4. **Timeout** — If the Evaluator hasn't responded after the Generator's proposal, proceed with the proposal as-is

## Contract Template

See `template.md` in this skill's directory for the full template.

## Weighted Criteria

Every success criterion carries a percentage weight reflecting its importance to the sprint deliverable.

**How to assign weights:**
- Higher weight = more important to the sprint's success. Weight critical functionality higher than cosmetic concerns.
- Typical range: 5–15% per criterion. Avoid concentrating >20% on a single criterion unless it is the sprint's core deliverable.

**Weight sum rule:** Success criteria weights must sum to exactly 100%. The evaluator computes a weighted score by multiplying each criterion's weight by its pass/fail result (1 or 0) and summing. This weighted score determines whether the sprint meets its pass threshold — a sprint can pass despite minor criterion failures if the weighted total exceeds the configured threshold.

**Should-NOT criteria do not carry weights.** They are gates: any Should-NOT failure is an automatic sprint FAIL regardless of the weighted score.

## Grader Types

Each criterion must be tagged with one of three grader types:

- **Behavioral** — Verified by *running* the artifact (invoking a skill, triggering a hook, executing a binary, calling a function) and observing the output, state change, or side effect. The strongest form of evidence: it proves the feature works, not just that the code exists.
- **Structural** — Verified by inspecting an artifact at rest (grep, jq, schema check, file existence, frontmatter field). Use for cheap pre-flight checks that gate a behavioral criterion, or for genuinely static artifacts (documentation, config schemas with no runtime).
- **LLM-as-judge** — Requires reading comprehension, subjective assessment, or nuanced evaluation that no command can capture. Use when neither behavioral nor structural verification is feasible.

**Behavioral coverage rule:** Behavioral criteria must hold **≥ 60% of total weight** across all success criteria. If a sprint genuinely has no behavioral surface (e.g., it produces only static documentation), state the reason in the contract's `## Technical Notes` so the Evaluator can verify the exception during contract review.

The evaluator attempts code-based verification first for every criterion (behavioral and structural both qualify). It falls back to LLM judgment only when the criterion genuinely requires subjective assessment. Crucially, the evidence standard differs by tag: behavioral criteria require execution evidence (command + observed result); structural criteria accept artifact inspection; reading-the-source to confirm a behavior is documented does NOT satisfy a behavioral criterion.

## Negative (Should-NOT) Criteria

Should-NOT criteria define behaviors that must NOT occur. They are graded **PASS when the behavior is absent** — the opposite of normal criteria.

Use Should-NOT criteria for:
- Regression guards (don't break existing functionality)
- Security invariants (don't expose stack traces, don't leak credentials)
- Architectural boundaries (don't violate separation of concerns)

## Reference Solutions

Reference solutions provide known-working outputs for criteria where grader calibration is valuable. They are **optional** — not every criterion needs one.

**When to include a reference solution:**
- LLM-as-judge criteria benefit most (reduces inter-judge disagreement)
- Criteria where the expected format/structure might be ambiguous
- The highest-weighted criterion in the contract should have one if it is LLM-judged

**Purpose:** Reference solutions calibrate grader accuracy. They give the evaluator a concrete example of what PASS looks like, reducing the chance of false-fail or false-pass judgments.

## Task Taxonomy: sprint-NN.tasks.json

After the contract is approved (Status: APPROVED from the Evaluator review), emit a sibling
`.harness/contracts/sprint-{NN}.tasks.json` file alongside the markdown contract. This is the
**machine-readable source of record** for the sprint's criteria — it feeds the regression gate
(Step 0.5), the Batch API submission grouping (Step 3d), and the harness-summary
saturation-graduation step that promotes always-passing criteria into a regression suite.

**When to emit:** right after the Evaluator writes `**Status: APPROVED**` and before the
Generator enters IMPLEMENTATION mode. Guarded by `config.taxonomy.emit_tasks_json`
(default `true`).

**Schema:** one entry per criterion in the approved contract — both Success Criteria and
Should-NOT gate criteria.

```json
{
  "sprint": 9,
  "tasks": [
    {
      "task_id": "s09-c1",
      "criterion": "<verbatim criterion text from the contract>",
      "grader_type": "behavioral",
      "weight": 8,
      "is_gate": false,
      "verification_command": "jq '.tasks | length' .harness/contracts/sprint-09.tasks.json",
      "rubric_dimension": "methodology_completeness"
    },
    {
      "task_id": "s09-sn1",
      "criterion": "<Should-NOT criterion text>",
      "grader_type": "structural",
      "weight": 0,
      "is_gate": true,
      "verification_command": "grep -c '^## Negotiation Protocol' plugins/trine-eval/skills/sprint-contract/SKILL.md",
      "rubric_dimension": "grading_architecture"
    }
  ]
}
```

**Field semantics:**

- `task_id` — Stable identifier: `s<NN>-c<N>` for success criteria (numbered from 1),
  `s<NN>-sn<N>` for Should-NOT gates. Stability matters because regression gates and
  transcript correlation key off this id across trials.
- `criterion` — Verbatim criterion text from the markdown contract (no paraphrasing).
  This is what the Evaluator and downstream tools read.
- `grader_type` — `"behavioral"`, `"structural"`, or `"llm-judge"`, matching the tag in
  the markdown contract. The cached v0.3.3 schema used a 2-way `"deterministic" | "llm-judge"`
  enum; this repo adopted the 3-way split in commit 408e8a2. The term `"deterministic"` is
  not used.
- `weight` — The percentage weight from the markdown contract. Gate (Should-NOT) criteria
  use `0` — they are binary, not weighted.
- `is_gate` — `true` for Should-NOT gates, `false` for scored success criteria.
- `verification_command` — For behavioral and structural criteria, a runnable shell command
  whose exit code or stdout determines PASS/FAIL. For llm-judge criteria, `null`. The
  regression gate executes these commands directly.
- `rubric_dimension` — Which rubric dimension this criterion informs. Valid values for this
  project: `methodology_completeness`, `grading_architecture`, `generator_evaluator_separation`,
  `context_engineering`, `extensibility_aci`. Used by harness-summary for per-dimension
  rollups.

**Note on `bucket` field:** The cached v0.3.3 schema includes a `bucket` field (integer 1–3)
referencing `rules/harness-conventions.md`. That rules file is not present in this repo. The
`bucket` field is **omitted** from this ported schema pending a separate port of
`rules/harness-conventions.md`. The harness-summary skill treats missing-`bucket` as `1`
(the most conservative reading) for all entries that lack the field.

**Self-bootstrap note:** Sprint 09 is the sprint that ports this schema into the in-repo
SKILL.md. Sprint 09's own `tasks.json` is therefore emitted *after* the schema port lands
(during or after IMPLEMENTATION mode), not at Step 1d. This avoids using the schema to
describe itself before it exists in-repo. This is a one-time exception for the porting
sprint itself; from Sprint 10 onward, `tasks.json` emission resumes at Step 1d as normal.

## Guidelines for Good Criteria

**Good criterion:** "GET /api/users returns 200 with a JSON array. Each user object contains id (number), name (string), and email (string)."

**Bad criterion:** "The API works correctly." (Too vague — what does "correctly" mean?)

**Good criterion:** "The search bar filters the list in real-time as the user types. Typing 'abc' with 100 items shows only items containing 'abc' within 200ms."

**Bad criterion:** "Search is fast." (What's fast? How do you measure it?)

Each criterion should describe:
- The action to take (input)
- The expected result (output)
- How to verify it (test method)

## No-Op Detection

Before finalizing a contract, run each behavioral and structural criterion's verification command against the current codebase. If a criterion already passes (the grep count meets the threshold, the file already exists, the artifact already produces the expected output, etc.), it is a **no-op** — it provides zero signal about whether the sprint's implementation was successful. Revise no-op criteria by raising the threshold, narrowing the search scope, choosing a different observable result, or replacing with a criterion that tests new content specifically. No-op structural criteria are especially dangerous because they pass even when nothing was built.
