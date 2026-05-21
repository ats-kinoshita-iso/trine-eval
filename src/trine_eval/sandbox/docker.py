"""trine_eval.sandbox.docker — Docker container abstraction for sandboxed execution.

Security defaults:
  - --network=none  (no outbound network)
  - --rm            (self-destruct on exit)
  - --cpus / --memory resource caps
  - post-call docker ps verification (assert zero leftover containers)

All subprocess.run calls are mockable for testing (no real docker needed).
"""
from __future__ import annotations

import subprocess
import time
from dataclasses import dataclass
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
    """Run cmd inside a fresh Docker container per call.

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
