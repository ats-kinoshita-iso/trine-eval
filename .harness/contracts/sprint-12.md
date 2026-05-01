# Sprint 12 Contract: External-Service Runtime Hookups and Sprint 11 Follow-ups

## What I Will Build

Close the remaining Phase 2 gaps that depend on external services (Batch API HTTP, Playwright MCP, `thinking.profile` runtime dispatch, edge-case multi-sprint aggregation) and land the four mechanical follow-ups Sprint 11's eval explicitly called out: (a) add `Write` to `agents/evaluator.md` `tools` so future evaluations don't fall back to main-thread orchestration; (b) write generic regression invariants to `.harness/regression/regression.json` (the saturated criterion-types from Phase 2 are sprint-scoped and cannot be graduated verbatim — Sprint 12 rewrites them as generic invariants); (c) codify the empirical sprint-contract authoring rules (reference-solution-must, prose-vs-verification-command consistency, deterministic-criterion authoring checklist with five trap categories); (d) document the Evaluator-fallback escape valve and the `thinking.profile` runtime translation in `skills/harness-sprint/SKILL.md`.

The deliverable is a mix of (1) **agent/skill markdown updates** for the mechanical follow-ups; (2) **scripts under `tests/`** for the external-service hookups, each with a clean offline/online split — an offline smoke path that runs in any environment and an online runtime path gated by an environment variable that emits `[SKIP]` when the service is absent (exit 0, not silent failure); and (3) a `.harness/contracts/sprint-12.tasks.json` taxonomy. The fixture project introduced in Sprint 11 (`tests/fixture-project/`) is the seed for Sprint 12's edge-case multi-sprint aggregation test (a second synthetic sprint declares edge-case criteria; the harness-summary aggregator computes the cross-sprint edge-case pass rate).

**Out of scope and explicitly named below**: actually running every Sprint 1–11 eval through the new forked-context Evaluator (would invalidate the historical eval audit trail); rewriting Sprint 11's `tests/fixture-project/` (additive extension only — Sprint 11's deliverables are graduated); eliminating Sprint 11's `## Process Note` from `sprint-11-r1.md` (history is append-only).

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **Evaluator agent declares `Write` in its tool list**: `agents/evaluator.md` frontmatter contains `Write` in the `tools:` field. Verify via `awk '/^---$/{c++; next} c==1' agents/evaluator.md | grep -E '^tools:.*Write'`. The criterion text deliberately matches what the verification command runs — "frontmatter `tools:` line contains `Write`". [weight: 6%]

2. **Generic regression invariants are appended to `.harness/regression/regression.json`**: the file's `tasks` array contains at least 2 entries, each with `task_id`, `verification_command`, `grader_type`, `weight`, `is_gate`, `rubric_dimension`, AND a `graduated_from_sprint` field. The verification commands must be **generic** (not sprint-scoped) — at least one entry's command must use `git ls-files` with a glob like `sprint-*.md` (matching all sprint files including 2-digit sprint numbers, NOT a `sprint-0[0-9]*` glob that would silently miss Sprint 10+) so the invariant protects every prior sprint's artifacts. Verify via `python -c "import json; d=json.load(open('.harness/regression/regression.json')); ts=d['tasks']; assert len(ts)>=2 and all('task_id' in t and 'verification_command' in t and 'graduated_from_sprint' in t and 'grader_type' in t and 'weight' in t and 'is_gate' in t and 'rubric_dimension' in t for t in ts) and any('git ls-files' in t['verification_command'] for t in ts) and not any('sprint-0[0-9]' in t['verification_command'] for t in ts); print('PASS')"`. [weight: 10%]

