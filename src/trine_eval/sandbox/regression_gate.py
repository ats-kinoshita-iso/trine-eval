"""trine_eval.sandbox.regression_gate — FAIL_TO_PASS / PASS_TO_PASS regression gate.

Captures pre-patch test outcomes, applies a candidate patch, re-runs tests,
and auto-fails any PASS_TO_PASS -> FAIL transition or any remaining FAIL_TO_PASS failure.
"""
from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class RegressionGateResult:
    fail_to_pass_passed: int
    fail_to_pass_total: int
    pass_to_pass_regressions: list[str]
    verdict: Literal["pass", "fail"]


def _parse_test_outcomes(output: str) -> dict[str, str]:
    """Parse pytest -v output: returns {test_name: "PASSED"|"FAILED"|...}"""
    results: dict[str, str] = {}
    for line in output.splitlines():
        for status in ("PASSED", "FAILED", "ERROR", "SKIPPED"):
            if f" {status}" in line:
                test_name = line.split()[0]
                results[test_name] = status
                break
    return results


def evaluate_regression_gate(
    repo_dir: str | Path,
    *,
    patch_command: str,
    test_command: str,
    fail_to_pass: list[str],
    pass_to_pass: list[str],
) -> RegressionGateResult:
    """Run pre-patch baseline, apply patch, run post-patch tests.

    Any PASS_TO_PASS -> FAIL transition is an automatic verdict=fail.
    Any remaining FAIL_TO_PASS failure is also verdict=fail.
    """
    repo = Path(repo_dir)

    # Pre-patch baseline
    pre = subprocess.run(
        test_command.split(),
        capture_output=True,
        text=True,
        cwd=repo,
    )
    pre_outcomes = _parse_test_outcomes(pre.stdout + pre.stderr)

    # Apply patch
    subprocess.run(
        patch_command.split(),
        capture_output=True,
        text=True,
        cwd=repo,
        check=True,
    )

    # Post-patch outcomes
    post = subprocess.run(
        test_command.split(),
        capture_output=True,
        text=True,
        cwd=repo,
    )
    post_outcomes = _parse_test_outcomes(post.stdout + post.stderr)

    regressions = [
        t for t in pass_to_pass
        if post_outcomes.get(t, "FAILED") != "PASSED"
    ]
    ftp_passed = sum(
        1 for t in fail_to_pass
        if post_outcomes.get(t, "FAILED") == "PASSED"
    )
    verdict: Literal["pass", "fail"] = (
        "fail" if (regressions or ftp_passed < len(fail_to_pass)) else "pass"
    )
    return RegressionGateResult(
        fail_to_pass_passed=ftp_passed,
        fail_to_pass_total=len(fail_to_pass),
        pass_to_pass_regressions=regressions,
        verdict=verdict,
    )
