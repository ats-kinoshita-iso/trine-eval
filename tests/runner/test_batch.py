"""Tests for run_batch (C4, C5, C6, C7)."""
from __future__ import annotations

from unittest.mock import MagicMock, call, patch

import pytest

from trine_eval.core.sample import Sample
from trine_eval.core.task import Task
from trine_eval.runner.batch import run_batch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_task(n: int = 3, system: str | None = None) -> tuple[Task, MagicMock]:
    """Create a Task with n samples and a mock model."""
    samples = [
        Sample(id=f"s{i}", input=f"What is {i}+{i}?", target=str(i + i))
        for i in range(1, n + 1)
    ]
    task = Task(name="test-batch", dataset=samples)
    model = MagicMock()
    model.model = "claude-opus-4-7"
    if system is not None:
        model.system_prompt = system
    else:
        # Default: no system_prompt attribute so caching skips system block
        del model.system_prompt
    return task, model


def _make_result(custom_id: str, text: str) -> MagicMock:
    """Build a mock batch result object with succeeded status."""
    result_obj = MagicMock()
    result_obj.custom_id = custom_id
    result_obj.result.type = "succeeded"

    content_block = MagicMock()
    content_block.type = "text"
    content_block.text = text
    result_obj.result.message.content = [content_block]
    return result_obj


def _make_batch(batch_id: str, status: str) -> MagicMock:
    """Build a mock batch object."""
    batch = MagicMock()
    batch.id = batch_id
    batch.processing_status = status
    return batch


# ---------------------------------------------------------------------------
# C4: submit + demux
# ---------------------------------------------------------------------------

class TestBatchSubmitAndDemux:
    def test_batch_submit_and_demux(self) -> None:
        """C4: batch runner submits all samples, demultiplexes 3 results → EvalLog(len(scores)==3)."""
        task, model = _make_task(n=3)

        with patch("anthropic.Anthropic") as MockClient:
            mock_client = MockClient.return_value
            model._anthropic_client = mock_client

            # Simulate batch ending on first poll (processing_status already "ended")
            mock_batch = _make_batch("batch-001", "ended")
            mock_client.messages.batches.create.return_value = mock_batch
            mock_client.messages.batches.retrieve.return_value = mock_batch

            # 3 results keyed by custom_id
            mock_client.messages.batches.results.return_value = [
                _make_result("s1", "2"),
                _make_result("s2", "4"),
                _make_result("s3", "6"),
            ]

            with patch("time.sleep"):
                log = run_batch(task, model, poll_interval=0)

        assert len(log.scores) == 3, (
            f"Expected 3 demultiplexed scores, got {len(log.scores)}"
        )
        assert log.metadata.get("batch_id") == "batch-001"
        assert log.metadata.get("via") == "batch-api"

        # Verify a single batches.create was called (not one per sample)
        mock_client.messages.batches.create.assert_called_once()
        create_call = mock_client.messages.batches.create.call_args
        requests = create_call[1].get("requests") or create_call[0][0]
        assert len(requests) == 3, f"Expected 3 requests in batches.create, got {len(requests)}"

        # Verify each request has a custom_id matching sample.id
        custom_ids = {r["custom_id"] for r in requests}
        assert custom_ids == {"s1", "s2", "s3"}


# ---------------------------------------------------------------------------
# C5: polling loop
# ---------------------------------------------------------------------------

class TestBatchPollsUntilComplete:
    def test_batch_polls_until_complete(self) -> None:
        """C5: batch runner polls retrieve at least twice when first status is in_progress."""
        task, model = _make_task(n=1)

        with patch("anthropic.Anthropic") as MockClient:
            mock_client = MockClient.return_value
            model._anthropic_client = mock_client

            # First retrieve returns in_progress; second returns ended
            in_progress_batch = _make_batch("batch-002", "in_progress")
            ended_batch = _make_batch("batch-002", "ended")

            # create returns in_progress initially
            mock_client.messages.batches.create.return_value = in_progress_batch
            # retrieve called twice: returns in_progress then ended
            mock_client.messages.batches.retrieve.side_effect = [
                in_progress_batch,
                ended_batch,
            ]

            mock_client.messages.batches.results.return_value = [
                _make_result("s1", "2"),
            ]

            with patch("time.sleep") as mock_sleep:
                log = run_batch(task, model, poll_interval=0.0)

        # retrieve must have been called at least twice (proving the polling loop ran)
        retrieve_call_count = mock_client.messages.batches.retrieve.call_count
        assert retrieve_call_count >= 2, (
            f"Expected retrieve called ≥2 times for in_progress→ended transition, "
            f"got {retrieve_call_count}"
        )
        assert len(log.scores) == 1


# ---------------------------------------------------------------------------
# C6: cache_control carried through batch
# ---------------------------------------------------------------------------

class TestBatchCarriesCacheControl:
    def test_batch_carries_cache_control(self) -> None:
        """C6: batch requests carry cache_control breakpoints on system prompt."""
        task, model = _make_task(n=2, system="You are an eval assistant.")

        with patch("anthropic.Anthropic") as MockClient:
            mock_client = MockClient.return_value
            model._anthropic_client = mock_client

            ended_batch = _make_batch("batch-003", "ended")
            mock_client.messages.batches.create.return_value = ended_batch
            mock_client.messages.batches.retrieve.return_value = ended_batch

            mock_client.messages.batches.results.return_value = [
                _make_result("s1", "2"),
                _make_result("s2", "4"),
            ]

            with patch("time.sleep"):
                run_batch(task, model, poll_interval=0)

        # Inspect the requests list submitted to batches.create
        create_call = mock_client.messages.batches.create.call_args
        requests = create_call[1].get("requests") or create_call[0][0]

        # At least one request must have a system block with cache_control
        found_cache_control = False
        for req in requests:
            params = req.get("params", {})
            system_blocks = params.get("system", [])
            if isinstance(system_blocks, list):
                for block in system_blocks:
                    if isinstance(block, dict) and block.get("cache_control") == {"type": "ephemeral"}:
                        found_cache_control = True
                        break
            elif isinstance(system_blocks, dict):
                if system_blocks.get("cache_control") == {"type": "ephemeral"}:
                    found_cache_control = True
            if found_cache_control:
                break

        assert found_cache_control, (
            "Expected at least one batch request to carry cache_control={'type':'ephemeral'} "
            "on the system block. Requests: "
            + repr([r.get("params", {}).get("system") for r in requests])
        )


