"""Tests for trine_eval.sandbox.regression_gate — evaluate_regression_gate.

All subprocess.run calls are mocked — no real commands are executed.
Test outcome strings use pytest -v format: "test_name PASSED" / "test_name FAILED".
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from trine_eval.sandbox.regression_gate import RegressionGateResult, evaluate_regression_gate


def _make_completed_process(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class TestFailToPassPositive:
    """C10: FAIL_TO_PASS positive case — test_foo was failing, now passes -> verdict="pass"."""

    def test_fail_to_pass_positive(self) -> None:
        # (a) pre-patch: test_foo FAILED, test_bar PASSED
        pre_patch_output = "test_foo FAILED\ntest_bar PASSED\n"
        pre_patch_result = _make_completed_process(returncode=1, stdout=pre_patch_output)

        # patch_command (git apply) result
        patch_apply_result = _make_completed_process(returncode=0)

        # (b) post-patch: test_foo PASSED, test_bar PASSED
        post_patch_output = "test_foo PASSED\ntest_bar PASSED\n"
        post_patch_result = _make_completed_process(returncode=0, stdout=post_patch_output)

        with patch(
            "subprocess.run",
            side_effect=[pre_patch_result, patch_apply_result, post_patch_result],
        ):
            # (c) call evaluate_regression_gate
            result = evaluate_regression_gate(
                repo_dir="/tmp",
                patch_command="git apply patch.diff",
                test_command="pytest",
                fail_to_pass=["test_foo"],
                pass_to_pass=["test_bar"],
            )

        # (d) assertions
        assert result.fail_to_pass_passed == 1
        assert result.fail_to_pass_total == 1
        assert result.pass_to_pass_regressions == []
        assert result.verdict == "pass"


class TestPassToPassRegression:
    """C11: PASS_TO_PASS regression — test_bar was passing, now fails -> verdict="fail"."""

    def test_pass_to_pass_regression(self) -> None:
        # (a) pre-patch: test_bar PASSED
        pre_patch_output = "test_bar PASSED\n"
        pre_patch_result = _make_completed_process(returncode=0, stdout=pre_patch_output)

        # patch_command result
        patch_apply_result = _make_completed_process(returncode=0)

        # (b) post-patch: test_bar FAILED (regression!)
        post_patch_output = "test_bar FAILED\n"
        post_patch_result = _make_completed_process(returncode=1, stdout=post_patch_output)

        with patch(
            "subprocess.run",
            side_effect=[pre_patch_result, patch_apply_result, post_patch_result],
        ):
            # (c) call evaluate_regression_gate
            result = evaluate_regression_gate(
                repo_dir="/tmp",
                patch_command="git apply patch.diff",
                test_command="pytest",
                fail_to_pass=[],
                pass_to_pass=["test_bar"],
            )

        # (d) assertions
        assert result.pass_to_pass_regressions == ["test_bar"]
        # (e) verdict == "fail"
        assert result.verdict == "fail"


class TestTrivialPassBypassRejected:
    """C12: Trivial-pass-bypass catcher.

    A gate that always returns verdict="pass" must FAIL this test.
    The real implementation must return verdict="fail" for both sub-cases:
      - Sub-case 1: PASS_TO_PASS regression (test_stable was PASSED, now FAILED)
      - Sub-case 2: FAIL_TO_PASS still failing (test_new was FAILED, still FAILED post-patch)
    """

    def test_trivial_pass_bypass_rejected(self) -> None:
        # Sub-case 1: PASS_TO_PASS regression
        # pre-patch: test_stable PASSED
        pre_patch_1 = _make_completed_process(returncode=0, stdout="test_stable PASSED\n")
        # patch apply
        patch_apply_1 = _make_completed_process(returncode=0)
        # post-patch: test_stable FAILED (obvious regression)
        post_patch_1 = _make_completed_process(returncode=1, stdout="test_stable FAILED\n")

        with patch(
            "subprocess.run",
            side_effect=[pre_patch_1, patch_apply_1, post_patch_1],
        ):
            result1 = evaluate_regression_gate(
                repo_dir="/tmp",
                patch_command="git apply patch.diff",
                test_command="pytest",
                fail_to_pass=[],
                pass_to_pass=["test_stable"],
            )

        # (c) verdict must be "fail" — a trivial stub returning "pass" fails this
        assert result1.verdict == "fail"
        # (d) test_stable must be in regressions
        assert "test_stable" in result1.pass_to_pass_regressions

        # Sub-case 2: FAIL_TO_PASS test still failing post-patch
        # pre-patch: test_new FAILED
        pre_patch_2 = _make_completed_process(returncode=1, stdout="test_new FAILED\n")
        # patch apply
        patch_apply_2 = _make_completed_process(returncode=0)
        # post-patch: test_new FAILED (not fixed)
        post_patch_2 = _make_completed_process(returncode=1, stdout="test_new FAILED\n")

        with patch(
            "subprocess.run",
            side_effect=[pre_patch_2, patch_apply_2, post_patch_2],
        ):
            result2 = evaluate_regression_gate(
                repo_dir="/tmp",
                patch_command="git apply patch.diff",
                test_command="pytest",
                fail_to_pass=["test_new"],
                pass_to_pass=[],
            )

        # Sub-case 2: verdict must be "fail" (FAIL_TO_PASS test still failing)
        assert result2.verdict == "fail"
