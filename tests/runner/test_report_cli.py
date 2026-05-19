"""Behavioural tests for `trine-eval report <log>`.

C6: prints token-efficiency metrics including accuracy_per_dollar
    and success_per_1k_tokens.
"""
from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path

from trine_eval.core.log import EvalLog
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.runner.logformat import save


def _make_fixture_log() -> EvalLog:
    """Build an EvalLog with token metadata so metrics are non-zero."""
    return EvalLog(
        task_name="report-test",
        samples=[
            Sample(id="1", input="hello", target="world"),
            Sample(id="2", input="foo", target="bar"),
        ],
        scores=[
            Score(value=1.0, answer="world", explanation="correct"),
            Score(value=0.0, answer="baz", explanation="wrong"),
        ],
        model="claude-opus-4-7",
        timestamp=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        aggregate={"accuracy": 0.5},
        metadata={
            "total_input_tokens": 100,
            "total_output_tokens": 200,
        },
    )


def test_report_exits_0(tmp_path: Path) -> None:
    """trine-eval report <log> exits with code 0."""
    log_path = tmp_path / "fixture.json"
    save(_make_fixture_log(), log_path, format="json")

    result = subprocess.run(
        ["uv", "run", "trine-eval", "report", str(log_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        f"Expected exit 0, got {result.returncode}.\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )


def test_report_contains_accuracy_per_dollar(tmp_path: Path) -> None:
    """trine-eval report stdout contains accuracy_per_dollar."""
    log_path = tmp_path / "fixture.json"
    save(_make_fixture_log(), log_path, format="json")

    result = subprocess.run(
        ["uv", "run", "trine-eval", "report", str(log_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "accuracy_per_dollar" in result.stdout.lower() or "accuracy-per-dollar" in result.stdout.lower(), (
        f"Expected 'accuracy_per_dollar' in stdout:\n{result.stdout}"
    )


def test_report_contains_success_per_1k_tokens(tmp_path: Path) -> None:
    """trine-eval report stdout contains success_per_1k_tokens."""
    log_path = tmp_path / "fixture.json"
    save(_make_fixture_log(), log_path, format="json")

    result = subprocess.run(
        ["uv", "run", "trine-eval", "report", str(log_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "success_per_1k_tokens" in result.stdout.lower() or "success-per-1k-tokens" in result.stdout.lower(), (
        f"Expected 'success_per_1k_tokens' in stdout:\n{result.stdout}"
    )
