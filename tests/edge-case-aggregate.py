"""Sprint 12 Criterion 7 -- cross-sprint edge-case pass rate aggregator.

Walks the fixture project's contracts and most-recent-round evals, counts
edge-case PASS / FAIL outcomes per sprint, and emits a single aggregate
line on stdout:

    aggregate edge-case pass rate: P/T = X%

where P = total PASS, T = total criteria across every sprint that declared
an `## Edge Case Criteria` section. Sprints that omit the section
contribute neither to numerator nor denominator. When no sprint declared
edge-case criteria, the script prints `aggregate edge-case pass rate: N/A`.

Operates strictly on local files; no network access, no Anthropic API
involvement. Targets the fixture project under tests/fixture-project/ by
default; an alternate root may be passed via the FIXTURE_ROOT env var.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path


def fixture_root() -> Path:
    override = os.environ.get("FIXTURE_ROOT")
    if override:
        return Path(override)
    return Path(__file__).parent / "fixture-project"


def contract_has_edge_case_section(contract_path: Path) -> bool:
    if not contract_path.is_file():
        return False
    text = contract_path.read_text(encoding="utf-8")
    return bool(re.search(r"^## Edge Case Criteria\s*$", text, flags=re.MULTILINE))


def latest_round_eval(evals_dir: Path, sprint_name: str) -> Path | None:
    candidates = sorted(evals_dir.glob(f"{sprint_name}-r*.md"))
    if not candidates:
        return None
    return candidates[-1]


def count_edge_case_outcomes(eval_path: Path) -> tuple[int, int]:
    """Return (passes, total) over the eval's Edge Case Results section."""
    text = eval_path.read_text(encoding="utf-8")
    edge_section_match = re.search(
        r"^## Edge Case Results\s*$(.*?)(?=^## |\Z)",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if not edge_section_match:
        return 0, 0

    body = edge_section_match.group(1)
    result_lines = re.findall(r"^\*\*Result:\*\*\s*(\w+)", body, flags=re.MULTILINE)
    passes = sum(1 for r in result_lines if r.upper() == "PASS")
    total = len(result_lines)
    return passes, total


def collect_sprint_names(contracts_dir: Path) -> list[str]:
    names = []
    for contract in sorted(contracts_dir.glob("sprint-*.md")):
        name = contract.stem
        if name.endswith(".tasks"):
            continue
        names.append(name)
    return names


def aggregate(root: Path) -> tuple[int, int, list[tuple[str, int, int]]]:
    contracts_dir = root / ".harness" / "contracts"
    evals_dir = root / ".harness" / "evals"

    if not contracts_dir.is_dir():
        return 0, 0, []
    if not evals_dir.is_dir():
        return 0, 0, []

    per_sprint: list[tuple[str, int, int]] = []
    total_pass = 0
    total_total = 0
    for sprint_name in collect_sprint_names(contracts_dir):
        contract_path = contracts_dir / f"{sprint_name}.md"
        if not contract_has_edge_case_section(contract_path):
            continue
        eval_path = latest_round_eval(evals_dir, sprint_name)
        if eval_path is None:
            continue
        passes, total = count_edge_case_outcomes(eval_path)
        per_sprint.append((sprint_name, passes, total))
        total_pass += passes
        total_total += total

    return total_pass, total_total, per_sprint


def main() -> int:
    root = fixture_root()
    total_pass, total_total, per_sprint = aggregate(root)

    for name, p, t in per_sprint:
        print(f"  {name}: {p}/{t}")

    if total_total == 0:
        print("aggregate edge-case pass rate: N/A (no sprint declared edge-case criteria)")
        return 0

    pct = (total_pass / total_total) * 100
    print(f"aggregate edge-case pass rate: {total_pass}/{total_total} = {pct:.1f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