3. **Sprint-contract skill enforces reference-solution-must and adds the deterministic-criterion authoring checklist**: `skills/sprint-contract/SKILL.md` contains a level-2 or level-3 heading containing the literal text `Before Submitting` (a brand-new section — pre-Sprint-12 the file has no such heading) AND the literal phrase `must have a reference solution` (case-insensitive) AND the literal phrase `Authoring Checklist` (case-insensitive — used as a unique marker to distinguish new authoring-rules content from the pre-existing `weight sum` paragraph at line 33) AND the five trap categories — `multi-line`, `permutation`, `pre-existing`, `weight sum`, AND `prose-vs-verification` (or `prose vs verification` / `prose vs. verification`). Note: `weight sum` appears in `skills/sprint-contract/SKILL.md:33` BEFORE Sprint 12 starts (in the existing weighted-scoring paragraph); the `Before Submitting` heading and `Authoring Checklist` marker requirements ensure Sprint 12's checklist is genuinely new content, not a spurious pre-existing match. Verify via `grep -qE '^#{2,3} .*Before Submitting' skills/sprint-contract/SKILL.md && grep -qiE 'must have a reference solution' skills/sprint-contract/SKILL.md && grep -qi 'authoring checklist' skills/sprint-contract/SKILL.md && grep -qi 'multi-line' skills/sprint-contract/SKILL.md && grep -qi 'permutation' skills/sprint-contract/SKILL.md && grep -qi 'pre-existing' skills/sprint-contract/SKILL.md && grep -qi 'weight sum' skills/sprint-contract/SKILL.md && grep -qiE 'prose[ -]vs[\.\ -]+verification' skills/sprint-contract/SKILL.md`. [weight: 8%]

4. **Harness-sprint skill documents both the Evaluator-fallback escape valve and the `thinking.profile` runtime translation**: `skills/harness-sprint/SKILL.md` contains a level-2 or level-3 heading containing the literal text `Evaluator Fallback` (or `Evaluator fallback`) AND the literal phrase `tool limitation` AND a level-2 or level-3 heading containing the literal text `thinking.profile` AND the three reserved values `default`, `fast`, `thorough` each appearing on a line that maps the value to its API translation. Verify via `grep -qE '^#{2,3} .*[Ee]valuator [Ff]allback' skills/harness-sprint/SKILL.md && grep -qi 'tool limitation' skills/harness-sprint/SKILL.md && grep -qE '^#{2,3} .*thinking\.profile' skills/harness-sprint/SKILL.md && grep -q '"default"' skills/harness-sprint/SKILL.md && grep -q '"fast"' skills/harness-sprint/SKILL.md && grep -q '"thorough"' skills/harness-sprint/SKILL.md`. [weight: 8%]

