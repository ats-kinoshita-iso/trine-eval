from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Sample(BaseModel):
    """A single evaluation sample with input and optional target."""

    id: str
    input: str
    target: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
