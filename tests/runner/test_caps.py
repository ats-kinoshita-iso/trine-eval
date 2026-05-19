"""Hard-cap enforcement tests: token_limit, time_limit, cost_limit, max_concurrency."""
from __future__ import annotations

import asyncio

import pytest

from trine_eval.core.log import EvalLog
from trine_eval.core.sample import Sample
from trine_eval.core.task import Task
from trine_eval.runner.engine import TokenUsage, run


class _TokenHeavyModel:
    """Stub model that uses many tokens per call."""

    model = "stub-model"

    def __init__(self, tokens_per_call: int = 100) -> None:
        self._tokens = tokens_per_call

    async def agenerate(self, sample: Sample) -> tuple[str, TokenUsage]:
        return "answer", TokenUsage(self._tokens // 2, self._tokens // 2)


class _SlowModel:
    """Stub model that sleeps to simulate wall-clock time."""

    model = "stub-model"

    def __init__(self, delay: float = 0.1) -> None:
        self._delay = delay

    async def agenerate(self, sample: Sample) -> tuple[str, TokenUsage]:
        await asyncio.sleep(self._delay)
        return "answer", TokenUsage(1, 1)


class _CostlyModel:
    """Stub model with high output token count to drive up cost quickly."""

    model = "stub-model"

    # Uses OPUS_47_OUTPUT_PRICE = 15.00 / 1_000_000 = $0.000015 per output token
    # 1000 output tokens = $0.015 cost
    def __init__(self, output_tokens: int = 10_000) -> None:
        self._output_tokens = output_tokens

    async def agenerate(self, sample: Sample) -> tuple[str, TokenUsage]:
        return "answer", TokenUsage(1, self._output_tokens)


def _make_task(n: int = 10) -> Task:
    samples = [Sample(id=str(i), input=f"q{i}", target="answer") for i in range(n)]
    return Task(name="cap-test", dataset=samples)


@pytest.mark.asyncio
async def test_token_limit_cap() -> None:
    """When token_limit is exceeded, cap_hit == 'token_limit' and log is partial."""
    # Each call uses 100 tokens; limit at 150 so only 1-2 samples complete
    model = _TokenHeavyModel(tokens_per_call=100)
    task = _make_task(n=10)
    log = await run(task, model, token_limit=150)

    assert isinstance(log, EvalLog)
    assert log.metadata.get("cap_hit") == "token_limit"
    assert len(log.scores) < 10  # partial result


@pytest.mark.asyncio
async def test_time_limit_cap() -> None:
    """When time_limit is exceeded, cap_hit == 'time_limit' and log is partial."""
    # Each sample takes 0.15s; limit at 0.2s so only ~1 sample completes
    model = _SlowModel(delay=0.15)
    task = _make_task(n=10)
    log = await run(task, model, max_concurrency=1, time_limit=0.2)

    assert isinstance(log, EvalLog)
    assert log.metadata.get("cap_hit") == "time_limit"
    assert len(log.scores) < 10  # partial result


@pytest.mark.asyncio
async def test_cost_limit_cap() -> None:
    """When cost_limit is exceeded, cap_hit == 'cost_limit' and log is partial."""
    # Each sample: 1 input token ($0.000005) + 10_000 output tokens ($0.15) ≈ $0.15
    # cost_limit=0.2 → only 1 sample completes before cap fires
    model = _CostlyModel(output_tokens=10_000)
    task = _make_task(n=10)
    log = await run(task, model, cost_limit=0.2)

    assert isinstance(log, EvalLog)
    assert log.metadata.get("cap_hit") == "cost_limit"
    assert len(log.scores) < 10  # partial result


@pytest.mark.asyncio
async def test_max_concurrency_throttles_without_cap_hit() -> None:
    """max_concurrency limits simultaneous in-flight samples without triggering cap_hit."""
    max_conc = 3
    peak_concurrency = 0
    current_concurrency = 0
    lock = asyncio.Lock()

    class _CountingModel:
        model = "stub-model"

        async def agenerate(self, sample: Sample) -> tuple[str, TokenUsage]:
            nonlocal peak_concurrency, current_concurrency
            async with lock:
                current_concurrency += 1
                peak_concurrency = max(peak_concurrency, current_concurrency)
            await asyncio.sleep(0.01)  # simulate work
            async with lock:
                current_concurrency -= 1
            return "answer", TokenUsage(1, 1)

    model = _CountingModel()
    task = _make_task(n=15)
    log = await run(task, model, max_concurrency=max_conc)

    # Peak concurrency must not exceed the limit
    assert peak_concurrency <= max_conc
    # All samples completed (no cap_hit)
    assert "cap_hit" not in log.metadata
    assert len(log.scores) == 15
