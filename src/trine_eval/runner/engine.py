"""Async runner engine with hard caps (token/time/cost/concurrency)."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Protocol

from trine_eval.core.log import EvalLog
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.core.task import Task

# Opus 4.7 pricing constants (USD per token).
# Update these when Anthropic publishes final pricing.
OPUS_47_INPUT_PRICE: float = 5.00 / 1_000_000   # $5.00 per 1M input tokens
OPUS_47_OUTPUT_PRICE: float = 15.00 / 1_000_000  # $15.00 per 1M output tokens


class TokenUsage:
    """Simple token usage container."""

    def __init__(self, input_tokens: int = 0, output_tokens: int = 0) -> None:
        self.input_tokens = input_tokens
        self.output_tokens = output_tokens

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


def _compute_cost(usage: TokenUsage) -> float:
    """Compute USD cost from token usage using Opus 4.7 pricing."""
    return (
        usage.input_tokens * OPUS_47_INPUT_PRICE
        + usage.output_tokens * OPUS_47_OUTPUT_PRICE
    )


class ModelProtocol(Protocol):
    """Protocol for model objects that can generate responses."""

    async def agenerate(self, sample: Sample) -> tuple[str, TokenUsage]:
        """Generate a response for a sample. Returns (answer, usage)."""
        ...


class SolverProtocol(Protocol):
    """Protocol for solver callables."""

    async def __call__(self, sample: Sample, model: Any) -> tuple[str, TokenUsage]:
        ...


async def _default_solve(sample: Sample, model: Any) -> tuple[str, TokenUsage]:
    """Default solver: calls model.agenerate if available, else returns empty."""
    if hasattr(model, "agenerate"):
        return await model.agenerate(sample)
    return ("", TokenUsage())


def _default_score(sample: Sample, answer: str) -> Score:
    """Default scorer: exact match on target."""
    target = sample.target or ""
    value = 1.0 if answer.strip() == target.strip() else 0.0
    return Score(value=value, answer=answer)


async def run(
    task: Task,
    model: Any,
    *,
    max_concurrency: int = 4,
    token_limit: int | None = None,
    time_limit: float | None = None,
    cost_limit: float | None = None,
    solver: Any | None = None,
    scorer: Any | None = None,
) -> EvalLog:
    """
    Run an eval task asynchronously with hard caps.

    Parameters
    ----------
    task:
        The Task to evaluate.
    model:
        The model to use. Must support ``agenerate(sample) -> (str, TokenUsage)``
        or be a plain callable. If neither, a no-op solver is used.
    max_concurrency:
        Maximum number of samples that may execute concurrently. Passive cap —
        does NOT cause early abort or set ``cap_hit``.
    token_limit:
        Total token budget across all samples. When exceeded, sets
        ``cap_hit = "token_limit"`` and returns a partial log.
    time_limit:
        Wall-clock elapsed time limit in seconds. When exceeded, sets
        ``cap_hit = "time_limit"`` and returns a partial log.
    cost_limit:
        USD cost budget. When exceeded, sets ``cap_hit = "cost_limit"``
        and returns a partial log.
    solver:
        Async callable ``(sample, model) -> (str, TokenUsage)``.
        Defaults to ``model.agenerate`` if available, else no-op.
    scorer:
        Callable ``(sample, answer) -> Score``.
        Defaults to exact-match on ``sample.target``.

    Returns
    -------
    EvalLog
        Complete or partial log. ``metadata["cap_hit"]`` is set if a budget
        cap fired (token/time/cost only — not max_concurrency).
    """
    solve = solver or _default_solve
    score_fn = scorer or _default_score

    sem = asyncio.Semaphore(max_concurrency)
    loop = asyncio.get_event_loop()
    start_time = loop.time()

    total_tokens: int = 0
    total_cost: float = 0.0
    cap_hit: str | None = None

    completed_scores: list[Score] = []
    completed_samples: list[Sample] = []
    lock = asyncio.Lock()

    async def run_sample(sample: Sample) -> None:
        nonlocal total_tokens, total_cost, cap_hit

        async with sem:
            # Check caps before executing the sample
            async with lock:
                if cap_hit:
                    return

                elapsed = loop.time() - start_time
                if time_limit is not None and elapsed >= time_limit:
                    cap_hit = "time_limit"
                    return

                if token_limit is not None and total_tokens >= token_limit:
                    cap_hit = "token_limit"
                    return

                if cost_limit is not None and total_cost >= cost_limit:
                    cap_hit = "cost_limit"
                    return

            # Execute the sample (outside the lock so concurrency is real)
            answer, usage = await solve(sample, model)

            async with lock:
                # Re-check caps after execution (token/cost can be exceeded mid-run)
                total_tokens += usage.total_tokens
                sample_cost = _compute_cost(usage)
                total_cost += sample_cost

                if cap_hit:
                    # Another coroutine hit a cap while we were executing; discard
                    return

                # Check if THIS sample's contribution pushed us over a cap
                if token_limit is not None and total_tokens > token_limit:
                    cap_hit = "token_limit"
                    return

                if cost_limit is not None and total_cost > cost_limit:
                    cap_hit = "cost_limit"
                    return

                s = score_fn(sample, answer)
                completed_scores.append(s)
                completed_samples.append(sample)

    samples = task.dataset
    await asyncio.gather(*(run_sample(s) for s in samples))

    metadata: dict[str, Any] = {}
    if cap_hit:
        metadata["cap_hit"] = cap_hit

    # Compute aggregate accuracy
    if completed_scores:
        accuracy = sum(s.value for s in completed_scores) / len(completed_scores)
        aggregate = {"accuracy": accuracy}
    else:
        aggregate = {}

    return EvalLog(
        task_name=task.name,
        samples=completed_samples,
        scores=completed_scores,
        model=getattr(model, "model", str(model)),
        timestamp=datetime.now(timezone.utc),
        aggregate=aggregate,
        metadata=metadata,
    )
