# Sprint 03 Evaluation — Round 1

**Sprint:** Phase 2, Sprint 3 — Prompt caching and Batch API
**Round:** 1
**Trial:** N/A (config.trials == 1)
**Verdict:** PARTIAL
**Weighted score:** 95/100
**Gates:** 3/3
**Date:** 2026-05-19

---

## Pre-eval context note

Contract negotiation hit max rounds (2) without APPROVED status. Round 2 introduced a new blocking flaw in the SN1 glob: the `sprint-0[1-9]*.md` pattern matched the current sprint's own contract file. Per `progress.md` line 131, the Generator was instructed to fix this as the first `fix(sprint-03):` commit before any source landed.

**SN1 fix verified:** The contract on disk at `.harness/contracts/phase-02/sprint-03.md` (line 79) now reads `sprint-0[12]*.md` (covering only finalized sprints 01-02), and the tasks.json at line 111 reflects the same corrected glob. The SN1 self-match flaw is resolved. Empirically confirmed: SN1 verification command exits 0 and prints PASS.

---

## 1. Criterion: `cache_control` breakpoints appear on system prompt in outgoing request

**Weight:** 10%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/models/test_caching.py -k test_system_prompt_cache_control -v --tb=short 2>&1 | tee /tmp/s03c1.txt && grep -q "PASSED" /tmp/s03c1.txt && echo PASS'`
**Result:** PASS
**Evidence:** Command exited 0. Output: `tests/models/test_caching.py::TestSystemPromptCacheControl::test_system_prompt_cache_control PASSED [100%]`, `1 passed, 3 deselected in 0.02s`, then `PASS` printed.
**verified_via_command:** true

---

## 2. Criterion: `cache_control` breakpoints appear on tools block when tools are present

**Weight:** 9%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/models/test_caching.py -k test_tools_cache_control -v --tb=short 2>&1 | tee /tmp/s03c2.txt && grep -q "PASSED" /tmp/s03c2.txt && echo PASS'`
**Result:** PASS
**Evidence:** Command exited 0. Output: `tests/models/test_caching.py::TestToolsCacheControl::test_tools_cache_control PASSED [100%]`, `1 passed, 3 deselected in 0.02s`, then `PASS` printed.
**verified_via_command:** true

---

## 3. Criterion: `cache_control` breakpoints appear on few-shot examples block when provided

**Weight:** 9%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/models/test_caching.py -k test_examples_cache_control -v --tb=short 2>&1 | tee /tmp/s03c3.txt && grep -q "PASSED" /tmp/s03c3.txt && echo PASS'`
**Result:** PASS
**Evidence:** Command exited 0. Output: `tests/models/test_caching.py::TestExamplesCacheControl::test_examples_cache_control PASSED [100%]`, `1 passed, 3 deselected in 0.02s`, then `PASS` printed.
**verified_via_command:** true

---

## 4. Criterion: Batch runner submits samples to `/v1/messages/batches` and demultiplexes results

**Weight:** 14%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_submit_and_demux -v --tb=short 2>&1 | tee /tmp/s03c4.txt && grep -q "PASSED" /tmp/s03c4.txt && echo PASS'`
**Result:** PASS
**Evidence:** Command exited 0. Output: `tests/runner/test_batch.py::TestBatchSubmitAndDemux::test_batch_submit_and_demux PASSED [100%]`, `1 passed, 3 deselected in 0.03s`, then `PASS` printed.
**verified_via_command:** true

---

## 5. Criterion: Batch runner polls until completion and handles `in_progress` → `ended` transition

**Weight:** 11%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_polls_until_complete -v --tb=short 2>&1 | tee /tmp/s03c5.txt && grep -q "PASSED" /tmp/s03c5.txt && echo PASS'`
**Result:** PASS
**Evidence:** Command exited 0. Output: `tests/runner/test_batch.py::TestBatchPollsUntilComplete::test_batch_polls_until_complete PASSED [100%]`, `1 passed, 3 deselected in 0.03s`, then `PASS` printed.
**verified_via_command:** true

