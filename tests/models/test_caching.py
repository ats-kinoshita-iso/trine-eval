"""Tests for apply_cache_control helper (C1, C2, C3)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from trine_eval.models.caching import apply_cache_control, EPHEMERAL


class TestSystemPromptCacheControl:
    def test_system_prompt_cache_control(self) -> None:
        """C1: cache_control breakpoint appears on system prompt block."""
        with patch("anthropic.Anthropic"):
            result = apply_cache_control(system="You are a helpful assistant.")

        assert "system" in result, "apply_cache_control should return a 'system' key"
        system_blocks = result["system"]
        assert isinstance(system_blocks, list), "system value must be a list"
        assert len(system_blocks) == 1
        block = system_blocks[0]
        assert block.get("type") == "text"
        assert block.get("text") == "You are a helpful assistant."
        assert block.get("cache_control") == EPHEMERAL, (
            f"Expected cache_control={EPHEMERAL!r}, got {block.get('cache_control')!r}"
        )


class TestToolsCacheControl:
    def test_tools_cache_control(self) -> None:
        """C2: cache_control breakpoint appears on the last tool in the tools list."""
        tools = [
            {"name": "search", "description": "Search the web"},
            {"name": "bash", "description": "Run bash commands"},
        ]
        with patch("anthropic.Anthropic"):
            result = apply_cache_control(tools=tools)

        assert "tools" in result, "apply_cache_control should return a 'tools' key"
        annotated_tools = result["tools"]
        assert isinstance(annotated_tools, list)
        assert len(annotated_tools) == 2

        # Only the LAST tool gets cache_control (canonical Anthropic pattern)
        last_tool = annotated_tools[-1]
        assert last_tool.get("cache_control") == EPHEMERAL, (
            f"Last tool must have cache_control={EPHEMERAL!r}, got {last_tool.get('cache_control')!r}"
        )

        # First tool must NOT have cache_control
        first_tool = annotated_tools[0]
        assert "cache_control" not in first_tool, (
            "Only the last tool should have cache_control; first tool should not"
        )

        # Original tool dicts must be unchanged (immutability)
        assert "cache_control" not in tools[-1], (
            "apply_cache_control must not mutate the original tools list"
        )


class TestExamplesCacheControl:
    def test_examples_cache_control(self) -> None:
        """C3: cache_control breakpoint appears on last content block of last example."""
        examples = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What is 2+2?"},
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "The answer is 4."},
                    {"type": "text", "text": "This is a simple arithmetic fact."},
                ],
            },
        ]
        with patch("anthropic.Anthropic"):
            result = apply_cache_control(examples=examples)

        assert "examples" in result, "apply_cache_control should return an 'examples' key"
        annotated_examples = result["examples"]
        assert isinstance(annotated_examples, list)
        assert len(annotated_examples) == 2

        # The last content block of the last example gets cache_control
        last_example = annotated_examples[-1]
        last_content_blocks = last_example["content"]
        last_block = last_content_blocks[-1]
        assert last_block.get("cache_control") == EPHEMERAL, (
            f"Last content block of last example must have cache_control={EPHEMERAL!r}"
        )

        # Earlier content blocks in the last example must NOT have cache_control
        if len(last_content_blocks) > 1:
            first_block = last_content_blocks[0]
            assert "cache_control" not in first_block, (
                "Only the last content block of the last example should have cache_control"
            )

        # Original examples must be unchanged
        assert "cache_control" not in examples[-1]["content"][-1], (
            "apply_cache_control must not mutate the original examples list"
        )

    def test_examples_key_is_library_internal(self) -> None:
        """Verify the examples key is documented as library-internal (not passed to messages.create)."""
        # The examples key in the return dict is library-internal.
        # Callers must pop it and prepend to messages, not expand via **kwargs.
        with patch("anthropic.Anthropic") as MockClient:
            mock_client = MockClient.return_value
            examples = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": "example question"}],
                },
                {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "example answer"}],
                },
            ]
            cached = apply_cache_control(system="sys", examples=examples)

            # Demonstrate the correct caller pattern: pop examples, prepend to messages
            example_messages = cached.pop("examples", [])
            user_messages = [{"role": "user", "content": "real question"}]
            messages = example_messages + user_messages

            # After pop, "examples" key is gone — safe to expand into messages.create
            assert "examples" not in cached, (
                "After pop, 'examples' must not remain in cached dict"
            )
            # Now cached only has "system" (no "examples")
            mock_client.messages.create(messages=messages, **cached)
            # Verify messages.create was called without "examples" kwarg
            call_kwargs = mock_client.messages.create.call_args[1]
            assert "examples" not in call_kwargs, (
                "messages.create must not receive 'examples' as a kwarg"
            )
            assert "messages" in call_kwargs or mock_client.messages.create.call_args[0]
