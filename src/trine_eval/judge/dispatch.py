"""Three-tier dispatcher for trine_eval judge routing.

Routes each sample to one of three grading tiers based on the scorer's
declared ``tier`` attribute:

    code  — call the scorer directly; judge_model is NEVER invoked.
    model — call the scorer (or judge); record tier in metadata.
    human — enqueue the sample to the human annotation queue; return None.

The dispatcher NEVER auto-escalates a code-tier scorer to the model tier,
regardless of the score value returned.
"""
from __future__ import annotations

from typing import Any

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.judge.queue import get_default_queue

_VALID_TIERS = frozenset({"code", "model", "human"})


def dispatch_score(
    sample: Sample,
    *,
    scorer: Any,
    judge_model: Any | None = None,
) -> Score | None:
    """Route a sample to the appropriate grading tier.

    Tier is read from ``scorer.tier`` (a string attribute set at decoration
    time or directly on the scorer object).  If ``scorer.tier`` is absent,
    the tier defaults to ``"code"``.

    Parameters
    ----------
    sample:
        The evaluation sample to grade.
    scorer:
        A callable with a ``.tier`` attribute declaring its grading tier.
        For ``tier="code"``, calling ``scorer(sample)`` must return a
        ``Score``.  For ``tier="model"``, calling
        ``scorer(sample, judge_model=judge_model)`` must return a ``Score``.
    judge_model:
        Required for ``tier="model"``.  Ignored (and never called) for
        ``tier="code"`` or ``tier="human"``.

    Returns
    -------
    Score | None
        ``Score`` for ``code`` and ``model`` tiers; ``None`` for ``human``.

    Raises
    ------
    ValueError
        If ``scorer.tier`` is not one of {code, model, human}, or if
        ``tier="model"`` is requested but ``judge_model`` is ``None``.

    Notes
    -----
    - Does NOT auto-escalate code → model under any condition.
    - The judge_model is NEVER called for code or human tiers.
    """
    tier: str = getattr(scorer, "tier", "code")
    if tier not in _VALID_TIERS:
        raise ValueError(
            f"Unknown tier {tier!r}. Must be one of {sorted(_VALID_TIERS)}."
        )

    if tier == "code":
        score: Score = scorer(sample)
        score.metadata["tier"] = "code"
        return score

    if tier == "model":
        if judge_model is None:
            raise ValueError("judge_model is required for tier='model'")
        score = scorer(sample, judge_model=judge_model)
        score.metadata["tier"] = "model"
        return score

    # tier == "human"
    queue = get_default_queue()
    queue.enqueue(sample)
    return None
