"""Token-efficiency and cost-efficiency metrics for EvalLog analysis."""
from __future__ import annotations

from trine_eval.core.log import EvalLog

# Opus 4.7 pricing constants (USD per token) — must match engine.py
OPUS_47_INPUT_PRICE: float = 5.00 / 1_000_000   # $5.00 per 1M input tokens
OPUS_47_OUTPUT_PRICE: float = 15.00 / 1_000_000  # $15.00 per 1M output tokens


def _total_cost(log: EvalLog) -> float:
    """Compute total USD cost from EvalLog metadata or token counts."""
    # If cost is stored directly in aggregate/metadata, use it
    if "total_cost_usd" in log.metadata:
        return float(log.metadata["total_cost_usd"])

    # Fall back to computing from token counts if available
    input_tokens = int(log.metadata.get("total_input_tokens", 0))
    output_tokens = int(log.metadata.get("total_output_tokens", 0))
    return input_tokens * OPUS_47_INPUT_PRICE + output_tokens * OPUS_47_OUTPUT_PRICE


def _total_tokens(log: EvalLog) -> int:
    """Compute total tokens from EvalLog metadata."""
    if "total_tokens" in log.metadata:
        return int(log.metadata["total_tokens"])
    return (
        int(log.metadata.get("total_input_tokens", 0))
        + int(log.metadata.get("total_output_tokens", 0))
    )


def _accuracy(log: EvalLog) -> float:
    """Compute accuracy from scores (fraction correct)."""
    if "accuracy" in log.aggregate:
        return float(log.aggregate["accuracy"])
    if not log.scores:
        return 0.0
    return sum(s.value for s in log.scores) / len(log.scores)


def accuracy_per_dollar(log: EvalLog) -> float:
    """
    Accuracy / total USD cost.

    Returns 0.0 when cost is zero (to avoid ZeroDivisionError).
    This metric rewards high accuracy at low cost.

    Parameters
    ----------
    log:
        The EvalLog to analyse. Cost is read from ``metadata["total_cost_usd"]``
        or computed from ``metadata["total_input_tokens"]`` +
        ``metadata["total_output_tokens"]`` using Opus 4.7 pricing.

    Returns
    -------
    float
        Accuracy per USD. Higher is better.
    """
    cost = _total_cost(log)
    if cost <= 0.0:
        return 0.0
    return _accuracy(log) / cost


def success_per_1k_tokens(log: EvalLog) -> float:
    """
    Number of successful samples (score >= 1.0) per 1,000 tokens consumed.

    Returns 0.0 when total tokens is zero.

    Parameters
    ----------
    log:
        The EvalLog to analyse. Token count is read from ``metadata["total_tokens"]``
        or ``metadata["total_input_tokens"]`` + ``metadata["total_output_tokens"]``.

    Returns
    -------
    float
        Successes per 1k tokens. Higher is better.
    """
    total = _total_tokens(log)
    if total <= 0:
        return 0.0
    successes = sum(1 for s in log.scores if s.value >= 1.0)
    return successes / (total / 1000.0)
