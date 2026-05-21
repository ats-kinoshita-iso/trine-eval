# Sprint 05 Contract: Docker sandbox + cheap pre-filter + regression-safety gate

## What I Will Build

Sprint 5 ships the `src/trine_eval/sandbox/` package, which delivers three cooperating capabilities: (1) a per-sample Docker container abstraction (`sandbox/docker.py`) that wraps `subprocess.run([...docker run...])` with `--network=none` default-deny, `--rm` guaranteed teardown, CPU/memory limits, bind-mount, hard timeout, and a `SandboxResult` return type; (2) a four-stage pre-filter pipeline (`sandbox/prefilter.py`) running `ruff → mypy → AST-diff → pytest` that short-circuits on the first failing stage and returns a structured `PrefilterResult`; and (3) a FAIL_TO_PASS / PASS_TO_PASS regression gate (`sandbox/regression_gate.py`) that captures pre-patch test outcomes, applies a candidate patch, re-runs tests, and auto-fails any PASS_TO_PASS → FAIL transition. All tests mock `subprocess.run` — no real Docker is required in the eval environment.

## Success Criteria

Each criterion must be independently testable. Weights sum to 100%.

### Deterministic (code-verifiable)

1. **`run_in_sandbox` default `network` parameter is `"none"` and constructed argv contains `--network=none`**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_docker.py -k test_default_network_is_none -v --tb=short 2>&1 | tee /tmp/s05c1.txt && grep -q "PASSED" /tmp/s05c1.txt && echo PASS'
   ```
   `tests/sandbox/test_docker.py` must contain `test_default_network_is_none`. The test must: (a) patch `subprocess.run` via `unittest.mock.patch("subprocess.run", ...)`, (b) call `trine_eval.sandbox.docker.run_in_sandbox(cmd=["echo", "hello"], repo_dir="/tmp")` without specifying `network`, (c) capture the argv passed to the mocked `subprocess.run`, and (d) assert both that `"--network=none"` appears in the argv AND that the `network` parameter of `run_in_sandbox` has a default of `"none"` (inspectable via `inspect.signature` or by asserting the default keyword argument). PASS when exit code is 0 and output contains `PASSED`. [weight: 7%]

2. **Every `run_in_sandbox` invocation includes `--rm` in the docker run argv**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_docker.py -k test_rm_always_present -v --tb=short 2>&1 | tee /tmp/s05c2.txt && grep -q "PASSED" /tmp/s05c2.txt && echo PASS'
   ```
   `tests/sandbox/test_docker.py` must contain `test_rm_always_present`. The test must: (a) patch `subprocess.run`, (b) call `run_in_sandbox` with various combinations of arguments (at minimum: default call, call with `network="bridge"`, call with custom `image`), and (c) for each call, assert that `"--rm"` appears in the argv list passed to the mocked `subprocess.run`. PASS when exit code is 0 and output contains `PASSED`. [weight: 6%]

3. **`run_in_sandbox` enforces hard timeout — returns `SandboxResult(timed_out=True)` when subprocess timeout elapses**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_docker.py -k test_timeout_enforcement -v --tb=short 2>&1 | tee /tmp/s05c3.txt && grep -q "PASSED" /tmp/s05c3.txt && echo PASS'
   ```
   `tests/sandbox/test_docker.py` must contain `test_timeout_enforcement`. The test must: (a) patch `subprocess.run` to raise `subprocess.TimeoutExpired(cmd=["docker"], timeout=1)`, (b) call `run_in_sandbox(cmd=["sleep", "100"], repo_dir="/tmp", timeout_s=1)`, (c) assert the returned `SandboxResult.timed_out is True`, and (d) assert the returned `SandboxResult.exit_code` is a non-zero integer (e.g., -1 or 124). The function must NOT re-raise `TimeoutExpired` — it must catch it and return a `SandboxResult` with `timed_out=True`. PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

4. **Zero containers remain after `run_in_sandbox` call — `docker ps` verification asserts empty**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_docker.py -k test_no_leftover_containers -v --tb=short 2>&1 | tee /tmp/s05c4.txt && grep -q "PASSED" /tmp/s05c4.txt && echo PASS'
   ```
   `tests/sandbox/test_docker.py` must contain `test_no_leftover_containers`. The test must: (a) patch `subprocess.run` for BOTH the `docker run` call AND the `docker ps` verification call, (b) configure the `docker ps` mock to return a `CompletedProcess` with `stdout=""` (empty — no containers), (c) call `run_in_sandbox`, (d) assert that `subprocess.run` was called at least twice (once for `docker run`, once for `docker ps`), and (e) assert that the second call's argv contains `"ps"` and a filter argument (e.g., `"--filter"` with a label like `"label=trine-eval-sandbox=true"` or similar). The test verifies the abstraction EXPLICITLY checks for leftover containers after every call, not just relying on `--rm`. PASS when exit code is 0 and output contains `PASSED`. [weight: 7%]

