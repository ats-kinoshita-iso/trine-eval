"""Human annotation queue for samples that require manual review.

Provides ``ListQueue``, an in-memory queue that supports ``enqueue``,
``list``, and ``resolve`` operations, and ``get_default_queue`` which
returns a module-level singleton for use by the dispatcher.
"""
from __future__ import annotations

from typing import Any

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score


class ListQueue:
    """In-memory queue for pending human annotation requests.

    Items are stored as a list of ``Sample`` objects keyed by ``sample.id``.
    ``resolve`` removes the item from the pending list and returns a ``Score``.
    """

    def __init__(self) -> None:
        self._pending: dict[str, Sample] = {}

    def enqueue(self, sample: Sample) -> None:
        """Add a sample to the pending annotation queue.

        Parameters
        ----------
        sample:
            The sample awaiting human review.  Duplicate enqueues with the
            same ``sample.id`` overwrite the previous entry silently.
        """
        self._pending[sample.id] = sample

    def list(self) -> list[dict[str, Any]]:
        """Return all pending items as a list of dicts.

        Each dict has at minimum ``{"id": str, "input": str}``.
        """
        return [
            {"id": s.id, "input": s.input, **s.metadata}
            for s in self._pending.values()
        ]

    def resolve(self, sample_id: str, value: float) -> Score:
        """Mark a pending item as resolved with a human-provided score.

        Parameters
        ----------
        sample_id:
            The ``id`` of the sample to resolve.
        value:
            The human-assigned score (e.g. 1.0 for correct, 0.0 for incorrect).

        Returns
        -------
        Score
            A ``Score`` object with ``value`` set and ``metadata["tier"] == "human"``.

        Raises
        ------
        KeyError
            If ``sample_id`` is not found in the pending queue.
        """
        if sample_id not in self._pending:
            raise KeyError(f"No pending item with id={sample_id!r}")
        del self._pending[sample_id]
        return Score(value=value, metadata={"tier": "human", "resolved": True})


# Module-level singleton
_default_queue: ListQueue | None = None


def get_default_queue() -> ListQueue:
    """Return the module-level singleton ``ListQueue``.

    Creates the queue on first call.
    """
    global _default_queue
    if _default_queue is None:
        _default_queue = ListQueue()
    return _default_queue
