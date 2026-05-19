"""Tests for the CoT-rubric scorer (C1, C2, C3).

All tests mock the judge model so no real Anthropic API calls are made.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import trine_eval.core.registry as registry
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.judge.rubric import model_graded_qa


# ---------------------------------------------------------------------------
# C1 — prompt contains criterion and golden answer
# ---------------------------------------------------------------------------

def test_rubric_prompt_contains_criterion_and_golden() -> None:
    """C1: model_graded_qa embeds criterion and golden_answer in the prompt."""
    sample = Sample(id="s1", input="Light is absorbed by chlorophyll pigments.")
    criterion = "Explain photosynthesis"
    golden = "Plants convert light to energy"

    captured_prompt: list[str] = []

    mock_model = MagicMock()
    mock_model.complete.side_effect = lambda prompt: (
        captured_prompt.append(prompt) or "PASS"
    )

    score = model_graded_qa(
        sample,
        criterion=criterion,
        golden_answer=golden,
        judge_model=mock_model,
    )

    assert len(captured_prompt) == 1, "judge_model.complete should be called once"
    prompt_text = captured_prompt[0]

    assert criterion in prompt_text, (
        f"Prompt should contain criterion text: {criterion!r}"
    )
    assert golden in prompt_text, (
        f"Prompt should contain golden answer: {golden!r}"
    )
    assert score.value in (0.0, 1.0), (
        f"Score.value must be 0.0 or 1.0, got {score.value!r}"
    )


# ---------------------------------------------------------------------------
# C2 — verdict parsing and reasoning storage
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "response_text, expected_value",
    [
        (
            "The student correctly identifies chlorophyll.\nThe answer is complete.\nPASS",
            1.0,
        ),
        (
            "The student answer is missing key concepts.\nThe answer is incomplete.\nFAIL",
            0.0,
        ),
    ],
)
def test_rubric_parses_verdict_and_reasoning(
    response_text: str, expected_value: float
) -> None:
    """C2: model_graded_qa parses PASS/FAIL verdict and stores full response in reasoning."""
    sample = Sample(id="s2", input="Some student answer.")
    mock_model = MagicMock()
    mock_model.complete.return_value = response_text

    score = model_graded_qa(
        sample,
        criterion="Some criterion",
        golden_answer="Some golden answer",
        judge_model=mock_model,
    )

    assert score.value == expected_value, (
        f"Expected Score.value == {expected_value}, got {score.value!r}"
    )
    assert isinstance(score.reasoning, str) and len(score.reasoning) > 0, (
        "Score.reasoning must be a non-empty string"
    )
    assert score.reasoning == response_text, (
        "Score.reasoning must store the full judge response, not just the verdict token"
    )


# ---------------------------------------------------------------------------
# C3 — scorer registered in registry
# ---------------------------------------------------------------------------

def test_rubric_scorer_registered() -> None:
    """C3: importing trine_eval.judge.rubric registers model_graded_qa in the scorer registry."""
    # Importing rubric triggers the @scorer decorator at module level.
    # The import already happened at the top of this file, so we just check.
    import trine_eval.judge.rubric  # noqa: F401 — ensure module is imported

    assert "model_graded_qa" in registry.scorers, (
        "'model_graded_qa' must be registered in trine_eval.core.registry.scorers "
        "as a side-effect of importing trine_eval.judge.rubric"
    )
