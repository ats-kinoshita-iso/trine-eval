"""Calibration helpers for LLM-as-judge binary scoring.

Provides ``compute_tpr_tnr``, which computes True Positive Rate (TPR)
and True Negative Rate (TNR) for a binary scorer against a labeled dataset.

Definitions
-----------
    TPR (sensitivity / recall) = TP / (TP + FN)
    TNR (specificity)          = TN / (TN + FP)

where the positive class is ``label == 1`` and a prediction is considered
positive when ``Score.value >= 0.5``.
"""
from __future__ import annotations

from typing import Iterable


def compute_tpr_tnr(
    predictions: Iterable[float],
    labels: Iterable[int],
) -> tuple[float, float]:
    """Compute binary TPR and TNR from parallel prediction/label sequences.

    Parameters
    ----------
    predictions:
        Iterable of predicted scores (floats). A value >= 0.5 is treated as
        a positive prediction; < 0.5 is treated as negative.
    labels:
        Iterable of ground-truth binary labels (0 or 1).

    Returns
    -------
    (tpr, tnr)
        Both are floats in [0.0, 1.0].

    Raises
    ------
    ValueError
        If the number of predictions does not match the number of labels, or
        if there are no positive / no negative examples (division by zero).
    """
    pred_list = list(predictions)
    label_list = list(labels)

    if len(pred_list) != len(label_list):
        raise ValueError(
            f"Length mismatch: {len(pred_list)} predictions vs "
            f"{len(label_list)} labels."
        )

    tp = tn = fp = fn = 0
    for pred, label in zip(pred_list, label_list):
        predicted_positive = pred >= 0.5
        if label == 1:
            if predicted_positive:
                tp += 1
            else:
                fn += 1
        else:  # label == 0
            if predicted_positive:
                fp += 1
            else:
                tn += 1

    if (tp + fn) == 0:
        raise ValueError("No positive examples (TP + FN == 0); TPR is undefined.")
    if (tn + fp) == 0:
        raise ValueError("No negative examples (TN + FP == 0); TNR is undefined.")

    tpr = tp / (tp + fn)
    tnr = tn / (tn + fp)
    return tpr, tnr
