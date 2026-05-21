"""trine_eval.judge — LLM-as-judge subsystem.

Public surface:
    model_graded_qa  — CoT rubric scorer (rubric.py)
    compute_tpr_tnr  — calibration arithmetic (calibration.py)
    bootstrap_ci     — bootstrap CI estimator (bootstrap.py)
    BootstrapCI      — result namedtuple (bootstrap.py)
    dispatch_score   — three-tier dispatcher (dispatch.py)
    ListQueue        — human annotation queue (queue.py)
    get_default_queue— singleton queue accessor (queue.py)
"""
from __future__ import annotations

from trine_eval.judge.bootstrap import BootstrapCI, bootstrap_ci
from trine_eval.judge.calibration import compute_tpr_tnr
from trine_eval.judge.dispatch import dispatch_score
from trine_eval.judge.queue import ListQueue, get_default_queue
from trine_eval.judge.rubric import model_graded_qa

__all__ = [
    "BootstrapCI",
    "ListQueue",
    "bootstrap_ci",
    "compute_tpr_tnr",
    "dispatch_score",
    "get_default_queue",
    "model_graded_qa",
]
