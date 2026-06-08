# Sprint 03 Contract: Prompt caching and Batch API

## What I Will Build

Sprint 3 adds two Anthropic-specific optimisation paths to the Python library and extends the F6 thinking-block invariant to cover them. First, `AnthropicModel` (or a sibling helper in `src/trine_eval/models/`) will attach `cache_control: {"type": "ephemeral"}` breakpoints on the system prompt block, the tools block (when tools are provided), and a few-shot / golden-examples block (when provided) — without requiring callers to construct cache_control by hand. Second, a new `batch` module under `src/trine_eval/runner/` will submit a list of samples to Anthropic's `/v1/messages/batches` endpoint when `offline=True` is passed to the runner, poll for completion, and demultiplex results by `custom_id` back into the per-sample scoring flow. Batching and caching compose: batch requests carry the same cache_control breakpoints. The F6 byte-identical thinking-block invariant (proven for the streaming path in Sprint 1) is extended to the batch path with a new mock-based test.

## Success Criteria

Each criterion must be independently testable. Weights sum to 100%.

### Deterministic (code-verifiable)

1. **`cache_control` breakpoints appear on system prompt in outgoing request**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/models/test_caching.py -k test_system_prompt_cache_control -v --tb=short 2>&1 | tee /tmp/s03c1.txt && grep -q "PASSED" /tmp/s03c1.txt && echo PASS'
   ```
   `tests/models/test_caching.py` must contain `test_system_prompt_cache_control`. The test must: (a) mock `anthropic.Anthropic` so no real API calls are made, (b) call `AnthropicModel` (or a new `build_cached_request` / `apply_cache_control` helper from `trine_eval.models.caching`) with a system prompt string, and (c) inspect the outgoing `messages.create` call and assert that the request payload's `system` argument is either a list containing a block with `"cache_control": {"type": "ephemeral"}` or that a top-level `cache_control` field is present on the system block. PASS when exit code is 0 and output contains `PASSED`. [weight: 10%]

2. **`cache_control` breakpoints appear on tools block when tools are present**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/models/test_caching.py -k test_tools_cache_control -v --tb=short 2>&1 | tee /tmp/s03c2.txt && grep -q "PASSED" /tmp/s03c2.txt && echo PASS'
   ```
   `tests/models/test_caching.py` must contain `test_tools_cache_control`. The test must: (a) mock `anthropic.Anthropic`, (b) call the model/helper with a non-empty `tools` list, and (c) assert the outgoing `tools` argument has `"cache_control": {"type": "ephemeral"}` on its last element (the canonical Anthropic pattern is to attach the breakpoint to the last item in the `tools` array). PASS when exit code is 0 and output contains `PASSED`. [weight: 9%]

3. **`cache_control` breakpoints appear on few-shot examples block when provided**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/models/test_caching.py -k test_examples_cache_control -v --tb=short 2>&1 | tee /tmp/s03c3.txt && grep -q "PASSED" /tmp/s03c3.txt && echo PASS'
   ```
   `tests/models/test_caching.py` must contain `test_examples_cache_control`. The test must: (a) mock `anthropic.Anthropic`, (b) call the model/helper passing a `examples` list (few-shot / golden examples represented as message dicts), and (c) assert the last example message has `"cache_control": {"type": "ephemeral"}` on its final content block. PASS when exit code is 0 and output contains `PASSED`. [weight: 9%]

4. **Batch runner submits samples to `/v1/messages/batches` and demultiplexes results**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_submit_and_demux -v --tb=short 2>&1 | tee /tmp/s03c4.txt && grep -q "PASSED" /tmp/s03c4.txt && echo PASS'
   ```
   `tests/runner/test_batch.py` must contain `test_batch_submit_and_demux`. The test must: (a) mock `anthropic.Anthropic` (including `client.messages.batches.create` and `client.messages.batches.retrieve`), (b) call `trine_eval.runner.batch.run_batch(task, model)` or the `run(task, model, offline=True)` engine path with a 3-sample task, (c) simulate the batch reaching `ended` status on the first poll, (d) simulate `results()` returning per-request results keyed by `custom_id`, and (e) assert the returned `EvalLog` has `len(scores) == 3` (all samples demultiplexed). PASS when exit code is 0 and output contains `PASSED`. [weight: 14%]

5. **Batch runner polls until completion and handles `in_progress` → `ended` transition**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_polls_until_complete -v --tb=short 2>&1 | tee /tmp/s03c5.txt && grep -q "PASSED" /tmp/s03c5.txt && echo PASS'
   ```
   `tests/runner/test_batch.py` must contain `test_batch_polls_until_complete`. The test must: (a) mock `client.messages.batches.retrieve` to return `in_progress` on the first call and `ended` on the second, (b) assert `retrieve` was called at least twice (proving polling occurred), and (c) assert the final `EvalLog` reflects the demultiplexed results. PASS when exit code is 0 and output contains `PASSED`. [weight: 11%]

6. **Batch requests carry `cache_control` breakpoints (caching + batching compose)**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_carries_cache_control -v --tb=short 2>&1 | tee /tmp/s03c6.txt && grep -q "PASSED" /tmp/s03c6.txt && echo PASS'
   ```
   `tests/runner/test_batch.py` must contain `test_batch_carries_cache_control`. The test must: (a) mock `anthropic.Anthropic`, (b) call the batch runner with a task that includes a system prompt, (c) inspect the request body submitted to `batches.create` (the `requests` list), and (d) assert at least one request in the batch contains a system block with `"cache_control": {"type": "ephemeral"}`. PASS when exit code is 0 and output contains `PASSED`. [weight: 12%]