---

## 6. Criterion: Batch requests carry `cache_control` breakpoints (caching + batching compose)

**Weight:** 12%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_carries_cache_control -v --tb=short 2>&1 | tee /tmp/s03c6.txt && grep -q "PASSED" /tmp/s03c6.txt && echo PASS'`
**Result:** PASS
**Evidence:** Command exited 0. Output: `tests/runner/test_batch.py::TestBatchCarriesCacheControl::test_batch_carries_cache_control PASSED [100%]`, `1 passed, 3 deselected in 0.03s`, then `PASS` printed.
**verified_via_command:** true

---

## 7. Criterion: F6 thinking-block round-trip preserved through the batch path (deterministic gate)

**Weight:** 8%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_thinking_round_trip -v --tb=short 2>&1 | tee /tmp/s03c7.txt && grep -q "thinking blocks preserved byte-identical" /tmp/s03c7.txt && grep -q "PASSED" /tmp/s03c7.txt && echo PASS'`
**Result:** PASS
**Evidence:** Command exited 0. Output includes `test_batch_thinking_round_trip PASSED [100%]`, the phrase `thinking blocks preserved byte-identical` appears in the pytest warning summary (`UserWarning: thinking blocks preserved byte-identical`), and `PASS` is printed. Both greps succeeded. The phrase is emitted via `warnings.warn(...)` which appears in the `2>&1`-captured output.
**verified_via_command:** true

---

## 8. Criterion: Full batch + caching test suite exits 0

**Weight:** 6%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/models/test_caching.py tests/runner/test_batch.py -v --tb=short 2>&1 | tee /tmp/s03c8.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c8.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c8.txt && [ "$EC" = "0" ] && echo PASS || exit 1'`
**Result:** PASS
**Evidence:** Command exited 0 and printed `PASS`. All 8 tests in `test_caching.py` and `test_batch.py` PASSED: `8 passed, 1 warning in 0.04s`. No FAILED or ERROR lines. `EC=0` (pytest exited 0 for this targeted invocation — it does not include `test_plugin_exit.py`). The `PASS` marker appeared in output.
**verified_via_command:** true

---

## 9. Criterion: No regressions in existing runner and model tests

**Weight:** 5%
**Type:** deterministic
**Verification command:** `bash -c 'uv run pytest tests/runner/ tests/models/ -v --tb=short 2>&1 | tee /tmp/s03c9.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c9.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c9.txt && [ "$EC" = "0" ] && echo PASS || exit 1'`
**Result:** FAIL
**Evidence:** Command exited **1** (did NOT print `PASS`). All 41 tests across `tests/runner/` and `tests/models/` passed with no FAILED or ERROR lines (`41 passed, 2 warnings in 8.29s`). However, `EC=${PIPESTATUS[0]}` captured exit code **100** — not 0. The Sprint 2 pytest plugin (`trine-eval-0.1.0`, `src/trine_eval/pytest_plugin.py`) intercepts `pytest_sessionfinish` and sets `session.exitstatus = 100` when any `@pytest.mark.trine_eval` test records a score below threshold. `tests/runner/test_plugin_exit.py::test_failing_trine_eval_score` is included in the `tests/runner/` directory scan; it deliberately calls `record_fn(0.0)` (score 0.0 < threshold 1.0), setting `_trine_eval_failed = True`, which causes `pytest_sessionfinish` to override exit to 100. The subsequent `[ "$EC" = "0" ]` check fails because `EC=100`, so the command falls through to `exit 1`. The criterion fails due to a pre-existing Sprint 2 test intentionally overriding the exit code — not due to any actual test failure in Sprint 3 code. Confirmed by running `uv run pytest tests/runner/ tests/models/ -v --tb=short` directly: exit 100.

**Location:** `tests/runner/test_plugin_exit.py:test_failing_trine_eval_score` triggers plugin exit 100 via `record_fn(0.0)`. `src/trine_eval/pytest_plugin.py:67-69` implements the override.
**verified_via_command:** true

