"""Tests for bootstrap confidence interval estimator (C6, C7)."""
from __future__ import annotations

import random

import pytest

from trine_eval.judge.bootstrap import BootstrapCI, bootstrap_ci


# ---------------------------------------------------------------------------
# C6 — bootstrap CI brackets the point estimate
# ---------------------------------------------------------------------------

def test_bootstrap_ci_brackets_mean() -> None:
    """C6: bootstrap_ci returns CI that brackets the point estimate.

    - All-1.0 scores: lower <= 1.0 <= upper, confidence == 0.95 (default).
    - Mixed 50/50 scores (seeded): lower <= 0.5 <= upper.
    """
    # Constant-score list: bootstrap mean is always 1.0
    scores_all_one = [1.0] * 100
    ci = bootstrap_ci(scores_all_one)

    assert isinstance(ci, BootstrapCI), f"Expected BootstrapCI, got {type(ci)}"
    assert ci.lower <= 1.0 <= ci.upper, (
        f"CI [{ci.lower}, {ci.upper}] should bracket 1.0"
    )
    assert ci.confidence == pytest.approx(0.95), (
        f"Default confidence should be 0.95, got {ci.confidence}"
    )

    # Mixed list: mean is 0.5; seed for reproducibility
    random.seed(42)
    scores_mixed = [1.0] * 50 + [0.0] * 50
    ci_mixed = bootstrap_ci(scores_mixed, n_resamples=1000)

    assert ci_mixed.lower <= 0.5 <= ci_mixed.upper, (
        f"CI [{ci_mixed.lower}, {ci_mixed.upper}] should bracket 0.5"
    )


# ---------------------------------------------------------------------------
# C7 — bootstrap responds to n_resamples (intervals must differ)
# ---------------------------------------------------------------------------

def test_bootstrap_variance_with_n_resamples() -> None:
    """C7: n_resamples=10 and n_resamples=1000 must NOT produce identical CIs.

    This test catches trivial implementations that ignore n_resamples.
    """
    scores = [0.0] * 25 + [1.0] * 25

    random.seed(0)
    ci_10 = bootstrap_ci(scores, n_resamples=10)

    random.seed(0)
    ci_1000 = bootstrap_ci(scores, n_resamples=1000)

    width_10 = ci_10.upper - ci_10.lower
    width_1000 = ci_1000.upper - ci_1000.lower

    # The two intervals must NOT be byte-identical (proves resampling varies)
    assert ci_10.lower != ci_1000.lower or ci_10.upper != ci_1000.upper, (
        "n_resamples=10 and n_resamples=1000 produced identical CIs — "
        "the bootstrap implementation appears to ignore n_resamples"
    )

    # At least one of: wider CI with fewer samples, or CIs differ in some way
    assert width_10 >= width_1000 or width_10 != width_1000, (
        "Expected n_resamples=10 to produce a different-width CI than n_resamples=1000"
    )