5. **CPU and memory limits are passed as `--cpus` and `--memory` flags in the docker run argv**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_docker.py -k test_resource_limits -v --tb=short 2>&1 | tee /tmp/s05c5.txt && grep -q "PASSED" /tmp/s05c5.txt && echo PASS'
   ```
   `tests/sandbox/test_docker.py` must contain `test_resource_limits`. The test must: (a) patch `subprocess.run`, (b) call `run_in_sandbox(cmd=["echo"], repo_dir="/tmp", cpu_limit="2", memory_limit="512m")`, (c) assert the argv contains `"--cpus"` followed by `"2"` (or `"--cpus=2"`), and (d) assert the argv contains `"--memory"` followed by `"512m"` (or `"--memory=512m"`). A second sub-case must call with the defaults and assert `"--cpus"` is `"1"` and `"--memory"` is `"1g"` (the default limits specified in the contract). PASS when exit code is 0 and output contains `PASSED`. [weight: 6%]

6. **`SandboxResult` has correct shape: `exit_code`, `stdout`, `stderr`, `duration_s`, `timed_out` fields**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_docker.py -k test_sandbox_result_shape -v --tb=short 2>&1 | tee /tmp/s05c6.txt && grep -q "PASSED" /tmp/s05c6.txt && echo PASS'
   ```
   `tests/sandbox/test_docker.py` must contain `test_sandbox_result_shape`. The test must: (a) patch `subprocess.run` to return a `subprocess.CompletedProcess(args=[], returncode=0, stdout="hello\n", stderr="")`, (b) call `run_in_sandbox`, (c) assert `result.exit_code == 0`, (d) assert `result.stdout == "hello\n"`, (e) assert `result.stderr == ""`, (f) assert `isinstance(result.duration_s, float)` and `result.duration_s >= 0.0`, and (g) assert `result.timed_out is False`. PASS when exit code is 0 and output contains `PASSED`. [weight: 4%]

7. **Four-stage pre-filter pipeline runs all four stages in order on success and returns `PrefilterResult(passed=True)`**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_prefilter.py -k test_all_stages_run_on_success -v --tb=short 2>&1 | tee /tmp/s05c7.txt && grep -q "PASSED" /tmp/s05c7.txt && echo PASS'
   ```
   `tests/sandbox/test_prefilter.py` must contain `test_all_stages_run_on_success`. The test must: (a) patch `run_in_sandbox` (or `subprocess.run`) so all four stages — `ruff`, `mypy`, `ast-diff`, and `pytest` — return exit code 0 / success, (b) call `trine_eval.sandbox.prefilter.run_prefilter(repo_dir="/tmp", patch_files=["foo.py"])`, (c) assert the returned `PrefilterResult.passed is True`, and (d) assert the invocation log (call_args_list or similar) shows all four stages were invoked in the order: ruff first, mypy second, ast-diff third, pytest fourth. The test must capture call order, not just call count. PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

8. **Pre-filter pipeline short-circuits on first failure — stages after the failing stage are NOT invoked**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_prefilter.py -k test_short_circuit_on_failure -v --tb=short 2>&1 | tee /tmp/s05c8.txt && grep -q "PASSED" /tmp/s05c8.txt && echo PASS'
   ```
   `tests/sandbox/test_prefilter.py` must contain `test_short_circuit_on_failure`. The test must cover at least two failure cases: (a) **ruff fails**: mock ruff to exit non-zero; assert mypy, ast-diff, and pytest are NOT invoked; assert `PrefilterResult.stage == "ruff"` and `PrefilterResult.passed is False`; (b) **mypy fails**: mock ruff to succeed and mypy to fail; assert ast-diff and pytest are NOT invoked; assert `PrefilterResult.stage == "mypy"` and `PrefilterResult.passed is False`. In both cases the mock call count for the skipped stages must be zero. PASS when exit code is 0 and output contains `PASSED`. [weight: 9%]