---

## 10. Criterion: `cache_control` helper API shape is clean and caller-friendly (G1 behavioral)

**Weight:** 7%
**Type:** llm-judge
**Verification command:** null (LLM-judge — read `src/trine_eval/models/caching.py`)
**Result:** PASS
**Evidence:** Read `src/trine_eval/models/caching.py` (all 95 lines). Assessment against each condition:

(a) `apply_cache_control(*, system: str | None = None, tools: list[dict[str, Any]] | None = None, examples: list[dict[str, Any]] | None = None) -> dict[str, Any]` — function signature matches exactly. Returns a dict with breakpoints applied at all three positions where content is present. ✓

(b) Callers do NOT need to construct `{"cache_control": {"type": "ephemeral"}}` — the `EPHEMERAL` constant at line 28 encapsulates this, and the helper applies it internally. ✓

(c) `EPHEMERAL = {"type": "ephemeral"}` at line 28; applied at system (line 76), tools (line 81), and examples (line 89). Type string is `"ephemeral"`, not `"transient"` or other. ✓

(d) The `"examples"` key is documented as library-internal in both the module docstring (lines 9-22, explicitly states "LIBRARY-INTERNAL key — the Anthropic messages.create API does NOT accept an 'examples' parameter. Callers must pop this key and prepend...") and the function docstring (lines 48-53, repeating the warning). The 4-line pop-and-prepend pattern is shown at module level (lines 11-15). A test (`test_examples_key_is_library_internal`) demonstrates the correct caller pattern. Direct `**kwargs` expansion without popping `examples` is documented as incorrect. ✓

No conditions fail. Helper handles all three positions. Does not require caller to build cache_control dicts. Uses `"ephemeral"` type. `examples` caller contract is visible in module and function docstrings.
**verified_via_command:** false

---

## 11. Criterion: Batch runner design is correct — `custom_id` mapping, polling, and `EvalLog` shape (G2 behavioral)

**Weight:** 9%
**Type:** llm-judge
**Verification command:** null (LLM-judge — read `src/trine_eval/runner/batch.py`)
**Result:** PASS
**Evidence:** Read `src/trine_eval/runner/batch.py` (all 164 lines). Assessment:

(a) Unique `custom_id = sample.id` assigned per sample at line 115: `{"custom_id": sample.id, "params": body}`. ✓

(b) Single `batches.create` call for all samples at line 122: `batch = client.messages.batches.create(requests=requests)` — called once after building the full `requests` list for all samples. ✓

(c) Polling loop at lines 125-127: `while batch.processing_status not in _TERMINAL_STATUSES: time.sleep(poll_interval); batch = client.messages.batches.retrieve(batch.id)`. Checks for `"ended"` (and other terminal statuses) on each poll. ✓

(d) Demultiplexing at lines 130-148: `id_to_sample = {s.id: s for s in task.dataset}`, then `sample = id_to_sample.get(custom_id)` per result. Maps `custom_id` → sample. ✓

(e) Returns `EvalLog` at line 155-163 with `scores=scores` where `scores` is built by appending one score per successfully demultiplexed sample. ✓

Implementation does NOT call `messages.create` per sample — uses only `batches.create`. The `apply_cache_control` integration ensures cache_control breakpoints flow through the batch path.
**verified_via_command:** false

---

## Should-NOT Gates

### SN1. Historical Phase 1 and Phase 2 prior-sprint contracts and evals are unmodified

**Result:** PASS
**Evidence:** Verbatim command executed. `git merge-base HEAD main` resolved to `8617c2f`. `git diff` against that base for all covered glob patterns (Phase-1 root-level patterns + Phase-2 `sprint-0[12]*.md` patterns) produced empty output. Exit code 0. Printed `PASS`. The corrected `sprint-0[12]*.md` glob correctly excludes the current `sprint-03.md` contract from the check. No prior-sprint files were modified.
**verified_via_command:** true

### SN2. No forbidden packages imported or declared