7. **F6 thinking-block round-trip preserved through the batch path (deterministic gate)**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_batch.py -k test_batch_thinking_round_trip -v --tb=short 2>&1 | tee /tmp/s03c7.txt && grep -q "thinking blocks preserved byte-identical" /tmp/s03c7.txt && grep -q "PASSED" /tmp/s03c7.txt && echo PASS'
   ```
   `tests/runner/test_batch.py` must contain `test_batch_thinking_round_trip`. The test must: (a) mock `anthropic.Anthropic` (including the batch endpoints), (b) construct a thinking block `{"type": "thinking", "thinking": "...", "signature": "sig-batch-001"}`, (c) simulate a batch result that returns a response containing that thinking block, (d) simulate a follow-up batch turn (multi-turn tool use) where the thinking block is echoed back, and (e) assert the thinking block in the follow-up batch request has `"signature" == "sig-batch-001"` — byte-identical to what was returned. The test must emit the literal phrase `thinking blocks preserved byte-identical` (e.g., via `print()`) so this gate's grep succeeds. PASS when exit code is 0 and both greps succeed. [weight: 8%]

8. **Full batch + caching test suite exits 0**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/models/test_caching.py tests/runner/test_batch.py -v --tb=short 2>&1 | tee /tmp/s03c8.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c8.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c8.txt && [ "$EC" = "0" ] && echo PASS || exit 1'
   ```
   All new test files from this sprint pass together with no failures or errors. This is a holistic green-light check. PASS when pytest exit code is 0, output contains `passed`, and no `FAILED` or `ERROR` lines appear. [weight: 6%]

9. **No regressions in existing runner and model tests**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/ tests/models/ -v --tb=short 2>&1 | tee /tmp/s03c9.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c9.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c9.txt && ( [ "$EC" = "0" ] || [ "$EC" = "100" ] ) && echo PASS || exit 1'
   ```
   All prior Sprint 1 and Sprint 2 tests under `tests/runner/` and `tests/models/` continue to pass. PASS when pytest exits 0 (or 100 — Sprint 2's pytest plugin deliberately overrides session exit to 100 when a `@pytest.mark.trine_eval` test records a score below threshold; the regression check accepts 100 because no genuine test failure prints `FAILED` or `ERROR`), output contains `passed`, and no `FAILED` or `ERROR` lines appear. [weight: 5%]

### LLM-as-judge (requires reading comprehension)

10. **`cache_control` helper API shape is clean and caller-friendly (G1 behavioral)**: read `src/trine_eval/models/caching.py` (or the relevant section of `src/trine_eval/models/anthropic.py` if the helper is inlined). The implementation must: (a) expose a function or method that accepts `system: str | None`, `tools: list | None`, and `examples: list[dict] | None` and returns a dict with `cache_control` breakpoints applied at all three positions where content is present; (b) NOT require callers to manually construct `{"cache_control": {"type": "ephemeral"}}` dicts — the helper encapsulates this; (c) produce `"cache_control": {"type": "ephemeral"}` (not `"transient"` or any other type) at each breakpoint position; (d) for the `examples` key specifically: the return dict contains `examples` as a library-internal key (the Anthropic `messages.create` API does not accept an `examples` parameter); the caller is responsible for popping this key and prepending the annotated example messages into the `messages` array before calling `messages.create` — the helper must NOT be designed so that callers expand its full return dict directly into `messages.create(**kwargs)`; this caller contract must be visible in the module docstring or function docstring. A helper that only handles system prompt and ignores tools/examples is FAIL. A helper that requires callers to build cache_control dicts is FAIL. A caller or test that passes `examples` directly via `**kwargs` expansion into `messages.create` is FAIL. [weight: 7%]

11. **Batch runner design is correct — `custom_id` mapping, polling, and `EvalLog` shape (G2 behavioral)**: read `src/trine_eval/runner/batch.py` (or wherever the batch path is implemented). The implementation must: (a) assign a unique `custom_id` to each sample before submission (e.g., `sample.id` or a UUID), (b) submit all samples in a single `batches.create` call (not one call per sample), (c) poll `batches.retrieve(batch_id)` on a loop checking `processing_status` for `"ended"` (or equivalent terminal status), (d) iterate the batch results and map each result back to the originating sample by matching `custom_id` → sample, and (e) return an `EvalLog` whose `scores` list is in the same length as the number of successfully demultiplexed samples. An implementation that calls `messages.create` per sample (the streaming path) rather than `batches.create` is FAIL. [weight: 9%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **Historical Phase 1 and Phase 2 prior-sprint contracts and evals are unmodified**: no file matching Phase-1 or prior Phase-2 sprint paths is modified on this branch. Verify by diffing all commits against the merge-base:
   ```
   bash -c 'BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~$(git rev-list --count HEAD)^); diff_out=$(git diff $BASE..HEAD -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" ".harness/contracts/phase-02/sprint-0[12]*.md" ".harness/contracts/phase-02/sprint-1*.md" ".harness/evals/phase-02/sprint-0[12]*.md" ".harness/evals/phase-02/sprint-1*.md" 2>/dev/null); [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" && exit 1)'
   ```
   PASS when exit code is 0 (diff is empty). This covers both Phase-1 root-level files and Phase-2 subdirectory files under `.harness/contracts/phase-02/` and `.harness/evals/phase-02/`. The Phase-2 patterns use `sprint-0[12]*.md` (not `sprint-0[1-9]*.md`) to exclude the current sprint-03 contract from the immutability check.

2. **No forbidden packages imported or declared**: the strings `langgraph`, `ragas`, `pgvector`, and `fastapi` must not appear in `pyproject.toml`, `src/trine_eval/**/*.py`, or `tests/**/*.py`. Verify via:
   ```
   bash -c 'git grep -rn --count -E "langgraph|ragas|pgvector|fastapi" pyproject.toml src/ tests/ 2>/dev/null | grep -v "^Binary" | grep -v ":0$" && echo FAIL && exit 1 || echo PASS'
   ```
   PASS when the command exits 0 and prints `PASS`.

3. **No real Anthropic API calls in tests**: no test under `tests/` calls `anthropic.Anthropic()` or `client.messages.batches.create` without mocking (i.e., without a `unittest.mock.patch` or `pytest-mock` fixture wrapping the call). The Evaluator must read the key test source files (`tests/models/test_caching.py`, `tests/runner/test_batch.py`, and any other file that imports `anthropic`) and verify that every `anthropic.Anthropic(...)` instantiation and every `batches.create` call is enclosed in a `mocker.patch(...)` block or a `unittest.mock.patch(...)` context manager. A bare `anthropic.Anthropic()` call at module level or in a test body without a surrounding patch is FAIL. PASS when no unguarded `anthropic.Anthropic()` instantiation is found in test source files.

## Reference Solutions

**Criterion C1–C3 — `cache_control` helper API shape (LLM-judge anchor for C10):**

A correct `src/trine_eval/models/caching.py` implementation:

```python
# src/trine_eval/models/caching.py
from __future__ import annotations
from typing import Any

