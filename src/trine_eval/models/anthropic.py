from __future__ import annotations

from typing import Any, Literal

import anthropic
from pydantic import BaseModel, field_validator

# Effort tier → thinking budget_tokens mapping.
# low: 1_000, medium: 8_000, high: 16_000, xhigh: 32_000, max: 100_000
EFFORT_BUDGET: dict[str, int] = {
    "low": 1_000,
    "medium": 8_000,
    "high": 16_000,
    "xhigh": 32_000,
    "max": 100_000,
}

# Beta header required for interleaved thinking support.
INTERLEAVED_THINKING_BETA = "interleaved-thinking-2025-05-14"

EffortLiteral = Literal["low", "medium", "high", "xhigh", "max"]


class AnthropicModel(BaseModel):
    """
    Thin wrapper around the Anthropic SDK with effort-tier thinking support.

    Parameters
    ----------
    model:
        The Anthropic model ID. Defaults to "claude-opus-4-7".
    effort:
        Thinking budget tier. One of: low, medium, high, xhigh, max.
        Maps to budget_tokens: low→1k, medium→8k, high→16k, xhigh→32k, max→100k.
    api_key:
        Optional API key. Falls back to the ANTHROPIC_API_KEY environment variable.
    """

    model: str = "claude-opus-4-7"
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

    @property
    def beta_headers(self) -> list[str]:
        """Return the list of beta headers required for interleaved thinking."""
        return [INTERLEAVED_THINKING_BETA]

    @property
    def budget_tokens(self) -> int:
        """Return the thinking budget_tokens for the current effort tier."""
        return EFFORT_BUDGET[self.effort]

    def create(
        self,
        messages: list[dict[str, Any]],
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> Any:
        """
        Call messages.create with interleaved thinking enabled.

        Thinking blocks in the assistant's content are passed through verbatim —
        the caller is responsible for including them unmodified in subsequent turns.
        """
        return self._anthropic_client.messages.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            betas=[INTERLEAVED_THINKING_BETA],
            thinking={"type": "enabled", "budget_tokens": EFFORT_BUDGET[self.effort]},
            **kwargs,
        )
