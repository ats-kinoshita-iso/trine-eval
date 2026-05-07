# Sprint FY Evaluation
**Round:** 1
**Trial:** N/A (single-trial fixture)

## Summary
- Total criteria: 1
- Passed: 1
- Failed: 0
- Weighted score: 100% (sum of passed criteria weights)
- Gate criteria: 0/0
- Verdict: PASS

## Criteria Results

### 1. Sentinel file exists
**Grader:** deterministic
**Result:** PASS
**Evidence:** Ran `test -s tests/fixture-project/.harness/dependent.txt` from the fixture root — exit 0. Sprint FX's sentinel is intact.
**Location:** tests/fixture-project/.harness/dependent.txt

## Edge Case Results

These edge cases are graded PASS/FAIL but are NOT folded into the weighted
score (per the Edge Case Pass Rate documentation in `skills/sprint-contract/SKILL.md`).

### EC1. Empty input handling
**Grader:** deterministic
**Result:** PASS
**Evidence:** Hypothetical CLI tool printed a usage banner and exited 2 when invoked with no arguments. Verified via fixture stub.

### EC2. Oversize input handling
**Grader:** deterministic
**Result:** FAIL
**Evidence:** Hypothetical CLI tool OOM'd on a 1 GB input rather than rejecting cleanly. The fixture deliberately includes this FAIL to exercise the cross-sprint aggregator's non-100% path.

## Gate (Should-NOT) Results

None defined for this fixture.

## Rubric Scores

This fixture inherits the eval-harness rubric from the parent project. Per-dimension scoring is not exercised by the synthetic fixture — the single deterministic criterion stands as the verdict.

## Transcript Trailer

```json
{
  "sprint": "fy",
  "round": 1,
  "trial": null,
  "messages": [],
  "tool_calls": [
    {"name": "Bash", "arguments_summary": "test -s tests/fixture-project/.harness/dependent.txt", "result_summary": "exit 0", "task_id": "sfy-c1"}
  ],
  "criteria_audit": [
    {"task_id": "sfy-c1", "verified_via_command": true},
    {"task_id": "sfy-ec1", "verified_via_command": false},
    {"task_id": "sfy-ec2", "verified_via_command": false}
  ],
  "token_usage": {"input": null, "output": null, "cache_hit": null},
  "timing": {"ttft_ms": null, "total_ms": null},
  "thinking_summary": "Sprint FY exists alongside Sprint FX to give the cross-sprint edge-case aggregator a non-trivial mixed PASS/FAIL corpus. EC1 PASS + EC2 FAIL combined with Sprint FX's 0/0 edge cases produces an aggregate of 1/2 = 50%."
}
```
