---
name: sprint-contract
description: Template and protocol for Generator-Evaluator sprint contract negotiation
allowed-tools: Read, Write
---

# Sprint Contract

This skill provides the contract template and negotiation protocol for Generator-Evaluator agreement on sprint success criteria.

## Negotiation Protocol

1. **Generator proposes first** — Writes a draft contract using the template below
2. **Evaluator reviews** — Checks each criterion for:
   - **Testability:** Can this be verified automatically? (If it requires human judgment, it needs rewording)
   - **Completeness:** Are there obvious features in the sprint scope that have no criterion?
   - **Specificity:** Would two independent evaluators agree on pass/fail for this criterion?
3. **Revision rounds** — Max rounds configured in `.harness/config.json` (`contract_negotiation_rounds`, default 2)
4. **Timeout** — If the Evaluator hasn't responded after the Generator's proposal, proceed with the proposal as-is

## Contract Template

See `template.md` in this skill's directory for the full template.

## Weighted Criteria

Every success criterion carries a percentage weight reflecting its importance to the sprint deliverable.

**How to assign weights:**
- Higher weight = more important to the sprint's success. Weight critical functionality higher than cosmetic concerns.
- Typical range: 5–15% per criterion. Avoid concentrating >20% on a single criterion unless it is the sprint's core deliverable.

**Weight sum rule:** Success criteria weights must sum to exactly 100%. The evaluator computes a weighted score by multiplying each criterion's weight by its pass/fail result (1 or 0) and summing. This weighted score determines whether the sprint meets its pass threshold — a sprint can pass despite minor criterion failures if the weighted total exceeds the configured threshold.

**Should-NOT criteria do not carry weights.** They are gates: any Should-NOT failure is an automatic sprint FAIL regardless of the weighted score.

## Grader Types

Each criterion must be tagged with one of three grader types:

- **Behavioral** — Verified by *running* the artifact (invoking a skill, triggering a hook, executing a binary, calling a function) and observing the output, state change, or side effect. The strongest form of evidence: it proves the feature works, not just that the code exists.
- **Structural** — Verified by inspecting an artifact at rest (grep, jq, schema check, file existence, frontmatter field). Use for cheap pre-flight checks that gate a behavioral criterion, or for genuinely static artifacts (documentation, config schemas with no runtime).
- **LLM-as-judge** — Requires reading comprehension, subjective assessment, or nuanced evaluation that no command can capture. Use when neither behavioral nor structural verification is feasible.

**Behavioral coverage rule:** Behavioral criteria must hold **≥ 60% of total weight** across all success criteria. If a sprint genuinely has no behavioral surface (e.g., it produces only static documentation), state the reason in the contract's `## Technical Notes` so the Evaluator can verify the exception during contract review.

The evaluator attempts code-based verification first for every criterion (behavioral and structural both qualify). It falls back to LLM judgment only when the criterion genuinely requires subjective assessment. Crucially, the evidence standard differs by tag: behavioral criteria require execution evidence (command + observed result); structural criteria accept artifact inspection; reading-the-source to confirm a behavior is documented does NOT satisfy a behavioral criterion.

## Negative (Should-NOT) Criteria

Should-NOT criteria define behaviors that must NOT occur. They are graded **PASS when the behavior is absent** — the opposite of normal criteria.

