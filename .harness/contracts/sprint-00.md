# Sprint 00 Contract: Meta-harness prereqs for Phase 2 Python build

## What I Will Build

Three concrete additions that unblock Sprints 1–6 before any Python code is written: (1) create `.harness/sprint-state.json` so the harness Step 0 session-resumption path works correctly; (2) add a `python_build` section to `.harness/config.json` so Sprint 1 knows where Python source lives, how to invoke the test runner, and what the uv-managed project root is; (3) decide and document the Phase 2 eval file-naming convention (commit the choice between the `sprint-NN+5-offset` scheme and the `phase-02/` subdirectory scheme that `spec.md` left open). The four features cited in `sprints.json` — trials, tasks.json, adaptive thinking, transcript capture — were shipped in Phase 2 meta-sprints 6–12 and are verified-live as written; Sprint 00 does not re-implement them.

## Success Criteria

Each criterion must be independently testable. Weights sum to 100%.

### Deterministic (code-verifiable)

1. **`sprint-state.json` exists and is structurally valid**: `.harness/sprint-state.json` is present, is valid JSON, contains a top-level `current_sprint` integer field set to `1` (the first Phase 2 Python sprint), a top-level `last_updated` ISO-8601 timestamp string, and a `sprints` object (or array) that carries at minimum one entry for Sprint 0 with `status: "PASS"`. Verify via `python -c "import json; d=json.load(open('.harness/sprint-state.json')); assert isinstance(d.get('current_sprint'), int) and d['current_sprint']==1 and isinstance(d.get('last_updated'), str) and ('sprints' in d); print('PASS')"`. [weight: 25%]

