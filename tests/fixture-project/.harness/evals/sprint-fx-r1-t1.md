# Sprint FX Evaluation
**Round:** 1
**Trial:** 1

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
**Evidence:** Ran `test -s tests/fixture-project/.harness/dependent.txt` from a clean tmpdir checkout (sandbox.mode = "tmpdir") — exit 0. The fixture's dependent file exists with non-empty contents.
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
  "trial": 1,
  "messages": [],
  "tool_calls": [
    {"name": "Bash", "arguments_summary": "test -s tests/fixture-project/.harness/dependent.txt", "result_summary": "exit 0", "task_id": "sfx-c1"}
  ],
  "criteria_audit": [
    {"task_id": "sfx-c1", "verified_via_command": true}
  ],
  "token_usage": {"input": null, "output": null, "cache_hit": null},
  "timing": {"ttft_ms": null, "total_ms": null},
  "thinking_summary": "Trial 1 of 3. Sandbox mode tmpdir produced an isolated working tree before running the verification command. Exit 0 means the dependent file is present and non-empty."
}
```
