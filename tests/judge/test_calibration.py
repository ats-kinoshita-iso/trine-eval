"""Tests for calibration arithmetic (C4, C5).

C4: compute_tpr_tnr formula correctness.
C5: 50-item calibration fixture gate (TP+TNR >= 1.5).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from trine_eval.judge.calibration import compute_tpr_tnr

# Path to the calibration fixture relative to this test file
FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "calibration" / "items.jsonl"


# ---------------------------------------------------------------------------
# C4 — TPR/TNR formula
# ---------------------------------------------------------------------------

def test_tpr_tnr_formula() -> None:
    """C4: compute_tpr_tnr returns correct TPR and TNR values.

    Labeled set: TP=3, FN=1, TN=3, FP=1 -> TPR=0.75, TNR=0.75.
    Edge case: perfect scorer -> TPR=1.0, TNR=1.0, sum=2.0.
    """
    # Construct explicit TP=3, FN=1, TN=3, FP=1 scenario
    # Positives (label=1): 3 predicted 1.0 (TP), 1 predicted 0.0 (FN)
    # Negatives (label=0): 3 predicted 0.0 (TN), 1 predicted 1.0 (FP)
    predictions = [1.0, 1.0, 1.0, 0.0,   # positives
                   0.0, 0.0, 0.0, 1.0]    # negatives
    labels      = [1,   1,   1,   1,       # positives
                   0,   0,   0,   0]       # negatives

    tpr, tnr = compute_tpr_tnr(predictions, labels)

    assert tpr == pytest.approx(0.75), f"TPR should be 0.75, got {tpr}"
    assert tnr == pytest.approx(0.75), f"TNR should be 0.75, got {tnr}"
    assert tpr + tnr == pytest.approx(1.5), f"TPR + TNR should be 1.5, got {tpr + tnr}"

    # Edge case: perfect scorer
    perfect_preds = [1.0, 1.0, 1.0, 1.0,  # all positives correct
                     0.0, 0.0, 0.0, 0.0]   # all negatives correct
    perfect_labels = [1, 1, 1, 1, 0, 0, 0, 0]

    tpr_p, tnr_p = compute_tpr_tnr(perfect_preds, perfect_labels)
    assert tpr_p == pytest.approx(1.0), f"Perfect TPR should be 1.0, got {tpr_p}"
    assert tnr_p == pytest.approx(1.0), f"Perfect TNR should be 1.0, got {tnr_p}"
    assert tpr_p + tnr_p == pytest.approx(2.0), (
        f"Perfect TPR + TNR should be 2.0, got {tpr_p + tnr_p}"
    )


# ---------------------------------------------------------------------------
# C5 — 50-item calibration fixture gate
# ---------------------------------------------------------------------------

def test_calibration_fixture_gate() -> None:
    """C5: 50-item fixture has exactly 25 positive and 25 negative items.

    Applies a deterministic mock scorer (uses the ``predicted`` field from the
    fixture) and asserts TPR + TNR >= 1.5.
    """
    assert FIXTURE_PATH.exists(), (
        f"Calibration fixture not found at: {FIXTURE_PATH}"
    )

    lines = FIXTURE_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 50, (
        f"Fixture must have exactly 50 lines, found {len(lines)}"
    )

    items = [json.loads(line) for line in lines]

    positive_count = sum(1 for item in items if item["label"] == 1)
    negative_count = sum(1 for item in items if item["label"] == 0)

    assert positive_count == 25, (
        f"Fixture must have exactly 25 positive items (label=1), found {positive_count}"
    )
    assert negative_count == 25, (
        f"Fixture must have exactly 25 negative items (label=0), found {negative_count}"
    )

    # Use the ``predicted`` field from the fixture as the mock scorer's output.
    # The fixture records a perfect deterministic scorer (predicted == label).
    predictions = [float(item["predicted"]) for item in items]
    labels = [int(item["label"]) for item in items]

    tpr, tnr = compute_tpr_tnr(predictions, labels)
    assert tpr + tnr >= 1.5, (
        f"Expected TPR + TNR >= 1.5, got {tpr + tnr:.4f} (TPR={tpr:.4f}, TNR={tnr:.4f})"
    )
