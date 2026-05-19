# Sprint 02 Contract: Runner, replayable logs, pytest plugin, observability

## What I Will Build

The second sprint wires together the Python library's execution layer on top of Sprint 1's primitives: an async runner with four hard caps (`max_concurrency`, `token_limit`, `time_limit`, `cost_limit`); binary + JSON replayable log format using `msgpack`; deterministic seed utilities and version-capture; OpenTelemetry spans exported to a self-hosted Langfuse instance via `ops/langfuse-compose.yaml`; a pytest plugin that exits with code 100 when a trine-eval task scores below threshold; a `trine-eval score --log` rescoring CLI subcommand and a `trine-eval report` metric subcommand; and a documentation criterion that records the `sprint-state.json` `phase-02-N` key convention in `rules/harness-conventions.md`.

## Success Criteria

Each criterion must be independently testable. Weights sum to 100%.

### Deterministic (code-verifiable)

1. **Async runner returns an `EvalLog` for a no-op task**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_engine.py -k test_run_noop -v --tb=short 2>&1 | tee /tmp/s02c1.txt && grep -q "PASSED" /tmp/s02c1.txt && echo PASS'
   ```
   The test `test_run_noop` must import `asyncio` and `trine_eval.runner.engine.run`, create a minimal `Task` (one `Sample`, an identity solver, an exact-match scorer), call `asyncio.run(run(task, model))` with a stub/mock model that returns a fixed string, and assert the return value is an `EvalLog` instance with `len(scores) == 1`. PASS when exit code is 0 and output contains `PASSED`. [weight: 10%]

2. **Hard-cap enforcement — all four caps fire correctly**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_caps.py -v --tb=short 2>&1 | tee /tmp/s02c2.txt && grep -q "PASSED" /tmp/s02c2.txt && grep -E "4 passed|[5-9] passed|[1-9][0-9]+ passed" /tmp/s02c2.txt && echo PASS'
   ```
   `tests/runner/test_caps.py` must contain at least four independent tests, one per cap type. Three tests — for `token_limit`, `time_limit`, and `cost_limit` — must use a mock or fake task/model that drives the cap to trigger before all samples complete and assert the returned `EvalLog.metadata` contains a `"cap_hit"` key whose value names the triggered cap (e.g., `"token_limit"`, `"time_limit"`, `"cost_limit"`). The fourth test — for `max_concurrency` — must verify that no more than the configured number of tasks run concurrently at any instant (e.g., via a counter of simultaneous in-flight samples) without asserting `cap_hit`, because `max_concurrency` only throttles parallelism and does NOT cause early abort or set `cap_hit`. PASS when exit code is 0, output contains `PASSED`, and the grep for `4 passed` (or more) succeeds. [weight: 16%]

3. **Log round-trip — JSON and msgpack**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_logformat.py -v --tb=short 2>&1 | tee /tmp/s02c3.txt && grep -q "PASSED" /tmp/s02c3.txt && grep -E "2 passed|[3-9] passed|[1-9][0-9]+ passed" /tmp/s02c3.txt && echo PASS'
   ```
   `tests/runner/test_logformat.py` must contain at least two tests: `test_json_round_trip` and `test_msgpack_round_trip`. Each constructs a non-trivial `EvalLog` (at least 2 samples, 2 scores, non-empty `aggregate`), saves it with `trine_eval.runner.logformat.save(log, path, format=<fmt>)`, loads it back with `trine_eval.runner.logformat.load(path)`, and asserts `loaded == original` (Pydantic model equality). PASS when exit code is 0, output contains `PASSED`, and at least 2 tests passed. [weight: 12%]

4. **pytest plugin exits 100 on failing trine-eval test**: running the following chain exits 0 and prints `PLUGIN_OK`:
   ```
   bash -c 'uv run pytest tests/runner/test_plugin_exit.py --tb=short 2>&1; CODE=$?; [ "$CODE" = "100" ] && echo PLUGIN_OK || (echo "Got exit $CODE expected 100" && exit 1)'
   ```
   `tests/runner/test_plugin_exit.py` must use `trine_eval.pytest_plugin` (registered via `conftest.py` or `pytest11` entry point) and contain a test that deliberately causes a trine-eval score below threshold (e.g., score 0.0 with default threshold 1.0), triggering the exit-100 behaviour. The surrounding shell chain checks the exit code — `CODE=100` prints `PLUGIN_OK`. PASS when the entire chain exits 0 and prints `PLUGIN_OK`. [weight: 12%]

5. **`trine-eval score --log <path> --scorer <name>` rescores without re-running model**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_rescore_cli.py -v --tb=short 2>&1 | tee /tmp/s02c5.txt && grep -q "PASSED" /tmp/s02c5.txt && echo PASS'
   ```
   `tests/runner/test_rescore_cli.py` must: (a) save a fixture `EvalLog` containing pre-cached model responses to a temp file, (b) invoke `trine-eval score --log <tmpfile> --scorer exact_match` via `subprocess.run(["uv", "run", "trine-eval", "score", "--log", tmpfile, "--scorer", "exact_match"])` and assert exit code 0, (c) assert stdout contains a score value (e.g., `"score:"` or `"accuracy:"`), and (d) confirm no real Anthropic API call was made (monkeypatch anthropic client or assert the mock was never called). PASS when exit code is 0 and output contains `PASSED`. [weight: 10%]

