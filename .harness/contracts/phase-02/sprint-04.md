# Sprint 04 Contract: LLM-as-judge: CoT rubric, binary scores, bootstrap CI, three-tier grading, calibration

## What I Will Build

Sprint 4 ships the `src/trine_eval/judge/` package, which implements four cooperating subsystems: (1) a CoT-rubric scorer (`judge/rubric.py`) that constructs a chain-of-thought grading prompt embedding the criterion text and golden answer, calls a judge model (mocked in tests), parses a binary 0/1 verdict, and returns `Score(value=0.0|1.0, reasoning="<judge CoT>")` registered via `@scorer`; (2) calibration helpers (`judge/calibration.py`) that compute TPR, TNR, and their sum against a labeled fixture set; (3) a bootstrap CI utility (`judge/bootstrap.py`) that produces `BootstrapCI(lower, upper, confidence)` from a list of score values via N-resample resampling; (4) a three-tier dispatcher (`judge/dispatch.py`) that routes each Score to one of `code | model | human` tiers based on the scorer's declared tier without auto-escalating; and (5) an in-memory + JSONL human annotation queue (`judge/queue.py`). A 50-item synthetic calibration fixture (25 positive + 25 negative, JSONL) is created under `tests/fixtures/calibration/` and a calibration test proves `TPR + TNR ≥ 1.5` on the fixture arithmetic.

## Success Criteria

Each criterion must be independently testable. Weights sum to 100%.

### Deterministic (code-verifiable)

1. **CoT-rubric scorer constructs prompt with criterion text and golden answer, returns binary Score**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_cot_rubric.py -k test_rubric_prompt_contains_criterion_and_golden -v --tb=short 2>&1 | tee /tmp/s04c1.txt && grep -q "PASSED" /tmp/s04c1.txt && echo PASS'
   ```
   `tests/judge/test_cot_rubric.py` must contain `test_rubric_prompt_contains_criterion_and_golden`. The test must: (a) mock `anthropic.Anthropic` so no real API calls are made, (b) call `trine_eval.judge.rubric.model_graded_qa(sample, criterion="Explain photosynthesis", golden_answer="Plants convert light to energy", judge_model=mock_model)`, (c) capture the prompt string passed to the mocked judge model, (d) assert the prompt contains both the criterion text and the golden answer as substrings, and (e) assert the returned `Score` object has `value` equal to `0.0` or `1.0`. PASS when exit code is 0 and output contains `PASSED`. [weight: 12%]

2. **CoT-rubric scorer parses judge response into binary Score and stores CoT in `reasoning`**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_cot_rubric.py -k test_rubric_parses_verdict_and_reasoning -v --tb=short 2>&1 | tee /tmp/s04c2.txt && grep -q "PASSED" /tmp/s04c2.txt && echo PASS'
   ```
   `tests/judge/test_cot_rubric.py` must contain `test_rubric_parses_verdict_and_reasoning`. The test must: (a) mock the judge model to return a response whose text contains `PASS` (or `1` / `correct`) and some reasoning text, (b) call `model_graded_qa` with that mocked model, (c) assert `Score.value == 1.0`, and (d) assert `Score.reasoning` is a non-empty string containing the judge's text. A second sub-test (or parametrized case) must mock the judge to return a response containing `FAIL` (or `0` / `incorrect`) and assert `Score.value == 0.0`. PASS when exit code is 0 and output contains `PASSED`. [weight: 10%]

3. **`@scorer` decorator registers the CoT-rubric scorer in the registry**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_cot_rubric.py -k test_rubric_scorer_registered -v --tb=short 2>&1 | tee /tmp/s04c3.txt && grep -q "PASSED" /tmp/s04c3.txt && echo PASS'
   ```
   `tests/judge/test_cot_rubric.py` must contain `test_rubric_scorer_registered`. The test must: (a) import `trine_eval.core.registry` and (b) assert that `"model_graded_qa"` (or the scorer's registered name) is a key in `registry.scorers`. The scorer must be registered as a side-effect of importing `trine_eval.judge.rubric` — no explicit registration call required from the caller. PASS when exit code is 0 and output contains `PASSED`. [weight: 4%]

4. **Binary TPR and TNR computed correctly against labeled fixture**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_calibration.py -k test_tpr_tnr_formula -v --tb=short 2>&1 | tee /tmp/s04c4.txt && grep -q "PASSED" /tmp/s04c4.txt && echo PASS'
   ```
   `tests/judge/test_calibration.py` must contain `test_tpr_tnr_formula`. The test must: (a) import `trine_eval.judge.calibration.compute_tpr_tnr`, (b) construct a small labeled set — e.g., 4 positive items (golden label `1`) and 4 negative items (golden label `0`) with mock scorer predictions — where TP=3, FN=1, TN=3, FP=1, (c) assert `TPR == 3/(3+1) == 0.75`, (d) assert `TNR == 3/(3+1) == 0.75`, and (e) assert `TPR + TNR == 1.5`. Edge case: assert that a perfect scorer (all correct) returns `TPR + TNR == 2.0`. PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

