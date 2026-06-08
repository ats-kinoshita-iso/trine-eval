"""
Prompt caching helpers for the Anthropic messages.create API.

This module provides :func:`apply_cache_control`, which annotates system prompts,
tool lists, and few-shot example messages with ``cache_control: {"type": "ephemeral"}``
breakpoints so that Anthropic's prompt-caching layer can store and reuse those
segments across requests.

Caller-side usage (the "examples" key must be handled separately):

    cached = apply_cache_control(system=sys, tools=tools, examples=exs)
    example_messages = cached.pop("examples", [])
    user_messages = [{"role": "user", "content": user_prompt}]
    messages = example_messages + user_messages
    response = client.messages.create(messages=messages, **cached)

The ``"examples"`` key is a LIBRARY-INTERNAL key — the Anthropic ``messages.create``
API does NOT accept an ``"examples"`` parameter. Callers must pop this key and prepend
the annotated example messages to the ``messages`` array before calling
``messages.create``. Passing ``**apply_cache_control(...)`` directly to
``messages.create`` without popping ``"examples"`` first will raise a TypeError with a
real Anthropic client.
"""
from __future__ import annotations

from typing import Any

EPHEMERAL: dict[str, str] = {"type": "ephemeral"}


def apply_cache_control(
    *,
    system: str | None = None,
    tools: list[dict[str, Any]] | None = None,
    examples: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build cache_control-annotated kwargs for messages.create.

    Breakpoints are placed at:
      1. The system prompt block (when present)
      2. The last tool in the tools array (when present)
      3. The last content block of the last example message (when present)

    Returns a dict with keys:
      - ``"system"``: list[dict]   — ready for ``messages.create(system=...)``
      - ``"tools"``:  list[dict]   — ready for ``messages.create(tools=...)``
      - ``"examples"``: list[dict] — LIBRARY-INTERNAL KEY. The Anthropic
        ``messages.create`` API does NOT accept an ``"examples"`` parameter.
        Callers must pop this key and prepend the annotated example messages
        to the messages array before calling ``messages.create``.
        See the module-level docstring for the canonical caller pattern.

    Each key is only included in the returned dict when the corresponding
    argument is non-None (and non-empty for lists). A call with all-None
    arguments returns an empty dict ``{}``.

    Parameters
    ----------
    system:
        Plain text system prompt. When present, wrapped as
        ``[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]``.
    tools:
        List of tool definition dicts. When present, ``cache_control`` is added
        to the **last** item (the canonical Anthropic pattern).
    examples:
        List of few-shot / golden example message dicts (each with ``"role"`` and
        ``"content"``). When present, ``cache_control`` is added to the last
        content block of the last example message. The annotated list is returned
        under the library-internal ``"examples"`` key — see caller pattern above.
    """
    kwargs: dict[str, Any] = {}

    if system is not None:
        kwargs["system"] = [
            {"type": "text", "text": system, "cache_control": EPHEMERAL}
        ]

    if tools:
        annotated_tools = list(tools)
        annotated_tools[-1] = {**annotated_tools[-1], "cache_control": EPHEMERAL}
        kwargs["tools"] = annotated_tools

    if examples:
        annotated_examples = list(examples)
        last = dict(annotated_examples[-1])
        content = list(last.get("content", []))
        if content:
            content[-1] = {**content[-1], "cache_control": EPHEMERAL}
            last["content"] = content
        annotated_examples[-1] = last
        kwargs["examples"] = annotated_examples

    return kwargs
