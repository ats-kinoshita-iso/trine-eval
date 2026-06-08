#!/usr/bin/env python3
"""Idempotently bump .harness/sprint-state.json's last_updated field.

Args: <path-to-sprint-state.json> <new-iso-timestamp>

The PostToolUse hook fires on every state-changing tool call (Task/Edit/Write).
Without debounce, that thrashes the file dozens of times per sprint and races
with the harness orchestrator's own writes (the Edit/Write stale-file guard
keeps tripping). This helper skips the write entirely when last_updated is
already within DEBOUNCE_SECONDS of now, so repeated tool calls within the
same wall-clock minute become a no-op.

Failures are silent: this is a hook, not a CLI. We never want to break a tool
call because the timestamp bumper hit a race or a malformed JSON state file.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

DEBOUNCE_SECONDS = 60


def parse_iso(ts: str) -> float:
    if not ts:
        return 0.0
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).timestamp()
    except (ValueError, TypeError):
        return 0.0


def main() -> int:
    if len(sys.argv) != 3:
        return 0
    path = Path(sys.argv[1])
    new_ts = sys.argv[2]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    if parse_iso(new_ts) - parse_iso(data.get("last_updated", "")) < DEBOUNCE_SECONDS:
        return 0
    data["last_updated"] = new_ts
    try:
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    except OSError:
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