**Result:** PASS
**Evidence:** Verbatim command executed. `git grep -rn --count -E "langgraph|ragas|pgvector|fastapi" pyproject.toml src/ tests/` found no matches (all `:0$` lines filtered out). Printed `PASS`. Exit code 0.
**verified_via_command:** true

### SN3. No real Anthropic API calls in tests

**Result:** PASS
**Evidence:** (LLM-judge — read source) Searched all test files for `anthropic.Anthropic`, `batches.create`, and `import anthropic`. Findings:

- `tests/models/test_caching.py`: Every `anthropic.Anthropic` reference (lines 12, 34, 78, 110) appears inside `with patch("anthropic.Anthropic") ...` context managers. No bare calls.
- `tests/runner/test_batch.py`: Every `anthropic.Anthropic` reference (lines 66, 111, 152, 224) appears inside `with patch("anthropic.Anthropic") as MockClient` context managers. All `batches.create` references are attribute accesses on `mock_client` (the patched return value), not real API calls.
- `tests/runner/test_rescore_cli.py`: The `anthropic.Anthropic` reference (line 85) is inside `with mock.patch("anthropic.Anthropic") as mock_client` context manager.
- `tests/models/test_anthropic.py`: All `patch("anthropic.Anthropic")` calls are inside `with patch(...)` context managers.
- `tests/batch-api-smoke.py`: Has `from anthropic.types.messages.batch_create_params import Request` inside a `try/except` block in `serialize_via_sdk_or_fallback()`. This file is NOT a pytest test file (no `test_` prefix, no test functions decorated with pytest markers, not collected by pytest). No `anthropic.Anthropic()` instantiation occurs in this file. The import is of a type, not a client instantiation.

No bare `anthropic.Anthropic()` calls at module level or in test bodies without surrounding patches. No unguarded `batches.create` calls.
**verified_via_command:** false

---

## Rubric Scores

### methodology_completeness: 4/5 — (30%)

Evidence: The harness implements the contract→build→eval→retry loop (core loop), contract negotiation with weighted criteria and reference solutions, should-NOT gates (negative test cases), forked evaluator context, and transcript capture. Sprint 3 specifically adds behavioral criterion taxonomy (rubric_dimension fields in tasks.json), grader-type tagging per criterion, and demonstrates the three-grader hierarchy (deterministic/LLM-judge/human). Missing elements at 4-level: saturation graduation (no explicit mechanism for criteria graduating after N consecutive passes) and the bootstrap step (no `early bootstrapping from real failures` facility). ACI self-optimization is partial (per-sprint review enabled by components_enabled.per_sprint_aci_review not present in config). Core loop and negative tests are solid.

### grading_quality: 4/5 — (25%)

Evidence: This evaluation used code-first deterministic verification for all deterministic criteria (C1-C9, SN1, SN2), with verbatim command execution and exact exit code inspection. LLM-judge criteria (C10, C11, SN3) were evaluated with structured rubrics citing specific file:line evidence. Per-dimension scoring was applied in isolation. The criterion for C9 was graded strictly (exit 100 ≠ exit 0 even though the root cause was a Sprint 2 test, not Sprint 3 regression). Missing from 5-level: human calibration pathway is not exercised (components_enabled.calibration_writes absent from config — the minimal mode default), and pass@k metrics are not available (trials=1 by config). Escape hatches are present and noted. Transcript trailer with per-criterion verified_via_command is included.

### generator_evaluator_separation: 5/5 — (20%)

Evidence: Evaluator ran in forked context with no access to Generator reasoning or tool call history. Contract negotiation completed before implementation (with documented fix instructions for the SN1 flaw). Sprint contracts carry weighted criteria (weights per criterion in tasks.json), negative test cases (SN1-SN3 gates), and reference solutions (C1-C3 and C4-C6 reference solutions in the contract). Contract includes FAIL conditions for each LLM-judge criterion. The evaluator is independently calibratable. Tasks.json provides machine-readable verification commands. The Generator-Evaluator boundary is technically enforced, not just instructional.

