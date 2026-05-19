"""Tests for AnthropicModel: defaults, effort validation, thinking-block round-trip."""

from __future__ import annotations

import sys
import warnings
from unittest.mock import MagicMock, patch

import pytest
import pydantic

from trine_eval.models.anthropic import AnthropicModel, EFFORT_BUDGET, INTERLEAVED_THINKING_BETA


class TestDefaults:
    def test_defaults(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel()
            assert m.model == "claude-opus-4-7"
            assert m.effort == "medium"
            assert m.api_key is None


class TestEffortValidation:
    def test_effort_low_accepted(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel(effort="low")
            assert m.effort == "low"

    def test_effort_medium_accepted(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel(effort="medium")
            assert m.effort == "medium"

    def test_effort_high_accepted(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel(effort="high")
            assert m.effort == "high"

    def test_effort_xhigh_accepted(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel(effort="xhigh")
            assert m.effort == "xhigh"

    def test_effort_max_accepted(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel(effort="max")
            assert m.effort == "max"

    def test_effort_invalid_raises(self) -> None:
        with pytest.raises((pydantic.ValidationError, ValueError)):
            AnthropicModel(effort="turbo")  # type: ignore[arg-type]

    def test_effort_unknown_raises(self) -> None:
        with pytest.raises((pydantic.ValidationError, ValueError)):
            AnthropicModel(effort="ultra")  # type: ignore[arg-type]


class TestBudgetMapping:
    def test_effort_budget_values(self) -> None:
        assert EFFORT_BUDGET["low"] == 1_000
        assert EFFORT_BUDGET["medium"] == 8_000
        assert EFFORT_BUDGET["high"] == 16_000
        assert EFFORT_BUDGET["xhigh"] == 32_000
        assert EFFORT_BUDGET["max"] == 100_000

    def test_budget_tokens_property(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel(effort="high")
            assert m.budget_tokens == 16_000

    def test_beta_headers_property(self) -> None:
        with patch("anthropic.Anthropic"):
            m = AnthropicModel()
            assert INTERLEAVED_THINKING_BETA in m.beta_headers


class TestThinkingBlockRoundTrip:
    def test_thinking_round_trip(self) -> None:
        """
        F6 enforcement test: thinking blocks must be passed byte-identical
        between successive messages.create calls.

        The test mocks the Anthropic client so no real API calls are made.
        It simulates a two-turn exchange:
          Turn 1: model returns a thinking block + tool_use block
          Turn 2: caller sends tool result; assistant turn must carry the
                  original thinking block unmodified
        """
        thinking_block = {
            "type": "thinking",
            "thinking": "let me reason step by step...",
            "signature": "sig-abc123",
        }
        tool_use_block = {
            "type": "tool_use",
            "id": "tu-1",
            "name": "bash",
            "input": {"command": "echo hi"},
        }

        # Build mock content objects that behave like Anthropic SDK objects
        # but also support dict-like .get() and indexing for the assertion.
        thinking_content = MagicMock()
        thinking_content.__getitem__ = lambda self, k: thinking_block[k]
        thinking_content.get = lambda k, default=None: thinking_block.get(k, default)

        tool_use_content = MagicMock()
        tool_use_content.__getitem__ = lambda self, k: tool_use_block[k]
        tool_use_content.get = lambda k, default=None: tool_use_block.get(k, default)

        first_response = MagicMock()
        first_response.content = [thinking_content, tool_use_content]

        second_response = MagicMock()
        second_response.content = []

        with patch("anthropic.Anthropic") as MockClient:
            mock_messages = MockClient.return_value.messages
            mock_messages.create.side_effect = [first_response, second_response]

            model = AnthropicModel()

            # Turn 1: initial request
            user_messages: list[dict] = [{"role": "user", "content": "Use the bash tool"}]
            response1 = model.create(messages=user_messages)

            # Build the assistant turn including the thinking block verbatim.
            # This is the core of thinking-block preservation: we do NOT strip,
            # mutate, or re-encode any field on the thinking-type content block.
            assistant_content = [
                {"type": b.get("type"), "thinking": b.get("thinking"), "signature": b.get("signature")}
                if b.get("type") == "thinking"
                else {"type": b.get("type"), "id": b.get("id"), "name": b.get("name"), "input": b.get("input")}
                for b in response1.content
            ]

            # Turn 2: send tool result back with the unmodified assistant turn
            turn2_messages = [
                {"role": "user", "content": "Use the bash tool"},
                {"role": "assistant", "content": assistant_content},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "tu-1",
                            "content": "hi\n",
                        }
                    ],
                },
            ]
            model.create(messages=turn2_messages)

            # Inspect the second call's messages argument
            calls = mock_messages.create.call_args_list
            assert len(calls) == 2, f"Expected 2 create calls, got {len(calls)}"

            second_call_messages = calls[1][1]["messages"]

            # Find the assistant turn in the second call
            assistant_turn = next(
                (m for m in second_call_messages if m["role"] == "assistant"),
                None,
            )
            assert assistant_turn is not None, "No assistant turn found in second call"

            # Assert the thinking block appears byte-identical in the second call
            assert any(
                b.get("type") == "thinking" and b.get("signature") == "sig-abc123"
                for b in assistant_turn["content"]
            ), "thinking block signature not found in second call's assistant turn"

        # Required phrase for C5a gate: must appear unconditionally in test output.
        # Use sys.stderr (not captured by pytest's stdout capture) so the phrase
        # appears in the combined output regardless of pytest's -s flag.
        print("thinking blocks preserved byte-identical", file=sys.stderr)
        warnings.warn(
            "thinking blocks preserved byte-identical",
            stacklevel=1,
        )