6. **`trine-eval report <log>` prints token-efficiency metrics**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/runner/test_report_cli.py -v --tb=short 2>&1 | tee /tmp/s02c6.txt && grep -q "PASSED" /tmp/s02c6.txt && echo PASS'
   ```
   `tests/runner/test_report_cli.py` must call `trine-eval report <fixture_log_path>` via subprocess and assert (a) exit code 0, (b) stdout contains `accuracy_per_dollar` or `accuracy-per-dollar` (case-insensitive), and (c) stdout contains `success_per_1k_tokens` or `success-per-1k-tokens` (case-insensitive). PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

7. **OTel + Langfuse wiring composes without errors**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/observability/test_otel.py -v --tb=short 2>&1 | tee /tmp/s02c7.txt && grep -q "PASSED" /tmp/s02c7.txt && echo PASS'
   ```
   `tests/observability/test_otel.py` must: (a) import `trine_eval.observability.otel` and call `init_tracer(exporter="noop")` without raising; (b) start and end a span via the returned tracer object; (c) import `trine_eval.observability.langfuse` and call `get_langfuse_client(public_key="pk-test", secret_key="sk-test", host="http://localhost:3000")` without network calls — the function should return a client object or stub when Langfuse is not reachable (test must mock network calls or use a local-only stub path). PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

