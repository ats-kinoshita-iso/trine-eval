# Sprint 01 Contract: Python library bootstrap + core primitives

## What I Will Build

The first runnable Python package: `src/trine_eval/` with `pyproject.toml` (uv-managed, Python 3.12+), five Pydantic v2 core models (`Sample`, `Score`, `Task`, `EvalLog`, and supporting types), a decorator-based registry (`@task`, `@solver`, `@scorer`, `@metric`, `@tool`), a thin Anthropic SDK wrapper defaulting to `claude-opus-4-7` with effort tiers and interleaved thinking support, CLI entry-point stubs, and a `tests/` suite that proves all the above behave correctly including a thinking-block round-trip test enforced by mock. The convention extension closing the Sprint 00 oversight (contracts under `phase-02/`) is included as a docs-only criterion.

## Success Criteria

Each criterion must be independently testable. Weights sum to 100%.

### Deterministic (code-verifiable)

1. **`pyproject.toml` is uv-installable and collects tests**: running `uv sync` exits 0, and `uv run pytest --collect-only -q` exits 0 and reports at least 10 test items collected from `tests/`. Verify via:
   ```
   bash -c 'uv sync && uv run pytest --collect-only 2>&1 | grep -E "^[0-9]+ tests? collected" | head -1'
   ```
   PASS when exit code is 0 and the grep matches a line with N ≥ 10. [weight: 10%]

2. **Core Pydantic models are importable and validate correctly**: running the following command exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/core/test_models.py -v --tb=short 2>&1 | tee /tmp/c2.txt && grep -q "PASSED" /tmp/c2.txt && echo PASS'
   ```
   The test file `tests/core/test_models.py` must cover: `Sample`, `Score`, `Task`, and `EvalLog` all import without error; `Sample(id='x', input='hello', target='world').model_dump()['id'] == 'x'`; `Score(value=0.9, ...).value == 0.9`; and that `target` is optional (constructing `Sample` without `target` does not raise). PASS when exit code is 0 and output contains `PASSED`. [weight: 12%]

3. **Decorator registry round-trip — all five decorator types**: running the following command exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/core/test_decorators.py -v --tb=short 2>&1 | tee /tmp/c3.txt && grep -q "PASSED" /tmp/c3.txt && echo PASS'
   ```
   The test file `tests/core/test_decorators.py` must cover all five decorator types (`@task`, `@solver`, `@scorer`, `@metric`, `@tool`): each registers the decorated function by `__name__` in the corresponding `registry` dict and the stored callable executes correctly. PASS when exit code is 0 and output contains `PASSED`. [weight: 14%]