5. **Batch API runtime hookup script exists with offline/online dual mode**: `tests/batch-api-smoke.py` exists. The script: (a) when invoked with no `ANTHROPIC_API_KEY` env var, emits `[SKIP]` to stdout and exits 0; (b) when invoked with `ANTHROPIC_API_KEY` set (even to a placeholder like `sk-test-fake`), attempts to construct a 2-criterion batch payload using the Anthropic SDK or raw HTTP, dry-runs the request shape (does NOT send to the network — uses the SDK's `model_dump_json()` or equivalent for the request body) and exits 0 on success. Verify via `unset ANTHROPIC_API_KEY; python tests/batch-api-smoke.py | grep -q '\[SKIP\]'` AND `ANTHROPIC_API_KEY=sk-test-fake python tests/batch-api-smoke.py; test $? -eq 0`. The "dry-run only — does not send to network" guarantee keeps Sprint 12 reproducible without a real account. [weight: 12%]

6. **Playwright MCP runtime hookup script exists with offline/online dual mode**: `tests/playwright-smoke.py` exists. The script: (a) checks for the presence of a Playwright MCP connection by reading a probe file at `tests/.playwright-available` (test-only contract — the file is a stand-in for true MCP discovery, which depends on the Claude Code runtime); (b) when the probe file is absent, emits `[SKIP] Playwright MCP not connected` to stdout and exits 0; (c) when the probe file exists, attempts to import `playwright` (Python package) and confirm the import succeeds; if `playwright` is not installed, emits `[SKIP] playwright python package not installed` and exits 0. The script never starts a browser (avoids requiring a real web-app fixture in this sprint). Verify via `rm -f tests/.playwright-available; python tests/playwright-smoke.py | grep -q '\[SKIP\]'; test $? -eq 0` AND `touch tests/.playwright-available; python tests/playwright-smoke.py; rc=$?; rm -f tests/.playwright-available; test $rc -eq 0`. [weight: 12%]

7. **Edge-case multi-sprint aggregation in harness-summary**: `skills/harness-summary/SKILL.md` describes the cross-sprint edge-case aggregation logic AND a synthetic test fixture exercises it. The skill file must contain the literal phrase `cross-sprint edge case` (case-insensitive) AND describe the formula `total edge-case PASS / total edge-case criteria` (or an equivalent). The synthetic test fixture: `tests/fixture-project/.harness/contracts/sprint-fy.md` exists with a level-2 heading `## Edge Case Criteria` AND `tests/fixture-project/.harness/evals/sprint-fy-r1.md` exists declaring at least one edge-case criterion result. The aggregation script `tests/edge-case-aggregate.py` reads both Sprint FX and Sprint FY fixtures and emits a single aggregate edge-case pass rate. Verify via `grep -qiE 'cross.sprint edge.case' skills/harness-summary/SKILL.md && test -f tests/fixture-project/.harness/contracts/sprint-fy.md && test -f tests/fixture-project/.harness/evals/sprint-fy-r1.md && grep -qE '^## Edge Case Criteria' tests/fixture-project/.harness/contracts/sprint-fy.md && python tests/edge-case-aggregate.py | grep -qE 'aggregate edge.case pass rate'`. [weight: 10%]

8. **`sprint-12.tasks.json` is emitted**: `.harness/contracts/sprint-12.tasks.json` exists, is valid JSON, has top-level `sprint: 12`, and contains entries for every criterion in this contract — 8 deterministic + 3 LLM-judge + 3 Should-NOT gates = **14 entries** — each with the Sprint-6 schema fields (`task_id`, `grader_type`, `weight`, `is_gate`). Verify via `python -c "import json; d=json.load(open('.harness/contracts/sprint-12.tasks.json')); assert d['sprint']==12 and len(d['tasks'])>=14 and all('task_id' in t and 'grader_type' in t and 'weight' in t and 'is_gate' in t for t in d['tasks']); print('PASS')"`. [weight: 4%]

### LLM-as-judge (requires reading comprehension)

9. **Sprint 12 round-1 eval was authored by the forked-context Evaluator subagent (not main-thread fallback)**: a reader of `.harness/evals/sprint-12-r1.md` should be able to confirm the eval was produced normally by the Evaluator subagent — specifically, the eval file does NOT contain a `## Process Note` section disclosing a main-thread orchestrator fallback (Sprint 11's pattern), AND the transcript trailer's `thinking_summary` field is consistent with forked-context evaluator reasoning rather than orchestrator self-narration. The reader should also verify that the Sprint 11 audit script (`python tests/audit-verified-via-command.py .harness/evals/sprint-12-r1.md`) returns exit 0, demonstrating that Sprint 12's `verified_via_command` flags are honest. Sprint 12 round-1's eval being subagent-authored is the empirical proof that Criterion 1 (Evaluator `Write` tool) closes the Sprint 11 fallback. [weight: 10%]

10. **External-service guarding correctness across all four hookups**: a reader of `tests/batch-api-smoke.py`, `tests/playwright-smoke.py`, the cross-sprint edge-case aggregation script `tests/edge-case-aggregate.py`, and the new `thinking.profile` runtime translation in `skills/harness-sprint/SKILL.md` should be able to verify the four-way invariant: every external-service-dependent code path either (a) operates strictly on local files, (b) is guarded by an environment-variable / probe-file check that emits `[SKIP] <reason>` and exits 0 when the service is absent, or (c) uses dry-run / mock semantics that never touch the network. No path is allowed to fail silently or to silently exercise a service without its env-var guard present. Reference-solution example: the Sprint 11 `verify-runtime-hookups.sh` regression-abort subcommand's `if external_service_available; then ...; else echo '[SKIP]'; exit 0; fi` pattern. [weight: 10%]

11. **Backward compatibility audit is correct**: a reader of the Sprint 12 commits (`git diff <Sprint-11-tip>..HEAD --stat`) should come away confident that nothing in Sprint 12 modifies Sprint 11's deliverables under `tests/fixture-project/.harness/{config.json,contracts,evals,regression,transcripts}` (additive extension via `tests/fixture-project/.harness/contracts/sprint-fy.md` and `tests/fixture-project/.harness/evals/sprint-fy-r1.md` is permitted; modification of existing Sprint-FX files is not), AND nothing modifies the Sprint 1–10 contracts or evals (`.harness/contracts/sprint-0[1-9]*` and `.harness/contracts/sprint-10*` and the corresponding `.harness/evals/` files). The reader should also verify that the new `tests/audit-report.md` (regenerated from `tests/generate-audit-report.py`) reports zero suspect entries across all 12 sprints — Sprint 12's eval introduces no fabricated `verified_via_command: true` flags. [weight: 10%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **No regression of Sprint 11 deliverables**: `git diff HEAD -- tests/fixture-project/.harness/config.json tests/fixture-project/.harness/contracts/sprint-fx.md tests/fixture-project/.harness/contracts/sprint-fx.tasks.json tests/fixture-project/.harness/dependent.txt 'tests/fixture-project/.harness/evals/sprint-fx-r1-t*.md' tests/fixture-project/.harness/regression/regression.json tests/fixture-project/.harness/summary.md tests/fixture-project/.harness/transcripts/sprint-fx-r1-t1.json tests/audit-verified-via-command.py tests/check-thinking-frontmatter.py tests/generate-audit-report.py tests/verify-runtime-hookups.sh` must produce empty output (HEAD here is the Sprint 12 tip; the listed paths are the Sprint 11 deliverables, all of which Sprint 12 must leave untouched). Additive new files such as `tests/fixture-project/.harness/contracts/sprint-fy.md` are not in this list and are permitted. Verify via `test -z "$(git diff HEAD -- tests/fixture-project/.harness/config.json tests/fixture-project/.harness/contracts/sprint-fx.md tests/fixture-project/.harness/contracts/sprint-fx.tasks.json tests/fixture-project/.harness/dependent.txt 'tests/fixture-project/.harness/evals/sprint-fx-r1-t*.md' tests/fixture-project/.harness/regression/regression.json tests/fixture-project/.harness/summary.md tests/fixture-project/.harness/transcripts/sprint-fx-r1-t1.json tests/audit-verified-via-command.py tests/check-thinking-frontmatter.py tests/generate-audit-report.py tests/verify-runtime-hookups.sh)"`.

2. **External-service paths emit `[SKIP]` cleanly with exit 0 when service unavailable**: in the absence of any external service (no `ANTHROPIC_API_KEY`, no `tests/.playwright-available` probe, no Playwright python package), running each new external-service script must produce a `[SKIP] <reason>` log line on stdout AND exit 0. No path is allowed to print `[FAIL]`, raise an unhandled exception, or exit non-zero because a service is unavailable. Verify by reading the script source and confirming each external-service path is guarded by an explicit check.

3. **No fabrication of `verified_via_command: true` in the Sprint 12 transcript trailer**: the Sprint 12 round-1 eval at `.harness/evals/sprint-12-r1.md` must satisfy the Sprint 11 audit script — every `criteria_audit` entry with `verified_via_command: true` must have a corresponding `task_id` in the `tool_calls` array. Verify via `python tests/audit-verified-via-command.py .harness/evals/sprint-12-r1.md`.

## Reference Solutions

**Criterion 5 (Batch API runtime hookup) — example offline/online dual-mode pattern:**

````python
# tests/batch-api-smoke.py
"""
Sprint 12 Criterion 5. Demonstrates that the Batch API protocol shipped in
Sprint 8 can construct a valid request body and survive an end-to-end shape
check, gated on ANTHROPIC_API_KEY being present.

Offline mode (no ANTHROPIC_API_KEY): exits 0 with [SKIP].
Online mode (ANTHROPIC_API_KEY set): constructs a 2-criterion batch payload,
serializes it via the SDK's model_dump_json (or raw dict-to-json), prints the
shape summary. NEVER sends to the network in either mode — the shape-check is
the test, not the live request.
"""

from __future__ import annotations
import json
import os
import sys


def main() -> int:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("[SKIP] ANTHROPIC_API_KEY not set — Batch API smoke test deferred")
        return 0

    # Construct the batch payload shape (NO network call).
    payload = {
        "requests": [
            {
                "custom_id": "sprint-12-c1",
                "params": {
                    "model": "claude-opus-4-7",
                    "max_tokens": 256,
                    "messages": [{"role": "user", "content": "Smoke 1"}],
                },
            },
            {
                "custom_id": "sprint-12-c2",
                "params": {
                    "model": "claude-opus-4-7",
                    "max_tokens": 256,
                    "messages": [{"role": "user", "content": "Smoke 2"}],
                },
            },
        ]
    }
    serialized = json.dumps(payload)
    print(f"[OK] Batch payload constructed: {len(serialized)} bytes, 2 requests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
````

**Criterion 9 (forked-context Evaluator authorship) — example contrast pattern:**

The Sprint 11 eval has a `## Process Note (Transparency)` heading at lines 4–8 disclosing main-thread fallback. The Sprint 12 eval should NOT have such a section. The contrast verification:

```bash
# Should exit 1 (no match):
grep -E '^## Process Note' .harness/evals/sprint-12-r1.md
```

## Out of Scope

- **Re-running every Sprint 1–11 eval through the new forked-context Evaluator**. The historical eval audit trail is append-only; rewriting prior evals would invalidate the audit chain.
- **Modifying Sprint 11's `tests/fixture-project/` deliverables**. Additive extension via `tests/fixture-project/.harness/contracts/sprint-fy.md` and the new edge-case aggregation script is permitted; mutation of existing Sprint-FX files is forbidden (SN1 enforces this deterministically).
- **Eliminating the `## Process Note` section from Sprint 11's `sprint-11-r1.md`**. History is append-only — Sprint 11's eval stays as-is. Criterion 9 verifies Sprint 12's eval is process-note-free, not Sprint 11's.
- **Live network calls during automated verification**. Both `tests/batch-api-smoke.py` and `tests/playwright-smoke.py` use dry-run / probe-file semantics. A live-API run is appropriate for manual smoke testing but is not a Sprint 12 criterion.
- **Redoing the Phase 2 gap analysis as a Sprint 12 deliverable**. The recommendation in the Sprint 11 summary stands as a follow-up, not a sprint criterion. The four external-service hookups Sprint 12 lands close the runtime side of Gaps 5b, 7, 8, 9; the gap-analysis re-run is a separate exercise.
- **Real `web-app` fixture for Playwright**. Sprint 12 verifies the protocol-level dispatch (probe-file detection + python-package import); end-to-end browser invocation against a rendered DOM is a follow-up sprint or an applied-harness use case (`web-app` consumer project).
- **Removing the "deprecated `pass@rounds`" terminology from prior summaries**. The deprecation label is preserved in the audit trail.

## Technical Notes

- **The Sprint 12 round-1 eval is the empirical test of Criterion 1.** If the Evaluator subagent successfully writes `.harness/evals/sprint-12-r1.md` without a `## Process Note` section, Criterion 1 (Write tool) is verified end-to-end, not just at the protocol level. This is the same protocol-vs-runtime split Sprint 11 closed for the prior gaps.

- **Generic regression invariants are the first non-fixture entries in `regression.json`.** Sprint 11 demonstrated the regression-abort path with a single fixture-scoped entry (`sfx-c1`). Sprint 12 graduates the saturated criterion-types from Phase 2 into generic invariants by **rewriting** them — not by copying a single sprint's `verification_command` verbatim. Recommended initial entries: (a) every committed `.harness/contracts/sprint-NN.md` has a sibling `sprint-NN.tasks.json` (use `git ls-files` to enumerate); (b) no previously-committed sprint artifact is modified in HEAD (use `git ls-files | git diff HEAD --` over the historical contract+eval set).

- **The five trap categories on the contract authoring checklist are empirical, not speculative.** Each was caught in a prior sprint: multi-line YAML frontmatter (Sprint 8), permutation regex (Sprint 8), pre-existing-content false positive (Sprint 9 review), weight sum mismatch (Sprint 11), prose-vs-verification-command mismatch (Sprint 11). The checklist's value is preventing recurrences, not enumerating hypothetical traps.

- **`thinking.profile` runtime translation is a documentation-only criterion in Sprint 12.** The actual API invocation requires the orchestrator to have the live runtime instrumentation that maps `config.thinking.profile` to per-message `thinking: { type: enabled, budget_tokens: ... }` parameters. Sprint 12 documents the translation table; the runtime hookup is observable when the harness drives a live API call (which only happens in the eval pipeline once the Evaluator can dispatch with the per-mode override). Documenting `default → standard thinking, fast → no thinking, thorough → high-budget thinking` (or the project's chosen translation) is sufficient for Criterion 4.

- **The Playwright probe-file pattern (`tests/.playwright-available`) is a test contract**, not a true MCP-discovery primitive. Real MCP discovery happens through the Claude Code runtime; the probe file lets the script's offline/online split be exercised in CI without depending on a Claude Code instance. The probe file is the moral equivalent of `[ -n "$ANTHROPIC_API_KEY" ]` for the Anthropic SDK.

- **Edge-case multi-sprint aggregation requires at least two synthetic sprints with edge-case criteria.** Sprint 11 introduced `sprint-fx`. Sprint 12 introduces `sprint-fy` with a `## Edge Case Criteria` section and at least one edge-case eval entry. The aggregation script `tests/edge-case-aggregate.py` walks both fixtures and computes the cross-sprint pass rate. The output format is intentionally minimal (one line: `aggregate edge-case pass rate: X/Y = Z%`) to keep the verification grep simple.

- **Activation steps for the user.** Once this contract is approved: (1) run `/harness-sprint 12` again to enter Step 2 (Implementation); (2) the Generator builds the deliverables in the order C1 → C2/C3/C4 → C5/C6/C7 → C8 (mechanical first, external-service second, taxonomy emission last), committing after each meaningful unit; (3) Step 3 spawns the Evaluator subagent (now with `Write`) and the Sprint 12 round-1 eval lands without a Process Note, validating Criterion 9 in real time.

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/sprint-12.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — 8 deterministic + 3 LLM-judge + 3 Should-NOT gates = 14 entries — with stable `task_id`s, `grader_type`, `weight`, `is_gate`, `verification_command` (where applicable), and `rubric_dimension`.

## Evaluator Review

**Status: APPROVED**

### Weight Sum Check

Extracted weights: C1=6, C2=10, C3=8, C4=8, C5=12, C6=12, C7=10, C8=4, C9=10, C10=10, C11=10. Sum = 100%. PASS.

### Tasks.json Count Check

8 deterministic (C1–C8) + 3 LLM-judge (C9–C11) + 3 Should-NOT gates (SN1–SN3) = 14 entries. Count matches C8's assertion. PASS.

### Trap-by-Trap Walkthrough

**Pre-existing content**: All three sets of novel markers checked. `Before Submitting` and `Authoring Checklist` are absent from `skills/sprint-contract/SKILL.md` (grep returned empty). The pre-existing `weight sum` at line 33 is correctly named and quarantined by requiring the `Authoring Checklist` anchor. `Evaluator Fallback` and `tool limitation` are absent from `skills/harness-sprint/SKILL.md`; only a passing `thinking.profile` mention appears at line 202 (in prose, not as a heading). `cross-sprint edge case` is absent from `skills/harness-summary/SKILL.md`. No false-positive traps remain.

**Multi-line greps**: All greps in C1–C8 use single-line patterns (`grep -q` and `grep -qE`). The patterns search for short phrases that cannot span lines. No multi-line trap identified.

**Permutation regex**: C3's verification chains multiple independent `grep -q` calls rather than a single regex requiring ordered elements. C4 does the same. No permutation ordering dependency is present in any verification command. No permutation trap identified.

**Prose-vs-verification-command consistency**: All deterministic criteria (C1–C8) have verification commands that directly test the stated prose. Minor note on C6 below — the "online" verification only checks exit 0, not that the script actually exercised the import path. This is a testability gap but is consistent with the prose's intent (the script exits 0 whether it imports or SKIPs).

### Pre-existing Content Audit

- **C1** (`agents/evaluator.md` tools field contains `Write`): `Write` appears at line 160 of `agents/evaluator.md` only in body prose ("Write results to…"), NOT in the frontmatter `tools:` field. Criterion is not trivially pre-satisfied. CLEAN.
- **C3** (`Before Submitting` heading, `Authoring Checklist`, `must have a reference solution` in `skills/sprint-contract/SKILL.md`): None of these strings exist pre-Sprint-12. `weight sum` pre-exists at line 33 as disclosed and is correctly handled by the `Authoring Checklist` anchor. CLEAN.
- **C4** (`Evaluator Fallback` heading, `tool limitation`, `thinking.profile` heading with `"default"/"fast"/"thorough"` in `skills/harness-sprint/SKILL.md`): Only a passing `thinking.profile` mention exists (line 202, body prose, not a heading); the heading form `^#{2,3} .*thinking\.profile` is absent. `Evaluator Fallback` and `tool limitation` are absent. CLEAN.
- **C7** (`cross-sprint edge case` in `skills/harness-summary/SKILL.md`): Absent. CLEAN.

### Self-Referential Criterion (C9)

C9 is verifiable without circular reasoning. The primary check — absence of `## Process Note` — is a deterministic grep that any reader can run before or after evaluation. The secondary check (`thinking_summary` field consistency) is acknowledged as subjective; it is LLM-judged and appropriately labeled. The contrast pattern in the Reference Solutions section (showing Sprint 11's `## Process Note` as the positive example of what must be absent) makes the grading anchor concrete. The criterion correctly describes how to detect main-thread fallback. No revision needed.

### Reference Solutions

The highest-weighted LLM-judge criterion is C9, C10, C11 (all 10%). C9 has a dedicated reference solution block (the Sprint 11 contrast pattern). C10's reference solution is the Sprint 11 `verify-runtime-hookups.sh` pattern cited inline in C10's prose. C11 has no standalone reference solution block, but its grading relies on `git diff --stat` output inspection which is self-explanatory. The highest-weighted LLM-judge criterion (any of the three tied at 10%) has adequate reference material. PASS.

### Feature Coverage

All 8 Sprint 12 features map to criteria:

- `evaluator-write-tool` → C1
- `generic-regression-invariants` → C2
- `contract-skill-authoring-rules` → C3
- `evaluator-fallback-documentation` + `thinking-profile-runtime-dispatch` → C4
- `batch-api-runtime-hookup` → C5
- `playwright-runtime-hookup` → C6
- `edge-case-multi-sprint-aggregation` → C7
- C8 (tasks.json taxonomy) is a harness-housekeeping deliverable not listed as a named feature in `sprints.json` but is standard Sprint 6+ practice

All 8 named features have criterion coverage. PASS.

### Feedback (per-criterion issues)

- **C6 (Playwright, minor)**: The "online" verification (`touch tests/.playwright-available; python tests/playwright-smoke.py; rc=$?; ... test $rc -eq 0`) verifies exit 0 but cannot distinguish a working import from a script that emits a second `[SKIP]` line (for missing `playwright` package). Both paths are defined as exit 0 by the criterion, so this is consistent — but a reader cannot confirm the script attempted the import in CI where `playwright` is not installed. Consider adding `|| grep -q '\[SKIP\] playwright python package not installed'` to the second verification branch. This is minor; the criterion is not broken.
- **C10 (scope framing, very minor)**: `tests/edge-case-aggregate.py` is listed as one of the four scripts to audit for external-service guarding, but it operates strictly on local files. It trivially satisfies guard condition (a). No confusion results, but the framing is slightly misleading given the criterion title "External-service guarding correctness across all four hookups."
- **C11 (glob in prose, informational)**: The LLM-judge prose references `.harness/contracts/sprint-0[1-9]*` (misses Sprint 10+), but since C11 is LLM-judged and SN1 covers the regression path deterministically, this is not a grading failure. Informational only.

### Approved Criteria

C1, C2, C3, C4, C5, C7, C8, C9, C10 — all well-formed as written. C6 approved with a minor note. C11 approved with informational note. SN1, SN2, SN3 — all well-formed gates.

### Final Verdict

The contract is structurally sound: weights sum to 100%, the 14-entry count is correct, all pre-existing-content traps are either absent or explicitly quarantined, and all 8 Sprint 12 features have criterion coverage. The three issues flagged (C6 online-path ambiguity, C10 scope framing, C11 glob in prose) are minor and do not block implementation. The contract may proceed to implementation as written. A Generator addressing C6 should be guided by the improvement note above, but the criterion as written is testable and will not produce false negatives.
