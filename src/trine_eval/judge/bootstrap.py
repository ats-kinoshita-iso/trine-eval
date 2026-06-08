"""Bootstrap confidence interval estimator for score aggregates.

Provides ``bootstrap_ci``, which computes a bootstrap percentile CI over a
list of scalar scores, and the ``BootstrapCI`` NamedTuple for its result.
"""
from __future__ import annotations

import random
from typing import NamedTuple


class BootstrapCI(NamedTuple):
    """Result of a bootstrap confidence interval computation.

    Attributes
    ----------
    lower:
        Lower percentile bound of the CI.
    upper:
        Upper percentile bound of the CI.
    confidence:
        The confidence level used (e.g., 0.95 for a 95% CI).
    """

    lower: float
    upper: float
    confidence: float


def bootstrap_ci(
    scores: list[float],
    *,
    n_resamples: int = 1000,
    confidence: float = 0.95,
    seed: int | None = None,
) -> BootstrapCI:
    """Compute a bootstrap percentile confidence interval over ``scores``.

    Parameters
    ----------
    scores:
        The observed score values to resample.
    n_resamples:
        Number of bootstrap resamples to draw.  More resamples give a
        smoother (and typically narrower) interval estimate.
    confidence:
        Desired confidence level, e.g. 0.95 for a 95% CI.
    seed:
        Optional random seed for reproducibility.  When provided, the
        random state is seeded before resampling begins.

    Returns
    -------
    BootstrapCI
        A named tuple with ``lower``, ``upper``, and ``confidence`` fields.

    Notes
    -----
    Uses the percentile bootstrap method:
        1. Draw ``n_resamples`` samples of ``len(scores)`` values with replacement.
        2. Compute the mean of each resample.
        3. Sort the means and take the ``alpha/2`` and ``1 - alpha/2`` quantiles
           where ``alpha = 1 - confidence``.
    """
    if seed is not None:
        random.seed(seed)

    n = len(scores)
    alpha = 1.0 - confidence
    lower_pct = alpha / 2.0
    upper_pct = 1.0 - lower_pct

    resample_means: list[float] = []
    for _ in range(n_resamples):
        resample = random.choices(scores, k=n)
        resample_means.append(sum(resample) / n)

    resample_means.sort()

    lower_idx = int(lower_pct * n_resamples)
    upper_idx = int(upper_pct * n_resamples) - 1
    # Clamp to valid range
    lower_idx = max(0, min(lower_idx, n_resamples - 1))
    upper_idx = max(0, min(upper_idx, n_resamples - 1))

    return BootstrapCI(
        lower=resample_means[lower_idx],
        upper=resample_means[upper_idx],
        confidence=confidence,
    )
