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

Each criterion should be tagged with its grader type:

- **Deterministic** — Can be verified by running a command, checking a file, parsing output, or comparing strings. Preferred whenever possible because it is fast, cheap, reproducible, and eliminates grader disagreement.
- **LLM-as-judge** — Requires reading comprehension, subjective assessment, or nuanced evaluation that no simple command can capture. Use when deterministic verification is not feasible.

The evaluator attempts deterministic verification first for every criterion. It falls back to LLM judgment only when the criterion genuinely requires subjective assessment.

## Negative (Should-NOT) Criteria

Should-NOT criteria define behaviors that must NOT occur. They are graded **PASS when the behavior is absent** — the opposite of normal criteria.

Use Should-NOT criteria for:
- Regression guards (don't break existing functionality)
- Security invariants (don't expose stack traces, don't leak credentials)
- Architectural boundaries (don't violate separation of concerns)

## Edge Case Criteria

Edge case criteria are an **optional** third class of contract criterion, distinct from the 100%-weighted Success Criteria and from Should-NOT gates. They are tracked separately because they answer a different question.

- **Success Criteria** ask: "Does the deliverable do what it should?" Weighted to 100% in aggregate; the weighted score is the headline pass-rate metric.
- **Should-NOT Criteria** ask: "Does the deliverable avoid behaviors it shouldn't?" Binary gates; any failure blocks the sprint.
- **Edge Case Criteria** ask: "Does the deliverable handle ambiguous, boundary, or adversarial inputs correctly?" Tracked as a separate **edge-case pass rate** metric in `harness-summary`, *not* folded into the weighted total.

**Why separate, not folded into the weighted total.** Folding edge cases into the 100% weighted score would be a one-sided eval — the same failure mode Anthropic's playbook calls out as "positive-case-and-negative-case-by-luck." An agent that passes only the obvious positive cases would earn the same weighted score whether or not it correctly declined the ambiguous ones; the asymmetry would be invisible. Reporting edge-case pass rate as a distinct metric makes the asymmetry visible and lets the operator decide how to weight robustness vs. core functionality. If a sprint scores 100% weighted but 30% on edge cases, that is a genuinely different outcome from 100% weighted with 95% on edge cases — and the eval should surface that difference.

**Why optional.** Not every sprint is the right place for edge-case criteria. A sprint that delivers a pure mechanical refactor or a documentation-only change adds no signal from edge-case scoring. The contract template includes the section as an optional slot; sprints that omit it produce the same `tasks.json` shape they would have produced before Sprint 10 — Should-NOT gates and weighted Success Criteria continue to be the only two entry classes.

**Per-rubric guidance.** During contract review, the Evaluator should propose edge-case coverage when the rubric is one of:

- **`web-app`** — well-known edge cases include: empty form submissions, max-length input fields, malformed URLs, concurrent state updates, browsers with JavaScript disabled, viewport extremes (320px and 4K), keyboard-only navigation.
- **`api-service`** — empty request bodies, oversized payloads, malformed JSON, concurrent identical requests, rate-limit boundaries, expired auth tokens, idempotency edge cases.
- **`rag-system`** — empty queries, very long queries, queries with no matching documents, queries that span document boundaries, queries containing the answer key verbatim, citation hallucination on out-of-corpus queries.

For `cli-tool` and `eval-harness` deliverables, the Evaluator may skip the edge-case recommendation — those rubrics typically encode their edge-case concerns directly in the dimension scoring tables, and adding a separate edge-case section adds noise without signal.

**How edge cases are graded.** Each edge case criterion is graded PASS or FAIL using the same code-based-first hierarchy as Success Criteria. The difference is what the harness does with the result: edge-case PASS/FAIL counts go into the **Edge Case Pass Rate** metric (see `skills/harness-summary/SKILL.md`), not into the weighted score. A sprint with 10 edge case criteria where 7 pass reports an Edge Case Pass Rate of 70% — independent of whether the weighted score was 100% or 60%.

## Reference Solutions

Reference solutions provide known-working outputs for criteria where grader calibration is valuable. They are **optional** — not every criterion needs one.

**When to include a reference solution:**
- LLM-as-judge criteria benefit most (reduces inter-judge disagreement)
- Criteria where the expected format/structure might be ambiguous
- The highest-weighted criterion in the contract should have one if it is LLM-judged

**Purpose:** Reference solutions calibrate grader accuracy. They give the evaluator a concrete example of what PASS looks like, reducing the chance of false-fail or false-pass judgments.

## Task Taxonomy: sprint-NN.tasks.json

After the contract is approved (Status: APPROVED from the Evaluator review), emit a sibling `.harness/contracts/sprint-{NN}.tasks.json` file alongside the markdown contract. This is the **machine-readable source of record** for the sprint's criteria — it feeds the regression gate (Sprint 7), the Batch API submission grouping (Sprint 8), transcript correlation by task_id (Sprint 9), and adversarial hygiene flags (Sprint 10). Do not skip it: later sprints assume it exists from Sprint 6 onward.

**When to emit:** right after the Evaluator writes `**Status: APPROVED**` and before the Generator enters IMPLEMENTATION mode. Guarded by `config.taxonomy.emit_tasks_json` (default `true`).

**Schema:** one entry per criterion in the approved contract — both Success Criteria (deterministic and LLM-judge) and Should-NOT gate criteria.

```json
{
  "sprint": 6,
  "tasks": [
    {
      "task_id": "s06-c1",
      "criterion": "<verbatim criterion text from the contract>",
      "grader_type": "deterministic",
      "weight": 8,
      "is_gate": false,
      "verification_command": "jq -e '.trials' .harness/config.json",
      "rubric_dimension": "methodology_completeness"
    },
    {
      "task_id": "s06-sn1",
      "criterion": "<Should-NOT criterion text>",
      "grader_type": "llm-judge",
      "weight": 0,
      "is_gate": true,
      "verification_command": null,
      "rubric_dimension": "generator_evaluator_separation"
    }
  ]
}
```

**Field semantics:**

- `task_id` — Stable identifier: `s<NN>-c<N>` for success criteria (numbered from 1), `s<NN>-sn<N>` for Should-NOT gates. Stability matters because Sprint 9 transcripts and Sprint 10 hygiene flags key off this id across trials.
- `criterion` — Verbatim criterion text from the markdown contract (no paraphrasing). This is what the Evaluator and downstream tools read.
- `grader_type` — `"deterministic"` or `"llm-judge"`, matching the tag in the markdown contract.
- `weight` — The percentage weight from the markdown contract. Gate (Should-NOT) criteria use `0` — they are binary, not weighted.
- `is_gate` — `true` for Should-NOT gates, `false` for scored success criteria.
- `verification_command` — For deterministic criteria, a runnable shell command whose exit code or stdout determines PASS/FAIL. For llm-judge criteria, `null`. Sprint 7's regression gate executes these commands directly.
- `rubric_dimension` — Which rubric dimension this criterion informs (e.g., `methodology_completeness`, `grading_architecture`). Used by Sprint 8 for batching by dimension and by harness-summary for per-dimension rollups.

**Emission process:** The Generator (or main thread in minimal mode) writes the JSON file after reading the approved contract. The Evaluator does not need to review the JSON separately — it is a mechanical transcription of the approved markdown contract, and any drift between the two is caught by the Evaluator's subsequent reads of both files during the EVALUATION step.

## Before Submitting: Authoring Checklist

Before handing the contract to the Evaluator, the author (Generator subagent or main thread in minimal mode) walks the following checklist. Each item below was empirically caught in a prior sprint's negotiation round; the checklist exists to prevent recurrences, not to enumerate hypothetical traps.

**The reference-solution-must rule.** The highest-weighted LLM-as-judge criterion **must have a reference solution**. Without one, the grader has no calibration anchor, two independent evaluators are likely to disagree, and the criterion's pass/fail signal becomes noise. If multiple criteria are tied at the top weight, the most subjective of them gets the reference solution. Lower-weighted LLM-judge criteria are encouraged but not required to carry one.

### Authoring Checklist (five trap categories)

These are the recurring authoring mistakes the Evaluator has flagged across Sprints 6–11. Walk every deterministic criterion through all five before submission.

1. **multi-line trap.** Does the verification command use a single-line `grep` or `grep -q` over content that actually spans multiple lines? YAML frontmatter blocks, multi-line code fences, and JSON pretty-printed across multiple lines are common offenders — `grep` matches on a line at a time. When the target genuinely spans lines, switch to `awk` over the relevant block (as in Sprint 12 C1's `awk '/^---$/{c++; next} c==1'` for frontmatter), or use `python` to parse the file. If a `grep` pattern looks like it should match a multi-key YAML or multi-line JSON value, it almost certainly will not.

2. **permutation trap.** Does the verification command rely on a regex that requires elements to appear in a specific order, when the order is not actually contractually required? `grep -E 'A.*B.*C'` is fragile against any reordering by the implementer — and rewriting in alphabetical order is a legitimate refactor. Prefer chained independent `grep -q` calls (`grep -q A && grep -q B && grep -q C`) so the verification stays robust to ordering.

3. **pre-existing trap.** Does the verification command match content that ALREADY exists in the file before the sprint starts? A criterion that grades PASS on the unmodified pre-Sprint-N codebase is not a criterion — it's a tautology. Before submitting, run each verification command against the current `HEAD` (no implementation yet) and confirm the result is FAIL. When a needed phrase happens to already exist (e.g., `weight sum` already in `skills/sprint-contract/SKILL.md` line 33), add a unique-marker anchor (`Authoring Checklist`) that quarantines the new content from the existing match.

4. **weight sum trap.** Do the per-criterion weights sum to exactly 100%? Add them up by hand or with a one-liner before submitting. Sums of 95%, 105%, 110% are the most common — they slip past visual inspection because criteria look reasonable individually. The Evaluator will reject any contract whose weights do not sum to 100%.

5. **prose-vs-verification trap.** Does the criterion's English prose actually describe what the verification command runs? When the prose says "verify the file contains a markdown table" but the command is `grep -q '|'`, the prose is over-promising — the grader is grading something narrower than the prose claims. Either tighten the prose to match the command exactly, or strengthen the command to verify what the prose claims. The two must be the same test.

If any item fails, fix the contract before invoking the Evaluator. Catching these at authoring time saves a negotiation round.

## Guidelines for Good Criteria

**Good criterion:** "GET /api/users returns 200 with a JSON array. Each user object contains id (number), name (string), and email (string)."

**Bad criterion:** "The API works correctly." (Too vague — what does "correctly" mean?)

**Good criterion:** "The search bar filters the list in real-time as the user types. Typing 'abc' with 100 items shows only items containing 'abc' within 200ms."

**Bad criterion:** "Search is fast." (What's fast? How do you measure it?)

Each criterion should describe:
- The action to take (input)
- The expected result (output)
- How to verify it (test method)
