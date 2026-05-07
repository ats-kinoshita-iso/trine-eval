# Sprint FX Evaluation
**Round:** 1
**Trial:** 2

## Summary
- Total criteria: 1
- Passed: 1
- Failed: 0
- Weighted score: 100% (sum of passed criteria weights)
- Gate criteria: 0/0
- Verdict: PASS

## Criteria Results

### 1. Dependent file exists
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `test -s tests/fixture-project/.harness/dependent.txt` from a fresh tmpdir checkout — exit 0. Trial 2 ran from a distinct tmpdir from Trial 1, confirming sandbox isolation.
**Location:** tests/fixture-project/.harness/dependent.txt

## Gate (Should-NOT) Results

None defined for this fixture.

## Rubric Scores

This fixture inherits the eval-harness rubric from the parent project. Per-dimension scoring is not exercised by the synthetic fixture — the single deterministic criterion stands as the verdict.

## Transcript Trailer

```json
{
  "sprint": "fx",
  "round": 1,
  "trial": 2,
  "messages": [],
  "tool_calls": [
    {"name": "Bash", "arguments_summary": "test -s tests/fixture-project/.harness/dependent.txt", "result_summary": "exit 0", "task_id": "sfx-c1"}
  ],
  "criteria_audit": [
    {"task_id": "sfx-c1", "verified_via_command": true}
  ],
  "token_usage": {"input": null, "output": null, "cache_hit": null},
  "timing": {"ttft_ms": null, "total_ms": null},
  "thinking_summary": "Trial 2 of 3. New tmpdir, independent of Trial 1's tmpdir. Same deterministic verification, same exit 0."
}
```
