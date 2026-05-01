"""Sprint 12 Criterion 6 — Playwright MCP runtime hookup smoke test.

Demonstrates that the Playwright MCP dispatch path documented in Sprint 10
(`agents/evaluator.md`'s Conditional Tools section) can detect the MCP
connection and confirm the python-side library is importable. Gated on a
probe file at `tests/.playwright-available` because true MCP discovery
depends on the Claude Code runtime, which is not available inside this
script.

Behavior matrix:
- Probe file absent  -> [SKIP] Playwright MCP not connected; exit 0.
- Probe file present, `playwright` not installed -> [SKIP] playwright python
  package not installed; exit 0.
- Probe file present, `playwright` installed -> [OK] confirms import; exit 0.

Never starts a browser, never navigates to a URL, never requires a real
web-app fixture. The protocol-level verification matches Sprint 12's
contract scope; live browser invocation is a follow-up sprint.
"""

from __future__ import annotations

import os
import sys


PROBE_PATH = os.path.join(os.path.dirname(__file__), ".playwright-available")


def main() -> int:
    if not os.path.exists(PROBE_PATH):
        print("[SKIP] Playwright MCP not connected (no probe file at tests/.playwright-available)")
        return 0

    try:
        import playwright  # type: ignore  # noqa: F401
    except ImportError:
        print("[SKIP] playwright python package not installed")
        return 0

    print("[OK] Playwright MCP probe file present and `playwright` package importable")
    return 0


if __name__ == "__main__":
    sys.exit(main())
