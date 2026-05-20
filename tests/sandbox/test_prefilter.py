"""Tests for trine_eval.sandbox.prefilter — run_prefilter and PrefilterResult.

All subprocess.run calls are mocked — no real commands are executed.
The ast-diff stage is in-process and can be exercised with real or stub files.
"""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from trine_eval.sandbox.prefilter import PrefilterResult, run_prefilter


def _make_completed_process(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class TestAllStagesRunOnSuccess:
    """C7: Four-stage pipeline runs all four stages in order on success."""

    def test_all_stages_run_on_success(self) -> None:
        # (a) mock subprocess.run so all stages return exit code 0
        # Stages that use subprocess.run: ruff, mypy, pytest (3 calls)
        # ast-diff is in-process — no subprocess call
        ruff_result = _make_completed_process(returncode=0, stdout="", stderr="")
        mypy_result = _make_completed_process(returncode=0, stdout="", stderr="")
        pytest_result = _make_completed_process(returncode=0, stdout="", stderr="")

        call_order: list[str] = []

        def mock_run_side_effect(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
            # Identify which stage is being called by examining the command
            cmd_str = " ".join(str(c) for c in cmd)
            if "ruff" in cmd_str:
                call_order.append("ruff")
                return ruff_result
            elif "mypy" in cmd_str:
                call_order.append("mypy")
                return mypy_result
            elif "pytest" in cmd_str:
                call_order.append("tests")
                return pytest_result
            # Fallback
            return _make_completed_process(returncode=0)

        with patch("subprocess.run", side_effect=mock_run_side_effect) as mock_run:
            # (b) call run_prefilter — patch_files=["foo.py"] but no such file,
            # ast-diff will succeed trivially for empty/nonexistent list
            result = run_prefilter(repo_dir="/tmp", patch_files=[])

        # (c) assert passed is True
        assert result.passed is True

        # (d) verify invocation order: ruff first, mypy second, pytest fourth
        # ast-diff is in-process (no subprocess call), so we see: ruff, mypy, tests
        assert call_order[0] == "ruff", f"Expected ruff first, got {call_order}"
        assert call_order[1] == "mypy", f"Expected mypy second, got {call_order}"
        assert call_order[2] == "tests", f"Expected tests (pytest) third, got {call_order}"
        # All three subprocess stages ran
        assert len(call_order) == 3

        # Last stage result should be "tests"
        assert result.stage == "tests"


class TestShortCircuitOnFailure:
    """C8: Short-circuit on first failure — skipped stages have zero call count."""

    def test_short_circuit_on_failure(self) -> None:
        # (a) ruff fails: mypy, ast-diff, pytest must NOT be invoked
        ruff_fail = _make_completed_process(returncode=1, stdout="E302 ...", stderr="")

        ruff_calls = 0
        mypy_calls = 0
        pytest_calls = 0

        def mock_run_ruff_fail(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
            nonlocal ruff_calls, mypy_calls, pytest_calls
            cmd_str = " ".join(str(c) for c in cmd)
            if "ruff" in cmd_str:
                ruff_calls += 1
                return ruff_fail
            elif "mypy" in cmd_str:
                mypy_calls += 1
                return _make_completed_process(returncode=0)
            elif "pytest" in cmd_str:
                pytest_calls += 1
                return _make_completed_process(returncode=0)
            return _make_completed_process(returncode=0)

        with patch("subprocess.run", side_effect=mock_run_ruff_fail):
            result_ruff_fail = run_prefilter(repo_dir="/tmp", patch_files=[])

        assert result_ruff_fail.stage == "ruff"
        assert result_ruff_fail.passed is False
        # mypy and pytest must NOT have been called
        assert mypy_calls == 0, f"mypy should not be invoked when ruff fails, got {mypy_calls} calls"
        assert pytest_calls == 0, f"pytest should not be invoked when ruff fails, got {pytest_calls} calls"

        # (b) mypy fails: ruff succeeds, mypy fails, ast-diff and pytest NOT invoked
        ruff_calls2 = 0
        mypy_calls2 = 0
        pytest_calls2 = 0

        def mock_run_mypy_fail(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
            nonlocal ruff_calls2, mypy_calls2, pytest_calls2
            cmd_str = " ".join(str(c) for c in cmd)
            if "ruff" in cmd_str:
                ruff_calls2 += 1
                return _make_completed_process(returncode=0)
            elif "mypy" in cmd_str:
                mypy_calls2 += 1
                return _make_completed_process(returncode=1, stdout="", stderr="Type error found")
            elif "pytest" in cmd_str:
                pytest_calls2 += 1
                return _make_completed_process(returncode=0)
            return _make_completed_process(returncode=0)

        with patch("subprocess.run", side_effect=mock_run_mypy_fail):
            result_mypy_fail = run_prefilter(repo_dir="/tmp", patch_files=[])

        assert result_mypy_fail.stage == "mypy"
        assert result_mypy_fail.passed is False
        # ast-diff is in-process (no subprocess call), but pytest must NOT be invoked
        assert pytest_calls2 == 0, f"pytest should not be invoked when mypy fails, got {pytest_calls2} calls"


class TestPrefilterResultShape:
    """C9: PrefilterResult has stage, passed, reason, stdout, stderr fields."""

    def test_prefilter_result_shape(self) -> None:
        # (a) mock ruff to fail with stdout="E302 ..." and stderr=""
        ruff_fail = _make_completed_process(returncode=1, stdout="E302 ...", stderr="")

        def mock_run_ruff_fail(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
            cmd_str = " ".join(str(c) for c in cmd)
            if "ruff" in cmd_str:
                return ruff_fail
            return _make_completed_process(returncode=0)

        with patch("subprocess.run", side_effect=mock_run_ruff_fail):
            # (b) call run_prefilter
            result = run_prefilter(repo_dir="/tmp", patch_files=[])

        # (c) stage == "ruff"
        assert result.stage == "ruff"

        # (d) passed is False
        assert result.passed is False

        # (e) reason is a non-None string
        assert result.reason is not None
        assert isinstance(result.reason, str)

        # (f) stdout == "E302 ..."
        assert result.stdout == "E302 ..."

        # (g) stderr == ""
        assert result.stderr == ""

        # Second sub-case: fully-passing run
        def mock_run_all_pass(cmd: list[str], **kwargs: object) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
            return _make_completed_process(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=mock_run_all_pass):
            result_pass = run_prefilter(repo_dir="/tmp", patch_files=[])

        assert result_pass.stage == "tests"
        assert result_pass.passed is True
        assert result_pass.reason is None