5. **50-item calibration fixture exists with exactly 25 positive and 25 negative items, and calibration gate passes**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_calibration.py -k test_calibration_fixture_gate -v --tb=short 2>&1 | tee /tmp/s04c5.txt && grep -q "PASSED" /tmp/s04c5.txt && echo PASS'
   ```
   `tests/judge/test_calibration.py` must contain `test_calibration_fixture_gate`. The test must: (a) read `tests/fixtures/calibration/items.jsonl` (or equivalent path — `items.jsonl`, `calibration_set.jsonl`, or similar single JSONL file), (b) assert the file exists and contains exactly 50 lines, (c) assert exactly 25 items have `label: 1` (positive) and 25 items have `label: 0` (negative), (d) apply a deterministic mock scorer that returns `Score(value=1.0)` for all positive items and `Score(value=0.0)` for all negative items (or use the item's own `predicted` field if the fixture pre-records a mock prediction), and (e) call `compute_tpr_tnr` and assert `TPR + TNR >= 1.5`. This proves the calibration arithmetic path is correct end-to-end on a fixture that can be deterministically verified. PASS when exit code is 0 and output contains `PASSED`. [weight: 9%]

6. **Bootstrap CI brackets the point estimate and `confidence=0.95` by default**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_bootstrap.py -k test_bootstrap_ci_brackets_mean -v --tb=short 2>&1 | tee /tmp/s04c6.txt && grep -q "PASSED" /tmp/s04c6.txt && echo PASS'
   ```
   `tests/judge/test_bootstrap.py` must contain `test_bootstrap_ci_brackets_mean`. The test must: (a) import `trine_eval.judge.bootstrap.bootstrap_ci`, (b) call it with a list of 100 scores all equal to `1.0` (`scores = [1.0] * 100`), (c) assert the returned `BootstrapCI` has `lower <= 1.0 <= upper`, (d) assert `BootstrapCI.confidence == 0.95` (the default), and (e) with a mixed list (50 ones and 50 zeros, seeded at `random.seed(42)`) call `bootstrap_ci(scores, n_resamples=1000)` and assert `BootstrapCI.lower <= 0.5 <= BootstrapCI.upper`. PASS when exit code is 0 and output contains `PASSED`. [weight: 7%]

7. **Bootstrap CI variance: `n_resamples=10` produces a different CI than `n_resamples=1000`**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_bootstrap.py -k test_bootstrap_variance_with_n_resamples -v --tb=short 2>&1 | tee /tmp/s04c7.txt && grep -q "PASSED" /tmp/s04c7.txt && echo PASS'
   ```
   `tests/judge/test_bootstrap.py` must contain `test_bootstrap_variance_with_n_resamples`. The test must: (a) generate a fixed list of 50 scores (`[0.0]*25 + [1.0]*25`) with `random.seed(0)` set before each call, (b) call `bootstrap_ci(scores, n_resamples=10)` and record `width_10 = ci_10.upper - ci_10.lower`, (c) call `bootstrap_ci(scores, n_resamples=1000)` and record `width_1000`, (d) assert `ci_10.lower != ci_1000.lower OR ci_10.upper != ci_1000.upper` (the two intervals must NOT be byte-identical — proves the resampling responds to `n_resamples`; this catches a trivial implementation that returns a constant `(0.0, 1.0)` regardless of resamples), and (e) assert `width_10 >= width_1000 OR width_10 != width_1000` (allowing either direction of width change while requiring some response). PASS when exit code is 0 and output contains `PASSED`. [weight: 4%]

8. **Three-tier dispatcher routes `tier=code` scorer without invoking the judge model**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_dispatch.py -k test_dispatch_code_tier_no_judge -v --tb=short 2>&1 | tee /tmp/s04c8.txt && grep -q "PASSED" /tmp/s04c8.txt && echo PASS'
   ```
   `tests/judge/test_dispatch.py` must contain `test_dispatch_code_tier_no_judge`. The test must: (a) import `trine_eval.judge.dispatch.dispatch_score`, (b) create a mock scorer declared with `tier="code"` that returns `Score(value=1.0, metadata={})`, (c) call `dispatch_score(sample, scorer=mock_code_scorer, judge_model=mock_judge)`, (d) assert the returned `Score.metadata["tier"] == "code"`, and (e) assert the mock judge model was **never called** (i.e., `mock_judge.call_count == 0` or equivalent). PASS when exit code is 0 and output contains `PASSED`. [weight: 10%]

9. **Three-tier dispatcher routes `tier=model` scorer through the judge and `tier=human` scorer to the queue**: running the following exits 0 and prints `PASS`:
   ```
   bash -c 'uv run pytest tests/judge/test_dispatch.py -k test_dispatch_model_and_human_tiers -v --tb=short 2>&1 | tee /tmp/s04c9.txt && grep -q "PASSED" /tmp/s04c9.txt && echo PASS'
   ```
   `tests/judge/test_dispatch.py` must contain `test_dispatch_model_and_human_tiers`. The test must: (a) test the `tier=model` case: call `dispatch_score` with a scorer declared `tier="model"`, assert the mock judge model IS called exactly once, and assert `Score.metadata["tier"] == "model"`; (b) test the `tier=human` case: call `dispatch_score` with a scorer declared `tier="human"`, assert the sample is enqueued to `trine_eval.judge.queue.ListQueue` (or the singleton queue), assert no synchronous Score is returned (the function may return `None` or a `Score(value=None, metadata={"tier": "human", "queued": True})` sentinel), and assert `mock_judge` was NOT called for the human-tier case. PASS when exit code is 0 and output contains `PASSED`. [weight: 10%]

10. **Human annotation queue enqueue → list → resolve round-trip**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/judge/test_queue.py -k test_queue_enqueue_list_resolve -v --tb=short 2>&1 | tee /tmp/s04c10.txt && grep -q "PASSED" /tmp/s04c10.txt && echo PASS'
    ```
    `tests/judge/test_queue.py` must contain `test_queue_enqueue_list_resolve`. The test must: (a) import `trine_eval.judge.queue.ListQueue`, (b) create a fresh `ListQueue` instance, (c) enqueue a sample with `queue.enqueue(sample)`, (d) call `queue.list()` and assert the returned list contains exactly 1 item with the sample's `id`, (e) call `queue.resolve(sample_id, value=1.0)` and assert it returns a `Score(value=1.0)`, and (f) call `queue.list()` again and assert the resolved item is no longer in the pending list. PASS when exit code is 0 and output contains `PASSED`. [weight: 8%]

11. **Full judge test suite exits 0 with no failures**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/judge/ -v --tb=short 2>&1 | tee /tmp/s04c11.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s04c11.txt && ! grep -qE "FAILED|ERROR" /tmp/s04c11.txt && [ "$EC" = "0" ] && echo PASS || exit 1'
    ```
    All new test files under `tests/judge/` from this sprint pass together with no failures or errors. PASS when pytest exit code is 0, output contains `passed`, and no `FAILED` or `ERROR` lines appear. [weight: 2%]