8. **`ops/langfuse-compose.yaml` is valid Docker Compose syntax (or YAML at minimum)**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'python -c "import sys, yaml; d=yaml.safe_load(open(\"ops/langfuse-compose.yaml\")); sys.exit(0 if isinstance(d, dict) and \"services\" in d else 1)" && echo PASS'
   ```
   The file `ops/langfuse-compose.yaml` must exist and parse as valid YAML with a top-level `services` key (basic Compose schema validation). If the file is missing, Python raises `FileNotFoundError` and the command exits non-zero; if `services` is absent, `sys.exit(1)` fires. The Python YAML check is used because Docker may not be installed on the eval machine; this criterion does NOT require Docker. PASS when exit code is 0 and output contains `PASS`. [weight: 4%]

9. **`phase-02-N` key convention documented in `rules/harness-conventions.md`**: running the following exits 0:
   ```
   bash -c 'grep -q "phase-02-N" rules/harness-conventions.md && grep -q "current_sprint" rules/harness-conventions.md && grep -q "current_phase" rules/harness-conventions.md && echo PASS || echo FAIL'
   ```
   The file must contain a new subsection (any heading level) that uses the literal string `phase-02-N`, references `current_sprint`, and references `current_phase` — documenting that Phase 2 sprint-state entries use `phase-02-N` keys and clarifying how `current_phase` disambiguates what `current_sprint` refers to. PASS when all three greps succeed (exit 0) and output contains `PASS`. [weight: 4%]

10. **All new tests collected and green — full runner + observability suite**: running the following exits 0:
    ```
    bash -c 'uv run pytest tests/runner/ tests/observability/ -v --tb=short 2>&1 | tee /tmp/s02c10.txt && grep -E "passed" /tmp/s02c10.txt && echo PASS'
    ```
    `uv run pytest tests/runner/ tests/observability/` exits 0 (no failures, no errors). This is a holistic green-light check covering all new test files from this sprint. PASS when exit code is 0 and output contains `passed`. [weight: 8%]

### LLM-as-judge (requires reading comprehension)

11. **Async runner hard-cap design is correct (A6 behavioral)**: read `src/trine_eval/runner/engine.py`. The `run` function must: (a) use `asyncio.Semaphore(max_concurrency)` to limit concurrent sample execution — not a thread pool or a sequential loop; (b) accumulate token usage across samples and short-circuit when `token_limit` is exceeded, returning a partial `EvalLog`; (c) enforce `time_limit` via wall-clock elapsed time (e.g., `asyncio.wait_for` or periodic checks); (d) compute cost in USD from token counts (input × price-per-input-token + output × price-per-output-token, using Opus 4.7 pricing) and abort on `cost_limit`; (e) embed a `"cap_hit"` key in `EvalLog.metadata` naming the first cap that fired. A runner that only has stubs, only enforces one cap, or enforces caps via `time.sleep` polling is FAIL. [weight: 5%]

12. **`pyproject.toml` dependency additions are complete and correct**: read `pyproject.toml`. Runtime dependencies must now include `msgpack>=1.0`, `opentelemetry-api>=1.20`, `opentelemetry-sdk>=1.20`, and `langfuse>=2.0`. The `[project.entry-points.pytest11]` table must define `trine-eval = "trine_eval.pytest_plugin"`. No forbidden packages (`langgraph`, `ragas`, `pgvector`, `fastapi`) appear anywhere. PASS when all four runtime deps are present, the `pytest11` entry point is declared, and no forbidden packages appear. [weight: 3%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **Historical Phase 1 contracts and evals are unmodified**: no file matching `.harness/contracts/sprint-0[1-9]*.md`, `.harness/contracts/sprint-1*.md`, `.harness/evals/sprint-0[1-9]*.md`, or `.harness/evals/sprint-1*.md` is modified on this branch. Verify by diffing all commits against the merge-base:
   ```
   bash -c 'BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~$(git rev-list --count HEAD)^); diff_out=$(git diff $BASE..HEAD -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" 2>/dev/null); [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" && exit 1)'
   ```
   PASS when exit code is 0 (diff is empty).

2. **No forbidden packages imported or declared**: the strings `langgraph`, `ragas`, `pgvector`, and `fastapi` must not appear in `pyproject.toml`, `src/trine_eval/**/*.py`, or `tests/**/*.py`. Verify via:
   ```
   bash -c 'git grep -rn --count -E "langgraph|ragas|pgvector|fastapi" pyproject.toml src/ tests/ 2>/dev/null | grep -v "^Binary" | grep -v ":0$" && echo FAIL && exit 1 || echo PASS'
   ```
   PASS when the command exits 0 and prints `PASS`.

3. **No real Anthropic API calls in tests**: no test under `tests/` calls `anthropic.Anthropic()` without mocking (i.e., without a `unittest.mock.patch` or `pytest-mock` fixture wrapping the call). The Evaluator must read the key test source files (`tests/runner/test_engine.py`, `tests/runner/test_caps.py`, `tests/runner/test_rescore_cli.py`, and any other file that imports `anthropic`) and verify that every `anthropic.Anthropic(...)` instantiation is enclosed in a `mocker.patch(...)` block or a `unittest.mock.patch(...)` context manager. A bare `anthropic.Anthropic()` call at module level or in a test body without a surrounding patch is FAIL. PASS when no unguarded `anthropic.Anthropic()` instantiation is found in test source files.

## Reference Solutions

**Criterion C2 — hard-cap enforcement (headline criterion):**

The key implementation shape for `engine.py`:

```python
async def run(
    task: Task,
    model: AnthropicModel,
    *,
    max_concurrency: int = 4,
    token_limit: int | None = None,
    time_limit: float | None = None,
    cost_limit: float | None = None,
) -> EvalLog:
    sem = asyncio.Semaphore(max_concurrency)
    start = asyncio.get_event_loop().time()
    total_tokens = 0
    total_cost = 0.0
    scores = []
    cap_hit: str | None = None

    async def run_sample(sample: Sample) -> Score | None:
        nonlocal total_tokens, total_cost, cap_hit
        async with sem:
            # check caps before each sample
            if cap_hit:
                return None
            elapsed = asyncio.get_event_loop().time() - start
            if time_limit and elapsed >= time_limit:
                cap_hit = "time_limit"
                return None
            if token_limit and total_tokens >= token_limit:
                cap_hit = "token_limit"
                return None
            if cost_limit and total_cost >= cost_limit:
                cap_hit = "cost_limit"
                return None
            # run sample ...
            result, usage = await _invoke_model(model, sample)
            total_tokens += usage.total_tokens
            total_cost += _compute_cost(usage)
            return score

    tasks = [run_sample(s) for s in task.samples]
    results = await asyncio.gather(*tasks)
    scores = [r for r in results if r is not None]

    metadata: dict[str, Any] = {}
    if cap_hit:
        metadata["cap_hit"] = cap_hit

    return EvalLog(
        task_name=task.name,
        samples=task.samples[:len(scores)],
        scores=scores,
        model=model.model,
        timestamp=datetime.utcnow(),
        metadata=metadata,
    )