EPHEMERAL = {"type": "ephemeral"}


def apply_cache_control(
    *,
    system: str | None = None,
    tools: list[dict[str, Any]] | None = None,
    examples: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Build cache_control-annotated kwargs for messages.create.

    Breakpoints are placed at:
      1. The system prompt block (when present)
      2. The last tool in the tools array (when present)
      3. The last content block of the last example message (when present)

    Returns a dict with keys:
      - "system": list[dict]   — ready for `messages.create(system=...)`
      - "tools":  list[dict]   — ready for `messages.create(tools=...)`
      - "examples": list[dict] — LIBRARY-INTERNAL KEY. The Anthropic
        messages.create API does NOT accept an "examples" parameter.
        Callers must pop this key and prepend the annotated example
        messages to the messages array before calling messages.create.
        See caller pattern below.

    Caller-side usage (the "examples" key must be handled separately):

        cached = apply_cache_control(system=sys, tools=tools, examples=exs)
        example_messages = cached.pop("examples", [])
        user_messages = [{"role": "user", "content": user_prompt}]
        messages = example_messages + user_messages
        response = client.messages.create(messages=messages, **cached)
    """
    kwargs: dict[str, Any] = {}

    if system is not None:
        kwargs["system"] = [
            {"type": "text", "text": system, "cache_control": EPHEMERAL}
        ]

    if tools:
        annotated_tools = list(tools)
        annotated_tools[-1] = {**annotated_tools[-1], "cache_control": EPHEMERAL}
        kwargs["tools"] = annotated_tools

    if examples:
        annotated_examples = list(examples)
        last = dict(annotated_examples[-1])
        content = list(last.get("content", []))
        if content:
            content[-1] = {**content[-1], "cache_control": EPHEMERAL}
            last["content"] = content
        annotated_examples[-1] = last
        kwargs["examples"] = annotated_examples

    return kwargs
```

PASS: helper present, all three breakpoints applied when respective arguments are non-empty, `"ephemeral"` type used, caller does not build cache_control by hand, `examples` key is documented as a library-internal key requiring pop-and-prepend before `messages.create`. FAIL: function missing, only one or two positions handled, wrong type string, requires caller to build dicts, or caller passes `examples` directly as `**kwargs` to `messages.create`.

**Criterion C4–C6 — batch runner design (LLM-judge anchor for C11):**

A correct `src/trine_eval/runner/batch.py` shape:

```python
# src/trine_eval/runner/batch.py
import time
from typing import Any

from trine_eval.core.log import EvalLog
from trine_eval.core.sample import Sample
from trine_eval.core.task import Task


def run_batch(
    task: Task,
    model: Any,
    *,
    poll_interval: float = 5.0,
    scorer: Any | None = None,
) -> EvalLog:
    """Submit task samples as a message batch and return demultiplexed EvalLog."""
    client = model._anthropic_client

    # Build one request per sample, assigning custom_id = sample.id
    requests = []
    for sample in task.dataset:
        cached_kwargs = _build_request_body(model, sample)
        requests.append({
            "custom_id": sample.id,
            "params": {
                "model": model.model,
                "max_tokens": 1024,
                **cached_kwargs,
            },
        })

    # Single batches.create call for ALL samples
    batch = client.messages.batches.create(requests=requests)

    # Poll until terminal status
    while batch.processing_status not in ("ended", "errored", "expired", "cancelled"):
        time.sleep(poll_interval)
        batch = client.messages.batches.retrieve(batch.id)

    # Demultiplex results by custom_id → sample
    id_to_sample = {s.id: s for s in task.dataset}
    scores = []
    completed_samples = []
    score_fn = scorer or _default_score

    for result in client.messages.batches.results(batch.id):
        sample = id_to_sample.get(result.custom_id)
        if sample and result.result.type == "succeeded":
            answer = _extract_text(result.result.message.content)
            scores.append(score_fn(sample, answer))
            completed_samples.append(sample)

    from datetime import datetime, timezone
    return EvalLog(
        task_name=task.name,
        samples=completed_samples,
        scores=scores,
        model=model.model,
        timestamp=datetime.now(timezone.utc),
        aggregate={"accuracy": sum(s.value for s in scores) / len(scores)} if scores else {},
        metadata={"batch_id": batch.id, "via": "batch-api"},
    )
```

PASS: `batches.create` called once with all samples; `custom_id = sample.id`; polling loop checks `processing_status`; results demultiplexed by `custom_id`; returns `EvalLog`. FAIL: calls `messages.create` per sample, or calls `batches.create` once per sample, or does not poll, or does not map by `custom_id`.

**Criterion C7 — thinking-block round-trip through batch (deterministic anchor):**

The test must emit the literal phrase `thinking blocks preserved byte-identical` to satisfy the grep gate. Recommended pattern:

```python
# tests/runner/test_batch.py
def test_batch_thinking_round_trip():
    thinking_block = {
        "type": "thinking",
        "thinking": "batch reasoning step...",
        "signature": "sig-batch-001",
    }
    # ... setup mock batch results returning this thinking block ...
    # ... simulate follow-up batch turn that echoes it back ...
    assert any(
        b.get("type") == "thinking" and b.get("signature") == "sig-batch-001"
        for b in follow_up_request_content
    ), "thinking block not preserved"
    print("thinking blocks preserved byte-identical")  # required phrase for C7 gate
```

PASS: thinking block echoed verbatim in follow-up batch request, `signature` field byte-identical, phrase emitted. FAIL: signature field stripped, not checked, or phrase absent.

## Out of Scope

- **v0.1 ship-gate numeric targets** (Batch run cost ≤ 55% of streaming; cache-read rate ≥ 85% on system prompt): these land in Sprint 6 calibration. Sprint 3 ships the mechanisms only.
- **LLM-as-judge infrastructure** (`src/trine_eval/judge/`): Sprint 4.
- **Docker sandbox** (`src/trine_eval/sandbox/`): Sprint 5.
- **SWE-bench Verified adapter** (`src/trine_eval/benchmarks/`): Sprint 6.
- **Real Anthropic API calls**: all tests mock the Anthropic client. No network dependency in any test.
- **`cache_control` on image/document blocks**: Sprint 3 covers text system prompt, tools, and text few-shot examples only. Binary-media caching is deferred.
- **Async batch runner**: the batch path may be synchronous (`time.sleep` polling) in Sprint 3. Async polling is a future optimisation.
- **`uv run ruff check` and `uv run mypy --strict src` clean**: not gated in this sprint (new modules are added quickly; strict typing enforcement continues from Sprint 2's baseline). Code must not introduce syntax errors.
- **Meta-harness Batch API toggle** (`config.batch.enabled`): this is the harness-level eval batching — Sprint 3 is about the Python library's Batch API, not the meta-harness's own batch toggle.
- **`cache_control` breakpoints on message turns (conversation history)**: only system, tools, and examples receive breakpoints in Sprint 3. Per-message-turn caching is a Sprint 6+ concern.

## Technical Notes

- **New files expected.** Sprint 3 will create: `src/trine_eval/models/caching.py` (the `apply_cache_control` helper), `src/trine_eval/runner/batch.py` (the batch submission + polling + demultiplexing), `tests/models/test_caching.py`, and `tests/runner/test_batch.py`. It may also extend `AnthropicModel.create` to accept `system`, `tools`, and `examples` kwargs that are automatically cached, but the caching logic must live in `caching.py` — not inlined into `anthropic.py` — to keep `AnthropicModel` small.

- **`cache_control` wire format.** Anthropic's API expects `cache_control` as a dict `{"type": "ephemeral"}`. For the system prompt, the value of the `system` parameter must be a list of content blocks: `[{"type": "text", "text": "...", "cache_control": {"type": "ephemeral"}}]`. For tools, `cache_control` is a top-level key on the tool dict. For few-shot examples, `cache_control` is placed on the last content block of the last example message. The C1, C2, C3 tests must assert these exact structural positions.

- **`examples` key is library-internal — not a `messages.create` parameter.** The Anthropic SDK's `messages.create` does not accept an `examples` keyword argument. `apply_cache_control` returns `"examples"` as a convenience key for the caller; the caller must pop it and prepend the annotated messages to the `messages` list before calling `messages.create`. The canonical pattern is: `example_messages = cached.pop("examples", []); messages = example_messages + user_messages; client.messages.create(messages=messages, **cached)`. Tests must follow this pattern — passing `**apply_cache_control(...)` directly to `messages.create` without popping `examples` is incorrect and will cause an SDK error with a real client.

- **Batch API mock shape.** The `anthropic` SDK's batch objects have: `batch.id` (string), `batch.processing_status` (`"in_progress" | "ended" | "errored" | "expired" | "cancelled"`), and `client.messages.batches.results(batch_id)` which yields result objects with `result.custom_id` and `result.result.type == "succeeded"`. The mock must reproduce this shape. If the SDK version installed does not expose `messages.batches`, mock the entire `anthropic.Anthropic` client.

- **F6 through batch — scope clarification.** Sprint 1 proved byte-identical thinking-block round-trip through the streaming/tool-use path (test `test_thinking_block_round_trip` in `tests/models/test_anthropic.py`). Sprint 3's C7 proves the same invariant through the batch path: a thinking block returned in a batch result must appear verbatim in a follow-up batch request. The mechanism for this is the same as streaming — the caller echoes the block unchanged — but the test must go through the batch machinery to count as F6 enforcement on the batch path.

- **`EvalLog.metadata` for batch runs.** Batch results should include `{"batch_id": "<id>", "via": "batch-api"}` in `EvalLog.metadata` to distinguish batch logs from streaming logs. This is useful for Sprint 6's cost-reporting logic. C4 may assert this key exists, but it is advisory — the graded assertion is the `len(scores) == 3` demultiplexing check.

- **`custom_id` collisions.** If `sample.id` values are not unique within a task, `custom_id` collisions will produce incorrect demultiplexing. The batch runner should not validate uniqueness (that is a Task validation concern), but the test fixture must use distinct sample IDs.

- **Polling sleep in tests.** Tests must not call real `time.sleep` — they should patch `time.sleep` or use `poll_interval=0` to make polling instant. The C5 test verifies that `retrieve` was called at least twice, which is sufficient to prove the polling loop exists.

- **`pyproject.toml` changes.** No new runtime dependencies are required for Sprint 3 — `anthropic>=0.40` (already declared) includes the Batch API client. No `pyproject.toml` entry needs to be added or changed.

- **Behavioral weight compliance.** Criteria C1–C9 are behavioral (they test API behavior and runtime correctness). C10 and C11 are behavioral LLM-judge criteria. Only SN1–SN3 gates and the structural aspects of the helper API shape are structural. Total behavioral weight: C1(10) + C2(9) + C3(9) + C4(14) + C5(11) + C6(12) + C7(8) + C8(6) + C9(5) + C10(7) + C11(9) = 100%. All criteria are behavioral by rubric_dimension.

---

**Weight verification:** C1(10) + C2(9) + C3(9) + C4(14) + C5(11) + C6(12) + C7(8) + C8(6) + C9(5) + C10(7) + C11(9) = **100%**. Confirmed.

**Behavioral weight:** all 11 success criteria are behavioral (≥60% threshold met at 100%).

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/phase-02/sprint-03.tasks.json` is emitted with one JSON entry per criterion. Task IDs: `s03-c1` through `s03-c11` for success criteria, `s03-sn1`, `s03-sn2`, `s03-sn3` for Should-NOT gates. Total entries: 11 success + 3 gate = 14. See `rules/harness-conventions.md` for the schema.

## Evaluator Review

**Status: NEEDS REVISION**

**Round: 1**

### Strengths

- Weight arithmetic is correct (C1-C11 sum to 100%). Confirmed.
- Behavioral coverage is complete: all 11 success criteria probe runtime correctness or API correctness; the ≥60% threshold is met at 100%.
- C1-C7 individual test greps use `grep -q "PASSED"` (uppercase) which tightly constrains the signal to the per-test pass marker — not easily spoofed by partial results.
- C7's dual-grep design (`grep -q "thinking blocks preserved byte-identical"` AND `grep -q "PASSED"`) prevents a false PASS when the phrase appears in a traceback but the test itself fails. The command scopes to `tests/runner/test_batch.py` only, so the pre-existing occurrence of the phrase in `tests/models/test_anthropic.py` cannot contaminate the C7 output.
- SN2 (forbidden packages) command logic is correct: the `|| echo PASS` is reached only when the `git grep ... && echo FAIL && exit 1` pipeline exits non-zero (no matches), which correctly signals no forbidden packages. Verified empirically.
- SN3 now explicitly names `batches.create` alongside `anthropic.Anthropic()` — an improvement over Sprint 2 where only the constructor was called out.
- C4 and C5 describe concrete mock shapes for `batches.create` / `batches.retrieve` polling — the implementer cannot misinterpret the expected behavior.
- Technical Notes section provides the Batch API mock object shape (`batch.id`, `batch.processing_status`, `results()`) which anchors the test fixture.

### Issues

1. **C8 verification_command: `| tee` masks pytest exit code — BLOCKING**

   C8's command is:
   ```
   bash -c 'uv run pytest tests/models/test_caching.py tests/runner/test_batch.py -v --tb=short 2>&1 | tee /tmp/s03c8.txt && grep -E "passed" /tmp/s03c8.txt && echo PASS'
   ```
   In bash, a pipeline's exit code is the exit code of the last command (`tee`), not `pytest`. Since `tee` exits 0 whenever it can write to the file, a pytest failure with exit code 1 is silently ignored. Verified empirically: `bash -c 'false 2>&1 | tee /tmp/x.txt; echo $?'` prints `0`. Consequence: if some tests in the two files pass and others fail, pytest exits 1, `tee` exits 0, `grep -E "passed"` matches the "X passed, Y failed" summary line (confirmed: the summary line "1 failed, 1 passed" contains "passed"), and `echo PASS` fires — a false PASS with 11% of the sprint's weight at stake. The C8 command has no `! grep -qE "FAILED|ERROR"` guard.

   **Fix:** Use `${PIPESTATUS[0]}` to capture pytest's exit code before `tee` swallows it, and add explicit failure guards:
   ```
   bash -c 'uv run pytest tests/models/test_caching.py tests/runner/test_batch.py -v --tb=short 2>&1 | tee /tmp/s03c8.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c8.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c8.txt && [ "$EC" = "0" ] && echo PASS || exit 1'
   ```

2. **SN1 glob does not cover Phase-2 contracts and evals — BLOCKING**

   SN1's git-diff glob patterns are:
   ```
   ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md"
   ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md"
   ```
   These match `.harness/contracts/sprint-01.md` (Phase-1 files at the root of `.harness/contracts/`) but do NOT match `.harness/contracts/phase-02/sprint-01.md` or `.harness/evals/phase-02/sprint-01-r1.md`. Both Phase-2 Sprint 1 and Sprint 2 contracts and evals live under `.harness/contracts/phase-02/` and `.harness/evals/phase-02/` — confirmed by directory inspection. A Generator that accidentally modifies `.harness/contracts/phase-02/sprint-02.md` (Phase-2 Sprint 2's finalized contract) would NOT be caught by SN1.

   **Fix:** Add Phase-2 path patterns to the git-diff glob arguments:
   ```
   bash -c 'BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~$(git rev-list --count HEAD)^); diff_out=$(git diff $BASE..HEAD -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" ".harness/contracts/phase-02/sprint-0[1-9]*.md" ".harness/contracts/phase-02/sprint-1*.md" ".harness/evals/phase-02/sprint-0[1-9]*.md" ".harness/evals/phase-02/sprint-1*.md" 2>/dev/null); [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" && exit 1)'
   ```

3. **Reference solution uses a fictional `examples` kwarg for `messages.create` — BLOCKING for C10 correctness**

   The C1-C3 reference solution (`apply_cache_control`) returns `kwargs["examples"] = annotated_examples`. The Anthropic `messages.create` API does not accept an `examples` parameter. Few-shot examples in the Anthropic API are embedded as regular `messages` entries (alternating user/assistant turns), not via a dedicated `examples` kwarg. If the Generator follows the reference solution verbatim and the caller does `client.messages.create(**kwargs)`, the API call will fail at runtime with an unexpected-keyword-argument error (or be silently ignored by the mock, producing a test that passes but is functionally broken).

   This creates an ambiguity for C10's LLM-judge: the criterion says the helper "returns a dict suitable for **kwargs expansion into messages.create" — but the reference solution contradicts this for the `examples` key. Two independent evaluators would disagree: one would FAIL (the `examples` kwarg is invalid), the other would PASS (the structural annotation logic is correct). The criterion is unresolvable without fixing the reference solution.

   **Fix (two options):**
   - Option A: Document explicitly that `examples` is a library-internal key — the caller does NOT expand it directly into `messages.create` but instead merges the annotated example messages into the `messages` array as user/assistant turns. Update the reference solution to show how the caller uses the helper output, not just what the helper returns.
   - Option B: Remove `examples` from `apply_cache_control`'s return dict and have the helper annotate the examples in-place within the `messages` list. Rename the return key to `messages_prefix` and document that it is prepended to the user messages before the `messages.create` call.

4. **C8 `grep -E "passed"` is weaker than C1-C7's `grep -q "PASSED"` — MODERATE (compounding Issue 1)**

   C1-C7 use `grep -q "PASSED"` (uppercase, exact per-test line marker) which is hard to spoof. C8 uses `grep -E "passed"` (lowercase) which matches the summary line "X passed, Y failed" — meaning a run with 2 passing and 4 failing tests would satisfy the grep. Combined with the `| tee` exit-code masking in Issue 1, this makes C8 incapable of distinguishing a partial-pass run from an all-pass run.

   **Fix:** Change C8's grep to `! grep -qE "FAILED|ERROR"` in addition to the exit-code fix from Issue 1 (already included in the Issue 1 fix command above).

5. **C9 exit-code masking — LOW (partially mitigated)**

   C9 has the same `| tee` masking as C8, but the `! grep -qE "FAILED|ERROR"` guard catches the most common failure mode (any individual test failure prints "FAILED" in the summary). The remaining gap is a pytest crash mode that exits non-zero without printing "FAILED" (e.g., internal error or collection crash that prints only "ERROR" — which IS caught). Practically, the guard is sufficient for the 5% weight criterion, but consistency with Issue 1's fix pattern is recommended.

   **Fix (recommended, not blocking):** Apply the same `${PIPESTATUS[0]}` pattern as Issue 1:
   ```
   bash -c 'uv run pytest tests/runner/ tests/models/ -v --tb=short 2>&1 | tee /tmp/s03c9.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c9.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c9.txt && [ "$EC" = "0" ] && echo PASS || exit 1'
   ```

### Notes

- The `| tee` masking pattern appears in C1-C7 as well. It is not blocking in those criteria because the `grep -q "PASSED"` guard is a strong signal (pytest only prints `PASSED` for a specific test if it genuinely passed, even when other tests fail). C8 and C9 use the weaker lowercase `passed` match and thus need the exit-code fix.
- C10's behavioral classification is borderline: the LLM-judge verifies it by reading source code (a structural activity), but the FAIL conditions check what the function produces at runtime (behavioral). At 100% behavioral coverage, the ≥60% rule is met regardless. The classification is defensible.
- The `ruff`/`mypy --strict` exclusion from gating is justified for Sprint 3 given the rapid new-module pace. The Technical Notes correctly note that no syntax errors may be introduced, and Sprint 2's baseline continues to apply to existing code.
- The three blocking issues (C8 masking, SN1 glob gap, reference solution `examples` kwarg) must all be resolved before APPROVAL. The C8 and C9 fixes are mechanical. The reference solution fix requires a design decision about how `examples` maps to the Anthropic API — Option A (documenting the caller's responsibility) is the lower-risk path.

## Revision Notes (Round 1 → Round 2)

- **Issue 1 (C8 exit-code masking):** Replaced C8's `| tee ... && grep ... && echo PASS` command with `${PIPESTATUS[0]}` capture, added `! grep -qE "FAILED|ERROR"` guard, and gated `echo PASS` on `[ "$EC" = "0" ]`. This prevents `tee`'s exit-0 from masking a pytest failure. The holistic-pass intent is preserved.
- **Issue 2 (SN1 glob):** Added Phase-2 path patterns `.harness/contracts/phase-02/sprint-0[1-9]*.md`, `.harness/contracts/phase-02/sprint-1*.md`, `.harness/evals/phase-02/sprint-0[1-9]*.md`, and `.harness/evals/phase-02/sprint-1*.md` to the SN1 `git diff` glob arguments. The criterion description was updated to mention both Phase-1 root-level files and Phase-2 subdirectory files. All prior Phase-2 sprint contracts/evals (Sprint 1 and Sprint 2) are now protected.
- **Issue 3 (Reference solution `examples` kwarg):** Applied Option A. The `apply_cache_control` function signature and `examples` return key are unchanged; the function docstring now explicitly documents that `examples` is a library-internal key, that `messages.create` does not accept it, and shows the 4-line caller-side pop-and-prepend pattern. The Reference Solution PASS/FAIL rubric was updated to require this documented caller contract. C10's LLM-judge criterion was updated to require (d): the `examples` key is library-internal, callers pop it and prepend to the `messages` array, direct `**kwargs` expansion into `messages.create` is FAIL. A new Technical Note was added explaining the `examples` caller contract with the canonical code pattern.
- **Advisory Issue 4 (C8 `grep -E "passed"` weakness):** Fixed as part of the C8 rewrite above. The new command includes both `! grep -qE "FAILED|ERROR"` and the exit-code check, making the holistic gate as tight as the individual per-test greps.
- **Advisory Issue 5 (C9 same pattern):** Applied the same `${PIPESTATUS[0]}` pattern to C9 for consistency. C9 already had `! grep -qE "FAILED|ERROR"` so this brings it fully in line with the Issue 1 fix.

## Evaluator Review — Round 2

**Status: NEEDS REVISION**

**Round: 2**

### Verification of Round 1 fixes

- **Issue 1 (C8 masking): VERIFIED**

  C8 (line 57) now reads:
  ```
  bash -c 'uv run pytest tests/models/test_caching.py tests/runner/test_batch.py -v --tb=short 2>&1 | tee /tmp/s03c8.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c8.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c8.txt && [ "$EC" = "0" ] && echo PASS || exit 1'
  ```
  All three guard elements present: `EC=${PIPESTATUS[0]}` (captures pytest exit before tee swallows it), `! grep -qE "FAILED|ERROR"` (rejects mixed-pass runs), `[ "$EC" = "0" ]` (explicit exit-code gate). Empirically verified the shape exits 1 when given a FAILED+passed output and exits 0 on clean pass.

- **Issue 2 (SN1 glob): NOT VERIFIED — NEW BLOCKING FLAW**

  The four Phase-2 patterns were added as required:
  - `.harness/contracts/phase-02/sprint-0[1-9]*.md`
  - `.harness/contracts/phase-02/sprint-1*.md`
  - `.harness/evals/phase-02/sprint-0[1-9]*.md`
  - `.harness/evals/phase-02/sprint-1*.md`

  However, the glob `sprint-0[1-9]*.md` matches `sprint-03.md` — the contract file being created this sprint. Running SN1 empirically against the current branch exits **1 (FAIL)** because `.harness/contracts/phase-02/sprint-03.md` is a new file on this branch and the diff includes it in the output. The SN1 gate would block every valid Generator that correctly creates the sprint-03 contract file.

  Empirical result (verified via Bash):
  ```
  FAIL
  diff --git a/.harness/contracts/phase-02/sprint-03.md b/.harness/contracts/phase-02/sprint-03.md
  new file mode 100644
  ... [full contract file shown as diff]
  ```
  Exit code: 1.

  The fix must either (a) scope the Phase-2 patterns to only prior sprints (e.g., `sprint-0[12]*.md` for Sprint 3; `sprint-0[123]*.md` for Sprint 4), or (b) use `sprint-0[1-9]*.md` but exclude the current sprint's contract by adding a path exclude (`:(exclude).harness/contracts/phase-02/sprint-03*`), or (c) split the check into two diffs — one for Phase-1 files and one for Phase-2 files, with the Phase-2 check only covering directories that contain finalized prior-sprint artefacts (i.e., exclude the current sprint number).

- **Issue 3 (Reference solution `examples` kwarg): VERIFIED**

  Docstring at lines 122–126 explicitly states: `"examples": list[dict] — LIBRARY-INTERNAL KEY. The Anthropic messages.create API does NOT accept an "examples" parameter. Callers must pop this key and prepend the annotated example messages to the messages array before calling messages.create.`

  The 4-line caller pop-and-prepend pattern is shown at lines 130–134:
  ```python
  cached = apply_cache_control(system=sys, tools=tools, examples=exs)
  example_messages = cached.pop("examples", [])
  messages = example_messages + user_messages
  response = client.messages.create(messages=messages, **cached)
  ```

  C10(d) at line 69 makes direct `**kwargs` expansion into `messages.create` a FAIL: "the helper must NOT be designed so that callers expand its full return dict directly into `messages.create(**kwargs)`; this caller contract must be visible in the module docstring or function docstring."

  Technical Note at line 277 repeats the canonical code pattern. Two independent evaluators would agree on C10 verdicts. VERIFIED.

- **Issue 4 (C8 grep weakness): VERIFIED**

  Covered by the C8 rewrite. The revised command includes `! grep -qE "FAILED|ERROR"` which rejects any run where individual tests fail. The shape test confirms this correctly rejects mixed-pass output.

- **Issue 5 (C9 pattern): VERIFIED**

  C9 (line 63) now reads:
  ```
  bash -c 'uv run pytest tests/runner/ tests/models/ -v --tb=short 2>&1 | tee /tmp/s03c9.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s03c9.txt && ! grep -qE "FAILED|ERROR" /tmp/s03c9.txt && [ "$EC" = "0" ] && echo PASS || exit 1'
  ```
  Same three-guard pattern as C8. VERIFIED.

### Empirical checks

**SN1 empirical run (current branch against merge-base):**
```
$ BASE=8617c2f; git diff $BASE..HEAD -- "[patterns]"
FAIL
diff --git a/.harness/contracts/phase-02/sprint-03.md b/.harness/contracts/phase-02/sprint-03.md
new file mode 100644
...
```
Exit code: 1. SN1 FAILS on the current branch because sprint-03.md itself matches the newly-added Phase-2 glob.

**C8/C9 shape sanity check (FAILED+passed scenario):**
Input to shape check: file containing `"FAILED test1"` and `"1 failed, 1 passed"`, `EC=1`.
`grep -E "passed"` matches (grep exits 0), `! grep -qE "FAILED|ERROR"` fails (grep finds FAILED), compound `&&` chain breaks, `|| exit 1` fires.
Exit code: 1 (correct — does NOT print PASS on a partially-failing run).

**C8/C9 shape sanity check (all-pass scenario):**
Input: file containing `"test1 PASSED"` and `"2 passed, 0 failed"`, `EC=0`.
All guards pass. Output: `PASS`. Exit code: 0 (correct).

**Weight arithmetic:** C1(10)+C2(9)+C3(9)+C4(14)+C5(11)+C6(12)+C7(8)+C8(6)+C9(5)+C10(7)+C11(9) = 100%. Confirmed. Behavioral coverage: all 11 criteria behavioral = 100% ≥ 60% threshold. Confirmed.

### Remaining concerns

SN1 glob over-captures current sprint — **blocking**. The `sprint-0[1-9]*.md` pattern in the Phase-2 glob matches the sprint-03 contract file being created this sprint. Any Generator that correctly creates `.harness/contracts/phase-02/sprint-03.md` (as required by the harness workflow) will trigger SN1 FAIL. This is a self-defeating gate.

Recommended fix — change the Phase-2 contract pattern to exclude the current sprint number. For Sprint 3 specifically, change:
```
".harness/contracts/phase-02/sprint-0[1-9]*.md"
```
to:
```
".harness/contracts/phase-02/sprint-0[12]*.md"
```
(covering only sprint-01 and sprint-02, which are finalized). Similarly the eval pattern: `.harness/evals/phase-02/sprint-0[12]*.md`. For Sprint 4, the pattern advances to `sprint-0[123]*.md`, etc. Alternatively, use a git pathspec exclude: `:(exclude).harness/contracts/phase-02/sprint-03*`.

No other blocking issues found.

### Final verdict

**NEEDS REVISION** — SN1 glob introduced in Round 2 matches the current sprint's own contract file, causing SN1 to emit FAIL on every correct Generator build. All five Round 1 issues are otherwise addressed; this single new flaw must be resolved before APPROVAL.
