from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score


class EvalLog(BaseModel):
    """A log of an evaluation run."""

    task_name: str
    samples: list[Sample]
    scores: list[Score]
    model: str
    timestamp: datetime
    aggregate: dict[str, Any] = Field(default_factory=dict)
