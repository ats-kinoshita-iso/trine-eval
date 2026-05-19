from __future__ import annotations

from pydantic import BaseModel

from trine_eval.core.sample import Sample


class Task(BaseModel):
    """A named evaluation task with a dataset and optional registered function names."""

    name: str
    dataset: list[Sample]
    # These fields name registered functions in the registry dicts.
    # Using strings avoids circular imports with registry.py / decorators.py.
    solver: str | None = None
    scorer: str | None = None
    metric: str | None = None