12. **No regressions in prior runner, model, and core tests**: running the following exits 0 and prints `PASS`:
    ```
    bash -c 'uv run pytest tests/runner/ tests/models/ tests/core/ -v --tb=short 2>&1 | tee /tmp/s04c12.txt; EC=${PIPESTATUS[0]}; grep -E "passed" /tmp/s04c12.txt && ! grep -qE "FAILED|ERROR" /tmp/s04c12.txt && ( [ "$EC" = "0" ] || [ "$EC" = "100" ] ) && echo PASS || exit 1'
    ```
    All prior Sprint 1, 2, and 3 tests under `tests/runner/`, `tests/models/`, and `tests/core/` continue to pass. PASS when pytest exits 0 (or 100 — Sprint 2's pytest plugin deliberately overrides session exit to 100 when a `@pytest.mark.trine_eval` test records a score below threshold; the regression check accepts 100 because no genuine test failure prints `FAILED` or `ERROR`), output contains `passed`, and no `FAILED` or `ERROR` lines appear. [weight: 2%]

### LLM-as-judge (requires reading comprehension)

13. **CoT-rubric scorer API shape and prompt construction are correct (E1 behavioral)**: read `src/trine_eval/judge/rubric.py`. The implementation must: (a) expose a function named `model_graded_qa` (or a class with `__call__`) that accepts at minimum `sample`, `criterion: str`, and `golden_answer: str` parameters; (b) construct a prompt string that embeds `criterion` and `golden_answer` as distinct substrings (not just the sample input); (c) call the judge model exactly once per invocation passing the constructed prompt; (d) parse the judge response text for a binary verdict — a PASS/FAIL, yes/no, 1/0, correct/incorrect, or equivalent marker — and convert it to `Score(value=1.0)` or `Score(value=0.0)`; (e) store the full judge response text in `Score.reasoning` (preferred) OR `Score.explanation` (acceptable if the Generator chose to reuse Sprint 1's existing field) — the full CoT text must be present, regardless of which field name is used. Storing only the extracted verdict token (PASS/FAIL/1/0) rather than the full response is FAIL; and (f) be registered in `trine_eval.core.registry.scorers` via the `@scorer` decorator (or equivalent import-time registration). An implementation that ignores `golden_answer` in the prompt is FAIL. An implementation that stores only the verdict string rather than the full CoT response is FAIL. [weight: 6%]

14. **Three-tier dispatcher design is correct — tier isolation and `tier` metadata key (E6 behavioral)**: read `src/trine_eval/judge/dispatch.py`. The implementation must: (a) read the scorer's declared `tier` attribute (e.g., `scorer.tier` or a function attribute set at decoration time) to decide routing — the tier must be introspected from the scorer, not passed as a separate argument; (b) for `tier="code"`: call the scorer directly and record `score.metadata["tier"] = "code"` — the judge model must NOT be invoked; (c) for `tier="model"`: call the judge (or the scorer with judge_model injected) and record `score.metadata["tier"] = "model"`; (d) for `tier="human"`: enqueue the sample to the human annotation queue and record `tier="human"` in the pending item — no synchronous score is computed; (e) NOT auto-escalate a `code`-tier scorer to `model` even when the code scorer returns `Score(value=None)` or raises. A dispatcher that ignores the `tier` attribute and calls the judge unconditionally is FAIL. A dispatcher that auto-escalates `code` → `model` on any condition is FAIL. [weight: 8%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **Historical Phase 1 and Phase 2 prior-sprint contracts and evals are unmodified**: no file matching Phase-1 or prior Phase-2 sprint paths is modified by any commit whose message contains `(sprint-04)` (the conventional commit prefix for this sprint). Verification iterates over all `(sprint-04)`-prefixed commits reachable from HEAD but not from the sprint-03 Phase-2 completion commit, and checks each commit's individual diff (`c^..c`) against the prior-sprint glob. The Phase-2 patterns use `sprint-0[123]*.md` (covering sprint-01, sprint-02, sprint-03 — all finalized) to exclude the current sprint-04 contract from the immutability check. When no sprint-04 commits exist yet, the loop runs zero iterations and exits PASS. Verify:
   ```
   bash -c 'failed=0; S03BASE=$(git log --format=%H --grep="complete sprint 03 (Phase 2)" -1 2>/dev/null); SPRINT_COMMITS=$(git log --format=%H --grep="(sprint-04)" HEAD ${S03BASE:+^$S03BASE} 2>/dev/null); for c in $SPRINT_COMMITS; do diff_out=$(git diff "${c}^".."${c}" -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" ".harness/contracts/phase-02/sprint-0[123]*.md" ".harness/contracts/phase-02/sprint-1*.md" ".harness/evals/phase-02/sprint-0[123]*.md" ".harness/evals/phase-02/sprint-1*.md" 2>/dev/null); if [ -n "$diff_out" ]; then echo "FAIL: $c modified prior-sprint files"; echo "$diff_out" | head -20; failed=1; fi; done; [ "$failed" = "0" ] && echo PASS || exit 1'
   ```
   PASS when exit code is 0. This covers both Phase-1 root-level files and Phase-2 subdirectory files under `.harness/contracts/phase-02/` and `.harness/evals/phase-02/`. The sprint-commit scope (using `^$S03BASE`) prevents historical Phase-1 `(sprint-04)` commits from being evaluated — only commits introduced during this Phase-2 sprint-04 work window are checked.

2. **No forbidden packages imported or declared**: the strings `langgraph`, `ragas`, `pgvector`, and `fastapi` must not appear in `pyproject.toml`, `src/trine_eval/**/*.py`, or `tests/**/*.py`. Verify via:
   ```
   bash -c 'git grep -rn --count -E "langgraph|ragas|pgvector|fastapi" pyproject.toml src/ tests/ 2>/dev/null | grep -v "^Binary" | grep -v ":0$" && echo FAIL && exit 1 || echo PASS'
   ```
   PASS when the command exits 0 and prints `PASS`.

3. **No real Anthropic API calls in tests**: no test under `tests/` calls `anthropic.Anthropic()` or any `client.messages.*` method without mocking. The Evaluator must read the key test source files (`tests/judge/test_cot_rubric.py`, `tests/judge/test_dispatch.py`, and any other file under `tests/judge/` that imports `anthropic`) and verify that every `anthropic.Anthropic(...)` instantiation and every `messages.create` / `batches.create` call is enclosed in a `mocker.patch(...)` block or a `unittest.mock.patch(...)` context manager. A bare `anthropic.Anthropic()` call at module level or in a test body without a surrounding patch is FAIL. PASS when no unguarded `anthropic.Anthropic()` instantiation is found in test source files under `tests/judge/`.

## Reference Solutions

**Criterion C1–C2, C13 — CoT-rubric scorer shape (LLM-judge anchor for C13):**

A correct `src/trine_eval/judge/rubric.py` implementation:

```python
# src/trine_eval/judge/rubric.py
from __future__ import annotations

from trine_eval.core.decorators import scorer
from trine_eval.core.sample import Sample
from trine_eval.core.score import Score

_COT_PROMPT_TEMPLATE = """\
You are a grader evaluating a student's answer.

Grading criterion:
{criterion}

Expected (golden) answer:
{golden_answer}

Student's answer:
{student_answer}

Think step by step. Then on a final line output exactly one of: PASS or FAIL.
"""

_VERDICT_MAP = {
    "pass": 1.0, "1": 1.0, "correct": 1.0, "yes": 1.0,
    "fail": 0.0, "0": 0.0, "incorrect": 0.0, "no": 0.0,
}


def _parse_verdict(text: str) -> float:
    """Extract binary verdict from judge response text."""
    for line in reversed(text.strip().splitlines()):
        token = line.strip().lower()
        if token in _VERDICT_MAP:
            return _VERDICT_MAP[token]
    # Fallback: scan for any verdict keyword
    lower = text.lower()
    for kw, val in _VERDICT_MAP.items():
        if kw in lower:
            return val
    return 0.0  # conservative default


@scorer
def model_graded_qa(
    sample: Sample,
    *,
    criterion: str,
    golden_answer: str,
    judge_model: object,
) -> Score:
    """
    Grade a sample using a CoT rubric prompt with a golden answer.

    The judge model is called once; its full response is stored in
    Score.reasoning. The binary verdict (0.0 or 1.0) is parsed from
    the last line of the response.
    """
    prompt = _COT_PROMPT_TEMPLATE.format(
        criterion=criterion,
        golden_answer=golden_answer,
        student_answer=sample.input,
    )
    response_text: str = judge_model.complete(prompt)
    value = _parse_verdict(response_text)
    return Score(
        value=value,
        reasoning=response_text,
        metadata={"judge": "model_graded_qa"},
    )
```

PASS: `criterion` and `golden_answer` both appear in the prompt string; response text stored in `Score.reasoning`; `@scorer` decorator registers the function; binary value 0.0 or 1.0 returned. FAIL: `golden_answer` absent from prompt, `reasoning` stores only the extracted verdict token, or scorer not in registry after import.

**Criterion C8–C9, C14 — three-tier dispatcher shape (LLM-judge anchor for C14):**

A correct `src/trine_eval/judge/dispatch.py` implementation:

```python
# src/trine_eval/judge/dispatch.py
from __future__ import annotations

from typing import Any

from trine_eval.core.sample import Sample
from trine_eval.core.score import Score
from trine_eval.judge.queue import get_default_queue

_VALID_TIERS = frozenset({"code", "model", "human"})


def dispatch_score(
    sample: Sample,
    *,
    scorer: Any,
    judge_model: Any | None = None,
) -> Score | None:
    """
    Route a sample to the appropriate grading tier.

    Tier is read from scorer.tier (a string attribute set at decoration time).
    - code:  call scorer directly; record metadata["tier"] = "code".
             The judge_model is NEVER invoked regardless of the code score.
    - model: call scorer with judge_model; record metadata["tier"] = "model".
    - human: enqueue to the human annotation queue; return None (no synchronous score).
             The judge_model is NEVER invoked.

    Raises ValueError if scorer.tier is not one of: code, model, human.
    Does NOT auto-escalate code → model under any condition.
    """
    tier = getattr(scorer, "tier", "code")
    if tier not in _VALID_TIERS:
        raise ValueError(f"Unknown tier {tier!r}. Must be one of {_VALID_TIERS}.")

    if tier == "code":
        score = scorer(sample)
        score.metadata["tier"] = "code"
        return score

    if tier == "model":
        if judge_model is None:
            raise ValueError("judge_model is required for tier='model'")
        score = scorer(sample, judge_model=judge_model)
        score.metadata["tier"] = "model"
        return score

    # tier == "human"
    queue = get_default_queue()
    queue.enqueue(sample)
    return None
```

PASS: tier introspected from `scorer.tier`; `code` tier never calls `judge_model`; `human` tier enqueues and returns `None`; `model` tier calls judge; no auto-escalation. FAIL: `judge_model` called for `code` tier, auto-escalation logic present, or tier passed as a separate argument rather than read from scorer attribute.

## Out of Scope

- **E3: Pairwise position-swap judge** — deferred to v0.2+.
- **E4: Verbosity-mitigation heuristics** — deferred to v0.2+.
- **E7: Self-consistency reduction** (multiple judge calls + majority vote) — deferred to v0.2+.
- **Real Anthropic API calls**: all tests mock the Anthropic client. No network dependency in any test.
- **Judge cascade (G5)** — deferred to v0.2+.
- **`trine-eval queue list` / `trine-eval queue resolve` CLI commands** — CLI surface for the human queue is out of scope; the queue Python API is sufficient for v0.1.
- **JSONL persistence for the human queue** — in-memory `ListQueue` is sufficient; JSONL flush is a bonus only if trivially added.
- **`uv run ruff check` and `uv run mypy --strict src` clean**: not gated in this sprint (new modules are added quickly; strict typing enforcement continues from Sprint 2/3's baseline). Code must not introduce syntax errors.
- **v0.1 ship-gate calibration run against a real Anthropic model**: the calibration test uses a deterministic mock scorer. The full 50-item calibration with a real judge model is Sprint 6 scope.
- **Docker sandbox** (`src/trine_eval/sandbox/`): Sprint 5.
- **SWE-bench Verified adapter** (`src/trine_eval/benchmarks/`): Sprint 6.
- **OTel spans on judge invocations**: the judge package need not emit OTel spans in this sprint; Sprint 2's observability infrastructure is in place but judge instrumentation is Sprint 5/6 scope.

## Technical Notes

- **New package structure.** Sprint 4 creates `src/trine_eval/judge/__init__.py`, `src/trine_eval/judge/rubric.py`, `src/trine_eval/judge/calibration.py`, `src/trine_eval/judge/bootstrap.py`, `src/trine_eval/judge/dispatch.py`, and `src/trine_eval/judge/queue.py`. New test directory: `tests/judge/` with `__init__.py`, `test_cot_rubric.py`, `test_calibration.py`, `test_bootstrap.py`, `test_dispatch.py`, and `test_queue.py`. Calibration fixture: `tests/fixtures/calibration/items.jsonl` (50 lines, checked into git).

- **`Score.reasoning` field.** Sprint 1's `Score` model has `explanation: str | None` but no `reasoning` field. The implementer must either (a) add `reasoning: str | None = None` to `Score` in `src/trine_eval/core/score.py` (preferred — makes the CoT provenance first-class), or (b) store the CoT text in `Score.explanation` and update C2/C13 assertions accordingly. C2 and C13 say `Score.reasoning` — if the field is named `explanation`, the Evaluator must accept either name. The contract's LLM-judge criterion C13 checks that the full judge response text is stored in the field, regardless of its name.

- **`scorer.tier` attribute.** The dispatcher reads `scorer.tier` from the scorer object. In v0.1, this is set as a function attribute: `my_scorer.tier = "code"`. The `@scorer` decorator in Sprint 1 does not currently support tier; the implementer should either (a) extend the decorator to accept a `tier` keyword (`@scorer(tier="code")`) or (b) set the attribute directly after registration. C8/C9 tests may set `mock_scorer.tier = "code"` directly — no decorator change is required for the tests to pass. The dispatcher must not assume tier defaults to anything other than `"code"` when `scorer.tier` is absent.

- **Calibration fixture schema.** Each line of `tests/fixtures/calibration/items.jsonl` is a JSON object with at minimum: `{"id": "<str>", "input": "<student answer>", "label": 0|1}`. Optional field: `"predicted": 0.0|1.0` — if present, the calibration test may use it directly as the mock prediction (avoids defining a scorer in the test). The fixture must have exactly 25 lines where `label == 1` and 25 where `label == 0`. Items may be trivially synthetic (e.g., `"input": "correct answer NN"` with `label: 1`).

- **Bootstrap CI `BootstrapCI` type.** A correct implementation: `BootstrapCI = NamedTuple` or `dataclass` or `Pydantic model` with fields `lower: float`, `upper: float`, `confidence: float`. The function signature: `bootstrap_ci(scores: list[float], *, n_resamples: int = 1000, confidence: float = 0.95, seed: int | None = None) -> BootstrapCI`. The resampling loop: draw `n_resamples` bootstrap samples of `len(scores)` values with replacement; compute the mean of each; sort the means; take the `alpha/2` and `1 - alpha/2` percentiles where `alpha = 1 - confidence`.

- **`tee` exit-code masking.** The holistic criteria C11 and C12 use `| tee` with `${PIPESTATUS[0]}` capture (the Sprint 3 pattern). C1–C10 scope to individual test functions with `grep -q "PASSED"` — no `${PIPESTATUS[0]}` needed because the `&&` chain only reaches `grep` if pytest exits 0. C11/C12 use the three-guard pattern: `EC=${PIPESTATUS[0]}; grep -E "passed" && ! grep -qE "FAILED|ERROR" && ( [ "$EC" = "0" ] || [ "$EC" = "100" ] ) && echo PASS || exit 1`.

- **pytest plugin exit-100 disjunction.** C12 covers `tests/runner/`, which includes `test_plugin_exit.py` — the Sprint 2 test that deliberately triggers `exit 100`. C12 uses `( [ "$EC" = "0" ] || [ "$EC" = "100" ] )` for this reason. C11 covers only `tests/judge/`, which does not include the plugin exit test; C11 uses `[ "$EC" = "0" ]` only.

- **Human queue JSONL persistence.** The `ListQueue` in v0.1 is in-memory. If the implementer additionally persists to `.trine_eval/human_queue.jsonl` on `enqueue`/`resolve`, that is welcome, but the C10 test only exercises the in-memory API and does not assert file persistence. Do not create `.trine_eval/` inside the repo root without a `.gitignore` entry.

- **Behavioral weight compliance.** C1-C12 are behavioral (they test runtime correctness via pytest). C13 and C14 are LLM-judge behavioral criteria. All 14 success criteria are behavioral by rubric_dimension (>=60% threshold met at 100%).

---

**Weight verification:** C1(12) + C2(10) + C3(4) + C4(8) + C5(9) + C6(7) + C7(4) + C8(10) + C9(10) + C10(8) + C11(2) + C12(2) + C13(6) + C14(8) = **100%**. Confirmed.

**Behavioral weight:** all 14 success criteria are behavioral by rubric_dimension (>=60% threshold met at 100%).

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/phase-02/sprint-04.tasks.json` is emitted with one JSON entry per criterion. Task IDs: `s04-c1` through `s04-c14` for success criteria, `s04-sn1`, `s04-sn2`, `s04-sn3` for Should-NOT gates. Total entries: 14 success + 3 gate = 17.

## Process Note

**Authorship of this Evaluator Review:** The `## Evaluator Review` section below was authored by the main-thread orchestrator, not by a forked Evaluator subagent. Two consecutive Evaluator subagent dispatches investigated the contract thoroughly (the second reached 41 tool calls confirming SN1 glob and bootstrap-variance edge cases) but neither completed a `Write` of the review section before its turn budget ran out — both ran investigative shell commands productively but never reached the synthesis-and-write step. Per `skills/harness-sprint/SKILL.md` "Operational Notes — Evaluator Fallback", the main thread may transcribe the review so the sprint can proceed; this is the documented escape valve, not the preferred path. All verification commands cited below were run verbatim from the contract (the audit chain is preserved); the degraded authorship will count against the `generator_evaluator_separation` rubric dimension in this sprint's eval per the fallback penalty in `skills/harness-sprint/SKILL.md`.

## Evaluator Review

**Status: NEEDS REVISION**

**Round: 1**

### Strengths

- **Weight arithmetic is correct.** C1(12)+C2(10)+C3(4)+C4(8)+C5(9)+C6(7)+C7(4)+C8(10)+C9(10)+C10(8)+C11(2)+C12(2)+C13(6)+C14(8) = 100%. Verified by computation.
- **Behavioral coverage is 100%** — all 14 success criteria carry `rubric_dimension: "behavioral"` in the sibling tasks.json. Far exceeds the ≥60% threshold from [project_behavioral_coverage_rule](memory/project_behavioral_coverage_rule.md).
- **C11 vs C12 plugin-exit distinction is correct.** C11 scopes to `tests/judge/` only (no Sprint-2 pytest plugin test there) and uses `[ "$EC" = "0" ]`; C12 covers `tests/runner/` (which holds `test_plugin_exit.py`) and uses the `( [ "$EC" = "0" ] || [ "$EC" = "100" ] )` disjunction. This is exactly the Sprint 3 lesson applied correctly.
- **`tee` exit-code masking is handled** in the two holistic criteria (C11 + C12) via `EC=${PIPESTATUS[0]}` plus the three-guard pattern (`grep -E "passed" && ! grep -qE "FAILED|ERROR" && [ EC = 0 ]`). C1–C10 scope to single `-k` test functions with `grep -q "PASSED"` — sufficient because the `&&` chain short-circuits on pytest failure.
- **Should-NOT design** — SN1 / SN2 / SN3 mirror Sprint 3's pattern faithfully (apart from the SN1 baseline bug below). SN2 verified empirically: `git grep` for `langgraph|ragas|pgvector|fastapi` against the current branch returns no matches, exits 0, prints `PASS`. The 17 tasks.json entries (14 + 3) match the markdown one-for-one.
- **Reference Solutions are well-anchored.** Two LLM-judge criteria (C13 for CoT-rubric scorer, C14 for three-tier dispatcher) each have a full code-shape reference with explicit PASS/FAIL conditions. Two independent evaluators reading C14 (tier isolation, no auto-escalation, judge_model never called for code tier) would agree.
- **All 17 tasks.json entries pass `bash -n` syntax check** on their `verification_command` strings — no shell-syntax errors in any criterion.
- **Coverage of sprint features is complete.** Every feature listed in `sprints.json` Sprint 4 has at least one criterion: CoT-rubric scorer (C1/C2/C3/C13), binary judge TPR/TNR (C4), bootstrap CI (C6/C7), three-tier grading (C8/C9/C14), human annotation queue (C10), 50-item calibration fixture (C5).

### Issues

#### Issue 1 — SN1 verification command empirically FAILS on the current branch (BLOCKING)

The SN1 command computes its diff baseline as `git merge-base HEAD main`, which resolves to `8617c2f` — a commit that **predates the entire Phase 2 Python build** (Sprints 00, 01, 02, 03). When the Phase-2 prior-sprint glob is widened from Sprint 3's `sprint-0[12]*.md` to Sprint 4's `sprint-0[123]*.md`, it now matches `.harness/contracts/phase-02/sprint-03.md` and `.harness/evals/phase-02/sprint-03-*.md`. The diff against `8617c2f` shows those files as `new file mode 100644` (they did not exist at the baseline), so SN1 produces non-empty output and exits 1.

**Empirical evidence (run against this branch, current HEAD `894b2ee`):**

```
$ git merge-base HEAD main
8617c2f6fddd915e9d2cc85945ceb424895c7249

$ bash -c 'BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~$(git rev-list --count HEAD)^); diff_out=$(git diff $BASE..HEAD -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" ".harness/contracts/phase-02/sprint-0[123]*.md" ".harness/contracts/phase-02/sprint-1*.md" ".harness/evals/phase-02/sprint-0[123]*.md" ".harness/evals/phase-02/sprint-1*.md" 2>/dev/null); [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" | head -10 && exit 1)'
FAIL
diff --git a/.harness/contracts/phase-02/sprint-03.md b/.harness/contracts/phase-02/sprint-03.md
new file mode 100644
index 0000000..50afbf3
--- /dev/null
+++ b/.harness/contracts/phase-02/sprint-03.md
@@ -0,0 +1,493 @@
+# Sprint 03 Contract: Prompt caching and Batch API
...
exit 1
```

Sprint 3 only "passed" SN1 with this same `merge-base HEAD main` baseline because its narrower glob (`sprint-0[12]*.md`) did not match `sprint-03.md`. Sprint 4 cannot use the same trick — sprint-03 is now a finalized prior sprint that MUST be protected, but the merge-base baseline predates it.

**The intent of SN1 is "don't modify prior-sprint files DURING this sprint's work."** The current implementation reads "any diff against the merge-base with main," which conflates Phase-2 file creation with Sprint-4 modification. As long as `main` predates Phase 2, the merge-base approach is structurally broken for any Phase-2 sprint whose glob covers another already-committed Phase-2 sprint.

**Fix (recommended).** Replace the merge-base baseline with a "scope to this sprint's commits" approach. Two options, in order of preference:

- **Option A (commit-scoped diff)** — iterate over commits whose subject contains `sprint-04` (matching the conventional commit prefix this sprint uses) and check each one's modifications against the prior-sprint glob:
  ```bash
  bash -c '
    failed=0
    SPRINT_COMMITS=$(git log --format=%H --grep="(sprint-04)" 2>/dev/null)
    for c in $SPRINT_COMMITS; do
      diff_out=$(git diff "${c}^".."${c}" -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" ".harness/contracts/phase-02/sprint-0[123]*.md" ".harness/contracts/phase-02/sprint-1*.md" ".harness/evals/phase-02/sprint-0[123]*.md" ".harness/evals/phase-02/sprint-1*.md" 2>/dev/null)
      if [ -n "$diff_out" ]; then echo "FAIL: $c modified prior-sprint files"; echo "$diff_out" | head -20; failed=1; fi
    done
    [ "$failed" = "0" ] && echo PASS || exit 1
  '
  ```
  This is semantically correct: it only flags a FAIL when a `sprint-04` commit actually touched a prior-sprint file. When no sprint-04 commits exist yet (e.g., during contract review), the loop does nothing and exits PASS. When sprint-04 has commits, each commit's `c^..c` diff is checked individually.

- **Option B (previous-sprint-completion baseline)** — pin the baseline to the commit that marked the previous sprint complete (`harness: complete sprint 03 (Phase 2) evaluation` = `894b2ee`):
  ```bash
  bash -c '
    BASE=$(git log --grep="harness: complete sprint 03" --format=%H -1 2>/dev/null)
    BASE=${BASE:-$(git merge-base HEAD main)}
    diff_out=$(git diff $BASE..HEAD -- ".harness/contracts/sprint-0[1-9]*.md" ".harness/contracts/sprint-1*.md" ".harness/evals/sprint-0[1-9]*.md" ".harness/evals/sprint-1*.md" ".harness/contracts/phase-02/sprint-0[123]*.md" ".harness/contracts/phase-02/sprint-1*.md" ".harness/evals/phase-02/sprint-0[123]*.md" ".harness/evals/phase-02/sprint-1*.md" 2>/dev/null)
    [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" | head -20 && exit 1)
  '
  ```

Option A is preferred — it does not rely on commit-message search-string conventions for the baseline and is more robust to future workflow changes. Update the SN1 verification_command in BOTH the markdown contract AND the sibling `.harness/contracts/phase-02/sprint-04.tasks.json` (entry `s04-sn1`).

#### Issue 2 — C7 (bootstrap variance) accepts a trivially-broken bootstrap (BLOCKING)

C7's verification text says:
> assert `width_10 >= width_1000` (...) or, if the test uses a fixed seed that produces the opposite, the test may instead assert that the two widths are different — at minimum, `ci_10 != ci_1000`.

A trivially-broken `bootstrap_ci` that always returns the same `BootstrapCI(0.0, 1.0, 0.95)` regardless of `n_resamples` satisfies `width_10 >= width_1000` (because both are `1.0`, so `1.0 >= 1.0` is true). It does NOT satisfy `ci_10 != ci_1000` — but the OR disjunction makes the criterion PASS as long as either clause holds. Combined with C6's tolerant checks (`lower <= 1.0 <= upper` for `[1.0]*100` and `lower <= 0.5 <= upper` for the mixed list), the trivial `(0.0, 1.0)` bootstrap also passes C6.

Net effect: a bootstrap implementation that completely ignores `n_resamples` and returns a constant `(0.0, 1.0)` interval would earn 7% (C6) + 4% (C7) = 11% of the sprint's weight. The criteria as written cannot distinguish a real bootstrap from a no-op stub.

**Fix.** Tighten C7 to require the CI actually responds to `n_resamples`. A minimal addition: require that at LEAST ONE of {lower, upper} differs between the two calls. Recommended C7 text:

> ... (c) call `bootstrap_ci(scores, n_resamples=1000)` and record `width_1000`, (d) assert `ci_10.lower != ci_1000.lower OR ci_10.upper != ci_1000.upper` (the two intervals must not be byte-identical — proves the resampling actually responds to `n_resamples`), and (e) assert `width_10 >= width_1000` OR `width_10 != width_1000` (allowing either direction of width change while requiring some response).

The new clause (d) catches the constant-output bootstrap; clause (e) preserves the existing flexibility for fixed-seed scenarios.

#### Issue 3 — C13 field-name ambiguity could split independent evaluators (ADVISORY)

C13's prose at line 87 says the implementation must "(e) store the full judge response text in `Score.reasoning` (not just the extracted verdict)." Technical Notes at lines 267–268 acknowledges Sprint 1's `Score` model has `explanation` but no `reasoning`, and says "the Evaluator must accept either name." This dependency on a separate Technical Note creates a risk: an evaluator reading C13's text strictly could FAIL the criterion if the field is named `explanation`, while one reading the Technical Note would PASS it.

The Sprint 3 lesson learned (per the Round 2 review of sprint-03's reference solution) was to embed acceptance criteria DIRECTLY in the criterion text. C13 should do the same.

**Fix (advisory).** Update C13's clause (e) to:

> (e) store the full judge response text in `Score.reasoning` (preferred) OR `Score.explanation` (acceptable if the Generator chose to reuse Sprint 1's existing field) — the full CoT text must be present, regardless of which field name is used. Storing only the extracted verdict token (PASS/FAIL/1/0) rather than the full response is FAIL.

The fix is advisory rather than blocking because the Technical Note IS present and the canonical Evaluator process is to read top-to-bottom. But aligning the criterion text with the Technical Note removes a calibration ambiguity at no cost.

### Missing Criteria

None. Every sprint-feature listed in `sprints.json` (cot-rubric-scorer-golden-answer, binary-judge-tpr-tnr, bootstrap-ci-aggregates, three-tier-grading-code-model-human, human-annotation-queue-skeleton, 50-item-calibration-set) is covered by at least one criterion.

### Notes

- The C13 reference solution shows `Score(value=value, reasoning=response_text, metadata={...})` — assuming `Score.reasoning` exists. If the Generator adds a `reasoning` field to `Score` in `src/trine_eval/core/score.py`, that change is itself a Sprint 1 file modification. SN1's prior-sprint glob is `sprint-0[1-9]*.md` for Phase-1 root contracts (Sprint 1's Phase-1 contract files), but `Score` lives at `src/trine_eval/core/score.py` — outside the SN1 scope. So adding `Score.reasoning` is permitted and does not trip SN1.
- Sprint 3's Round 2 eval graded SN1 PASS with the verbatim `merge-base HEAD main` baseline. That worked because Sprint 3's glob `sprint-0[12]*.md` did not match sprint-03.md. Issue 1 above is not a Sprint 3 regression — it is a structural flaw that Sprint 4 is the first to expose by widening the glob to include a prior Phase-2 sprint.
- C11 (full judge test suite) carries only 2% weight, and C12 (regression in tests/runner/ tests/models/ tests/core/) also carries only 2%. These are appropriately small because individual criteria C1–C10 cover the granular pass/fail signals — C11/C12 are the holistic safety nets. The weight allocation reflects this correctly.
- All three Should-NOT gates carry `weight: 0` in tasks.json with `is_gate: true` — the correct shape per `rules/harness-conventions.md`.
- The Generator's reported "Behavioral coverage: 100%" matches the empirical tasks.json computation (100/100 success-criterion weight is tagged `behavioral`). All other rubric_dimension values in tasks.json are `structural` (SN1, SN2) or `behavioral` (SN3) — consistent with the convention that Should-NOT gates may be structural even when success criteria are behavioral.

## Revision Notes (Round 1 → Round 2)

- **Issue 1 (SN1 baseline — BLOCKING):** Replaced the merge-base diff approach with a commit-scoped diff that iterates over `(sprint-04)`-prefixed commits. The critical fix was adding a sprint-03 Phase-2 completion anchor (`S03BASE=$(git log --grep="complete sprint 03 (Phase 2)")`) used as `^$S03BASE` in the git log range, which excludes historical Phase-1 commits that also carry the `(sprint-04)` subject pattern. Without this exclusion the Option A command from the Evaluator Review would find two Phase-1 commits (dated 2026-04-13) that legitimately created `.harness/contracts/sprint-04.md` (the Phase-1 root-level sprint-04 contract) and incorrectly flag them as SN1 violations. The revised command exits 0 (PASS) on the current branch since no Phase-2 sprint-04 commits exist yet. Changes: SN1 prose at lines 95–99 and the bash block at line 97; `s04-sn1.criterion` and `s04-sn1.verification_command` in tasks.json.

- **Issue 2 (C7 trivial-bootstrap loophole — BLOCKING):** Added clause (d) requiring `ci_10.lower != ci_1000.lower OR ci_10.upper != ci_1000.upper`, which catches a constant-output bootstrap that always returns `(0.0, 1.0)` regardless of `n_resamples` (such an implementation satisfies `width_10 >= width_1000` via equality but cannot satisfy the new non-identity check). Renumbered the original clause (d) to (e). The criterion title was updated from "wider CI" to "different CI" to match the tightened semantics. Changes: C7 at lines 49–53 in the markdown; `s04-c7.criterion` in tasks.json.

- **Issue 3 (C13 field-name ambiguity — ADVISORY):** Updated C13 clause (e) to embed the acceptance-of-both-field-names directly in the criterion text, matching the Technical Note at lines 267–268. The old text said only `Score.reasoning`; the revised text says `Score.reasoning` (preferred) OR `Score.explanation` (acceptable) and makes the full-CoT requirement explicit with a FAIL condition for storing only the verdict token. This removes the dependency on a separate Technical Note for calibration and aligns with Sprint 3's lesson about embedding acceptance criteria inline. Changes: C13 at lines 87 in the markdown; `s04-c13.criterion` in tasks.json.

## Evaluator Review — Round 2

**Status: APPROVED**

**Round: 2**

### Verification of Round 1 fixes

- **Issue 1 (SN1 commit-scoped diff): VERIFIED** — The SN1 `verification_command` in tasks.json entry `s04-sn1` now uses the commit-scoped diff approach with the S03BASE anchor. Running the command verbatim (extracted from tasks.json via `python -c "import json; print(json.load(...)['tasks'][14]['verification_command'])"` and then executed via `bash`) produced exit code 0 and printed `PASS`. The anchor `S03BASE=$(git log --format=%H --grep="complete sprint 03 (Phase 2)" -1)` resolves to `894b2ee634c0de47fdc1f576c5a2913a2f3b1cef`, which correctly excludes two historical Phase-1 commits that carry `(sprint-04)` in their subject (commits `1c984d7` and `a09eb1d`, predating Phase 2). After the exclusion, `SPRINT_COMMITS` is empty — the loop runs zero iterations and exits PASS. The keyword `S03BASE` appears on lines 97 and 99 of the markdown contract, confirming both the bash block and the prose description were updated consistently.

- **Issue 2 (C7 trivial-bootstrap catcher): VERIFIED** — C7 in the markdown (lines 49–53) now includes the required clause (d): `assert ci_10.lower != ci_1000.lower OR ci_10.upper != ci_1000.upper`. The same text appears verbatim in `s04-c7.criterion` in tasks.json. The trivial-bootstrap loophole analysis confirms the fix works: a bootstrap that always returns `BootstrapCI(0.0, 1.0, 0.95)` regardless of `n_resamples` produces `0.0 != 0.0 OR 1.0 != 1.0` = `False OR False` = `False`, which FAILS clause (d) as required. The old clause (d) has been renumbered to (e) and the criterion title updated to "different CI" — both consistent with the fix description in Revision Notes.

- **Issue 3 (C13 field-name acceptance): VERIFIED** — C13 clause (e) in the markdown (line 87) now reads: "store the full judge response text in `Score.reasoning` (preferred) OR `Score.explanation` (acceptable if the Generator chose to reuse Sprint 1's existing field) — the full CoT text must be present, regardless of which field name is used. Storing only the extracted verdict token (PASS/FAIL/1/0) rather than the full response is FAIL." The same text appears verbatim in `s04-c13.criterion` in tasks.json. The ambiguity that required an evaluator to cross-reference the Technical Note is resolved.

### Sanity checks

- **Tasks.json:** 17 total entries, 14 success criteria, 3 gates, total weight = 100%, behavioral weight = 100% — all verified by running the python sanity command (exit 0).
- **Round 1 Evaluator Review and Process Note:** Both sections (`## Process Note` at line 292 and `## Evaluator Review` at line 296) are present and unmodified. Confirmed by reading the file top-to-bottom; no structural changes to those sections were introduced by the Round 2 revision.

### Final verdict

**APPROVED** — All three Round 1 issues (two BLOCKING, one ADVISORY) are empirically verified as fixed; contract structure, weights, and behavioral coverage are unchanged.
