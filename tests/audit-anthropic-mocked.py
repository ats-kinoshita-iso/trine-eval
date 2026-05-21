#!/usr/bin/env python3
"""
audit-anthropic-mocked.py

Deterministic SN3 gate: every `anthropic.Anthropic(...)` call in a Python
test file must be enclosed in either a `with patch("anthropic.Anthropic") ...:`
context manager OR a function decorated with `@patch("anthropic.Anthropic")`.

This mechanizes the "no real Anthropic API calls in tests" gate that saturated
across Phase 2 Sprints 02-04 as an LLM-judge criterion (s02-sn3, s03-sn3,
s04-sn3) but could not be cleanly graduated to the regression suite until a
deterministic verification command existed. Sprint 06 closes the gap by
adding this script and graduating the criterion via `s04-sn3-deterministic`.

Exit codes:
  0 -- every `anthropic.Anthropic(...)` call is inside a patch context
       (or the file/directory makes no such call)
  1 -- one or more unmocked `anthropic.Anthropic(...)` calls were found
  2 -- input file or schema error

Usage:
  python tests/audit-anthropic-mocked.py PATH

PATH may be a single .py file or a directory. Directories are walked
recursively and every .py file is audited.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path


def _is_anthropic_anthropic_call(node: ast.Call) -> bool:
    """True if node is `anthropic.Anthropic(...)`."""
    func = node.func
    return (
        isinstance(func, ast.Attribute)
        and func.attr == "Anthropic"
        and isinstance(func.value, ast.Name)
        and func.value.id == "anthropic"
    )


def _is_patch_anthropic_call(node: ast.expr) -> bool:
    """True if node is `patch("anthropic.Anthropic")` or `mocker.patch("anthropic.Anthropic")`."""
    if not isinstance(node, ast.Call):
        return False
    args = node.args
    if not args or not isinstance(args[0], ast.Constant) or args[0].value != "anthropic.Anthropic":
        return False
    func = node.func
    if isinstance(func, ast.Name) and func.id == "patch":
        return True
    if isinstance(func, ast.Attribute) and func.attr == "patch":
        return True
    return False


def _attach_parents(tree: ast.AST) -> None:
    """Stamp .parent on every node so ancestors are walkable."""
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            child.parent = parent  # type: ignore[attr-defined]


def _enclosing_patches_anthropic(node: ast.AST) -> bool:
    """Walk ancestors: is `node` inside a `with patch(...)` block OR a function with `@patch(...)`?"""
    current: ast.AST = node
    while True:
        parent = getattr(current, "parent", None)
        if parent is None:
            return False
        if isinstance(parent, ast.With):
            for item in parent.items:
                if _is_patch_anthropic_call(item.context_expr):
                    return True
        if isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for dec in parent.decorator_list:
                if _is_patch_anthropic_call(dec):
                    return True
        current = parent


def audit_file(path: Path) -> tuple[int, list[str]]:
    """Return (exit_code, messages). 0 = clean, 1 = unmocked call, 2 = parse error."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return 2, [f"error: cannot read {path}: {exc}"]
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        return 2, [f"error: cannot parse {path}: {exc}"]

    _attach_parents(tree)

    unmocked: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and _is_anthropic_anthropic_call(node):
            if not _enclosing_patches_anthropic(node):
                unmocked.append(
                    f"UNMOCKED: {path}:{node.lineno} `anthropic.Anthropic(...)` call not enclosed "
                    f"in a `with patch(\"anthropic.Anthropic\") ...:` block or "
                    f"@patch(\"anthropic.Anthropic\") decorator"
                )

    if unmocked:
        return 1, unmocked
    return 0, []


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} PATH", file=sys.stderr)
        return 2

    target = Path(sys.argv[1])
    if not target.exists():
        print(f"error: {target} does not exist", file=sys.stderr)
        return 2

    if target.is_file():
        files = [target]
    else:
        files = sorted(target.rglob("*.py"))

    total_exit = 0
    total_unmocked: list[str] = []
    for f in files:
        exit_code, msgs = audit_file(f)
        if exit_code == 2:
            for m in msgs:
                print(m, file=sys.stderr)
            return 2
        if exit_code == 1:
            total_unmocked.extend(msgs)
            total_exit = 1

    if total_exit == 1:
        for m in total_unmocked:
            print(m, file=sys.stderr)
        return 1

    print(f"PASS: all anthropic.Anthropic(...) calls in {target} are inside a patch context")
    return 0


if __name__ == "__main__":
    sys.exit(main())
