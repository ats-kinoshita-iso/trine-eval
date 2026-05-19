"""Tests for the three-tier dispatcher (C8, C9).

All judge model interactions are mocked — no real Anthropic API calls.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.judge.dispatch import dispatch_score
from trine_eval.judge.queue import ListQueue


# ---------------------------------------------------------------------------
# C8 — code tier: judge model is NEVER called
# ---------------------------------------------------------------------------

def test_dispatch_code_tier_no_judge() -> None:
    """C8: dispatch_score with tier='code' scorer never invokes the judge model.

    The scorer is called directly; metadata["tier"] == "code".
    The mock judge model call_count must remain 0.
    """
    sample = Sample(id="c8-sample", input="Student answer for code-tier test.")

    # Mock scorer that returns a Score and has tier="code"
    mock_code_scorer = MagicMock(return_value=Score(value=1.0, metadata={}))
    mock_code_scorer.tier = "code"

    # Mock judge — must NEVER be called
    mock_judge = MagicMock()

    score = dispatch_score(sample, scorer=mock_code_scorer, judge_model=mock_judge)

    assert score is not None, "dispatch_score with code tier should return a Score"
    assert score.metadata.get("tier") == "code", (
        f"score.metadata['tier'] must be 'code', got {score.metadata.get('tier')!r}"
    )
    assert mock_judge.call_count == 0, (
        f"judge_model must NOT be called for code tier, "
        f"but call_count == {mock_judge.call_count}"
    )
    # Also assert the scorer itself was called once
    mock_code_scorer.assert_called_once_with(sample)


# ---------------------------------------------------------------------------
# C9 — model tier and human tier routing
# ---------------------------------------------------------------------------

def test_dispatch_model_and_human_tiers() -> None:
    """C9: tier=model routes through the judge; tier=human enqueues without a Score.

    Model tier:
      - judge_model IS called exactly once.
      - Returned Score.metadata["tier"] == "model".

    Human tier:
      - Sample is enqueued in the queue.
      - No synchronous Score is returned (returns None).
      - judge_model is NOT called.
    """
    # -----------------------------------------------------------------------
    # (a) tier=model
    # -----------------------------------------------------------------------
    sample_model = Sample(id="c9-model", input="Answer for model-tier test.")

    mock_judge = MagicMock()

    # A model-tier scorer accepts (sample, judge_model=...) and returns a Score
    def _model_scorer(s: Sample, *, judge_model: object) -> Score:
        # Invoke the judge (as the real implementation would)
        judge_model.complete("some prompt")  # type: ignore[union-attr]
        return Score(value=1.0, metadata={})

    mock_model_scorer = MagicMock(side_effect=_model_scorer)
    mock_model_scorer.tier = "model"

    score_model = dispatch_score(
        sample_model, scorer=mock_model_scorer, judge_model=mock_judge
    )

    assert score_model is not None, "dispatch_score with model tier should return a Score"
    assert score_model.metadata.get("tier") == "model", (
        f"score.metadata['tier'] must be 'model', got {score_model.metadata.get('tier')!r}"
    )
    # judge.complete should have been called exactly once (by _model_scorer)
    assert mock_judge.complete.call_count == 1, (
        f"judge_model.complete must be called exactly once for model tier, "
        f"got call_count={mock_judge.complete.call_count}"
    )

    # -----------------------------------------------------------------------
    # (b) tier=human
    # -----------------------------------------------------------------------
    sample_human = Sample(id="c9-human", input="Answer for human-tier test.")

    # Use a fresh ListQueue so we don't depend on the global singleton state
    fresh_queue = ListQueue()
    mock_human_scorer = MagicMock()
    mock_human_scorer.tier = "human"
    mock_judge2 = MagicMock()

    with patch("trine_eval.judge.dispatch.get_default_queue", return_value=fresh_queue):
        result_human = dispatch_score(
            sample_human, scorer=mock_human_scorer, judge_model=mock_judge2
        )

    # Human tier must return None (no synchronous score)
    assert result_human is None, (
        f"dispatch_score with human tier must return None, got {result_human!r}"
    )

    # Sample must have been enqueued
    pending = fresh_queue.list()
    assert len(pending) == 1, (
        f"Expected 1 pending item in queue after human-tier dispatch, got {len(pending)}"
    )
    assert pending[0]["id"] == sample_human.id, (
        f"Enqueued item id should be {sample_human.id!r}, got {pending[0]['id']!r}"
    )

    # Judge must NOT have been called for human tier
    assert mock_judge2.call_count == 0, (
        f"judge_model must NOT be called for human tier, "
        f"call_count={mock_judge2.call_count}"
    )
