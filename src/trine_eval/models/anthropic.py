from __future__ import annotations

from typing import Any, Literal

import anthropic
from pydantic import BaseModel, field_validator

EffortLiteral = Literal["low", "medium", "high", "xhigh", "max"]


class AnthropicModel(BaseModel):
    """
    Thin wrapper around the Anthropic SDK with adaptive thinking at a
    configurable effort level.

    Parameters
    ----------
    model:
        The Anthropic model ID. Defaults to "claude-opus-5".
    effort:
        API effort level (``output_config.effort``). One of: low, medium,
        high, xhigh, max. Controls thinking depth and overall token spend.
    api_key:
        Optional API key. Falls back to the ANTHROPIC_API_KEY environment variable.
    """

    model: str = "claude-opus-5"
    effort: EffortLiteral = "medium"
    api_key: str | None = None

    # Pydantic v2: private attribute for the SDK client
    model_config = {"arbitrary_types_allowed": True}

    @field_validator("effort", mode="before")
    @classmethod
    def validate_effort(cls, v: Any) -> Any:
        valid = {"low", "medium", "high", "xhigh", "max"}
        if v not in valid:
            raise ValueError(
                f"Invalid effort {v!r}. Must be one of: {sorted(valid)}"
            )
        return v

    def model_post_init(self, __context: Any) -> None:
        """Initialize the Anthropic SDK client after Pydantic validation."""
        object.__setattr__(self, "_client", anthropic.Anthropic(api_key=self.api_key))

    @property
    def _anthropic_client(self) -> anthropic.Anthropic:
        return object.__getattribute__(self, "_client")

    def create(
        self,
        messages: list[dict[str, Any]],
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Any:
        """
        Call messages.create with adaptive thinking at the configured effort.

        Adaptive thinking interleaves thinking between tool calls without a
        beta header. Thinking blocks in the assistant's content are passed
        through verbatim — the caller is responsible for including them
        unmodified in subsequent turns.
        """
        return self._anthropic_client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            thinking={"type": "adaptive"},
            output_config={"effort": self.effort},
            **kwargs,
        )
