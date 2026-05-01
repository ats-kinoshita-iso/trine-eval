# Sprint FX Contract: Fixture Sprint for Phase 2 Runtime Verification

## What I Will Build

A minimal one-criterion fixture sprint used by the parent trine-eval Sprint 11 verification harness to exercise the trial loop, sandbox tmpdir isolation, regression gate, and transcript-trailer machinery end-to-end. This sprint never runs as a real sprint — it exists only as a deterministic stand-in for runtime-hookup verification.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **Dependent file exists**: `tests/fixture-project/.harness/dependent.txt` exists with non-empty contents. Verify via `test -s tests/fixture-project/.harness/dependent.txt`. [weight: 100%]

## Should-NOT Criteria

None — this is a synthetic single-criterion fixture.

## Out of Scope

- Real implementation work. The fixture's only purpose is to exercise the trial loop, sandbox, and transcript machinery against a deterministic verification command.
- Recursive invocation of the parent trine-eval harness. The Sprint 11 verification script orchestrates this fixture's primitives directly.

## Technical Notes

- The verification command (`test -s tests/fixture-project/.harness/dependent.txt`) is deterministic: every trial returns exit 0 when the file exists. This produces pass@3 = pass^3 = 1.0, which verifies the trial-loop file naming and pass@k formula application without exercising the consistency-gap measurement (where pass@k > pass^k).
- The fixture's `regression.json` (sibling at `tests/fixture-project/.harness/regression/regression.json`) carries this same criterion as a graduated entry — Sprint 11's regression-abort verification (parent C5) breaks `dependent.txt`, runs the regression gate, expects abort, then restores the file.