9. **`PrefilterResult` has the correct shape: `stage`, `passed`, `reason`, `stdout`, `stderr` fields**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/sandbox/test_prefilter.py -k test_prefilter_result_shape -v --tb=short 2>&1 | tee /tmp/s05c9.txt && grep -q "PASSED" /tmp/s05c9.txt && echo PASS'
   ```
   `tests/sandbox/test_prefilter.py` must contain `test_prefilter_result_shape`. The test must: (a) mock ruff to fail with `stdout="E302 ..."` and `stderr=""`, (b) call `run_prefilter`, (c) assert `result.stage == "ruff"`, (d) assert `result.passed is False`, (e) assert `result.reason` is a non-`None` string (the reason for failure), (f) assert `result.stdout == "E302 ..."`, and (g) assert `result.stderr == ""`. A second sub-case must produce a `PrefilterResult` for a fully-passing run and assert `result.stage == "tests"`, `result.passed is True`, and `result.reason is None`. PASS when exit code is 0 and output contains `PASSED`. [weight: 7%]

10. **Regression gate FAIL_TO_PASS positive case — test that was failing now passes → `verdict="pass"`**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/sandbox/test_regression_gate.py -k test_fail_to_pass_positive -v --tb=short 2>&1 | tee /tmp/s05c10.txt && grep -q "PASSED" /tmp/s05c10.txt && echo PASS'
    ```
    `tests/sandbox/test_regression_gate.py` must contain `test_fail_to_pass_positive`. The test must: (a) mock the test-run command so pre-patch returns `test_foo FAILED` and `test_bar PASSED`; (b) mock the post-patch test-run to return `test_foo PASSED` and `test_bar PASSED`; (c) call `trine_eval.sandbox.regression_gate.evaluate_regression_gate(repo_dir="/tmp", patch_command="git apply patch.diff", test_command="pytest", fail_to_pass=["test_foo"], pass_to_pass=["test_bar"])`; (d) assert `result.fail_to_pass_passed == 1`, `result.fail_to_pass_total == 1`, `result.pass_to_pass_regressions == []`, and `result.verdict == "pass"`. PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

11. **Regression gate PASS_TO_PASS regression — test that was passing now fails → `verdict="fail"` with regressing test in `pass_to_pass_regressions`**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/sandbox/test_regression_gate.py -k test_pass_to_pass_regression -v --tb=short 2>&1 | tee /tmp/s05c11.txt && grep -q "PASSED" /tmp/s05c11.txt && echo PASS'
    ```
    `tests/sandbox/test_regression_gate.py` must contain `test_pass_to_pass_regression`. The test must: (a) mock pre-patch test run to show `test_bar PASSED` (a currently-passing test); (b) mock post-patch test run to show `test_bar FAILED` (regression!); (c) call `evaluate_regression_gate(..., pass_to_pass=["test_bar"])`; (d) assert `result.pass_to_pass_regressions == ["test_bar"]` (the specific test name is in the regressions list), (e) assert `result.verdict == "fail"`. PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

12. **Regression gate trivial-pass-bypass catcher — a gate that ignores inputs and always returns `verdict="pass"` must FAIL this test**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/sandbox/test_regression_gate.py -k test_trivial_pass_bypass_rejected -v --tb=short 2>&1 | tee /tmp/s05c12.txt && grep -q "PASSED" /tmp/s05c12.txt && echo PASS'
    ```
    `tests/sandbox/test_regression_gate.py` must contain `test_trivial_pass_bypass_rejected`. The test must: (a) construct an obvious PASS_TO_PASS regression scenario (pre-patch: `test_stable PASSED`; post-patch: `test_stable FAILED`); (b) call `evaluate_regression_gate(..., pass_to_pass=["test_stable"])`; (c) assert `result.verdict == "fail"` — if the implementation returns `"pass"` for this scenario, the assertion fails, rejecting the trivial bypass; (d) assert `"test_stable"` is in `result.pass_to_pass_regressions`. A second sub-case must construct a scenario where a FAIL_TO_PASS test still fails post-patch (pre: `test_new FAILED`; post: `test_new FAILED`); assert `result.verdict == "fail"` (any remaining FAIL_TO_PASS failure is also a verdict-fail). The test is PASS when the real implementation correctly returns `verdict="fail"` for both scenarios; any trivial stub that always returns `"pass"` will make these assertions fail and therefore the test FAIL. PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

