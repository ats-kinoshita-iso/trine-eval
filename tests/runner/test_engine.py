"""Smoke tests for the async runner engine."""
from __future__ import annotations

import asyncio

import pytest

from trine_eval.core.log import EvalLog
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.core.task import Task
from trine_eval.runner.engine import TokenUsage, run


class _FixedModel:
    """Stub model that always returns a fixed string with minimal token usage."""

    model = "stub-model"

    def __init__(self, answer: str = "world", input_tokens: int = 5, output_tokens: int = 5) -> None:
        self._answer = answer
        self._input_tokens = input_tokens
        self._output_tokens = output_tokens

    async def agenerate(self, sample: Sample) -> tuple[str, TokenUsage]:
        return self._answer, TokenUsage(self._input_tokens, self._output_tokens)


@pytest.mark.asyncio
async def test_run_noop() -> None:
    """Async runner returns an EvalLog for a single-sample no-op task."""
    model = _FixedModel(answer="world")
    task = Task(
        name="noop-task",
        dataset=[Sample(id="1", input="hello", target="world")],
    )
    log = await run(task, model)

    assert isinstance(log, EvalLog)
    assert len(log.scores) == 1
    assert log.scores[0].value == 1.0  # exact match: "world" == "world"
    assert log.task_name == "noop-task"


@pytest.mark.asyncio
async def test_run_multiple_samples() -> None:
    """Runner handles multiple samples and returns all scores."""
    model = _FixedModel(answer="yes")
    samples = [Sample(id=str(i), input=f"q{i}", target="yes") for i in range(5)]
    task = Task(name="multi", dataset=samples)
    log = await run(task, model)

    assert isinstance(log, EvalLog)
    assert len(log.scores) == 5
    assert all(s.value == 1.0 for s in log.scores)


@pytest.mark.asyncio
async def test_run_no_metadata_when_no_cap() -> None:
    """When no cap fires, metadata has no cap_hit key."""
    model = _FixedModel()
    task = Task(name="t", dataset=[Sample(id="1", input="x", target="world")])
    log = await run(task, model)
    assert "cap_hit" not in log.metadata
