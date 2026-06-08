"""trine_eval.sandbox — Docker sandbox, pre-filter pipeline, and regression gate.

Public surface:
    run_in_sandbox         — Docker container abstraction (docker.py)
    SandboxResult          — result dataclass (docker.py)
    run_prefilter          — four-stage pre-filter pipeline (prefilter.py)
    PrefilterResult        — result dataclass (prefilter.py)
    evaluate_regression_gate — FAIL_TO_PASS/PASS_TO_PASS gate (regression_gate.py)
    RegressionGateResult   — result dataclass (regression_gate.py)
"""
from __future__ import annotations

from trine_eval.sandbox.docker import SandboxResult, run_in_sandbox
from trine_eval.sandbox.prefilter import PrefilterResult, run_prefilter
from trine_eval.sandbox.regression_gate import RegressionGateResult, evaluate_regression_gate

__all__ = [
    "SandboxResult",
    "run_in_sandbox",
    "PrefilterResult",
    "run_prefilter",
    "RegressionGateResult",
    "evaluate_regression_gate",
]