```

A correct test for `token_limit` cap:
```python
async def test_token_limit_cap():
    model = MockModel(tokens_per_call=100)  # mock returns 100 tokens each
    task = make_task(samples=10)  # 10 samples
    log = await run(task, model, token_limit=150)  # cap after ~1-2 samples
    assert log.metadata["cap_hit"] == "token_limit"
    assert len(log.scores) < 10  # partial result
```

**Criterion C3 — log round-trip (second headline):**

```python
from trine_eval.runner.logformat import save, load

def test_json_round_trip(tmp_path):
    log = EvalLog(
        task_name="test",
        samples=[Sample(id="1", input="hello", target="world"),
                 Sample(id="2", input="foo", target="bar")],
        scores=[Score(value=1.0, answer="world", explanation="ok"),
                Score(value=0.0, answer="baz", explanation="wrong")],
        model="claude-opus-4-7",
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        aggregate={"accuracy": 0.5},
    )
    path = tmp_path / "log.json"
    save(log, path, format="json")
    loaded = load(path)
    assert loaded == log

def test_msgpack_round_trip(tmp_path):
    # same as above but format="msgpack", path suffix ".msgpack"
    ...
```

**Criterion C4 — pytest plugin exit code 100:**

The plugin must hook into `pytest_sessionfinish` and call `session.exitstatus = 100` (or `os._exit(100)`) when any trine-eval score fails threshold:

```python
# src/trine_eval/pytest_plugin.py
import pytest

def pytest_addoption(parser):
    parser.addoption("--trine-eval-threshold", type=float, default=1.0)

def pytest_sessionfinish(session, exitstatus):
    if hasattr(session, "_trine_eval_failed") and session._trine_eval_failed:
        session.exitstatus = 100
```

The `pyproject.toml` entry point:
```toml
[project.entry-points.pytest11]
trine-eval = "trine_eval.pytest_plugin"
```

PASS: pytest exits 100 (not 1) when a score is below threshold. FAIL: exits 1 (pytest default for failures).

**Criterion C9 — `phase-02-N` key convention:**

The new subsection in `rules/harness-conventions.md` should read approximately:

```markdown
## Sprint-State Phase-Qualifier Convention

`sprint-state.json` uses a namespaced key scheme to avoid collisions between
Phase 1 and Phase 2 sprint entries:

- **Phase 1** sprint entries use bare integer keys: `"1"` through `"12"`.
- **Phase 2** sprint entries use `phase-02-N` keys: `"phase-02-0"`, `"phase-02-1"`,
  `"phase-02-2"`, etc.
- The `current_phase` field disambiguates which phase `current_sprint` refers to:
  when `current_phase == 2`, `current_sprint: 2` means Phase 2 Sprint 2, whose
  state entry is keyed `"phase-02-2"`.
- **Bridging exception:** Sprint 0 of Phase 2 used the bare key `"0"` because
  Phase 1 had no Sprint 0 and no collision was possible. Sprint 1 introduced
  the `phase-02-N` form; Sprint 2+ use it exclusively.