4. **`AnthropicModel` defaults and effort validation**: running the following command exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/models/test_anthropic.py -k "defaults or effort" -v --tb=short 2>&1 | tee /tmp/c4.txt && grep -q "PASSED" /tmp/c4.txt && echo PASS'
   ```
   The test file `tests/models/test_anthropic.py` must include tests verifying: default `model` is `"claude-opus-4-7"`, default `effort` is `"medium"`, `effort="high"` is accepted, and `effort="turbo"` raises a validation exception. PASS when exit code is 0 and output contains `PASSED`. [weight: 10%]

5a. **Thinking-block round-trip test exits 0 and prints its success signature (F6, deterministic)**: running:
   ```
   bash -c 'uv run pytest tests/models/test_anthropic.py -k thinking_round_trip -v --tb=short 2>&1 | tee /tmp/c5a.txt && grep -q "thinking blocks preserved byte-identical" /tmp/c5a.txt && grep -q "PASSED" /tmp/c5a.txt && echo PASS'
   ```
   exits 0 and both greps succeed. The test must emit the literal phrase `thinking blocks preserved byte-identical` (e.g., via `print()` or as the assertion failure message that pytest echoes on success) so the grader can confirm the correct assertion ran. PASS when exit code is 0 and both strings are found in output. [weight: 10%]

5b. **Thinking-block round-trip assertion structure is correct (F6, llm-judge)**: read `tests/models/test_anthropic.py`. The `test_thinking_block_round_trip` function must (a) mock `anthropic.Anthropic` so no real API calls are made, (b) simulate a two-turn exchange where the first `messages.create` returns a response containing a `thinking`-type content block with a `signature` field, and (c) assert that the second `messages.create` call receives that thinking block unmodified — verified by comparing `b.get("signature") == <expected_value>` (or equivalent `model_dump()` comparison) on the assistant turn in the second call's `messages` argument. A test that calls `mock_messages.create` twice but asserts only call-count is FAIL. PASS when the assertion explicitly checks the signature (or all three fields: `type`, `thinking`, `signature`) survived the round-trip. [weight: 6%]

6. **`uv run pytest` green across `tests/core/` and `tests/models/`**: `uv run pytest tests/core/ tests/models/ -v --tb=short` exits 0 with zero failures and zero errors. This is a holistic green-light check that all unit tests for core primitives and the Anthropic wrapper pass together. PASS when exit code is 0. [weight: 10%]

7. **`trine-eval --help` exits 0 and prints usage**: `uv run trine-eval --help` exits 0 and stdout contains the strings `run`, `score`, and `report` (the three required subcommand names). PASS when exit code is 0 and all three strings appear. [weight: 8%]

8. **Phase 2 contract naming convention documented in `rules/harness-conventions.md`**: `rules/harness-conventions.md` contains a new subsection (level-2 or level-3 heading) that uses the phrase `Phase 2` and explicitly names the canonical paths for Phase 2 **contract** files: `.harness/contracts/phase-02/sprint-NN.md` and `.harness/contracts/phase-02/sprint-NN.tasks.json`. Verify via:
   ```
   grep -q "contracts/phase-02" rules/harness-conventions.md && echo PASS || echo FAIL
   ```
   PASS when `grep` exits 0. [weight: 6%]

### LLM-as-judge (requires reading comprehension)

9. **`AnthropicModel` correctly wires the interleaved-thinking beta header**: read `src/trine_eval/models/anthropic.py`. The implementation must include the `betas=["interleaved-thinking-2025-05-14"]` beta header when making API calls (either in a `create`/`stream` wrapper or as a constructor-level default). The `effort` parameter must map to a `budget_tokens` integer or analogous thinking-budget mechanism passed to the API — specifically: `low` ≤ 1000 tokens, `medium` ≤ 8000, `high` ≤ 16000, `xhigh` ≤ 32000, `max` ≤ 100000 (or equivalent max). The implementation must NOT strip, alter, or re-encode any field (`type`, `thinking`, `signature`) on `thinking`-type content blocks when re-passing them to a subsequent `messages.create` call. [weight: 5%]

10. **`pyproject.toml` metadata quality and dependency completeness**: read `pyproject.toml`. It must declare: `name = "trine-eval"`, `version = "0.1.0"`, `requires-python = ">=3.12"`. Runtime dependencies must include `pydantic>=2.0` and `anthropic>=0.40`. Dev dependencies (under `[dependency-groups]` or `[tool.uv.dev-dependencies]` or equivalent uv-compatible dev group) must include `pytest`, `pytest-asyncio`, `ruff`, and `mypy`. The `[project.scripts]` table must define `trine-eval = "trine_eval.cli:main"`. No forbidden packages (`langgraph`, `ragas`, `pgvector`, `fastapi`) appear anywhere in the dependency tables. [weight: 4%]

11. **`uv.lock` exists at repo root and is tracked by git**: running:
    ```
    bash -c '[ -f uv.lock ] && git ls-files uv.lock | grep -q uv.lock && echo PASS || echo FAIL'
    ```
    exits 0 and prints `PASS`. This enforces the hygiene requirement that `uv.lock` is committed after `uv sync` so the lock file is tracked. PASS when both conditions hold: file exists on disk AND `git ls-files` confirms it is tracked. [weight: 5%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **Historical Phase 1 contracts and evals are unmodified**: no file under `.harness/contracts/sprint-0[1-9]*.md`, `.harness/contracts/sprint-1*.md`, or `.harness/evals/sprint-*.md` is modified on the Sprint 01 branch. Verify by diffing ALL commits on the branch against `main`'s merge-base:
   ```
   bash -c 'BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~$(git rev-list --count HEAD)^); diff_out=$(git diff $BASE..HEAD -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-*.md" 2>/dev/null); [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" && exit 1)'
   ```
   PASS when exit code is 0 (diff is empty).

2. **No forbidden packages imported or declared**: the strings `langgraph`, `ragas`, `pgvector`, and `fastapi` must not appear in `pyproject.toml`, `src/trine_eval/**/*.py`, or `tests/**/*.py`. Verify via:
   ```
   bash -c 'git grep -rn --count -E "langgraph|ragas|pgvector|fastapi" pyproject.toml src/ tests/ 2>/dev/null | grep -v "^Binary" | grep -v ":0$" && echo FAIL && exit 1 || echo PASS'
   ```
   PASS when the command exits 0 and prints `PASS`.

## Reference Solutions

**Criterion C5a — thinking-block round-trip test exits 0 with success phrase (deterministic anchor):**

The test function must emit the literal phrase `thinking blocks preserved byte-identical` in its output. The simplest approach is to print it at the end of the test body, or include it as the `assert` failure message (pytest echoes assertion messages on success in `-v` mode when the test uses `pytest.approx` or similar, but a `print()` call is the most reliable way to guarantee the phrase appears in captured output regardless of verbosity). Recommended:

```python
def test_thinking_block_round_trip():
    # ... setup and assertions ...
    assert any(
        b.get("type") == "thinking" and b.get("signature") == "sig-abc123"
        for b in assistant_turn["content"]
    )
    print("thinking blocks preserved byte-identical")  # required phrase for C5a gate
