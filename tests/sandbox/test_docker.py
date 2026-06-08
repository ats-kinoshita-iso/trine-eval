"""Tests for trine_eval.sandbox.docker — run_in_sandbox and SandboxResult.

All subprocess.run calls are mocked — no real Docker invocation occurs.
"""
from __future__ import annotations

import inspect
import subprocess
from unittest.mock import MagicMock, call, patch

import pytest

from trine_eval.sandbox.docker import SandboxResult, run_in_sandbox


def _make_completed_process(
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess:  # type: ignore[type-arg]
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


class TestDefaultNetworkIsNone:
    """C1: run_in_sandbox default network parameter is 'none'."""

    def test_default_network_is_none(self) -> None:
        # (a) patch subprocess.run
        # Non-timeout path calls subprocess.run twice: docker run + docker ps
        docker_run_result = _make_completed_process(returncode=0, stdout="", stderr="")
        docker_ps_result = _make_completed_process(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=[docker_run_result, docker_ps_result]) as mock_run:
            # (b) call without specifying network
            result = run_in_sandbox(cmd=["echo", "hello"], repo_dir="/tmp")

        # (c) capture argv
        first_call_argv = mock_run.call_args_list[0][0][0]

        # (d) assert --network=none in argv AND default parameter is "none"
        assert "--network" in first_call_argv
        network_idx = first_call_argv.index("--network")
        assert first_call_argv[network_idx + 1] == "none"

        # Verify the default via inspect.signature
        sig = inspect.signature(run_in_sandbox)
        assert sig.parameters["network"].default == "none"


class TestRmAlwaysPresent:
    """C2: Every run_in_sandbox invocation includes --rm."""

    def test_rm_always_present(self) -> None:
        docker_run_result = _make_completed_process(returncode=0)
        docker_ps_result = _make_completed_process(returncode=0)

        # Default call
        with patch("subprocess.run", side_effect=[docker_run_result, docker_ps_result]) as mock_run:
            run_in_sandbox(cmd=["echo"], repo_dir="/tmp")
        argv1 = mock_run.call_args_list[0][0][0]
        assert "--rm" in argv1

        # Call with network="bridge"
        docker_run_result2 = _make_completed_process(returncode=0)
        docker_ps_result2 = _make_completed_process(returncode=0)
        with patch("subprocess.run", side_effect=[docker_run_result2, docker_ps_result2]) as mock_run2:
            run_in_sandbox(cmd=["echo"], repo_dir="/tmp", network="bridge")
        argv2 = mock_run2.call_args_list[0][0][0]
        assert "--rm" in argv2

        # Call with custom image
        docker_run_result3 = _make_completed_process(returncode=0)
        docker_ps_result3 = _make_completed_process(returncode=0)
        with patch("subprocess.run", side_effect=[docker_run_result3, docker_ps_result3]) as mock_run3:
            run_in_sandbox(cmd=["echo"], repo_dir="/tmp", image="ubuntu:22.04")
        argv3 = mock_run3.call_args_list[0][0][0]
        assert "--rm" in argv3


class TestTimeoutEnforcement:
    """C3: run_in_sandbox returns SandboxResult(timed_out=True) when timeout elapses."""

    def test_timeout_enforcement(self) -> None:
        # (a) patch subprocess.run to raise TimeoutExpired
        with patch(
            "subprocess.run",
            side_effect=subprocess.TimeoutExpired(cmd=["docker"], timeout=1),
        ):
            # (b) call with timeout_s=1
            result = run_in_sandbox(cmd=["sleep", "100"], repo_dir="/tmp", timeout_s=1)

        # (c) assert timed_out is True
        assert result.timed_out is True

        # (d) assert exit_code is non-zero
        assert result.exit_code != 0
        assert isinstance(result.exit_code, int)


class TestNoLeftoverContainers:
    """C4: Zero containers remain — docker ps verification asserts empty."""

    def test_no_leftover_containers(self) -> None:
        docker_run_result = _make_completed_process(returncode=0, stdout="", stderr="")
        # (b) configure docker ps mock to return empty stdout (no containers)
        docker_ps_result = _make_completed_process(returncode=0, stdout="", stderr="")

        with patch(
            "subprocess.run",
            side_effect=[docker_run_result, docker_ps_result],
        ) as mock_run:
            # (c) call run_in_sandbox
            run_in_sandbox(cmd=["echo"], repo_dir="/tmp")

        # (d) assert called at least twice
        assert mock_run.call_count >= 2

        # (e) assert second call contains "ps" and "--filter" with label
        second_call_argv = mock_run.call_args_list[1][0][0]
        assert "ps" in second_call_argv
        assert "--filter" in second_call_argv
        # Verify the label filter is present
        filter_idx = second_call_argv.index("--filter")
        filter_value = second_call_argv[filter_idx + 1]
        assert "label=" in filter_value


class TestResourceLimits:
    """C5: CPU and memory limits are passed as --cpus and --memory flags."""

    def test_resource_limits(self) -> None:
        # (a) patch subprocess.run
        # Sub-case 1: explicit cpu_limit and memory_limit
        docker_run_result = _make_completed_process(returncode=0)
        docker_ps_result = _make_completed_process(returncode=0)
        with patch("subprocess.run", side_effect=[docker_run_result, docker_ps_result]) as mock_run:
            # (b) call with explicit limits
            run_in_sandbox(cmd=["echo"], repo_dir="/tmp", cpu_limit="2", memory_limit="512m")

        first_argv = mock_run.call_args_list[0][0][0]

        # (c) assert --cpus "2" in argv
        assert "--cpus" in first_argv
        cpus_idx = first_argv.index("--cpus")
        assert first_argv[cpus_idx + 1] == "2"

        # (d) assert --memory "512m" in argv
        assert "--memory" in first_argv
        mem_idx = first_argv.index("--memory")
        assert first_argv[mem_idx + 1] == "512m"

        # Sub-case 2: default limits
        docker_run_result2 = _make_completed_process(returncode=0)
        docker_ps_result2 = _make_completed_process(returncode=0)
        with patch("subprocess.run", side_effect=[docker_run_result2, docker_ps_result2]) as mock_run2:
            run_in_sandbox(cmd=["echo"], repo_dir="/tmp")

        default_argv = mock_run2.call_args_list[0][0][0]
        assert "--cpus" in default_argv
        cpus_idx2 = default_argv.index("--cpus")
        assert default_argv[cpus_idx2 + 1] == "1"

        assert "--memory" in default_argv
        mem_idx2 = default_argv.index("--memory")
        assert default_argv[mem_idx2 + 1] == "1g"


class TestSandboxResultShape:
    """C6: SandboxResult has correct 5-field shape."""

    def test_sandbox_result_shape(self) -> None:
        # (a) patch subprocess.run to return CompletedProcess
        # Non-timeout path calls subprocess.run twice (docker run + docker ps)
        # Use side_effect to differentiate: first call is docker run, second is docker ps
        docker_run_result = _make_completed_process(returncode=0, stdout="hello\n", stderr="")
        docker_ps_result = _make_completed_process(returncode=0, stdout="", stderr="")

        with patch("subprocess.run", side_effect=[docker_run_result, docker_ps_result]):
            # (b) call run_in_sandbox
            result = run_in_sandbox(cmd=["echo", "hello"], repo_dir="/tmp")

        # (c) exit_code == 0
        assert result.exit_code == 0

        # (d) stdout == "hello\n"
        assert result.stdout == "hello\n"

        # (e) stderr == ""
        assert result.stderr == ""

        # (f) duration_s is a non-negative float
        assert isinstance(result.duration_s, float)
        assert result.duration_s >= 0.0

        # (g) timed_out is False
        assert result.timed_out is False
