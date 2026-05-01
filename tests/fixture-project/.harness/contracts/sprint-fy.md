# Sprint FY Contract: Edge-Case Fixture for Cross-Sprint Aggregation

## What I Will Build

A second synthetic fixture sprint, sibling to Sprint FX, used by the parent
trine-eval Sprint 12 verification harness to exercise cross-sprint edge-case
aggregation. Sprint FX has zero edge-case criteria; Sprint FY has two. The
combined two-sprint corpus lets the aggregation formula
(`total edge-case PASS / total edge-case criteria`) produce a non-trivial
value across at least two sprints, demonstrating that the harness-summary
edge-case rollup works end-to-end on a deterministic offline fixture.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **Sentinel file exists**: `tests/fixture-project/.harness/dependent.txt` exists with non-empty contents (re-using Sprint FX's sentinel; Sprint FY does not write its own). Verify via `test -s tests/fixture-project/.harness/dependent.txt`. [weight: 100%]

## Should-NOT Criteria

None — this is a synthetic fixture sprint.

## Edge Case Criteria

These are the edge-case criteria the parent Sprint 12 aggregator counts. Each is
graded PASS/FAIL but is not weighted into the 100% Success Criteria total —
they are rolled into the Edge Case Pass Rate metric instead.

1. **Empty input handling**: a hypothetical CLI tool, when invoked with no
   arguments, should print a usage banner and exit non-zero. PASS.
2. **Oversize input handling**: a hypothetical CLI tool, when invoked with a
   1 GB input file, should reject the request rather than OOM. FAIL (the
   fixture deliberately includes one FAIL so the cross-sprint aggregate is a
   non-trivial fraction).

## Out of Scope

- Real implementation work. Sprint FY is a deterministic stand-in; the edge-case
  PASS/FAIL counts are baked into the eval markdown for aggregation testing.
- Sprint FX modifications. Sprint FY exists alongside Sprint FX; mutating Sprint
  FX would violate the parent Sprint 12 SN1 gate.

## Technical Notes

- The 1 PASS / 1 FAIL split in this contract pairs with Sprint FX's 0/0 to
  produce an aggregate of 1/2 = 50% across the two-sprint corpus, exercising
  the aggregator's "sum-then-divide" path rather than a degenerate 100%-or-0%
  edge case.
- The aggregator script (`tests/edge-case-aggregate.py`) reads both sprint
  contracts plus the most recent eval round per sprint and computes the
  cross-sprint pass rate. The script never writes — it only reports.
