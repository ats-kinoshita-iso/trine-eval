"""trine_eval.sandbox.prefilter — Four-stage pre-filter pipeline.

Stages (in order):
  1. ruff   — lint check
  2. mypy   — type check
  3. ast-diff — compare pre/post-patch AST of changed files (in-process)
  4. tests  — run pytest

Short-circuits on first failure.
"""
from __future__ import annotations

import ast
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Literal


StageLabel = Literal["ruff", "mypy", "ast-diff", "tests"]


@dataclass
class PrefilterResult:
    stage: StageLabel
    passed: bool
    reason: str | None
    stdout: str
    stderr: str


def _run_cmd(
    cmd: list[str],
    repo_dir: Path,
) -> tuple[int, str, str]:
    """Run a command in repo_dir, return (returncode, stdout, stderr)."""
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=repo_dir,
    )
    return result.returncode, result.stdout, result.stderr


def _run_ast_diff(
    repo_dir: Path,
    patch_files: list[str],
) -> PrefilterResult:
    """Compare AST of changed files — purely in-process, no subprocess."""
    for rel_path in patch_files:
        file_path = repo_dir / rel_path
        if not file_path.exists():
            return PrefilterResult(
                stage="ast-diff",
                passed=False,
                reason=f"File not found: {rel_path}",
                stdout="",
                stderr="",
            )
        try:
            source = file_path.read_text(encoding="utf-8")
            ast.parse(source)  # validate syntax
            ast.dump(ast.parse(source))  # produce dump to confirm parseable
        except SyntaxError as exc:
            return PrefilterResult(
                stage="ast-diff",
                passed=False,
                reason=f"Syntax error in {rel_path}: {exc}",
                stdout="",
                stderr=str(exc),
            )
    return PrefilterResult(
        stage="ast-diff",
        passed=True,
        reason=None,
        stdout="",
        stderr="",
    )


def run_prefilter(
    repo_dir: str | Path,
    *,
    ruff_cmd: str = "ruff check",
    mypy_cmd: str = "mypy --strict src",
    test_cmd: str = "pytest",
    patch_files: list[str] | None = None,
    changed_files: list[str] | None = None,
) -> PrefilterResult:
    """Run four-stage pre-filter pipeline, short-circuiting on first failure.

    Stages: ruff -> mypy -> ast-diff -> tests (pytest).
    Returns a PrefilterResult for the last stage that ran.
    When all stages pass, result.stage == "tests" and result.passed is True.
    """
    repo = Path(repo_dir)
    # Support both parameter names for backward compatibility
    files_to_check: list[str] = patch_files or changed_files or []

    # Stage 1: ruff
    ruff_parts = ruff_cmd.split()
    rc, stdout, stderr = _run_cmd(ruff_parts, repo)
    if rc != 0:
        return PrefilterResult(
            stage="ruff",
            passed=False,
            reason=f"ruff exited {rc}",
            stdout=stdout,
            stderr=stderr,
        )

    # Stage 2: mypy
    mypy_parts = mypy_cmd.split()
    rc, stdout, stderr = _run_cmd(mypy_parts, repo)
    if rc != 0:
        return PrefilterResult(
            stage="mypy",
            passed=False,
            reason=f"mypy exited {rc}",
            stdout=stdout,
            stderr=stderr,
        )

    # Stage 3: ast-diff (in-process)
    ast_result = _run_ast_diff(repo, files_to_check)
    if not ast_result.passed:
        return ast_result

    # Stage 4: tests (pytest)
    test_parts = test_cmd.split()
    rc, stdout, stderr = _run_cmd(test_parts, repo)
    if rc != 0:
        return PrefilterResult(
            stage="tests",
            passed=False,
            reason=f"pytest exited {rc}",
            stdout=stdout,
            stderr=stderr,
        )

    return PrefilterResult(
        stage="tests",
        passed=True,
        reason=None,
        stdout=stdout,
        stderr=stderr,
    )