Use Should-NOT criteria for:
- Regression guards (don't break existing functionality)
- Security invariants (don't expose stack traces, don't leak credentials)
- Architectural boundaries (don't violate separation of concerns)

## Edge Case Criteria

Edge case criteria are an **optional** third class of contract criterion, distinct from the 100%-weighted Success Criteria and from Should-NOT gates. They are tracked separately because they answer a different question.

- **Success Criteria** ask: "Does the deliverable do what it should?" Weighted to 100% in aggregate; the weighted score is the headline pass-rate metric.
- **Should-NOT Criteria** ask: "Does the deliverable avoid behaviors it shouldn't?" Binary gates; any failure blocks the sprint.
- **Edge Case Criteria** ask: "Does the deliverable handle ambiguous, boundary, or adversarial inputs correctly?" Tracked as a separate **edge-case pass rate** metric in `harness-summary`, *not* folded into the weighted total.

**Why separate, not folded into the weighted total.** Folding edge cases into the 100% weighted score would be a one-sided eval — the same failure mode Anthropic's playbook calls out as "positive-case-and-negative-case-by-luck." An agent that passes only the obvious positive cases would earn the same weighted score whether or not it correctly declined the ambiguous ones; the asymmetry would be invisible. Reporting edge-case pass rate as a distinct metric makes the asymmetry visible and lets the operator decide how to weight robustness vs. core functionality. If a sprint scores 100% weighted but 30% on edge cases, that is a genuinely different outcome from 100% weighted with 95% on edge cases — and the eval should surface that difference.

**Why optional.** Not every sprint is the right place for edge-case criteria. A sprint that delivers a pure mechanical refactor or a documentation-only change adds no signal from edge-case scoring. The contract template includes the section as an optional slot; sprints that omit it produce the same `tasks.json` shape they would have produced before Sprint 10 — Should-NOT gates and weighted Success Criteria continue to be the only two entry classes.

**Per-rubric guidance.** During contract review, the Evaluator should propose edge-case coverage when the rubric is one of:

- **`web-app`** — well-known edge cases include: empty form submissions, max-length input fields, malformed URLs, concurrent state updates, browsers with JavaScript disabled, viewport extremes (320px and 4K), keyboard-only navigation.
- **`api-service`** — empty request bodies, oversized payloads, malformed JSON, concurrent identical requests, rate-limit boundaries, expired auth tokens, idempotency edge cases.
- **`rag-system`** — empty queries, very long queries, queries with no matching documents, queries that span document boundaries, queries containing the answer key verbatim, citation hallucination on out-of-corpus queries.

For `cli-tool` and `eval-harness` deliverables, the Evaluator may skip the edge-case recommendation — those rubrics typically encode their edge-case concerns directly in the dimension scoring tables, and adding a separate edge-case section adds noise without signal.

**How edge cases are graded.** Each edge case criterion is graded PASS or FAIL using the same code-based-first hierarchy as Success Criteria. The difference is what the harness does with the result: edge-case PASS/FAIL counts go into the **Edge Case Pass Rate** metric (see `skills/harness-summary/SKILL.md`), not into the weighted score. A sprint with 10 edge case criteria where 7 pass reports an Edge Case Pass Rate of 70% — independent of whether the weighted score was 100% or 60%.

## Functional Smoke Criteria

Functional Smoke criteria are a **fourth** class of contract criterion, complementary to mocked Success Criteria, Should-NOT gates, and Edge Case criteria. They exercise the deliverable against **real external systems** (live Anthropic API, real Docker, real filesystem, real judge model) to validate that code which passes architectural mocked tests also functions end-to-end. They were added in Sprint 07 alongside the `Functional Integration Coverage` rubric dimension.

**Why separate from Success Criteria.** A mocked test that asserts the right argv shape ships next to code that returns a beautifully-structured response — both pass — but the code may not actually trigger a cache hit, demultiplex a real batch result, or run a real container. Folding functional smoke into the 100% weighted total would let a sprint claim "100% coverage" on mocked tests alone; reporting smoke separately makes the asymmetry visible. The Functional Integration Coverage rubric dimension (10% weight) consumes the smoke pass rate plus structural indicators (env-var gating, budget cap, fixture parity).

**Gating and budget.** Live-API smoke tests are gated by env vars (`TRINE_EVAL_LIVE_API=1`, `TRINE_EVAL_LIVE_DOCKER=1`, etc.) so CI default skips them. Each sprint's combined live-API spend must stay under the budget defined in `config.json` `functional_smoke.budget_usd` (currently $1.00/sprint), enforced via the runner's existing `cost_limit` parameter. Recorded fixtures (VCR-style JSON, replay-style captures) are an acceptable substitute when live cost is prohibitive; they preserve the functional signal without the per-run dollar cost.

**Where smoke tests live.** Place them under `tests/smoke/<system>/test_<feature>_live.py`. The pytest `skipif` boilerplate at the top of each file gates on the relevant env var. The conventions doc (`rules/harness-conventions.md` — see "Architectural vs Functional Verification") is the source of record for the directory layout and env-var registry.

**How smoke results are graded.** Each Functional Smoke criterion is graded PASS or FAIL using the same code-based-first hierarchy as Success Criteria. The result feeds the **Functional Smoke Pass Rate** metric in `harness-summary` and informs the `Functional Integration Coverage` rubric dimension. A sprint with 4 smoke criteria where 3 pass reports a Functional Smoke Pass Rate of 75%, independent of the weighted Success Criteria total.

## Reference Solutions

Reference solutions provide known-working outputs for criteria where grader calibration is valuable. They are **optional** — not every criterion needs one.

**When to include a reference solution:**
- LLM-as-judge criteria benefit most (reduces inter-judge disagreement)
- Criteria where the expected format/structure might be ambiguous
- The highest-weighted criterion in the contract should have one if it is LLM-judged

**Purpose:** Reference solutions calibrate grader accuracy. They give the evaluator a concrete example of what PASS looks like, reducing the chance of false-fail or false-pass judgments.

## Task Taxonomy: sprint-NN.tasks.json

After the contract is approved (Status: APPROVED from the Evaluator review), emit a sibling
`.harness/contracts/sprint-{NN}.tasks.json` file alongside the markdown contract. This is the
**machine-readable source of record** for the sprint's criteria — it feeds the regression gate
(Step 0.5), the Batch API submission grouping (Step 3d), and the harness-summary
saturation-graduation step that promotes always-passing criteria into a regression suite.

**When to emit:** right after the Evaluator writes `**Status: APPROVED**` and before the
Generator enters IMPLEMENTATION mode. Guarded by `config.taxonomy.emit_tasks_json`
(default `true`).

**Schema:** one entry per criterion in the approved contract — both Success Criteria and
Should-NOT gate criteria.

```json
{
  "sprint": 9,
  "tasks": [
    {
      "task_id": "s09-c1",
      "criterion": "<verbatim criterion text from the contract>",
      "grader_type": "behavioral",
      "weight": 8,
      "is_gate": false,
      "verification_command": "jq -e '.trials' .harness/config.json",
      "rubric_dimension": "methodology_completeness",
      "bucket": 1
    },
    {
      "task_id": "s09-sn1",
      "criterion": "<Should-NOT criterion text>",
      "grader_type": "structural",
      "weight": 0,
      "is_gate": true,
      "verification_command": null,
      "rubric_dimension": "generator_evaluator_separation",
      "bucket": 2
    }
  ]
}
```

**Field semantics:**

- `task_id` — Stable identifier: `s<NN>-c<N>` for success criteria (numbered from 1),
  `s<NN>-sn<N>` for Should-NOT gates. Stability matters because regression gates and
  transcript correlation key off this id across trials.
- `criterion` — Verbatim criterion text from the markdown contract (no paraphrasing).
  This is what the Evaluator and downstream tools read.
- `grader_type` — `"behavioral"`, `"structural"`, or `"llm-judge"`, matching the tag in
  the markdown contract. The legacy 2-way deterministic/llm-judge enum is superseded —
  use `"behavioral"` or `"structural"` instead of `"deterministic"`.
- `weight` — The percentage weight from the markdown contract. Gate (Should-NOT) criteria
  use `0` — they are binary, not weighted.
- `is_gate` — `true` for Should-NOT gates, `false` for scored success criteria.
- `verification_command` — For behavioral and structural criteria, a runnable shell command
  whose exit code determines PASS/FAIL (see "Exit-Code-Faithful Verification Commands" below).
  For llm-judge criteria, `null`. The regression gate executes these commands directly.
- `rubric_dimension` — Which rubric dimension this criterion informs. Valid values for this
  project: `methodology_completeness`, `grading_architecture`, `generator_evaluator_separation`,
  `context_engineering`, `extensibility_aci`, `functional_integration_coverage`. Used by
  harness-summary for per-dimension rollups and by Batch API submission for grouping.
- `bucket` — Integer `1`, `2`, or `3`, matching the bucket framework in
  [`../../rules/harness-conventions.md`](../../rules/harness-conventions.md) → "Three Buckets
  of Verification". Used by `harness-summary` to compute bucket distribution per sprint and
  feed the `Functional Integration Coverage` rubric dimension. Sprint contracts authored
  before Sprint 07 do not carry this field; the summary skill treats missing-`bucket` as
  `1` (the most conservative reading) for those legacy entries.

**Emission process:** The Generator (or main thread in minimal mode) writes the JSON file after reading the approved contract. The Evaluator does not need to review the JSON separately — it is a mechanical transcription of the approved markdown contract, and any drift between the two is caught by the Evaluator's subsequent reads of both files during the EVALUATION step.

## Before Submitting: Authoring Checklist

Before handing the contract to the Evaluator, the author (Generator subagent or main thread in minimal mode) walks the following checklist. Each item below was empirically caught in a prior sprint's negotiation round; the checklist exists to prevent recurrences, not to enumerate hypothetical traps.

**The reference-solution-must rule.** The highest-weighted LLM-as-judge criterion **must have a reference solution**. Without one, the grader has no calibration anchor, two independent evaluators are likely to disagree, and the criterion's pass/fail signal becomes noise. If multiple criteria are tied at the top weight, the most subjective of them gets the reference solution. Lower-weighted LLM-judge criteria are encouraged but not required to carry one.

### Authoring Checklist (five trap categories)

These are the recurring authoring mistakes the Evaluator has flagged across Sprints 6–11. Walk every deterministic criterion through all five before submission.

1. **multi-line trap.** Does the verification command use a single-line `grep` or `grep -q` over content that actually spans multiple lines? YAML frontmatter blocks, multi-line code fences, and JSON pretty-printed across multiple lines are common offenders — `grep` matches on a line at a time. When the target genuinely spans lines, switch to `awk` over the relevant block (as in Sprint 12 C1's `awk '/^---$/{c++; next} c==1'` for frontmatter), or use `python` to parse the file. If a `grep` pattern looks like it should match a multi-key YAML or multi-line JSON value, it almost certainly will not.

2. **permutation trap.** Does the verification command rely on a regex that requires elements to appear in a specific order, when the order is not actually contractually required? `grep -E 'A.*B.*C'` is fragile against any reordering by the implementer — and rewriting in alphabetical order is a legitimate refactor. Prefer chained independent `grep -q` calls (`grep -q A && grep -q B && grep -q C`) so the verification stays robust to ordering.

3. **pre-existing trap.** Does the verification command match content that ALREADY exists in the file before the sprint starts? A criterion that grades PASS on the unmodified pre-Sprint-N codebase is not a criterion — it's a tautology. Before submitting, run each verification command against the current `HEAD` (no implementation yet) and confirm the result is FAIL. When a needed phrase happens to already exist (e.g., `weight sum` already in `skills/sprint-contract/SKILL.md` line 33), add a unique-marker anchor (`Authoring Checklist`) that quarantines the new content from the existing match.

   **Baseline-math corollary.** When the verification command is a threshold-style grep count (e.g., `grep -c X >= N`), confirming pre-implementation FAIL is not enough — the threshold `N` must require the count to **grow above the pre-implementation baseline**, not merely exceed zero. Two corrective patterns: (a) anchor on a unique-to-new-code constant introduced by the contract (e.g., a new module-level constant like `_EXPECTED_MODEL_KEYS` whose baseline count is 0); (b) set the threshold to `baseline + N_required_new_callsites` (e.g., grep target with baseline 6 from imports + docstring requires threshold `>= 7` for one new call site). The pre-implementation check must record BOTH the baseline count AND the post-implementation requirement, not just "this currently FAILs". A baseline of 3 with threshold `>= 2` is a tautology even though baseline > 0.

4. **weight sum trap.** Do the per-criterion weights sum to exactly 100%? Add them up by hand or with a one-liner before submitting. Sums of 95%, 105%, 110% are the most common — they slip past visual inspection because criteria look reasonable individually. The Evaluator will reject any contract whose weights do not sum to 100%.

5. **prose-vs-verification trap.** Does the criterion's English prose actually describe what the verification command runs? When the prose says "verify the file contains a markdown table" but the command is `grep -q '|'`, the prose is over-promising — the grader is grading something narrower than the prose claims. Either tighten the prose to match the command exactly, or strengthen the command to verify what the prose claims. The two must be the same test.

6. **bucket discipline trap.** Is the verification command bucket 1 (`grep -q "X" file.md`, `assert key in dict`, `[ -f path ]`) when a bucket 2 (behavioral with mocks) version would catch more? See `rules/harness-conventions.md` → "Three Buckets of Verification" for the canonical definitions. Bucket-1 criteria only verify that plumbing exists — a deliverable could ship at 100% PASS with bucket-1-only criteria while being non-functional at runtime. For every criterion authored as bucket 1, ask: "If I replaced this with a behavioral test that asserts an *outcome* of running the new code, would the test be feasible?" If yes, replace it. Bucket 1 is acceptable only when the deliverable is genuinely plumbing-only (a config key must be present; a convention must be documented). When the deliverable is behavior (a new function, a new agent instruction, a new sprint workflow), the verification must assert behavior. For harness-side deliverables whose "behavior" only manifests when an agent reads and acts on a new instruction, the bucket-2 pattern is **subagent-driven verification**: spawn a real subagent via the `Task` tool with a constructed input, assert on the subagent's output. This pays no raw API cost — the subagent uses Claude Code's existing auth chain. See the "Subagent-Driven Behavioral Verification" subsection below for the pattern.

If any item fails, fix the contract before invoking the Evaluator. Catching these at authoring time saves a negotiation round.

### Subagent-Driven Behavioral Verification

Most harness-side deliverables (a new skill section, an updated agent prompt, a new convention) only manifest as observable behavior when an agent reads and acts on them. The bucket-1 verification "the documentation landed" (`grep -q "X" agents/evaluator.md`) is cheap but catches only the gross omission. The bucket-2 verification is "an agent reading that documentation actually behaves differently" — and the cheap way to get there is to spawn a real subagent.

**Pattern.** Author the criterion's verification as a script that:

1. Constructs an input that should trigger the new behavior (a 10+-criterion contract for the Evaluator turn-budget guidance; a draft contract with a Windows-bash anti-pattern for the cross-platform-verification guidance; etc.).
2. Spawns the relevant subagent (`Task` with `subagent_type` matching `Generator`, `Evaluator`, or `general-purpose`) with that input and a focused prompt.
3. Asserts on the subagent's output — does the eval file appear with skeleton-then-fill structure? Did the Generator flag the anti-pattern in contract review? Etc.

**Cost.** The subagent runs through Claude Code's existing auth chain — no separate `ANTHROPIC_API_KEY`, no separate budget. The cost is the user's existing Claude Code session tokens, the same tokens spent on every other subagent dispatch in normal workflow. For verifications that need to be deterministic and fast in CI, prefer a smaller fixture-style verification; the subagent-driven version is best run on-demand or in a less-frequent verification cadence.

**Example.** For the R4 deliverable (Turn-budget defensive authorship in `agents/evaluator.md`), the bucket-1 verification is `grep -qE '^## Turn-budget defensive authorship' agents/evaluator.md`. The bucket-2 subagent-driven verification would:

```python
# Pseudo-pattern
spawn_subagent(
    subagent_type="Evaluator",
    prompt="Evaluate the synthetic 12-criterion contract at tests/fixtures/turn-budget/contract-12-criteria.md against tests/fixtures/turn-budget/rubric-stub.md. Write the eval to /tmp/eval-out.md.",
)
# After dispatch, assert on /tmp/eval-out.md:
assert eval_file_exists("/tmp/eval-out.md")  # file landed
assert "pending" in initial_file_state         # skeleton-first pattern was used
assert all_criteria_have_results(final_state)  # evidence was filled in
```

The bucket-2 verification catches the regression "documentation lands but agent doesn't follow it" — the actual failure mode Sprint 04 hit before R4 existed. The bucket-1 verification can't catch that.

## Cross-platform verification commands

Every Phase 2 R1 failure was a verification-command bug — never an implementation bug. Three concrete patterns kept biting, all preventable at contract-authoring time. Each pattern below is the *fix*; the trap is the natural-looking command you'd otherwise write.

**1. Windows shell routing.** `python -c "subprocess.run(cmd, shell=True)"` routes through `cmd.exe` on Windows and cannot parse bash syntax (no `set -e`, no `[[ ]]`, no arrays). Sprint 00 C4 shipped this and failed empirically on the operator's Windows machine. Fix template — invoke Git Bash explicitly when you must wrap a bash command in Python:

```python
import os, subprocess
bash = r'C:\Program Files\Git\usr\bin\bash.exe' if os.name == 'nt' else 'bash'
subprocess.run([bash, '-c', cmd], check=True)
```

Prefer a single `bash -c '...'` invocation over the Python wrapper when no Python pre-processing is needed — `bash` exists on Windows via Git for Windows and is the harness's target shell.

**2. Glob over-match.** `.harness/evals/sprint-*.md` matches `sprint-00-r1.md` even though sprint-00 is the *current* sprint and should be exempt from a "historical artifacts unmodified" check. Sprint 01 R1 shipped this glob and the SN1 gate failed. Fix template — anchor the digit range and test the glob against `git ls-files` output before contract approval:

```bash
# Restrict to sprints 01-09 and 1x, excluding sprint-00:
git ls-files '.harness/contracts/sprint-0[1-9]*.md' '.harness/contracts/sprint-1*.md'
# Each newly finalized sprint widens the bracket: sprint-0[12]*.md → sprint-0[123]*.md → ...
```

Every gate glob must FAIL when run against a clean pre-implementation checkout *and* PASS when run against a correct post-implementation checkout. Test both before approval.

**3. Exit-code expectations.** `[ "$EC" = "0" ]` rejects exit 100, but Sprint 2's pytest plugin (`pytest_plugin.py` `pytest_sessionfinish`) deliberately overrides session exit to 100 when a `@pytest.mark.trine_eval` test records a score below threshold. Sprint 03 C9's "no regressions" check shipped the strict `= 0` form and failed because the prior-sprint plugin produced exit 100 with all tests passing. Fix template — disjunction plus a redundant content guard:

```bash
EC=${PIPESTATUS[0]}
grep -E "passed" /tmp/output.txt && ! grep -qE "FAILED|ERROR" /tmp/output.txt \
  && ( [ "$EC" = "0" ] || [ "$EC" = "100" ] ) && echo PASS || exit 1
```

The `! grep -qE "FAILED|ERROR"` guard catches genuine test failures even if some other prior-sprint feature introduces a new sanctioned exit code. Document any new intentional exit codes in `rules/harness-conventions.md` so downstream contract authors know to accept them.

## Guidelines for Good Criteria

**Good criterion:** "GET /api/users returns 200 with a JSON array. Each user object contains id (number), name (string), and email (string)."

**Bad criterion:** "The API works correctly." (Too vague — what does "correctly" mean?)

**Good criterion:** "The search bar filters the list in real-time as the user types. Typing 'abc' with 100 items shows only items containing 'abc' within 200ms."

**Bad criterion:** "Search is fast." (What's fast? How do you measure it?)

Each criterion should describe:
- The action to take (input)
- The expected result (output)
- How to verify it (test method)

## No-Op Detection

Before finalizing a contract, run each behavioral and structural criterion's verification command against the current codebase. If a criterion already passes (the grep count meets the threshold, the file already exists, the artifact already produces the expected output, etc.), it is a **no-op** — it provides zero signal about whether the sprint's implementation was successful. Revise no-op criteria by raising the threshold, narrowing the search scope, choosing a different observable result, or replacing with a criterion that tests new content specifically. No-op structural criteria are especially dangerous because they pass even when nothing was built.

## Exit-Code-Faithful Verification Commands (regression-graduation discipline)

Any criterion whose `verification_command` might later be **graduated into the regression suite** (`.harness/regression/regression.json`, consumed by Step 0.5) MUST be **exit-code-faithful**: its exit code alone must encode PASS, because the regression runner records **PASS on exit code 0** and reads nothing else. A command that is correct for a human/LLM Evaluator reading its *stdout* can be silently wrong as a regression gate. Two failure modes recur:

- **Vacuous (always-PASS).** `jq '.x == true' file.json` prints `true`/`false` but **exits 0 regardless** — it can never FAIL as a gate. Use **`jq -e`** so the exit code encodes the boolean (`jq -e` exits 1 on `false`/`null`). Verify non-vacuity: the `-e` form must exit non-zero when the expression is false.
- **Inverted (PASS means the violation).** `test -d "examples"` exits 0 when `examples/` **exists** — but the criterion wants it ABSENT. Use **`test ! -d "examples"`** so exit 0 = absent = PASS. Verify polarity: the form must exit non-zero on the bad state.

Prefer exit-code-faithful forms: **`grep -q`** (exit 0 iff a match), **`jq -e`** (exit encodes the boolean), **`test ! -d` / `test ! -f`** (de-inverted negative assertions), and explicit `&& echo OK` chains. Avoid bare `jq` boolean prints, bare `test -d` for absence checks, and `grep -c …| wc -l` thresholds whose exit code does not encode the count. When in doubt, run the command twice — once on the good state (must exit 0) and once on a deliberately-bad state (must exit non-zero). See `sprint-workflow` Step 0.5 for the companion Windows git-bash invocation hazard.

## SN2 Carve-Out: Renumbering-Only Edits to Approved Contracts

**Scope.** This amendment (introduced in Sprint 13 under the SN2 carve-out) permits
renumbering-only edits to approved markdown contracts when a plan amendment has inserted a
new sprint that shifted all subsequent sprint numbers. These edits are the narrowest possible
post-approval change and carry a mandatory audit trail.

**Permitted edits under the carve-out:**

- Renumbering Sprint N references in approved markdown contracts (e.g., "Sprint 9" →
  "Sprint 10") where the original number was correct at contract-approval time but became
  stale because a plan amendment inserted a new sprint at a lower number.
- Adding a `## Revision History` block to the amended contract file, citing the
  plan-amendment commit and the date of renumbering.

**Forbidden edits — not permitted even under the carve-out:**

- Any change to criterion text, weights, grader type tags, Should-NOT gate text, or
  reference solutions.
- Adding, removing, or reordering criteria.
- Changing prose outside of sprint-number literals in scope (i.e., "Sprint N" renumberings).
- Applying the carve-out without a `## Revision History` block in the amended file. The
  Revision History block is the carve-out's required metadata — omitting it voids the
  carve-out protection and makes the edit indistinguishable from an unauthorized change.

**How to apply the carve-out.** When a plan-amendment commit authorizes renumbering:

1. Identify every occurrence of the stale sprint number in the approved contract file —
   not just the Out of Scope section but the full document (criterion text, Technical Notes,
   Evaluator Review sections, everywhere).
2. Replace each stale "Sprint N" literal with the corrected number.
3. Add or update the `## Revision History` block at the top of the contract file, citing:
   - The plan-amendment commit hash (or "Sprint NN plan amendment" if the commit is not yet
     final at renumbering time)
   - The date of renumbering
   - A one-line description of the change (e.g., "Renumber Sprint 9→10, 10→11, 11→12 per
     DEC-0010 plan amendment")
4. No other changes to the file are permitted.