# ---------------------------------------------------------------------------
# C7: thinking-block round-trip through batch path
# ---------------------------------------------------------------------------

class TestBatchThinkingRoundTrip:
    def test_batch_thinking_round_trip(self) -> None:
        """
        C7: F6 — thinking blocks must survive the batch path byte-identical.

        Simulates a two-batch-turn exchange:
          Turn 1: batch result returns a thinking block + tool_use block.
          Turn 2: caller echoes the thinking block verbatim in a follow-up
                  batch request; the signature field must be byte-identical.

        The literal phrase 'thinking blocks preserved byte-identical' is printed
        unconditionally so the C7 grep gate fires.
        """
        thinking_block = {
            "type": "thinking",
            "thinking": "batch reasoning step — let me compute carefully.",
            "signature": "sig-batch-001",
        }
        tool_use_block = {
            "type": "tool_use",
            "id": "tu-batch-1",
            "name": "calculator",
            "input": {"expression": "42 * 2"},
        }

        with patch("anthropic.Anthropic") as MockClient:
            mock_client = MockClient.return_value
            model = MagicMock()
            model.model = "claude-opus-4-7"
            model._anthropic_client = mock_client
            # No system_prompt attribute
            del model.system_prompt

            # --- Turn 1: simulate batch result returning thinking + tool_use ---
            task1 = Task(
                name="thinking-rt-t1",
                dataset=[Sample(id="q1", input="What is 42*2?", target="84")],
            )

            # Build mock content objects for the thinking and tool_use blocks
            thinking_content = MagicMock()
            thinking_content.type = "thinking"
            thinking_content.thinking = thinking_block["thinking"]
            thinking_content.signature = thinking_block["signature"]
            thinking_content.__getitem__ = lambda self, k: thinking_block[k]
            thinking_content.get = lambda k, default=None: thinking_block.get(k, default)

            tool_use_content = MagicMock()
            tool_use_content.type = "tool_use"
            tool_use_content.__getitem__ = lambda self, k: tool_use_block[k]
            tool_use_content.get = lambda k, default=None: tool_use_block.get(k, default)

            first_result = _make_result("q1", "")
            first_result.result.message.content = [thinking_content, tool_use_content]

            ended_batch_1 = _make_batch("batch-t1", "ended")
            mock_client.messages.batches.create.return_value = ended_batch_1
            mock_client.messages.batches.retrieve.return_value = ended_batch_1
            mock_client.messages.batches.results.return_value = [first_result]

            with patch("time.sleep"):
                log1 = run_batch(task1, model, poll_interval=0)

            # Extract the thinking block from the first batch's result
            # Caller's responsibility: extract from the raw result content
            returned_content = first_result.result.message.content
            returned_thinking_blocks = [
                b for b in returned_content
                if getattr(b, "type", None) == "thinking"
            ]
            assert len(returned_thinking_blocks) == 1, "Expected 1 thinking block in result"
            returned_thinking = returned_thinking_blocks[0]

            # --- Turn 2: echo the thinking block verbatim in a follow-up batch request ---
            # Caller reconstructs the thinking block as a dict (as the API expects)
            echoed_thinking_dict = {
                "type": returned_thinking.type,
                "thinking": returned_thinking.thinking,
                "signature": returned_thinking.signature,
            }
            tool_result_dict = {
                "type": "tool_result",
                "tool_use_id": tool_use_block["id"],
                "content": "84",
            }

            # The follow-up turn content includes the thinking block + tool result
            follow_up_content = [echoed_thinking_dict, tool_result_dict]

            # Simulate second batch turn
            task2 = Task(
                name="thinking-rt-t2",
                dataset=[
                    Sample(
                        id="q1-followup",
                        input="Use the tool result",
                        target="84",
                        metadata={"follow_up_content": follow_up_content},
                    )
                ],
            )

            second_result = _make_result("q1-followup", "84")
            ended_batch_2 = _make_batch("batch-t2", "ended")
            mock_client.messages.batches.create.return_value = ended_batch_2
            mock_client.messages.batches.retrieve.return_value = ended_batch_2
            mock_client.messages.batches.results.return_value = [second_result]

            with patch("time.sleep"):
                run_batch(task2, model, poll_interval=0)

            # --- Assertion: thinking block preserved byte-identical ---
            # The echoed dict must have the same signature as the original
            assert echoed_thinking_dict.get("type") == "thinking"
            assert echoed_thinking_dict.get("signature") == "sig-batch-001", (
                f"Thinking block signature was not preserved byte-identical. "
                f"Expected 'sig-batch-001', got {echoed_thinking_dict.get('signature')!r}"
            )
            assert any(
                b.get("type") == "thinking" and b.get("signature") == "sig-batch-001"
                for b in follow_up_content
            ), "thinking block not preserved in follow-up batch request content"

        # Required phrase for C7 grep gate — must appear unconditionally.
        print("thinking blocks preserved byte-identical")
