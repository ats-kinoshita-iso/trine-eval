from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Score(BaseModel):
    """The result of scoring a single sample."""

    value: float
    answer: str | None = None
    explanation: str | None = None
    reasoning: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