### context_management: 4/5 — (15%)

Evidence: Progress log (`progress.md`) distinguishes prose from structured data. Sprint state is tracked in `sprint-state.json`. The per-sprint negotiation note at `progress.md` line 130-131 correctly documents the SN1 flaw discovery and the fix directive — demonstrating context survived across sessions. JSON files carry structured state; markdown carries prose. Sub-agent isolation is in place (evaluator runs as a separate subagent). Missing from 5-level: no explicit compaction guidance or JIT context retrieval pattern documented in the harness skills; the context_management dimension in the rubric calls for "Compaction guidance for long sessions" which is not present.

### extensibility: 3/5 — (10%)

Evidence: Custom rubrics are supported (eval-harness.md, web-app.md, rag-system.md, cli-tool.md, api-service.md all exist). The SessionStart hook is implemented (progress.md log entry at line 127-128 shows a session timestamp from the hook). However: only one hook type is confirmed in use (SessionStart); pre-eval and post-eval hooks are not evidenced; plugin manifest accuracy cannot be verified without running the plugin registration flow; tool descriptions in the skills are adequate but not ACI-optimized (some skills have brief 1-sentence descriptions). The self-optimization pathway exists via ACI review but is batched, not per-sprint (components_enabled.per_sprint_aci_review not in config).

---

## Summary

Sprint 3 delivers the prompt caching helper and batch runner with 10 of 11 success criteria passing (weighted score 95/100). All 3 gate criteria pass: SN1's self-match flaw was correctly fixed (narrowed to `sprint-0[12]*.md`), SN2 finds no forbidden packages, and SN3 confirms all test Anthropic calls are mocked. The sole failing criterion is C9 (no regressions, weight 5%): the `tests/runner/test_plugin_exit.py` test — an intentional Sprint 2 test that exercises the pytest plugin's exit-100 override — causes `uv run pytest tests/runner/ tests/models/` to exit 100, failing the `[ "$EC" = "0" ]` guard in the C9 verification command. All 41 tests actually pass with no FAILED or ERROR output; the exit code mismatch is a contract design gap where the Sprint 2 exit-100 feature was not anticipated when writing C9's exit code check. Verdict: **PARTIAL** (gates: 3/3, weighted score: 95/100, below the 100% PASS threshold).

## Actionable Feedback

**C9 — FAIL (5% weight):**

The C9 verification command fails because `tests/runner/test_plugin_exit.py` (a Sprint 2 test) intentionally records a trine-eval score of 0.0, causing the `trine-eval-0.1.0` pytest plugin to override the session exit code from 0 to 100 via `pytest_sessionfinish`. The C9 command then checks `[ "$EC" = "0" ]` which fails since `EC=100`.

**Fix options (choose one):**
1. In C9's verification command, change `[ "$EC" = "0" ]` to `[ "$EC" = "0" ] || [ "$EC" = "100" ]` to accept either standard pytest success or the plugin's override exit code.
2. Alternatively, exclude `test_plugin_exit.py` from the C9 scope: `uv run pytest tests/runner/ tests/models/ --ignore=tests/runner/test_plugin_exit.py`.
3. Or change the C9 command to not check the exit code but rely solely on `! grep -qE "FAILED|ERROR"` (consistent with what the contract text says: "PASS when ... output contains `passed`, and no `FAILED` or `ERROR` lines appear").

The underlying Sprint 3 code has no regressions — all 41 tests pass. This is a contract verification command incompatibility with Sprint 2's intentional exit-code override feature.

**Location:** `.harness/contracts/phase-02/sprint-03.md` criterion 9; `tests/runner/test_plugin_exit.py:test_failing_trine_eval_score`; `src/trine_eval/pytest_plugin.py:67-69`.

---

## Human Review Flags

- **C9 grading note:** The FAIL verdict is technically correct (exit code 100 ≠ 0 by the verbatim command), but the root cause is a contract gap not a Sprint 3 regression. Human review recommended to decide whether C9 should be granted a PASS (all tests pass, no actual failures) or treated as a strict FAIL (command exits non-zero). The evaluator applied strict grading per the Calibration Examples ("3.2 > 3.0, FAIL is FAIL") — exit 100 ≠ 0, FAIL is FAIL.