Tooling that reads `sprint-state.json` must interpret `current_sprint` in the
context of `current_phase` — do not assume bare integer keys for Phase 2.
```

## Out of Scope

- **Prompt caching** (`cache_control` breakpoints, `src/trine_eval/models/caching.py`): Sprint 3.
- **Batch API** (`src/trine_eval/models/batch.py`): Sprint 3.
- **LLM-as-judge infrastructure** (`src/trine_eval/judge/`): Sprint 4.
- **Docker sandbox** (`src/trine_eval/sandbox/`): Sprint 5.
- **SWE-bench Verified adapter** (`src/trine_eval/benchmarks/`): Sprint 6.
- **Human annotation queue** (`H6`): Sprint 4+.
- **Live Langfuse export in tests**: tests use `exporter="noop"` or a stub. No test requires Docker or a real Langfuse instance.
- **Real Anthropic API calls**: all tests mock the Anthropic client. No network dependency.
- **`uv run ruff check` / `uv run mypy --strict src` clean**: not gated in this sprint (Sprint 2 introduces new modules rapidly; strict typing enforcement is a Sprint 3+ gate).
- **Docker validation of `ops/langfuse-compose.yaml`**: `docker compose config` is not required — YAML validity is checked via Python `yaml.safe_load`. Docker may not be installed on the eval machine.
- **Three-tier grading** (code/model/human): Sprint 4.
- **Bootstrap CI on aggregates**: Sprint 4.

## Technical Notes

- **`EvalLog.metadata` field.** Sprint 1's `EvalLog` did not include a `metadata: dict[str, Any]` field. Sprint 2 adds it (with a `Field(default_factory=dict)` default). This is a backward-compatible addition to the Pydantic model — existing code constructing `EvalLog` without `metadata=` continues to work.

- **Cap enforcement ordering.** The `max_concurrency` cap is passive (controlled by `asyncio.Semaphore`) and never results in a partial log — it just limits throughput. Only `token_limit`, `time_limit`, and `cost_limit` abort the run early. The `"cap_hit"` metadata key is set only for the three abort-triggering caps, not for `max_concurrency`. The test for `max_concurrency` verifies throughput is bounded (never more than N concurrent tasks), not early abort.

- **Opus 4.7 pricing for cost computation.** At the time of writing, Anthropic's Opus 4.7 pricing is not publicly final. Use `5.00 / 1_000_000` per input token and `15.00 / 1_000_000` per output token as placeholder constants, sourced from `src/trine_eval/runner/engine.py` as `OPUS_47_INPUT_PRICE` and `OPUS_47_OUTPUT_PRICE`. These are compile-time constants that a future sprint can update when pricing is confirmed.

- **`msgpack` serialization of Pydantic models.** `msgpack` serializes native Python types (dicts, lists, strings, ints, floats, bytes). The `save` function must call `log.model_dump(mode="json")` to get a JSON-serializable dict, then serialize that dict with `msgpack.packb`. The `load` function must call `msgpack.unpackb(..., raw=False)` and then `EvalLog.model_validate(...)`. This round-trip preserves all fields because Pydantic's `mode="json"` normalizes datetimes to ISO strings, which `model_validate` parses back correctly.

- **Log format detection.** `logformat.save` detects format from the `format=` keyword argument. `logformat.load` detects format from the file extension: `.json` → JSON, `.msgpack` → msgpack. If the extension is neither, `load` raises `ValueError`.

- **pytest plugin registration.** The plugin must be registered in `pyproject.toml` under `[project.entry-points.pytest11]`. For the plugin to activate automatically in `uv run pytest` (without `-p trine_eval.pytest_plugin`), the entry point must be declared AND `uv sync` must have been run so the entry point is installed into the editable install's dist-info. The test file `test_plugin_exit.py` should NOT import the plugin manually — it should rely on auto-discovery. If the entry-point discovery is unreliable in the test environment, a `conftest.py` at `tests/` root may `import trine_eval.pytest_plugin` as a fallback.

- **OTel noop exporter.** `trine_eval.observability.otel.init_tracer(exporter="noop")` must use `opentelemetry.sdk.trace.export.SimpleSpanProcessor` with a `NoOpSpanExporter` (or equivalent). This ensures tests never need a live OTel collector. The function signature should accept `exporter: Literal["noop", "langfuse"] = "noop"` — when `"langfuse"` is selected and env vars are present, it wires the Langfuse exporter; otherwise it falls back to noop.

- **Langfuse env-var fallback.** `get_langfuse_client()` reads `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, and `LANGFUSE_HOST` from the environment. If any are missing, it returns a stub/noop client object rather than raising — this keeps the library functional when Langfuse is not configured. Tests pass `public_key=`, `secret_key=`, and `host=` explicitly and mock any network calls.

