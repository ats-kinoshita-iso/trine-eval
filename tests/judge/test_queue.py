"""Tests for the human annotation queue (C10)."""
from __future__ import annotations

import pytest

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.judge.queue import ListQueue


# ---------------------------------------------------------------------------
# C10 — enqueue → list → resolve round-trip
# ---------------------------------------------------------------------------

def test_queue_enqueue_list_resolve() -> None:
    """C10: ListQueue supports a full enqueue → list → resolve round-trip.

    Steps:
      (a) Create a fresh ListQueue.
      (b) Enqueue a sample.
      (c) list() returns exactly 1 pending item with the correct id.
      (d) resolve(sample_id, value=1.0) returns Score(value=1.0).
      (e) list() after resolve returns an empty list (item is gone).
    """
    queue = ListQueue()
    sample = Sample(id="q-001", input="Human review needed.")

    # (b) Enqueue
    queue.enqueue(sample)

    # (c) List: exactly 1 pending item
    pending = queue.list()
    assert len(pending) == 1, (
        f"Expected 1 pending item after enqueue, got {len(pending)}"
    )
    assert pending[0]["id"] == sample.id, (
        f"Pending item id should be {sample.id!r}, got {pending[0]['id']!r}"
    )

    # (d) Resolve: returns Score(value=1.0)
    resolved_score = queue.resolve(sample.id, value=1.0)
    assert isinstance(resolved_score, Score), (
        f"resolve() must return a Score, got {type(resolved_score)}"
    )
    assert resolved_score.value == pytest.approx(1.0), (
        f"Resolved score value should be 1.0, got {resolved_score.value}"
    )

    # (e) List after resolve: item is gone
    pending_after = queue.list()
    assert len(pending_after) == 0, (
        f"Expected 0 pending items after resolve, got {len(pending_after)}"
    )