2. **`config.json` carries a `python_build` section with required fields**: `.harness/config.json` contains a top-level `python_build` object with at minimum: `project_root` (string, relative path to the Python project root, i.e., `"."` or the path of `pyproject.toml`'s parent), `src_root` (string, e.g., `"src/trine_eval"`), `test_command` (string, e.g., `"uv run pytest"`), `lint_command` (string, e.g., `"uv run ruff check"` or `"uv run ruff check && uv run mypy --strict src"`), `python_version` (string, e.g., `"3.12"` — per spec.md Technical Constraints: Python 3.12+), and `lock_file_path` (string, e.g., `"uv.lock"` — the uv-managed lock file that guarantees reproducible installs). Verify via `python -c "import json; d=json.load(open('.harness/config.json')); pb=d['python_build']; assert all(k in pb for k in ['project_root','src_root','test_command','lint_command','python_version','lock_file_path']); print('PASS')"`. [weight: 20%]

3. **Phase 2 eval file-naming convention is committed in `harness-conventions.md`**: `rules/harness-conventions.md` contains a new section (level-2 or level-3 heading) that uses the literal phrase `Phase 2` and explicitly names the chosen convention — either `phase-02/` subdirectory OR sprint-number offset — and includes the directory path or offset formula. The section must resolve the open question left in `spec.md` ("Convention decided in Sprint 0") by stating the canonical path pattern for Phase 2 eval files. Verify via `grep -qE '^#{2,3}.*Phase 2' rules/harness-conventions.md && grep -q 'phase-02' rules/harness-conventions.md`. [weight: 15%]

4. **Regression gate passes with the three graduated invariants**: running the three `verification_command` entries in `.harness/regression/regression.json` all exit 0 at the HEAD commit of Sprint 00. This confirms that Sprint 00's new files do not break the three invariants graduated from Sprints 12–13 (tasks.json coverage, historical-artifacts immutable, verified-via-command audit). Verify via `python -c "import json,subprocess; tasks=json.load(open('.harness/regression/regression.json'))['tasks']; [subprocess.run(['bash','-c',t['verification_command']], check=True) for t in tasks]; print('PASS')"`. **Implementation note:** the `harness-tasks-json-coverage` invariant requires `.harness/contracts/sprint-00.tasks.json` to exist AND be tracked by git. The Generator must `git add .harness/contracts/sprint-00.md .harness/contracts/sprint-00.tasks.json` and commit them together in the same commit before the eval runs. Leaving `sprint-00.tasks.json` as an untracked file will cause C4 to fail. Note: the `harness-historical-artifacts-immutable` invariant does NOT reference `sprint-state.json` anywhere in its verification_command — so `sprint-state.json` is safely mutable and will not trigger this invariant. [weight: 25%]

### LLM-as-judge (requires reading comprehension)

5. **`python_build` config values are consistent with `spec.md`'s technical constraints**: a reader of `.harness/config.json`'s `python_build` section should be able to confirm that `src_root` matches the `src/trine_eval/` layout specified in `spec.md`, that `test_command` uses `uv run pytest` (consistent with the global `CLAUDE.md` rule "always use `uv`"), that `lint_command` covers both `ruff check` and (at minimum) documents the mypy path, that `python_version` is `"3.12"` or higher (per spec.md Technical Constraints), and that `lock_file_path` refers to `"uv.lock"` or equivalent. The values should not contradict any constraint stated in `spec.md`'s Technical Constraints section. [weight: 15%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **Historical contracts and evals are unmodified**: no file under `.harness/contracts/sprint-0{1..9}*.md`, `.harness/contracts/sprint-1*.md`, or `.harness/evals/` (for pre-Sprint-00 eval round files) is modified by any commit on the Sprint 00 branch. Sprint 00 only adds new files (`.harness/sprint-state.json`, updates to `.harness/config.json`, updates to `rules/harness-conventions.md`). Verify by diffing all commits on the sprint branch against the merge-base with main, so that historical artifact edits in earlier commits of a multi-commit sprint are not missed: `bash -c 'BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~$(git rev-list --count HEAD)^); diff_out=$(git diff $BASE..HEAD -- .harness/contracts/sprint-0[1-9]*.md .harness/contracts/sprint-1*.md .harness/evals/sprint-*.md 2>/dev/null); [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" && exit 1)'`. (The test exits PASS when the full branch diff is empty for those paths — no historical artifacts were touched in any commit.)

2. **`sprint-state.json` does not fabricate trial or weighted-score data**: `.harness/sprint-state.json` must only record status data for sprints that actually ran (Sprints 01–12 per progress.md). It must NOT invent values for the fields `status`, `rounds`, or `weighted_score` that are not supported by `.harness/progress.md` or `.harness/evals/`. A reader should verify each Sprint entry in `sprint-state.json` against `progress.md` to confirm consistency for at least 3 sprint entries — specifically confirming that `status` matches the documented outcome, `rounds` matches the number of eval rounds recorded, and `weighted_score` is either absent or matches a score referenced in progress.md.

## Reference Solutions

**Criterion 1 — example `sprint-state.json` shape:**

```json
{
  "current_sprint": 1,
  "last_updated": "2026-05-18T00:00:00Z",
  "sprints": {
    "0": {
      "status": "PASS",
      "rounds": 1,
      "criteria_passed": 6,
      "criteria_total": 6,
      "weighted_score": 100,
      "date": "2026-05-18"
    }
  }
}
```

The `sprints` object should contain entries for sprints 1–12 (Phase 2 meta-sprints) populated from `progress.md`, plus the Sprint 00 entry above. Sprint numbering in the JSON matches the sprint numbers in `sprints.json` (0, 1, 2, …6 for Phase 2).

**Criterion 3 — example Phase 2 naming convention section:**

```markdown
## Phase 2 Eval File Naming Convention

Phase 2 (Python library build, Sprints 00–06) eval files use a `phase-02/`
subdirectory:

- `.harness/evals/phase-02/sprint-NN-rR.md` — single-trial eval
- `.harness/evals/phase-02/sprint-NN-rR-tT.md` — multi-trial eval (trials > 1)
- `.harness/transcripts/phase-02/sprint-NN-rR.json` — matching transcript

Phase 1 eval files under `.harness/evals/sprint-0{1..5}-*.md` are unaffected
and remain at the root `evals/` path as append-only audit history.
```

The `phase-02/` subdirectory is preferred over the sprint-number-offset scheme because it avoids collisions with the Phase 1 audit trail and makes the phase boundary unambiguous in `git log`.

**Criterion 5 — reference `python_build` block (LLM-judge anchor):**

```json
{
  "python_build": {
    "project_root": ".",
    "src_root": "src/trine_eval",
    "test_command": "uv run pytest",
    "lint_command": "uv run ruff check && uv run mypy --strict src",
    "python_version": "3.12",
    "lock_file_path": "uv.lock"
  }
}
```

Acceptable variations: `python_version` may be `"3.12"` or `">=3.12"` (both satisfy spec.md's "Python 3.12+" constraint). `lint_command` may omit the mypy invocation only if a separate `typecheck_command` key is present. `lock_file_path` must reference `"uv.lock"` specifically (not `"requirements.txt"` or `"poetry.lock"`). Any deviation from `src_root: "src/trine_eval"` is a FAIL — spec.md pins this layout.

## Out of Scope

- **Re-implementing trials, tasks.json, adaptive thinking, or transcript capture.** These were shipped in Phase 2 meta-sprints 6–12 and are live in the harness. Sprint 00 does not revisit them.
- **Creating `src/trine_eval/` or any Python source files.** That is Sprint 1's scope.
- **Creating `pyproject.toml`.** Sprint 1 scope.
- **Modifying agent frontmatter for adaptive thinking.** All three agents (`agents/generator.md`, `agents/evaluator.md`, `agents/planner.md`) already carry `thinking: { type: adaptive, effort: ... }` in their frontmatter. No change needed.
- **Changing `config.thinking.profile`.** It is already `"default"`, which is correct for the Python build. Override to `"thorough"` for specific adversarial eval rounds is a per-run operator choice, not a Sprint 00 config change.
- **Tuning `config.trials`.** Currently `1`. Increasing it to 3–5 for Phase 2 Python build is a valid option but is a separate decision the operator makes when starting Sprint 1, not a Sprint 00 prerequisite.
- **Closing GAP 2 (environment sandboxing) or GAPs 7–10.** Those are explicitly deferred in `spec.md` and `applied-harness-proposal-2026-05.md`.
- **Moving agent/skill files from a hypothetical `plugins/trine-eval/` path.** They live correctly at the worktree root (`./agents/`, `./skills/`, `./hooks/`). The `spec.md` reference to `plugins/trine-eval/` is a documentation discrepancy — see Technical Notes.

## Technical Notes

- **Plugin path discrepancy.** `spec.md` Technical Constraints says "Agents and skills under `plugins/trine-eval/`." The actual worktree layout has agents/skills at root (`./agents/`, `./skills/`, `./hooks/`). No migration is needed — the root layout is correct and the plugin is installed from there. The spec.md line is a leftover from the Phase 1 vision before the harness matured. It is noted here as a known inconsistency; correcting spec.md prose is out of scope for Sprint 00 but can be done as a docs-only commit.

- **`sprint-state.json` scope.** The file should cover Phase 2 sprints (0–6) in its `sprints` object. Backfilling Phase 1 sprints (01–05) from `progress.md` is optional but recommended so session-resumption reads a complete picture. The `harness-historical-artifacts-immutable` regression invariant uses `git diff HEAD` scoped to `.harness/contracts/` and `.harness/evals/` — not `sprint-state.json` — so the new file is safe to update every sprint.

- **Phase 2 eval naming decision.** This contract recommends the `phase-02/` subdirectory scheme (see Reference Solutions, Criterion 3). The sprint-number offset (NN+5) proposed in `spec.md` was written before Sprint 6–12 consumed those numbers (the meta-harness Phase 2 sprints already used sprint numbers 6–12). The `phase-02/` subdirectory avoids collision and makes the boundary explicit. The Evaluator should confirm this choice is reflected correctly in the convention document before approving.

- **`config.python_build` is metadata only.** Sprint 1 will read these fields to know where to create files. The harness orchestrator (`skills/harness-sprint/SKILL.md`) does not currently read `python_build` — that wiring happens in Sprint 1 as needed. Sprint 00 only establishes the config key so Sprint 1's Generator has a stable reference rather than inferring paths from spec.md prose.

- **Regression gate compatibility and commit-ordering.** The three existing regression invariants (`harness-tasks-json-coverage`, `harness-historical-artifacts-immutable`, `harness-verified-via-command-audit`) must all pass at the Sprint 00 tip commit. The `harness-tasks-json-coverage` invariant requires `.harness/contracts/sprint-00.tasks.json` to exist AND be tracked by git. **The Generator must stage and commit `sprint-00.md` and `sprint-00.tasks.json` together in the same commit** — if `sprint-00.tasks.json` is present on disk but untracked, the invariant will FAIL during eval. Use `git add .harness/contracts/sprint-00.md .harness/contracts/sprint-00.tasks.json` before committing.

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/sprint-00.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — 4 deterministic + 1 LLM-judge + 2 Should-NOT gates = 7 entries — with stable `task_id`s, `grader_type`, `weight`, `is_gate`, `verification_command` (where applicable), and `rubric_dimension`. Downstream sprints (regression gate, transcript capture, adversarial hygiene) consume that JSON; this markdown contract remains the human-readable source of truth. See `skills/sprint-contract/SKILL.md` for the schema.

## Evaluator Review

**Status: NEEDS REVISION**

### Feedback

**No-op verification results (run against current worktree HEAD):**

- C1 (sprint-state.json): FAILS today — file does not exist. Not a no-op. Correct.
- C2 (python_build in config.json): FAILS today — python_build key absent. Not a no-op. Correct.
- C3 (Phase 2 naming in harness-conventions.md): FAILS today — neither the heading pattern nor the string "phase-02" appears. Not a no-op. Correct.
- C4 (regression gate): Two of three invariants pass right now (harness-historical-artifacts-immutable and harness-verified-via-command-audit pass; harness-tasks-json-coverage FAILS because sprint-00.tasks.json exists on disk but is not yet tracked by git). This means C4 cannot pass until the Generator commits both sprint-00.md and sprint-00.tasks.json together in the same commit. The contract should state this prerequisite explicitly, or add a note in Technical Notes warning the Generator to commit tasks.json before the eval runs.
- C5 (sprint-state.json exclusion): PASSES today — the harness-historical-artifacts-immutable command does not reference "sprint-state" anywhere. This criterion is a no-op: it trivially passes before any Sprint 00 work because the invariant was written without that string. If the invariant were accidentally updated to include sprint-state, C4's regression gate would catch it. Remove C5 or fold it into C4's prose as a documentation note. The 10% weight is wasted on a criterion that cannot fail in practice.

**SN1 — HEAD~1..HEAD scope is too narrow.** The verification_command diffs only the most recent commit against its parent. A Generator making two or more commits during a sprint (common: one feature commit plus one lint-fix commit) could modify a historical artifact in an earlier commit without SN1 catching it. The graduated harness-historical-artifacts-immutable invariant uses git diff HEAD (working-tree vs. index), which also does not cover multi-commit history. Recommend changing SN1 to: git diff $(git merge-base HEAD main)..HEAD -- ... to catch all commits on the sprint branch. If that is operationally complex, document the known gap explicitly in Technical Notes.

**C2 — python_build missing python_version and lock_file_path.** The four required fields (project_root, src_root, test_command, lint_command) are necessary but insufficient. spec.md Technical Constraints specifies Python 3.12+ and a uv.lock file. Sprint 1's Generator will need python_version to configure the virtualenv and lock_file_path to verify reproducibility. These should be required fields in C2's verification assertion, or at minimum listed as recommended fields in a Technical Note so Sprint 1 does not have to rediscover them.

**C6 — LLM-judge criterion needs a reference solution.** Per evaluator.md: the highest-weighted LLM-judge criterion should have a reference solution. C6 is the only LLM-judge success criterion (15% weight). The contract provides reference solutions for C1 and C3 but not C6. Add a minimal example python_build block showing acceptable values for src_root, test_command, and lint_command so two independent evaluators would reach the same verdict.

**SN2 — LLM-judge gate is acceptable but could be deterministic.** Comparing sprint-state.json entries against progress.md for status/rounds consistency is feasible as a deterministic script. If the contract retains the LLM-judge approach, add explicit field names to check (status, rounds, weighted_score) to the criterion text so the evaluator has an unambiguous rubric.

### Missing Criteria

No criteria are missing for the stated scope. The three deliverables (sprint-state.json, python_build config, naming convention) each have a criterion. The regression gate and exclusion criteria address cross-sprint safety.

### Approved Criteria

- **C1** — structurally sound, verification command is deterministic and specific, reference solution provided.
- **C3** — grep-based verification is correct; confirmed to FAIL today and will PASS only after the Generator writes the section. Reference solution is concrete.
- **C4** — correct gate for regression invariants; commit-ordering caveat noted above must be addressed.
- **C6** — LLM-judge scope is appropriate; criterion prose is specific enough once a reference solution is added.

## Evaluator Review — Round 2

### Fix Verification (5 issues from Round 1)

**Issue 1 — No-op C5 removed and weights redistributed.**

Confirmed. The old C5 ("sprint-state.json is not referenced by the historical-artifacts invariant") no longer exists in the contract or in `sprint-00.tasks.json`. The contract now has exactly 5 success criteria (C1–C5). The old LLM-judge criterion (formerly C6) has been renumbered to C5. Weight check: 25 + 20 + 15 + 25 + 15 = 100%. Verified via tasks.json structural inspection — `task_id`s are `s00-c1` through `s00-c5`, no `s00-c6` or stale no-op entry present. RESOLVED.

**Issue 2 — C4 commit-ordering warning added.**

Confirmed. C4's criterion text now contains an explicit implementation note: "The Generator must `git add .harness/contracts/sprint-00.md .harness/contracts/sprint-00.tasks.json` and commit them together in the same commit before the eval runs. Leaving `sprint-00.tasks.json` as an untracked file will cause C4 to fail." The same warning is repeated verbatim in Technical Notes under "Regression gate compatibility and commit-ordering." Two locations means the Generator cannot miss it. RESOLVED.

**Issue 3 — SN1 scope expanded to merge-base.**

Confirmed. The SN1 `verification_command` (in both the markdown and `sprint-00.tasks.json`) now reads:

```
bash -c 'BASE=$(git merge-base HEAD main 2>/dev/null || git rev-parse HEAD~$(git rev-list --count HEAD)^); diff_out=$(git diff $BASE..HEAD -- .harness/contracts/sprint-0[1-9]*.md .harness/contracts/sprint-1*.md .harness/evals/sprint-*.md 2>/dev/null); [ -z "$diff_out" ] && echo PASS || (echo FAIL && echo "$diff_out" && exit 1)'
```

This covers ALL commits on the sprint branch against `main`'s merge-base, with a fallback for branches with no merge-base (e.g., orphan branches). Command was run against the current worktree and returned `PASS` with exit 0 — no historical artifacts have been modified. RESOLVED.

**Issue 4 — C2 now requires `python_version` and `lock_file_path`.**

Confirmed. C2's criterion prose explicitly lists `python_version` (annotated "per spec.md Technical Constraints: Python 3.12+") and `lock_file_path` (annotated "the uv-managed lock file that guarantees reproducible installs"). The verification command asserts all six keys: `['project_root','src_root','test_command','lint_command','python_version','lock_file_path']`. Command was run and correctly raises `KeyError: 'python_build'` today (work needed, not a no-op). The `sprint-00.tasks.json` entry for `s00-c2` carries the same six-key assertion. RESOLVED.

**Issue 5 — Reference solution added for the LLM-judge criterion (now C5).**

Confirmed. The Reference Solutions section now contains a "Criterion 5 — reference `python_build` block (LLM-judge anchor)" block showing all six required fields with their expected values, plus an explicit note on acceptable variations for `python_version` and `lint_command`, and a FAIL-on-deviation rule for `src_root: "src/trine_eval"`. This anchors two independent evaluators to the same verdict. RESOLVED.

### Weight and Structure Check

- Success criteria: 5 (4 deterministic + 1 LLM-judge). Weights: 25 + 20 + 15 + 25 + 15 = **100%**. Correct.
- Gate criteria: 2 (SN1 deterministic, SN2 LLM-judge), both `weight: 0`, `is_gate: true`. Correct.
- `sprint-00.tasks.json`: 7 entries total. `task_id`s: `s00-c1`, `s00-c2`, `s00-c3`, `s00-c4`, `s00-c5`, `s00-sn1`, `s00-sn2`. No stale `s00-c6`. Correct.

### Live Command Verification

- **C2 still FAILs (work needed):** `python -c "... assert all(k in pb for k in ['project_root','src_root','test_command','lint_command','python_version','lock_file_path']) ..."` raises `KeyError: 'python_build'` — confirmed, `python_build` does not yet exist in `config.json`. Not a no-op.
- **SN1 runs cleanly:** merge-base command executes without error and outputs `PASS` — no historical artifacts modified on this branch. Correct baseline behavior.

### No New Issues

No new problems introduced by the revision. The SN1 fallback path (`git rev-parse HEAD~$(git rev-list --count HEAD)^`) handles orphan-branch edge cases gracefully. The tasks.json is internally consistent with the markdown. The round-trip between the markdown criterion text and the `verification_command` in tasks.json matches for all 4 deterministic criteria.

**Status: APPROVED**