```

**Criterion C5b — thinking-block assertion structure (LLM-judge anchor):**

A correct implementation of the F6 thinking-block preservation test looks like the following. The key assertion is that the thinking block dict passed to the second `messages.create` call is **identical** to what was received from the first call — no fields added, removed, or mutated. This is what the LLM judge reads to confirm C5b.

```python
# tests/models/test_anthropic.py  (thinking-preservation test excerpt)
from unittest.mock import MagicMock, patch
from trine_eval.models.anthropic import AnthropicModel

def test_thinking_block_round_trip():
    thinking_block = {
        "type": "thinking",
        "thinking": "let me reason step by step...",
        "signature": "sig-abc123",
    }
    tool_use_block = {
        "type": "tool_use",
        "id": "tu-1",
        "name": "bash",
        "input": {"command": "echo hi"},
    }
    first_response = MagicMock()
    first_response.content = [
        MagicMock(**thinking_block),  # or plain dict — implementation decides
        MagicMock(**tool_use_block),
    ]
    second_response = MagicMock()
    second_response.content = []

    with patch("anthropic.Anthropic") as MockClient:
        mock_messages = MockClient.return_value.messages
        mock_messages.create.side_effect = [first_response, second_response]

        model = AnthropicModel()
        # Call the model, capture the second call's messages argument
        # Assert the thinking block appears byte-identical in the second call's messages
        calls = mock_messages.create.call_args_list
        second_call_messages = calls[1][1]["messages"]
        # The assistant turn that preceded the tool result must contain
        # the thinking block unmodified
        assistant_turn = next(
            m for m in second_call_messages if m["role"] == "assistant"
        )
        assert any(
            b.get("type") == "thinking" and b.get("signature") == "sig-abc123"
            for b in assistant_turn["content"]
        ), "thinking blocks preserved byte-identical"
    print("thinking blocks preserved byte-identical")
```

PASS: test exits 0, thinking block `type` and `signature` verified in assistant turn of second call. FAIL: any field stripped, mutated, assertion checks only call-count, or the test not existing.

**Criterion 9 — `AnthropicModel` beta header wiring (LLM-judge anchor):**

A correct `AnthropicModel.__init__` or `create` method includes:
```python
# effort → budget_tokens mapping (one acceptable shape)
EFFORT_BUDGET = {
    "low": 1_000,
    "medium": 8_000,
    "high": 16_000,
    "xhigh": 32_000,
    "max": 100_000,
}

# beta header in the API call
response = self._client.messages.create(
    model=self.model,
    betas=["interleaved-thinking-2025-05-14"],
    thinking={"type": "enabled", "budget_tokens": EFFORT_BUDGET[self.effort]},
    ...
)
```
Any equivalent that achieves the same wire effect (beta header present, budget derived from effort tier, thinking blocks passed unmodified) is PASS. Absent beta header or absent effort-to-budget mapping is FAIL.

**Criterion 10 — `pyproject.toml` LLM-judge anchor:**

A correct `pyproject.toml` fragment:
```toml
[project]
name = "trine-eval"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "pydantic>=2.0",
    "anthropic>=0.40",
    "httpx>=0.25",
    "typer>=0.12",
]

[project.scripts]
trine-eval = "trine_eval.cli:main"