13. **Full sandbox test suite exits 0 with no failures**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/sandbox/ -v --tb=short 2>&1 | tee /tmp/s05c13.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s05c13.txt && ! grep -qE "FAILED|ERROR" /tmp/s05c13.txt && [ "$EC" = "0" ] && echo PASS || exit 1'
    ```
    All new test files under `tests/sandbox/` from this sprint pass together with no failures or errors. PASS when pytest exit code is 0, output contains `passed`, and no `FAILED` or `ERROR` lines appear. [weight: 2%]

14. **No regressions in prior runner, model, core, and judge tests**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/runner/ tests/models/ tests/core/ tests/judge/ -v --tb=short 2>&1 | tee /tmp/s05c14.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s05c14.txt && ! grep -qE "FAILED|ERROR" /tmp/s05c14.txt && ( [ "$EC" = "0" ] || [ "$EC" = "100" ] ) && echo PASS || exit 1'
    ```
    All prior Sprint 1, 2, 3, and 4 tests under `tests/runner/`, `tests/models/`, `tests/core/`, and `tests/judge/` continue to pass. PASS when pytest exits 0 (or 100 — Sprint 2's pytest plugin deliberately overrides session exit to 100 when a `@pytest.mark.trine_eval` test records a score below threshold; the regression check accepts 100 because no genuine test failure prints `FAILED` or `ERROR`), output contains `passed`, and no `FAILED` or `ERROR` lines appear. [weight: 2%]

### LLM-as-judge (requires reading comprehension)

15. **`run_in_sandbox` API shape and security defaults are correct (A7 behavioral)**: read `src/trine_eval/sandbox/docker.py` (or wherever `run_in_sandbox` is implemented). The implementation must: (a) expose a function named `run_in_sandbox` with parameters `cmd: list[str]`, `repo_dir: str | pathlib.Path`, `image: str = "python:3.12-slim"`, `network: str = "none"`, `cpu_limit: str = "1"`, `memory_limit: str = "1g"`, `timeout_s: int | float = 60`, and return type `SandboxResult`; (b) construct a `docker run` command that always includes `--rm`, `--network=<network>`, `--cpus=<cpu_limit>`, `--memory=<memory_limit>`, and a bind-mount of `repo_dir` into the container; (c) pass `timeout=timeout_s` (or equivalent) to `subprocess.run` so the hard timeout is enforced; (d) catch `subprocess.TimeoutExpired` and return `SandboxResult(timed_out=True, exit_code=-1, stdout="", stderr="", duration_s=timeout_s)` or equivalent — must NOT re-raise; (e) after the `docker run` call, invoke `subprocess.run(["docker", "ps", "-a", "--filter", "label=trine-eval-sandbox=true", ...])` (or equivalent) to verify zero containers remain — the label scheme or equivalent must be consistent between the `docker run` invocation (where the label is SET on the container) and the `docker ps` verification (where the label FILTERS the results); (f) return `SandboxResult` with the five required fields populated from actual subprocess output. A `run_in_sandbox` that defaults `network` to anything other than `"none"` is FAIL. A `run_in_sandbox` that omits `--rm` is FAIL. A `run_in_sandbox` that omits the post-call container-count verification is FAIL. [weight: 5%]

16. **Regression gate design is correct — PASS_TO_PASS auto-fail and `RegressionGateResult` shape (D4 behavioral)**: read `src/trine_eval/sandbox/regression_gate.py`. The implementation must: (a) expose a function named `evaluate_regression_gate` with parameters `repo_dir: str | pathlib.Path`, `patch_command: str`, `test_command: str`, `fail_to_pass: list[str]`, `pass_to_pass: list[str]` and return type `RegressionGateResult`; (b) run the test suite BEFORE applying the patch to capture baseline pass/fail state for the listed tests; (c) apply the patch (via `subprocess.run([...patch_command...])` or equivalent); (d) run the test suite AFTER applying the patch; (e) compare pre/post results: any test in `pass_to_pass` that transitions from PASS→FAIL is added to `result.pass_to_pass_regressions`; (f) set `result.verdict = "fail"` if `len(result.pass_to_pass_regressions) > 0` OR if any `fail_to_pass` test still fails post-patch; set `result.verdict = "pass"` otherwise; (g) `RegressionGateResult` must have fields `fail_to_pass_passed: int`, `fail_to_pass_total: int`, `pass_to_pass_regressions: list[str]`, and `verdict: Literal["pass", "fail"]`. An implementation that returns `verdict="pass"` unconditionally without examining test outcomes is FAIL. An implementation that omits the pre-patch baseline run is FAIL. [weight: 5%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **Historical Phase 1 and Phase 2 prior-sprint contracts and evals are unmodified**: no file matching Phase-1 or prior Phase-2 sprint paths is modified by any commit whose message contains `(sprint-05)` (the conventional commit prefix for this sprint). Verification iterates over all `(sprint-05)`-prefixed commits reachable from HEAD but not from the sprint-04 Phase-2 completion commit, and checks each commit's individual diff (`c^..c`) against the prior-sprint glob. The Phase-2 patterns use `sprint-0[1234]*.md` (covering sprint-01, sprint-02, sprint-03, sprint-04 — all finalized) to exclude the current sprint-05 contract from the immutability check. When no sprint-05 commits exist yet, the loop runs zero iterations and exits PASS. Verify:
   ```
   bash -c 'failed=0; S04BASE=$(git log --format=%H --grep="complete sprint 04 (Phase 2)" -1 2>/dev/null); SPRINT_COMMITS=$(git log --format=%H --grep="(sprint-05)" HEAD ${S04BASE:+^$S04BASE} 2>/dev/null); for c in $SPRINT_COMMITS; do diff_out=$(git diff "${c}^".."${c}" -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" ".harness/contracts/phase-02/sprint-0[1234]*.md" ".harness/contracts/phase-02/sprint-1*.md" ".harness/evals/phase-02/sprint-0[1234]*.md" ".harness/evals/phase-02/sprint-1*.md" 2>/dev/null); if [ -n "$diff_out" ]; then echo "FAIL: $c modified prior-sprint files"; echo "$diff_out" | head -20; failed=1; fi; done; [ "$failed" = "0" ] && echo PASS || exit 1'
   ```
   PASS when exit code is 0. This covers both Phase-1 root-level files and Phase-2 subdirectory files under `.harness/contracts/phase-02/` and `.harness/evals/phase-02/`. The sprint-commit scope (using `^$S04BASE`) prevents historical Phase-1 `(sprint-05)` commits from being evaluated — only commits introduced during this Phase-2 sprint-05 work window are checked.

2. **No forbidden packages imported or declared**: the strings `langgraph`, `ragas`, `pgvector`, and `fastapi` must not appear in `pyproject.toml`, `src/trine_eval/**/*.py`, or `tests/**/*.py`. Verify via:
   ```
   bash -c 'git grep -rn --count -E "langgraph|ragas|pgvector|fastapi" pyproject.toml src/ tests/ 2>/dev/null | grep -v "^Binary" | grep -v ":0$" && echo FAIL && exit 1 || echo PASS'
   ```
   PASS when the command exits 0 and prints `PASS`.

3. **No real `docker run` invocations in tests — every `subprocess.run` call in `tests/sandbox/` is mocked**: the Evaluator reads `tests/sandbox/*.py` and confirms that every function or method call that would invoke `subprocess.run([... "docker" ...])` is enclosed in a `unittest.mock.patch("subprocess.run", ...)` context manager or `mocker.patch(...)`. A bare `subprocess.run` call at module level or in a test body without a surrounding patch targeting `subprocess.run` (or a wrapper function) is FAIL. No actual `docker run` command is executed during `uv run pytest tests/sandbox/`. PASS when no unguarded `subprocess.run(["docker"...])` invocation is found in any source file under `tests/sandbox/`.

## Reference Solutions

**Criteria C1–C6, C15 — `run_in_sandbox` API shape and security defaults (LLM-judge anchor for C15):**

A correct `src/trine_eval/sandbox/docker.py` implementation:

```python
# src/trine_eval/sandbox/docker.py
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path


_SANDBOX_LABEL = "trine-eval-sandbox=true"


@dataclass
class SandboxResult:
    exit_code: int
    stdout: str
    stderr: str
    duration_s: float
    timed_out: bool


def run_in_sandbox(
    cmd: list[str],
    *,
    repo_dir: str | Path,
    image: str = "python:3.12-slim",
    network: str = "none",
    cpu_limit: str = "1",
    memory_limit: str = "1g",
    timeout_s: int | float = 60,
) -> SandboxResult:
    """
    Run cmd inside a fresh Docker container per call.

    Security defaults:
      - --network=none  (no outbound network)
      - --rm            (self-destruct on exit)
      - --cpus / --memory resource caps
    All subprocess.run calls are mockable for testing (no real docker needed).
    """
    mount_target = "/repo"
    docker_argv = [
        "docker", "run", "--rm",
        "--label", _SANDBOX_LABEL,
        "--network", network,
        "--cpus", cpu_limit,
        "--memory", memory_limit,
        "-v", f"{Path(repo_dir).resolve()}:{mount_target}",
        "-w", mount_target,
        image,
        *cmd,
    ]
    start = time.monotonic()
    try:
        proc = subprocess.run(
            docker_argv,
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        duration = time.monotonic() - start
        # Explicit post-call verification: assert no containers linger
        subprocess.run(
            ["docker", "ps", "-a", "--filter", f"label={_SANDBOX_LABEL}", "--format", "{{.ID}}"],
            capture_output=True,
            text=True,
        )
        return SandboxResult(
            exit_code=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
            duration_s=duration,
            timed_out=False,
        )
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return SandboxResult(
            exit_code=-1,
            stdout="",
            stderr="",
            duration_s=duration,
            timed_out=True,
        )
```

PASS: `network` defaults to `"none"`; `--rm` always in argv; timeout caught and returns `timed_out=True`; post-call `docker ps` verification invoked; `SandboxResult` has all five fields. FAIL: `network` defaults to `"bridge"` or omits `--network` flag; `--rm` absent; `TimeoutExpired` re-raised; no post-call container check.

**Criteria C10–C12, C16 — `evaluate_regression_gate` shape (LLM-judge anchor for C16):**

A correct `src/trine_eval/sandbox/regression_gate.py` signature and verdict logic:

```python
# src/trine_eval/sandbox/regression_gate.py
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
    """
    Run pre-patch baseline, apply patch, run post-patch tests.
    Any PASS_TO_PASS → FAIL transition is an automatic verdict=fail.
    Any remaining FAIL_TO_PASS failure is also verdict=fail.
    """
    repo = Path(repo_dir)

    # Pre-patch baseline
    pre = subprocess.run(test_command.split(), capture_output=True, text=True, cwd=repo)
    pre_outcomes = _parse_test_outcomes(pre.stdout + pre.stderr)

    # Apply patch
    subprocess.run(patch_command.split(), capture_output=True, text=True, cwd=repo, check=True)

    # Post-patch outcomes
    post = subprocess.run(test_command.split(), capture_output=True, text=True, cwd=repo)
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
```

PASS: pre-patch baseline run exists; patch applied; post-patch run compared; PASS_TO_PASS regressions → `verdict="fail"`; FAIL_TO_PASS still failing → `verdict="fail"`; all four `RegressionGateResult` fields present. FAIL: unconditional `verdict="pass"`; no pre-patch run; `pass_to_pass_regressions` always empty.

## Out of Scope

- **Integration of sandbox into the async runner engine**: the sandbox API is shipped in Sprint 5; wiring it into `runner/engine.py` so real eval runs use per-sample containers is Sprint 6 scope.
- **SWE-bench Verified adapter** (`src/trine_eval/benchmarks/`): Sprint 6.
- **Real Docker invocations in tests**: all tests mock `subprocess.run`. No Docker daemon required in the eval environment.
- **`uv run ruff check` and `uv run mypy --strict src` clean on sandbox package**: strict type enforcement on new modules is a best-effort goal; syntax errors are a failure but minor type annotation gaps are not gated in this sprint.
- **AST-diff implementation details**: the AST-diff stage must use `ast.dump()` on pre/post-patch versions of changed Python files and confirm the dump differs (semantically meaningful patch, not whitespace-only). The exact algorithm for determining "which files changed" (git diff, explicit list, etc.) is an implementation decision.
- **OTel spans on sandbox calls**: sandbox instrumentation is out of scope for Sprint 5.
- **`uv run trine-eval run` CLI integration**: CLI is not extended in Sprint 5.
- **LangGraph, RAGAS, pgvector, FastAPI**: deferred to v0.2+.

## Technical Notes

- **New package structure.** Sprint 5 creates `src/trine_eval/sandbox/__init__.py`, `src/trine_eval/sandbox/docker.py`, `src/trine_eval/sandbox/prefilter.py`, and `src/trine_eval/sandbox/regression_gate.py`. New test directory: `tests/sandbox/` with `__init__.py`, `test_docker.py`, `test_prefilter.py`, and `test_regression_gate.py`.

- **Container label scheme.** The `--rm` flag guarantees teardown, but C4 requires an EXPLICIT verification call to `docker ps --filter label=trine-eval-sandbox=true` after each `run_in_sandbox` call. This means the `docker run` invocation must set a label (`--label trine-eval-sandbox=true`) so the follow-up `docker ps` can filter by it. Tests mock BOTH subprocess calls (the `docker run` and the `docker ps`). The label key-value is an implementation detail; whatever scheme the implementer chooses must be consistent between the `docker run` label-set and the `docker ps` label-filter.

- **`run_in_sandbox` bind-mount.** The `repo_dir` is bind-mounted read-write into the container at a fixed mount point (e.g., `/repo`). The working directory inside the container is set to the mount point. This is required for pre-filter stages (ruff, mypy, pytest) that need filesystem access to the repo being evaluated.

- **Pre-filter stage dispatch.** The `run_prefilter` function in `sandbox/prefilter.py` invokes each stage as a command via `run_in_sandbox` (preferred — runs in the sandbox) or via a direct `subprocess.run` call. Tests must mock whichever dispatch mechanism is used. The stage order is fixed: ruff → mypy → ast-diff → pytest. The `ast-diff` stage is special — it uses Python's `ast` module in-process (no subprocess needed) to compare ASTs of changed files; it does not require a container call. Tests for the ast-diff stage mock the file-read or `ast.parse` call rather than `subprocess.run`.

- **`PrefilterResult.stage` for a passing pipeline.** When all four stages pass, the `stage` field indicates which stage was the last to run (i.e., `"tests"` or `"pytest"`). This is consistent with the contract's C9 requirement: `result.stage == "tests"` for a fully-passing pipeline.

- **Regression gate test-outcome parsing.** The reference solution's `_parse_test_outcomes` parses `pytest -v` style output. Tests mock `subprocess.run` to return `CompletedProcess(stdout="test_foo PASSED\ntest_bar FAILED\n", ...)`. The exact parser logic is an implementation detail; the contract only requires that the gate correctly detects PASS_TO_PASS regressions and FAIL_TO_PASS failures.

- **`tee` exit-code masking.** C13 and C14 use `| tee` with `${PIPESTATUS[0]}` capture (the Sprint 3/4 three-guard pattern). C1–C12 scope to individual test functions with `grep -q "PASSED"` — no `${PIPESTATUS[0]}` needed because the `&&` chain only reaches `grep` if pytest exits 0.

- **pytest plugin exit-100 disjunction.** C14 covers `tests/runner/`, which includes `test_plugin_exit.py` — the Sprint 2 test that deliberately triggers `exit 100`. C14 uses `( [ "$EC" = "0" ] || [ "$EC" = "100" ] )` for this reason. C13 covers only `tests/sandbox/`, which does not include the plugin exit test; C13 uses `[ "$EC" = "0" ]` only.

- **Behavioral weight compliance.** All 16 success criteria are behavioral by rubric_dimension (they test runtime correctness via pytest execution or LLM reading-comprehension of source). Behavioral weight = 100%, exceeding the ≥60% threshold from the project behavioral coverage rule.

- **Backward compatibility with Sprint 2 runner.** The sandbox package is additive — it does not modify `src/trine_eval/runner/engine.py` or any other existing module. The sandbox is a NEW capability that the runner may consume in Sprint 6. No existing `tests/runner/` test is affected.

---

**Weight verification:** C1(7) + C2(6) + C3(8) + C4(7) + C5(6) + C6(4) + C7(8) + C8(9) + C9(7) + C10(8) + C11(8) + C12(8) + C13(2) + C14(2) + C15(5) + C16(5) = **100%**. Confirmed.

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/phase-02/sprint-05.tasks.json` is emitted with one JSON entry per criterion. Task IDs: `s05-c1` through `s05-c16` for success criteria, `s05-sn1`, `s05-sn2`, `s05-sn3` for Should-NOT gates. Total entries: 16 success + 3 gate = 19.

## Evaluator Review

**Status: APPROVED**

**Round: 1**

### Strengths
- Weight sum confirmed 100% (C1:7+C2:6+C3:8+C4:7+C5:6+C6:4+C7:8+C8:9+C9:7+C10:8+C11:8+C12:8+C13:2+C14:2+C15:5+C16:5). Behavioral coverage 100% (all 16 success criteria tagged `behavioral`), far exceeding the ≥60% threshold.
- SN1 verification command runs zero iterations on the current branch (no `(sprint-05)` commits yet) and exits PASS. `S04BASE` anchor resolves to `dde987c` ("complete sprint 04 (Phase 2) evaluation" — the exact commit). Phase-2 immutability glob `sprint-0[1234]*.md` correctly covers sprints 01–04 only, excluding the current sprint-05 contract.
- C12 trivial-pass-bypass catcher is structurally sound: two sub-cases (PASS_TO_PASS regression + FAIL_TO_PASS still failing) both assert `result.verdict == "fail"`. Any stub unconditionally returning `"pass"` fails both assertions, making the pytest test FAIL and the verification command exit non-zero.
- C8 short-circuit semantics are unambiguous: mock call count for skipped stages must be zero (not merely "stage result is FAIL"). Covers at least two failure positions (ruff fails, mypy fails), proving X+1..4 are skipped regardless of which stage fails.
- All 14 deterministic verification commands pass `bash -n` syntax check. No encoding or quoting errors.
- C13 and C14 correctly use `EC=${PIPESTATUS[0]}` to capture exit code before `tee` masks it. C14 uses `( [ "$EC" = "0" ] || [ "$EC" = "100" ] )` disjunction for Sprint 2's plugin exit-100. C13 uses `[ "$EC" = "0" ]` only (tests/sandbox/ does not include the plugin exit test).
- SN3 scope ("reads `tests/sandbox/*.py`") is unambiguous: any `subprocess.run` call not enclosed in a mock patch is FAIL. Two independent evaluators will agree.
- tasks.json structure: 16 success + 3 gate = 19 entries, IDs `s05-c1`..`s05-c16` + `s05-sn1`..`s05-sn3`. Gate weights all 0. Grader types correctly assigned (deterministic for C1–C14, SN1, SN2; llm-judge for C15, C16, SN3). LLM-judge criteria C15 and C16 both have reference solutions in the contract.

### Issues
None.

### Missing Criteria
None.

### Notes
- **Advisory — C6 dual-call mock design:** The C6 test patches `subprocess.run` to return `CompletedProcess(returncode=0, stdout="hello\n", stderr="")`, but the reference implementation calls `subprocess.run` twice (once for `docker run`, once for `docker ps`). A naive single-value mock will return the same `CompletedProcess` for both calls. The Generator's test must either use `side_effect=[first_response, second_response]` to differentiate the calls, or rely on the fact that `SandboxResult.stdout` is captured from the first call only. This is a test-design implementation detail, not a contract defect — the criterion is deterministic and verifiable once the test is written correctly.
- **Advisory — C3/C4 timeout path:** The reference implementation does NOT invoke the `docker ps` verification call when `TimeoutExpired` is caught (the except block returns early). C4 tests the non-timeout path, so there is no conflict between C3 and C4 as written. The Generator should be aware that the timeout path in `run_in_sandbox` is exempted from the leftover-container check per the reference design.
