"""CoT-rubric scorer for LLM-as-judge grading.

Exposes ``model_graded_qa``, registered in the scorer registry via ``@scorer``.
The function constructs a chain-of-thought grading prompt that embeds the
criterion text and the golden (reference) answer, calls the judge model once,
parses a binary verdict from the response, and returns a ``Score`` with the
full response stored in ``Score.reasoning``.
"""
from __future__ import annotations

from typing import Any

from trine_eval.core.decorators import scorer
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score

_COT_PROMPT_TEMPLATE = """\
You are a grader evaluating a student's answer.

Grading criterion:
{criterion}

Expected (golden) answer:
{golden_answer}

Student's answer:
{student_answer}

Think step by step. Then on a final line output exactly one of: PASS or FAIL.
"""

_VERDICT_MAP: dict[str, float] = {
    "pass": 1.0,
    "1": 1.0,
    "correct": 1.0,
    "yes": 1.0,
    "fail": 0.0,
    "0": 0.0,
    "incorrect": 0.0,
    "no": 0.0,
}


def _parse_verdict(text: str) -> float:
    """Extract binary verdict from judge response text.

    Scans lines in reverse order so the final verdict line wins.
    Falls back to scanning the whole text for any verdict keyword.
    Returns 0.0 (conservative) when no verdict is found.
    """
    for line in reversed(text.strip().splitlines()):
        token = line.strip().lower()
        if token in _VERDICT_MAP:
            return _VERDICT_MAP[token]
    # Fallback: scan for any verdict keyword in the full text
    lower = text.lower()
    for kw, val in _VERDICT_MAP.items():
        if kw in lower:
            return val
    return 0.0  # conservative default


@scorer
def model_graded_qa(
    sample: Sample,
    *,
    criterion: str,
    golden_answer: str,
    judge_model: Any,
) -> Score:
    """Grade a sample using a CoT rubric prompt with a golden answer.

    Parameters
    ----------
    sample:
        The evaluation sample; ``sample.input`` is treated as the student answer.
    criterion:
        The grading criterion text (embedded in the prompt).
    golden_answer:
        The reference answer (embedded in the prompt).
    judge_model:
        Any object with a ``complete(prompt: str) -> str`` method.

    Returns
    -------
    Score
        ``value`` is 1.0 (PASS) or 0.0 (FAIL).
        ``reasoning`` holds the full judge response text (CoT chain).
    """
    prompt = _COT_PROMPT_TEMPLATE.format(
        criterion=criterion,
        golden_answer=golden_answer,
        student_answer=sample.input,
    )
    response_text: str = judge_model.complete(prompt)
    value = _parse_verdict(response_text)
    return Score(
        value=value,
        reasoning=response_text,
        metadata={"judge": "model_graded_qa"},
    )