- **SN3 (no real API calls) intent.** The third Should-NOT criterion is primarily an intent gate, not a precise shell check. The Evaluator should read the key test files (`test_engine.py`, `test_caps.py`, `test_rescore_cli.py`) to confirm the Anthropic client is mocked. The `collect-only` grep in SN3's verification command is a structural sanity check (tests exist and are collected), not a behavioral check. The Evaluator may supplement with file reads.

- **`trine-eval score` and `trine-eval report` CLI extension.** `src/trine_eval/cli.py` must be extended (not rewritten) to handle the `score --log <path> --scorer <name>` and `report <log>` subcommands. The scorer lookup should use the decorator registry from Sprint 1 (`registry.get_scorer(name)`). The `report` subcommand calls `trine_eval.runner.metrics.accuracy_per_dollar(log)` and `trine_eval.runner.metrics.success_per_1k_tokens(log)`.

- **PowerShell portability.** All `verification_command` values in `sprint-02.tasks.json` use `bash -c '...'` wrappers. The `/tmp/` path for `tee` is available under Git Bash on Windows (confirmed in Sprint 1 review).

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/phase-02/sprint-02.tasks.json` is emitted with one JSON entry per criterion. Task IDs: `s02-c1` through `s02-c12` for success criteria (noting C11 and C12 are LLM-judge), `s02-sn1`, `s02-sn2`, `s02-sn3` for Should-NOT gates. Total entries: 12 success + 3 gate = 15. See `rules/harness-conventions.md` for the schema.

## Evaluator Review

**Status: NEEDS REVISION**

### Feedback

All verification commands were executed against the current (unbuilt) worktree. Commands for C1–C7, C10, C11, C12, C9 correctly FAIL (or error) because the implementation doesn't exist yet — that is the correct signal. Three issues require revision before approval.

---

**BUG 1 — C8 verification command exits 0 on missing file (no-op criterion)**

Confirmed by running the command:
```
bash -c 'python -c "import yaml; yaml.safe_load(open(\"ops/langfuse-compose.yaml\"))" && echo PASS || echo FAIL'
```
When `ops/langfuse-compose.yaml` does not exist, Python raises `FileNotFoundError`, the `&&` short-circuits to `|| echo FAIL`, which **prints `FAIL` but the overall shell exits 0**. The Evaluator sees exit code 0 with output `FAIL` and no criterion for checking the exit code in the chain. The criterion says PASS when "exit code is 0 and output contains `PASS`" — by that rule this command currently PASSes because exit code IS 0.

Additionally, the markdown criterion text states the file "must contain a `services` key (basic Compose schema validation)" but the tasks.json `verification_command` uses `yaml.safe_load()` with no `assert 'services' in d` check — silent divergence between prose and code.

**Fix:** Replace the verification command with one that fails explicitly on file-missing and validates the `services` key:
```
bash -c 'python -c "import yaml,sys; d=yaml.safe_load(open(\"ops/langfuse-compose.yaml\")); sys.exit(0 if \"services\" in d else 1)" && echo PASS || (echo FAIL && exit 1)'
```
Apply the same fix in `sprint-02.tasks.json` for `s02-c8`.

---

**BUG 2 — SN3 gate verification command is broken (currently produces FAIL on a correct implementation)**

Confirmed by running the command against the existing Sprint 1 test suite:
```
bash -c 'uv run pytest tests/ --collect-only -q 2>&1 | grep -c "test session starts" | grep -q "1" && echo PASS || echo FAIL'
```
In pytest's `-q` (quiet) mode, the string `"test session starts"` does **not** appear in output — the session header is suppressed. The `grep -c` returns `0`, `grep -q "1"` fails, and the command prints `FAIL` (exit 0). Running this against a perfect Sprint 2 implementation would also FAIL because `-q` mode never emits that string.

This means SN3 would block every sprint that correctly passes. The gate is inverted.

The Technical Notes section correctly acknowledges "The `collect-only` grep in SN3's verification command is a structural sanity check (tests exist and are collected), not a behavioral check" — but the command itself is broken regardless. Recommend reclassifying SN3 as `llm-judge` (grader reads test files for `anthropic.Anthropic()` without mock context) with no shell `verification_command`, or use a working structural proxy:
```
bash -c 'uv run pytest tests/ --collect-only 2>&1 | grep -qE "[0-9]+ tests? collected" && echo PASS || (echo FAIL && exit 1)'
```
Apply the same fix in `sprint-02.tasks.json` for `s02-sn3`.

---

**ISSUE 3 — C2 partial-implementation escape: tasks.json criterion text omits "partial log" assertion**

The markdown criterion states each cap test must "assert the returned `EvalLog.metadata` contains a `"cap_hit"` key... (e.g., `"token_limit"`, `"time_limit"`, `"cost_limit"`, `"max_concurrency"`)". The Technical Notes clarify that `max_concurrency` does NOT cause early abort — "The test for `max_concurrency` verifies throughput is bounded (never more than N concurrent tasks), not early abort." This means `max_concurrency` should NOT produce a `cap_hit` entry. But C2 requires `cap_hit` from four tests, including max_concurrency. A Generator that sets `cap_hit = "max_concurrency"` passes C2 but violates the Technical Notes.

The markdown should align with Technical Notes: the max_concurrency test verifies bounded concurrency (e.g., via a counter of simultaneous tasks), while only 3 tests assert `cap_hit`. Update C2 to require: "three tests assert `EvalLog.metadata['cap_hit']` names the triggered cap; one test (max_concurrency) asserts a concurrency bound without asserting `cap_hit`." The grep `4 passed` is still correct — just the criterion prose needs alignment.

---

**ISSUE 4 — C9 verification command is weak (no-op risk for partial documentation)**

The command greps for `"phase-02-N"` and `"current_sprint"` independently — two strings that happen to coexist but might be in unrelated sentences. As written, a Generator could satisfy C9 by sprinkling these strings anywhere in the file without writing a coherent subsection. This is low-risk given the reference solution is concrete, but the criterion text says "a new subsection" — the verification command cannot check for a heading. Recommend adding a third grep:
```
grep -q "current_phase" rules/harness-conventions.md
```
since the reference solution explicitly ties `current_phase` to `current_sprint` disambiguation. Alternatively, document that C9 is intentionally weak-grep and supplement with llm-judge for the "coherent subsection" aspect.

---

**Answers to Generator Open Questions**

**SN3: keep as gate or downgrade?** Keep as a gate — no-real-API-calls is a genuine sprint-blocking concern. Fix the broken `verification_command` per Bug 2 above, and reclassify SN3's `grader_type` in tasks.json to `"llm-judge"` with `verification_command: null`, per the Technical Notes' documented intent ("The Evaluator may also read key test files"). The structural collect-only check can be removed or kept as a separate informational check in the llm-judge rubric.

**C8: Python `yaml.safe_load` fallback acceptable?** Yes — the fallback is acceptable given Docker may not be available. The criterion and weight (4%) are appropriate for what it tests. The only issue is the broken exit-code behavior described in Bug 1 above, which must be fixed.

---

### Missing Criteria

None identified. The sprint scope (runner, caps, log format, pytest plugin, OTel/Langfuse, CLI, docs) is fully covered by C1–C12 + SN1–SN3. The behavioral-criterion weight (89%) exceeds the project's ≥60% threshold.

### Approved Criteria

C1 (correct), C2 (correct after prose alignment in Issue 3), C3 (correct — both JSON and msgpack required with `2 passed` guard), C4 (correct — `[ "$CODE" = "100" ]` checks literal 100), C5 (correct), C6 (correct — both metric names checked case-insensitively), C7 (correct — noop exporter, no network), C9 (acceptable, see Issue 4 note), C10 (correct), C11 (correct — llm-judge with reference solution provided), C12 (acceptable llm-judge), SN1 (correct glob narrowing), SN2 (correct).

**Required fixes before approval:** Bug 1 (C8 exit-code), Bug 2 (SN3 verification command). Issue 3 is strongly recommended. Issue 4 is advisory.
