#!/usr/bin/env python3
"""
audit-verified-via-command.py

Adversarial-hygiene audit script for Sprint 10's `verified_via_command` flag.

Given a transcript JSON (raw `.json`) or a markdown eval that contains a fenced
`## Transcript Trailer` JSON block, this script confirms that every criterion
flagged `verified_via_command: true` has a corresponding `tool_calls` entry
tagged with the same `task_id`. If the flag is true but no tool call ran for
that criterion, the verifier did not actually execute — the flag was fabricated.

Exit codes:
  0 — all `verified_via_command: true` entries are backed by a tool call
  1 — one or more inconsistencies (true flag without matching tool call)
  2 — input file or schema error

Usage:
  python tests/audit-verified-via-command.py PATH

`PATH` may be either a `.json` transcript file or a `.md` eval file. Markdown
files have their trailing fenced JSON block extracted before audit.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


TRAILER_HEADING_RE = re.compile(r"^##\s+Transcript Trailer\s*$", re.MULTILINE)
JSON_FENCE_RE = re.compile(r"```json\s*\n(.*?)```", re.DOTALL)


def load_trailer(path: Path) -> dict[str, Any]:
    """Load a transcript trailer from either a .json file or a markdown eval."""
    text = path.read_text(encoding="utf-8")
    if path.suffix == ".json":
        return json.loads(text)

    heading_match = TRAILER_HEADING_RE.search(text)
    if heading_match is None:
        raise ValueError(f"No '## Transcript Trailer' heading in {path}")

    after_heading = text[heading_match.end():]
    fence_match = JSON_FENCE_RE.search(after_heading)
    if fence_match is None:
        raise ValueError(f"No ```json fenced block after '## Transcript Trailer' in {path}")

    return json.loads(fence_match.group(1))


def audit(trailer: dict[str, Any]) -> tuple[int, list[str]]:
    """Return (exit_code, messages). Exit 0 = consistent, 1 = inconsistencies."""
    audit_entries = trailer.get("criteria_audit", [])
    tool_calls = trailer.get("tool_calls", [])

    if not isinstance(audit_entries, list):
        return 2, [f"criteria_audit must be a list, got {type(audit_entries).__name__}"]
    if not isinstance(tool_calls, list):
        return 2, [f"tool_calls must be a list, got {type(tool_calls).__name__}"]

    tool_call_task_ids: set[str] = {
        tc["task_id"] for tc in tool_calls
        if isinstance(tc, dict) and "task_id" in tc
    }

    inconsistencies: list[str] = []
    for entry in audit_entries:
        if not isinstance(entry, dict):
            continue
        task_id = entry.get("task_id")
        verified = entry.get("verified_via_command")
        if verified is True and task_id not in tool_call_task_ids:
            inconsistencies.append(
                f"INCONSISTENT: criteria_audit[{task_id!r}] has verified_via_command=true "
                f"but no tool_calls entry carries task_id={task_id!r}"
            )

    if inconsistencies:
        return 1, inconsistencies
    return 0, []


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PATH", file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2

    try:
        trailer = load_trailer(path)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    exit_code, messages = audit(trailer)
    for msg in messages:
        print(msg, file=sys.stderr if exit_code != 0 else sys.stdout)
    if exit_code == 0:
        print(f"PASS: all verified_via_command=true entries are backed by tool calls in {path}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
