#!/usr/bin/env python3
"""
check-thinking-frontmatter.py

Sprint 11 Criterion 8 verification: confirm that each agent file's YAML
frontmatter declares the expected `effort` value for adaptive thinking,
in the inline form `thinking: { type: adaptive, effort: ... }` (Sprint 8
mandate — see .harness/contracts/sprint-08.md).

Expected effort values:
  agents/planner.md             -> medium
  agents/generator.md           -> medium
  agents/evaluator.md           -> high
  skills/harness-summary/SKILL.md -> max

Exit 0 if every file's frontmatter matches the expected effort. Exit 1 with
a per-file diagnostic otherwise.

Usage:
  python tests/check-thinking-frontmatter.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

EXPECTED: dict[str, str] = {
    "agents/planner.md": "medium",
    "agents/generator.md": "medium",
    "agents/evaluator.md": "high",
    "skills/harness-summary/SKILL.md": "max",
}

# Match the inline-mapping form: `thinking: { type: adaptive, effort: <value> }`
INLINE_THINKING_RE = re.compile(
    r"^thinking:\s*\{\s*type:\s*adaptive\s*,\s*effort:\s*([A-Za-z]+)\s*\}\s*$",
    re.MULTILINE,
)
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def extract_effort(file_path: Path) -> str | None:
    text = file_path.read_text(encoding="utf-8")
    fm_match = FRONTMATTER_RE.match(text)
    if fm_match is None:
        return None
    frontmatter = fm_match.group(1)
    inline_match = INLINE_THINKING_RE.search(frontmatter)
    if inline_match is None:
        return None
    return inline_match.group(1).strip()


def main() -> int:
    failures: list[str] = []
    for rel_path, expected_effort in EXPECTED.items():
        full = Path(rel_path)
        if not full.exists():
            failures.append(f"MISSING FILE: {rel_path}")
            continue
        actual = extract_effort(full)
        if actual is None:
            failures.append(
                f"NO INLINE THINKING DECLARATION: {rel_path} — expected "
                f"`thinking: {{ type: adaptive, effort: {expected_effort} }}` in YAML frontmatter"
            )
        elif actual != expected_effort:
            failures.append(
                f"MISMATCH: {rel_path} declares effort={actual!r}, expected {expected_effort!r}"
            )

    if failures:
        for line in failures:
            print(line, file=sys.stderr)
        return 1

    print("PASS: all four files declare the expected effort in inline thinking frontmatter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
