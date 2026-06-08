"""
Batch runner: submit a Task's samples to Anthropic's /v1/messages/batches endpoint.

This module provides :func:`run_batch`, which submits all samples in a single
``batches.create`` call, polls until the batch reaches a terminal status, demultiplexes
results by ``custom_id``, and returns a :class:`~trine_eval.core.log.EvalLog`.

Batching and caching compose: each request in the batch carries the same
``cache_control`` breakpoints produced by :func:`~trine_eval.models.caching.apply_cache_control`.
"""
from __future__ import annotations

import time
from datetime import datetime, timezone
from typing import Any

from trine_eval.core.log import EvalLog
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.core.task import Task
from trine_eval.models.caching import apply_cache_control

# Terminal batch processing statuses per the Anthropic API.
_TERMINAL_STATUSES = frozenset({"ended", "errored", "expired", "cancelled"})


def _default_score(sample: Sample, answer: str) -> Score:
    """Default scorer: exact match on target."""
    target = sample.target or ""
    value = 1.0 if answer.strip() == target.strip() else 0.0
    return Score(value=value, answer=answer)


def _extract_text(content: list[Any]) -> str:
    """Extract plain text from a content block list."""
    parts: list[str] = []
    for block in content:
        # Handle both dict-like and attribute-like block objects
        if isinstance(block, dict):
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
        else:
            if getattr(block, "type", None) == "text":
                parts.append(getattr(block, "text", ""))
    return " ".join(parts).strip()


def _build_request_body(model: Any, sample: Sample) -> dict[str, Any]:
    """
    Build the per-sample request body for a batch request entry.

    Applies cache_control breakpoints on the system prompt (if the model
    carries a system attribute) so that caching and batching compose.
    """
    system: str | None = getattr(model, "system_prompt", None)
    cached_kwargs = apply_cache_control(system=system)
    # examples are not used for individual sample requests in the batch path
    cached_kwargs.pop("examples", None)

    messages = [{"role": "user", "content": sample.input}]

    body: dict[str, Any] = {
        "model": getattr(model, "model", "claude-opus-4-7"),
        "max_tokens": 1024,
        "messages": messages,
    }
    # Merge in cached kwargs (system with cache_control if present)
    body.update(cached_kwargs)
    return body


def run_batch(
    task: Task,
    model: Any,
    *,
    poll_interval: float = 5.0,
    scorer: Any | None = None,
) -> EvalLog:
    """
    Submit task samples as a message batch and return a demultiplexed EvalLog.

    All samples are submitted in a **single** ``batches.create`` call. The runner
    then polls ``batches.retrieve`` until the batch reaches a terminal status
    (``ended``, ``errored``, ``expired``, or ``cancelled``), iterates the results,
    and maps each result back to its originating sample via ``custom_id``.

    Parameters
    ----------
    task:
        The Task whose ``dataset`` samples will be submitted.
    model:
        An :class:`~trine_eval.models.anthropic.AnthropicModel` (or any object
        with a ``_anthropic_client`` property and a ``model`` attribute).
    poll_interval:
        Seconds between ``batches.retrieve`` polls. Set to ``0`` or a very small
        value in tests (patch ``time.sleep`` to avoid real delays).
    scorer:
        Optional ``(sample, answer) -> Score`` callable. Defaults to exact-match
        on ``sample.target``.

    Returns
    -------
    EvalLog
        ``scores`` has one entry per successfully demultiplexed sample.
        ``metadata`` includes ``{"batch_id": ..., "via": "batch-api"}``.
    """
    client = model._anthropic_client
    score_fn = scorer or _default_score

    # Build one request per sample, assigning custom_id = sample.id.
    requests: list[dict[str, Any]] = []
    for sample in task.dataset:
        body = _build_request_body(model, sample)
        requests.append(
            {
                "custom_id": sample.id,
                "params": body,
            }
        )

    # Single batches.create call for ALL samples.
    batch = client.messages.batches.create(requests=requests)

    # Poll until a terminal status is reached.
    while batch.processing_status not in _TERMINAL_STATUSES:
        time.sleep(poll_interval)
        batch = client.messages.batches.retrieve(batch.id)

    # Demultiplex results by custom_id → sample.
    id_to_sample: dict[str, Sample] = {s.id: s for s in task.dataset}
    scores: list[Score] = []
    completed_samples: list[Sample] = []

    for result in client.messages.batches.results(batch.id):
        custom_id = result.custom_id
        sample = id_to_sample.get(custom_id)
        if sample is None:
            continue  # unknown custom_id — skip

        result_obj = result.result
        result_type = getattr(result_obj, "type", None)
        if result_type != "succeeded":
            continue  # errored / expired individual request — skip

        message = result_obj.message
        content = getattr(message, "content", [])
        answer = _extract_text(content)
        scores.append(score_fn(sample, answer))
        completed_samples.append(sample)

    aggregate: dict[str, Any] = {}
    if scores:
        aggregate["accuracy"] = sum(s.value for s in scores) / len(scores)

    return EvalLog(
        task_name=task.name,
        samples=completed_samples,
        scores=scores,
        model=getattr(model, "model", str(model)),
        timestamp=datetime.now(timezone.utc),
        aggregate=aggregate,
        metadata={"batch_id": batch.id, "via": "batch-api"},
    )
