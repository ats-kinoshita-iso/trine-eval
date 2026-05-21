"""
Functional smoke: prompt caching produces a real cache hit on the second call.

This is the first live-API smoke test under Sprint 07's `## Functional Smoke`
contract class. It validates that `apply_cache_control` -- which the architectural
unit tests in `tests/models/test_caching.py` verify produces the right argv shape --
actually triggers Anthropic's prompt-caching layer when called against the real
API.

Gating:
- Skipped unless `TRINE_EVAL_LIVE_API=1` is set (CI default skips).
- Skipped unless `ANTHROPIC_API_KEY` is set in the environment.

Cost (per run): two `messages.create` calls with a ~2k-token system prompt
+ 64 max output tokens each, on `claude-opus-4-7`. Approximate cost: $0.025.
Combined sprint smoke spend must stay under `functional_smoke.budget_usd`
(currently $1.00) per `.harness/config.json`.

Measured signal: `response.usage.cache_read_input_tokens > 0` on the second
call. A returned value of 0 means the cache layer never engaged -- the
architectural helper passed its unit tests but the integration is broken.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.skipif(
    not os.environ.get("TRINE_EVAL_LIVE_API"),
    reason="live API smoke test; set TRINE_EVAL_LIVE_API=1 to run",
)


# Cache eligibility for Opus requires at least 1024 cached tokens. Lorem ipsum
# at ~5 tokens per phrase -> 500 repetitions yields ~2500 tokens, comfortably
# above the threshold.
_LONG_SYSTEM_PROMPT = (
    "You are a deterministic test fixture for the trine-eval prompt-caching "
    "smoke test. Always respond with exactly one word. Reference padding: "
    + ("Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 80)
)


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="requires ANTHROPIC_API_KEY in environment",
)
def test_apply_cache_control_produces_real_cache_hit() -> None:
    """Two real Anthropic calls with the same cached system prompt should yield cache_read_input_tokens > 0 on call 2."""
    import anthropic

    from trine_eval.models.caching import apply_cache_control

    helper_kwargs = apply_cache_control(system=_LONG_SYSTEM_PROMPT)
    # apply_cache_control returns {"system": [...]} for system-only callers.
    # The "examples" key would be present and need popping if examples were passed.
    assert "system" in helper_kwargs
    assert helper_kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}

    client = anthropic.Anthropic()
    first = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16,
        messages=[{"role": "user", "content": "Reply with the single word: alpha"}],
        **helper_kwargs,
    )
    second = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=16,
        messages=[{"role": "user", "content": "Reply with the single word: beta"}],
        **helper_kwargs,
    )

    first_usage = first.usage
    second_usage = second.usage

    # First call should write the cache. cache_creation_input_tokens > 0 is the
    # signal that the helper successfully marked the system prompt as cacheable.
    assert getattr(first_usage, "cache_creation_input_tokens", 0) > 0, (
        f"first call did not write to cache; usage={first_usage}. "
        "apply_cache_control may not have produced a cacheable system block."
    )

    # Second call is the headline assertion: the cache must actually be hit.
    cache_read = getattr(second_usage, "cache_read_input_tokens", 0)
    assert cache_read > 0, (
        f"second call did not read from cache; usage={second_usage}. "
        "Architectural tests pass but the integration is broken."
    )