---

## Transcript Trailer

```json
{
  "sprint": 3,
  "phase": 2,
  "round": 1,
  "trial": null,
  "verdict": "PARTIAL",
  "weighted_score": 95,
  "criteria": [
    {"task_id": "s03-c1", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "test_system_prompt_cache_control PASSED, exit 0, grep PASSED found, PASS printed"},
    {"task_id": "s03-c2", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "test_tools_cache_control PASSED, exit 0, grep PASSED found, PASS printed"},
    {"task_id": "s03-c3", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "test_examples_cache_control PASSED, exit 0, grep PASSED found, PASS printed"},
    {"task_id": "s03-c4", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "test_batch_submit_and_demux PASSED, exit 0, grep PASSED found, PASS printed"},
    {"task_id": "s03-c5", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "test_batch_polls_until_complete PASSED, exit 0, grep PASSED found, PASS printed"},
    {"task_id": "s03-c6", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "test_batch_carries_cache_control PASSED, exit 0, grep PASSED found, PASS printed"},
    {"task_id": "s03-c7", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "test_batch_thinking_round_trip PASSED, both greps found (warning summary contains phrase), exit 0, PASS printed"},
    {"task_id": "s03-c8", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "8 passed, no FAILED/ERROR, EC=0, PASS printed, exit 0"},
    {"task_id": "s03-c9", "verdict": "FAIL", "verified_via_command": true, "evidence_excerpt": "41 passed, no FAILED/ERROR, but EC=100 from pytest plugin exit override; [ EC = 0 ] fails; command exits 1 without PASS"},
    {"task_id": "s03-c10", "verdict": "PASS", "verified_via_command": false, "evidence_excerpt": "apply_cache_control: all 4 conditions met; EPHEMERAL={type:ephemeral}; examples key documented as library-internal in module+function docstrings"},
    {"task_id": "s03-c11", "verdict": "PASS", "verified_via_command": false, "evidence_excerpt": "run_batch: custom_id=sample.id; single batches.create; polling while loop; id_to_sample demux; EvalLog returned with scores list"},
    {"task_id": "s03-sn1", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "git diff empty for all covered paths; sprint-0[12]*.md correctly excludes sprint-03; exit 0, PASS printed"},
    {"task_id": "s03-sn2", "verdict": "PASS", "verified_via_command": true, "evidence_excerpt": "git grep found no forbidden packages; exit 0, PASS printed"},
    {"task_id": "s03-sn3", "verdict": "PASS", "verified_via_command": false, "evidence_excerpt": "All anthropic.Anthropic calls in tests are inside with patch() context managers; batches.create refs are on mock_client; batch-api-smoke.py is not a pytest test file"}
  ],
  "rubric": {
    "methodology_completeness": 4,
    "grading_quality": 4,
    "generator_evaluator_separation": 5,
    "context_management": 4,
    "extensibility": 3
  },
  "token_usage": {"input": null, "output": null, "cache_hit": null},
  "timing": {"ttft_ms": null, "total_ms": null},
  "thinking_summary": "Ran each deterministic verification command verbatim in Bash, capturing exact exit codes and stdout/stderr. Identified the critical C9 failure: all 41 tests pass but the Sprint 2 pytest plugin (test_plugin_exit.py deliberately records score=0.0) causes pytest_sessionfinish to override exit to 100, failing the [ EC = 0 ] check. Did not rationalize this away — exit 100 != 0, C9 FAIL per the calibration rule. Verified SN1 fix is in place (sprint-0[12]*.md glob in both contract and tasks.json). Read caching.py and batch.py fully for LLM-judge criteria C10/C11; both meet all stated conditions. SN3 checked all test files that import or reference anthropic — all calls are properly mocked. Rubric scored per dimension in isolation."
}
```
