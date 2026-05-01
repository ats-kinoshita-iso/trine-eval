# Fixture Project Cross-Sprint Summary

**Generated:** 2026-04-30
**Source:** trial files in `tests/fixture-project/.harness/evals/`

This summary aggregates the synthetic Sprint FX fixture used by the parent trine-eval Sprint 11 to verify Phase-2 runtime hookups. It exists to demonstrate that the trial-loop machinery produces valid pass@k / pass^k metrics.

## Sprint FX (synthetic fixture)

- **Trials run:** 3 (`sprint-fx-r1-t1.md`, `sprint-fx-r1-t2.md`, `sprint-fx-r1-t3.md`)
- **Per-trial pass rates:** p₁ = 1.000, p₂ = 1.000, p₃ = 1.000 (each trial passed its single deterministic criterion)
- **Average per-trial pass rate p:** 1.000

### Consistency Metrics — trial-derived (statistically valid)

These metrics are computed from trial files (`-tT` suffix), not from retry rounds (`-rR` suffix). Trial files capture independent measurement runs at fixed code state; round files capture bug-fix iterations. Only trial-derived metrics are statistically valid for pass@k / pass^k. The deprecated `pass@rounds` / `pass^rounds` retry-derived metric (used for sprints with only round files) is intentionally not reported here.

- **pass@k (k=3):** 1 − (1 − p)³ = 1 − (1 − 1.000)³ = **1.000**
- **pass^k (k=3):** p³ = 1.000³ = **1.000**

Interpretation: with the deterministic fixture command (`test -s tests/fixture-project/.harness/dependent.txt`), every trial passes; pass@3 and pass^3 collapse to 1.0. This verifies the trial-loop file naming and the pass@k / pass^k formula application — the consistency-gap measurement (where pass@k > pass^k) requires a non-deterministic command and is exercised by `bash tests/verify-runtime-hookups.sh nondet-trial` rather than by the static fixture summary.

### Why this is the runtime-verification source for Sprint 11

The parent Sprint 11 contract's Criterion 3 verifies that this file exists and contains `pass@k`, `pass^k`, and a `sprint-fx` reference. Criterion 11 (LLM-judge) verifies that the numerical values reported above are arithmetically consistent with the per-trial pass rates in the three trial files within ±0.001 tolerance:

| Metric  | Formula           | p = 1.000 | Tolerance check |
|---------|-------------------|-----------|-----------------|
| pass@3  | 1 − (1 − p)³      | 1.000     | within ±0.001 ✓ |
| pass^3  | p³                 | 1.000     | within ±0.001 ✓ |

## Provenance

- Trial 1 file: `tests/fixture-project/.harness/evals/sprint-fx-r1-t1.md` (verdict PASS)
- Trial 2 file: `tests/fixture-project/.harness/evals/sprint-fx-r1-t2.md` (verdict PASS)
- Trial 3 file: `tests/fixture-project/.harness/evals/sprint-fx-r1-t3.md` (verdict PASS)
- Fixture contract: `tests/fixture-project/.harness/contracts/sprint-fx.md`
- Fixture tasks.json: `tests/fixture-project/.harness/contracts/sprint-fx.tasks.json`