[dependency-groups]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "ruff>=0.4",
    "mypy>=1.10",
]
```
PASS: all required fields present, no forbidden packages. FAIL: missing `[project.scripts]`, missing `requires-python`, or any of `langgraph/ragas/pgvector/fastapi` present.

## Out of Scope

- **Async runner** (`src/trine_eval/runner/`): Sprint 2.
- **Replayable binary/JSON logs** (`src/trine_eval/runner/logformat.py`): Sprint 2.
- **OTel + Langfuse observability** (`src/trine_eval/observability/`): Sprint 2.
- **pytest plugin** (`src/trine_eval/pytest_plugin.py`) with exit-code 100 gating: Sprint 2.
- **Prompt caching** (`cache_control` breakpoints, `src/trine_eval/models/caching.py`): Sprint 3.
- **Batch API** (`src/trine_eval/models/batch.py`): Sprint 3.
- **LLM-as-judge infrastructure** (`src/trine_eval/judge/`): Sprint 4.
- **Docker sandbox** (`src/trine_eval/sandbox/`): Sprint 5.
- **SWE-bench Verified adapter** (`src/trine_eval/benchmarks/`): Sprint 6.
- **`model_roles` dict on Task** (`target`, `judge` keys): the `Task` model may have a stub `model_roles: dict = {}` field, but the full wiring between roles and the runner is Sprint 2+.
- **`uv run trine-eval list-tasks`** discovering `@task` fixtures at runtime: the compass plan mentions this but the CLI subcommand may be a no-op stub in Sprint 1 — the decorator round-trip test (C3) proves registration works without requiring runtime discovery.
- **Deterministic seeds and pinned version recording** in `EvalLog`: Sprint 2 adds `seeds.py` and `versions.py`; `EvalLog` may have placeholder fields.
- **`uv run ruff check` and `uv run mypy --strict src` clean**: enforced from Sprint 2 onward. Sprint 1 must not produce import errors or syntax errors, but strict type-annotation coverage is not gated here.
- **`structlog`, `opentelemetry-api`, `opentelemetry-sdk`, `langfuse` as runtime deps**: they are listed in the compass plan for Sprint 1's `pyproject.toml`, but since no code consumes them until Sprint 2, they may be declared as optional extras or dev dependencies rather than hard runtime deps. The contract does not gate on their presence.

## Technical Notes

- **`pyproject.toml` CLI entry point.** The compass plan lists `typer` as the CLI framework. The `[project.scripts]` entry points to `trine_eval.cli:main`. The CLI stubs must produce a non-error exit when `--help` is invoked. A minimal `typer.Typer()` app with three placeholder subcommands (`run`, `score`, `report`) printing `"not implemented in v0.1"` satisfies C7.

- **Circular import avoidance between `task.py` and `registry.py`.** `Task` references solver/scorer/metric by name (string) or callable type, not by importing from decorators. `registry.py` should be a plain module with module-level dicts; `decorators.py` imports from `registry.py` (not the reverse). `task.py` may import `Sample`, `Score` from sibling modules but should not import from `registry.py` or `decorators.py` to avoid cycles.

- **Pydantic v2 syntax required.** All models use `model_config = ConfigDict(...)` (not `class Config:`), `model_dump()` (not `.dict()`), and `model_validate()` (not `.from_orm()`). The `target: str | None = None` pattern (union with None) is idiomatic v2.

- **Thinking-block mock strategy.** The F6 test (C5) must mock at the `anthropic.Anthropic` constructor level (or via `unittest.mock.patch`) — it must NOT make real API calls. The mock must simulate a two-turn exchange: first `messages.create` returns a response with a `thinking` block and a `tool_use` block; the test then calls `AnthropicModel` again with a tool result and asserts the thinking block appears byte-identical in the second call's `messages` argument.

- **`effort` validation.** `AnthropicModel` must reject invalid effort values at construction time — the five valid literals are `"low"`, `"medium"`, `"high"`, `"xhigh"`, `"max"`. Using `Literal["low","medium","high","xhigh","max"]` as the type annotation (with Pydantic or `typing.get_args`) is the preferred approach. C4's one-liner verifies this rejection.

- **`anthropic>=0.40` version floor.** Version 0.40+ includes the `betas` parameter on `messages.create` and the `interleaved-thinking-2025-05-14` header support. Earlier versions lack this. The constraint must appear in `pyproject.toml`'s `dependencies`.

- **Phase 2 contract naming convention (this sprint's docs criterion).** Sprint 00's naming convention in `rules/harness-conventions.md` covered evals and transcripts under `phase-02/` but NOT contracts. This sprint adds a subsection explicitly documenting that Phase 2 contracts live at `.harness/contracts/phase-02/sprint-NN.md` with sibling `.harness/contracts/phase-02/sprint-NN.tasks.json`. The `harness-tasks-json-coverage` regression invariant uses `git ls-files ".harness/contracts/sprint-*.md"` which does NOT recurse into subdirectories, so Phase 2 contract files are invisible to that invariant — this is by design and is noted here for future sprint operators.

- **`project_type` in `config.json`.** Currently `"eval-harness"`. Sprint 1 produces a `cli-tool`-flavored Python library, but the meta-harness that evaluates it is itself an eval-harness. Changing `project_type` is out of scope for this sprint — the Evaluator uses the `eval-harness` rubric to assess the harness's own output quality. If the rubric dimensions feel mismatched for Python code quality, note this in the eval for the operator to decide before Sprint 2.

- **`uv.lock` commit.** After `uv sync`, the `uv.lock` file must be committed to git so the lock file is tracked. The `lock_file_path: "uv.lock"` in `config.json` specifies this. C1's `uv sync` exit-0 is the behavioral gate; committing the lock file is a hygiene requirement called out here.

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/phase-02/sprint-01.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — 9 deterministic + 3 LLM-judge success criteria + 2 Should-NOT gates = 14 entries — with stable `task_id`s `s01-c1` through `s01-c11` (where C5 is split into `s01-c5a` and `s01-c5b`) and `s01-sn1`, `s01-sn2`. Downstream sprints consume that JSON; this markdown contract remains the human-readable source of truth. See `rules/harness-conventions.md` for the schema.

## Evaluator Review

**Status: NEEDS REVISION**

### Feedback

**Issue 1 — C2, C3, C4: Multi-line `-c` strings are not portable to PowerShell (BLOCKING)**

The verification commands for C2, C3, and C4 embed multi-line Python code blocks directly inside `uv run python -c "..."`. On Linux/macOS bash this works because the shell passes the literal newlines through. On Windows PowerShell — the declared shell for this environment (`Platform: win32`, `Shell: PowerShell`) — a multi-line argument to `-c` is not valid and will produce a syntax error or truncation. The Evaluator runs in PowerShell and will invoke these commands literally.

Required fix: either (a) wrap each command in `bash -c '...'` as the Should-NOT criteria already do, or (b) collapse each multi-line block to a semicolon-delimited single line (replacing newlines with `;` inside the Python string). The Should-NOT commands already use `bash -c '...'`, proving bash is available — use the same pattern for C2, C3, C4.

Example fix for C2:
```
bash -c 'uv run python -c "from trine_eval.core.sample import Sample; from trine_eval.core.score import Score; from trine_eval.core.task import Task; from trine_eval.core.log import EvalLog; s = Sample(id=\"x\", input=\"hello\", target=\"world\"); assert s.model_dump()[\"id\"] == \"x\"; sc = Score(value=0.9, answer=\"42\", explanation=\"correct\"); assert sc.value == 0.9; import pydantic; pydantic.TypeAdapter(Sample).validate_python({\"id\": \"y\", \"input\": \"hi\"}); print(\"PASS\")"'
```
(A Python script file approach, invoking via `uv run python tests/verify_c2.py`, is cleaner and more readable for complex assertions — consider that for C3.)

**Issue 2 — C5: Deterministic gate (exit 0) does not enforce the byte-identity assertion (MODERATE)**

C5 is tagged deterministic and the verification command is `uv run pytest tests/models/test_anthropic.py -k thinking -v`. Exit 0 passes the criterion. However, the criterion prose requires the test to "assert the thinking block is passed back to the API byte-identical." A Generator could write a test that (a) mocks the two-call exchange but (b) asserts only that the second call happened, not that the thinking block fields survived intact — and still exit 0.

The reference solution partially mitigates this by showing the correct assertion. But the reference solution is a calibration aid for the Evaluator, not an enforcement mechanism. The deterministic gate alone cannot distinguish a correct test from a weak one.

Suggested tightening: add a criterion clause like "The test must include an explicit `assert` checking that `b.get('signature') == <expected_value>` on the thinking block in the second call's messages argument. The Evaluator may read the test source to verify this assertion exists." Alternatively, promote a portion of C5 to llm-judge (the assertion-existence check) and keep the exit-0 gate as a separate lighter criterion. As written, a test that simply calls `mock_messages.create` twice and exits 0 would earn the 16% weight.

**Issue 3 — C1: `tail -5` truncation may hide the collection count (MINOR)**

`uv run pytest --collect-only -q 2>&1 | tail -5` limits output to the final 5 lines. pytest's `--collect-only -q` prints one line per test item followed by a summary line (e.g., `47 tests collected in 0.12s`). If there are warnings or notes printed after the summary line, `tail -5` will capture them and the summary line may not be in the final 5. The PASS check is "output contains a line matching `\d+ tests? collected`" — if that line isn't in the tail, the Evaluator cannot confirm it. Fix: remove `tail -5` or increase to `tail -10`, or grep the full output: `uv sync && uv run pytest --collect-only -q 2>&1 | grep -E '^\d+ tests? collected'`.

**Issue 4 — C7: `--help` string-presence check is underspecified (MINOR)**

C7 checks that stdout "contains the strings `run`, `score`, and `report`." These are very common English words. A help page that says "Run this tool to score a report" would pass even without three distinct subcommands named `run`, `score`, and `report`. Tighten to require the strings appear as words (not substrings): `grep -E '\brun\b' && grep -E '\bscore\b' && grep -E '\breport\b'`, or check for lines beginning with the subcommand name in the help output. This is minor because typer's `--help` output format makes false positives unlikely in practice, but the criterion as worded is not precise.

### Missing Criteria

**Missing: `uv.lock` committed to git.** The Technical Notes section says "the `uv.lock` file must be committed to git" but no criterion enforces this. It is marked as a "hygiene requirement" but hygiene requirements that are not criteriated will be skipped by a Generator under time pressure. Either add a criterion (e.g., `git ls-files uv.lock | grep -q uv.lock`) or explicitly mark it as out-of-scope for the sprint gate. As written, a Generator can skip committing `uv.lock` and still pass all 10 criteria.

**Missing: `Score.value` bounds validation.** C2 verifies `Score(value=0.9, ...)` works but doesn't verify that `Score(value=1.5, ...)` raises a validation error — if scores are semantically in [0, 1]. If there is no intended bound, this is fine; if there is, this is an unverified invariant that a later sprint will assume holds.

### Approved Criteria

- **C5** — approved with the caveat in Issue 2 above; the reference solution provides sufficient evaluator calibration for an acceptable risk level if the Generator is trusted to write honest tests. If the Generator is considered adversarial, this must be revised.
- **C6** — approved. Not a duplicate of C1; C1 collects, C6 executes.
- **C7** — approved with minor caveat (Issue 4).
- **C8** — approved. `grep -q "contracts/phase-02"` is a reasonable proxy for the docs criterion. The current `rules/harness-conventions.md` does not contain this string, so the criterion correctly requires new work.
- **C9** — approved. LLM-judge with reference solution. Criterion text is specific: exact beta header string, specific budget_token bounds per tier, explicit non-stripping requirement.
- **C10** — approved. LLM-judge with reference solution. All required fields enumerated.
- **SN1** — approved. `bash -c '...'` wrapper ensures portability. The fallback `git rev-parse HEAD~...` handles repos with no `main` branch.
- **SN2** — approved. `git grep --count` pattern correctly catches both declared dependencies and imported strings.
- **Weight sum** — 10+12+14+10+16+10+8+6+8+6 = 100. Confirmed.
- **Grader tagging** — C1-C8 deterministic, C9-C10 llm-judge. Correctly tagged.
- **Rubric mismatch** — The Generator's acknowledgment in Technical Notes is sufficient for Sprint 1. The eval-harness rubric assesses contract quality and harness methodology (which this contract itself demonstrates), not Python library implementation quality. No revision required for Sprint 1; flag for Sprint 2 operator decision.
- **No-op detection** — No `src/` directory or `pyproject.toml` exists. All deterministic criteria (C1-C8) would currently FAIL against the empty tree. C8 would FAIL because `grep -q "contracts/phase-02" rules/harness-conventions.md` returns no match (the file only documents evals and transcripts, not contracts). Zero no-op risk.
