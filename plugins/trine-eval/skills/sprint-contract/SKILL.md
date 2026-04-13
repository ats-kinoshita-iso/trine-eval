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

## Reference Solutions

Reference solutions provide known-working outputs for criteria where grader calibration is valuable. They are **optional** — not every criterion needs one.

**When to include a reference solution:**
- LLM-as-judge criteria benefit most (reduces inter-judge disagreement)
- Criteria where the expected format/structure might be ambiguous
- The highest-weighted criterion in the contract should have one if it is LLM-judged

**Purpose:** Reference solutions calibrate grader accuracy. They give the evaluator a concrete example of what PASS looks like, reducing the chance of false-fail or false-pass judgments.

## Guidelines for Good Criteria

**Good criterion:** "GET /api/users returns 200 with a JSON array. Each user object contains id (number), name (string), and email (string)."

**Bad criterion:** "The API works correctly." (Too vague — what does "correctly" mean?)

**Good criterion:** "The search bar filters the list in real-time as the user types. Typing 'abc' with 100 items shows only items containing 'abc' within 200ms."

**Bad criterion:** "Search is fast." (What's fast? How do you measure it?)

Each criterion should describe:
- The action to take (input)
- The expected result (output)
- How to verify it (test method)
