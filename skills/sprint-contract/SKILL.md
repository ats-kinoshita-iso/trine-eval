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

```markdown
# Sprint {NN} Contract: {Title}

## What I Will Build
{2-3 sentences describing the deliverable at a high level}

## Success Criteria
Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.

1. {Criterion}: {How to verify — specific command, URL, or check}
2. {Criterion}: {How to verify}
3. {Criterion}: {How to verify}
...

## Out of Scope
{Explicitly list things that might be assumed but are NOT included in this sprint}

## Technical Notes
{Any design decisions, constraints, or dependencies relevant to evaluation}
```

## Guidelines for Good Criteria

**Good criterion:** "GET /api/users returns 200 with a JSON array. Each user object contains id (number), name (string), and email (string)."

**Bad criterion:** "The API works correctly." (Too vague — what does "correctly" mean?)

**Good criterion:** "The search bar filters the list in real-time as the user types. Typing 'abc' with 100 items shows only items containing 'abc' within 200ms."

**Bad criterion:** "Search is fast." (What's fast? How do you measure it?)

Each criterion should describe:
- The action to take (input)
- The expected result (output)
- How to verify it (test method)
