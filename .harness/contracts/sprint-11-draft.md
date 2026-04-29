# Sprint 11 (DRAFT) Contract: Synthetic Verification of Phase 2 Runtime Hookups

> **DRAFT** — This contract is a proposal, not yet an active sprint. To activate: append a Sprint 11 entry to `.harness/sprints.json`, rename this file to `sprint-11.md`, then run `/harness-sprint 11`.

## What I Will Build

Verify that the seven runtime hookups deferred during Phase 2 (Sprints 6/7/9/10) work end-to-end against a live system, not just at the protocol level. The verification scope is strictly **internal**: trial loop file naming + count, sandbox tmpdir isolation, regression abort triggering, real transcript JSON file emission, `verified_via_command` ground-truth auditing, and adaptive-thinking frontmatter dispatch. **Out of scope and explicitly deferred to Sprint 12**: Batch API HTTP submission against a live `ANTHROPIC_API_KEY`, Playwright MCP invocation against a real `web-app` project, and edge-case-pass-rate aggregation across a multi-sprint test fixture — those depend on external services and a separate fixture project, and conflating them with Sprint 11 would balloon the scope past what one sprint can land cleanly.

The deliverable is a `tests/fixture-project/` self-contained harness instance plus a verification script (`tests/verify-runtime-hookups.sh` or `.py`) that exercises each runtime path by direct file operations rather than recursively invoking `/harness-sprint`. This avoids the recursion / infinite-loop risk while still confirming the harness machinery — file naming conventions, schema serialization, gate semantics — produces the expected on-disk artifacts. Where direct verification is genuinely impossible without recursive invocation (e.g., the regression gate's Step 0.5 hook), the verification script documents the manual steps with copy-pasteable commands.

## Success Criteria

Weights sum to 100%. Each criterion must be independently testable.

### Deterministic (code-verifiable)

1. **Fixture project structure exists**: `tests/fixture-project/` directory exists with `tests/fixture-project/.harness/config.json` declaring `trials: 3` and `sandbox.mode: "tmpdir"`, a one-success-criterion sprint contract at `tests/fixture-project/.harness/contracts/sprint-fx.md`, and a sibling `tests/fixture-project/.harness/contracts/sprint-fx.tasks.json`. Verify via `test -d tests/fixture-project && test -f tests/fixture-project/.harness/config.json && test -f tests/fixture-project/.harness/contracts/sprint-fx.md && test -f tests/fixture-project/.harness/contracts/sprint-fx.tasks.json && python -c "import json; d=json.load(open('tests/fixture-project/.harness/config.json')); assert d['trials']==3 and d['sandbox']['mode']=='tmpdir'"`. [weight: 8%]

2. **Trial files emitted in clean state**: Three trial files exist at `tests/fixture-project/.harness/evals/sprint-fx-r1-t1.md`, `-t2.md`, `-t3.md`, each as an independent file (different mtimes) with its own `## Summary` block stamped with the trial number. Verify via `test -f tests/fixture-project/.harness/evals/sprint-fx-r1-t1.md && test -f tests/fixture-project/.harness/evals/sprint-fx-r1-t2.md && test -f tests/fixture-project/.harness/evals/sprint-fx-r1-t3.md && grep -q '\*\*Trial:\*\* 1' tests/fixture-project/.harness/evals/sprint-fx-r1-t1.md && grep -q '\*\*Trial:\*\* 2' tests/fixture-project/.harness/evals/sprint-fx-r1-t2.md && grep -q '\*\*Trial:\*\* 3' tests/fixture-project/.harness/evals/sprint-fx-r1-t3.md`. [weight: 9%]

3. **pass@k / pass^k computed from trial files in fixture summary**: `tests/fixture-project/.harness/summary.md` exists and reports both `pass@k` and `pass^k` values for sprint FX, computed from the three trial files (not from rounds). The values match the formulas in `skills/harness-summary/SKILL.md`: pass@3 = 1 − (1−p)³ and pass^3 = p³, where p is the average per-trial pass rate. Verify via `test -f tests/fixture-project/.harness/summary.md && grep -q 'pass@k' tests/fixture-project/.harness/summary.md && grep -q 'pass^k' tests/fixture-project/.harness/summary.md && grep -qE 'sprint.fx' tests/fixture-project/.harness/summary.md`. [weight: 9%]

4. **Sandbox tmpdir mode produces side-effect isolation**: The verification script demonstrates that with `sandbox.mode: "tmpdir"`, a side-effect file written during trial 1 is NOT visible in trial 2 or trial 3. Specifically, the fixture's verification command writes `/tmp/<random>/trial-marker-<T>` and the script confirms each trial's tmpdir is distinct (different paths). Verify via `bash tests/verify-runtime-hookups.sh sandbox-isolation` returning exit 0 with output naming three distinct tmpdir paths. [weight: 8%]

5. **Regression abort fires when graduated criterion fails**: `tests/fixture-project/.harness/regression/regression.json` is populated with at least one entry. The verification script: (a) breaks the file the entry's `verification_command` depends on, (b) attempts to start a new sprint via the harness, (c) confirms Step 0.5 aborts with a "regression failed" message naming the failing `task_id` and `graduated_from_sprint` before contract negotiation begins. Verify via `bash tests/verify-runtime-hookups.sh regression-abort` returning exit 0 (the script orchestrates break → run → expect-abort → restore). [weight: 11%]

6. **Real transcript JSON file emitted by Step 3e**: The verification script triggers an evaluator run against the fixture sprint and confirms `tests/fixture-project/.harness/transcripts/sprint-fx-r1-t1.json` exists with valid JSON containing all eight Sprint 9 schema fields (`sprint`, `round`, `trial`, `messages`, `tool_calls`, `token_usage`, `timing`, `thinking_summary`) AND the Sprint 10 `criteria_audit` array with at least one entry. Verify via `python -c "import json; d=json.load(open('tests/fixture-project/.harness/transcripts/sprint-fx-r1-t1.json')); required=['sprint','round','trial','messages','tool_calls','token_usage','timing','thinking_summary','criteria_audit']; assert all(k in d for k in required) and len(d['criteria_audit'])>=1; print('PASS')"`. [weight: 11%]

7. **`verified_via_command` ground-truth audit script**: `tests/audit-verified-via-command.py` exists and, given a transcript JSON, returns exit 0 when every `criteria_audit[i].verified_via_command == true` entry has a corresponding `tool_calls` entry tagged with the same `task_id` (i.e., a verification command actually ran for that criterion). The script returns non-zero with a list of inconsistencies otherwise. Verify by running it against the Sprint-10 transcript trailer (extracted from `.harness/evals/sprint-10-r1.md`'s `## Transcript Trailer` block): `python tests/audit-verified-via-command.py .harness/evals/sprint-10-r1.md` returns exit 0. [weight: 9%]

8. **Adaptive-thinking frontmatter dispatch is observable**: A small inspection script confirms that each agent file declares the expected `effort` value in its frontmatter — `medium` for `agents/planner.md`, `medium` for `agents/generator.md`, `high` for `agents/evaluator.md`, `max` for `skills/harness-summary/SKILL.md`. This is the protocol-level check; runtime dispatch into actual API calls is observable only via inspecting per-message metadata when the harness drives a live API call (deferred to Sprint 12). Verify via `python tests/check-thinking-frontmatter.py` returning exit 0 (the script reads each agent file's YAML frontmatter and asserts the effort values). [weight: 7%]

9. **`sprint-11.tasks.json` is emitted**: A file `.harness/contracts/sprint-11.tasks.json` exists, is valid JSON, has top-level `sprint: 11`, and contains entries for every criterion in this contract — 9 deterministic + 3 LLM-judge + 3 Should-NOT gates = **15 entries** — each with the Sprint-6 schema fields. Verify via `python -c "import json; d=json.load(open('.harness/contracts/sprint-11.tasks.json')); assert d['sprint']==11 and len(d['tasks'])>=15 and all('task_id' in t and 'grader_type' in t and 'weight' in t and 'is_gate' in t for t in d['tasks']); print('PASS')"`. [weight: 4%]

### LLM-as-judge (requires reading comprehension)

10. **Backward compatibility audit is correct**: A reader of `tests/fixture-project/` and the verification script should come away confident that nothing in this sprint modifies the parent `trine-eval/.harness/` directory or any agent/skill/rules file outside `tests/`. The fixture project is a self-contained harness instance with its own `.harness/`, its own contracts, its own evals — no leakage into the parent. The reader should also verify that the verification script does not require any external service: no `ANTHROPIC_API_KEY`, no Docker daemon, no Playwright MCP, no network access beyond Git operations. The deferred Sprint-12 items (Batch API, Playwright, edge-case multi-sprint aggregation) must be explicitly named in this sprint's Out of Scope and the verification script must not silently exercise them. [weight: 13%]

11. **pass@k / pass^k numerical correctness**: A reader of `tests/fixture-project/.harness/summary.md` should be able to verify that the reported pass@3 and pass^3 values are arithmetically consistent with the per-trial pass rates observed in the three trial files. Specifically: if the three trials report pass rates p₁, p₂, p₃, then the average p = (p₁+p₂+p₃)/3, and the summary should report pass@3 ≈ 1−(1−p)³ and pass^3 ≈ p³. Tolerance: numerical results within ±0.001 of the formula. The reader should also confirm the summary explicitly labels these as "trial-derived (statistically valid)" to distinguish from the deprecated `pass@rounds` / `pass^rounds` retry-derived metric for sprints with only round files. [weight: 11%]

12. **Adversarial hygiene audit findings are reported**: After running `tests/audit-verified-via-command.py` against every existing Sprint 6–10 eval that has a `## Transcript Trailer` (Sprint 10 is the only one that does today), the verification script writes `tests/audit-report.md` summarizing: (a) which criteria had `verified_via_command: true` with a matching `tool_calls` entry (consistent — the verifier did run); (b) which had `verified_via_command: true` with NO matching `tool_calls` entry (the calibration drift Sprint 10 was designed to catch); (c) which had `verified_via_command: false` (LLM-judge or prose-graded — expected). The reader of `tests/audit-report.md` should be able to verify the audit logic is sound: a `false`-with-no-tool-call is fine (LLM-judge); a `true`-with-no-tool-call is the suspect case Sprint 10's Adversarial Hygiene Rules 1–3 exist to flag. [weight: 10%]

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.

1. **Fixture project must not pollute the parent harness**: After running the verification script, `git status` must report no changes to `.harness/evals/sprint-0[1-9]*`, `.harness/evals/sprint-10*`, `.harness/contracts/sprint-0[1-9]*`, `.harness/contracts/sprint-10*`, `.harness/regression/regression.json`, `.harness/transcripts/`, or any file outside `tests/` plus the new `.harness/contracts/sprint-11*` entries. Verify via `test -z "$(git diff HEAD -- .harness/evals/sprint-0[1-9]* .harness/evals/sprint-10* .harness/contracts/sprint-0[1-9]* .harness/contracts/sprint-10* .harness/regression/regression.json .harness/transcripts/)"`.

2. **Verification script must not require external services**: The script must run cleanly in an offline environment with no `ANTHROPIC_API_KEY`, no Docker daemon, no Playwright MCP, no network access beyond Git. Any criterion that would require an external service must explicitly be marked deferred-to-Sprint-12 and skipped with an exit code of 0 + an `[SKIP]` log line, not failed silently. Verify by reading the verification script source and confirming each criterion's runtime path either (a) operates on local files only, or (b) is guarded by an `if external_service_available` check that emits `[SKIP]` and continues when the service is absent.

3. **No fabrication of `verified_via_command: true`**: The fixture project's transcript trailer (and any new transcripts written by the verification script) must report `verified_via_command: true` only for criteria where a corresponding entry exists in `tool_calls`. The audit script (Criterion 7) is the deterministic enforcement mechanism. Verify by running the audit script against any newly-written transcript and confirming exit 0. The verification script must not bypass or stub the audit — it must actually run the audit and propagate its exit code.

## Reference Solutions

**Criterion 5 (regression abort) — example of the verification script's regression-abort orchestration:**

````bash
#!/usr/bin/env bash
# tests/verify-runtime-hookups.sh regression-abort
#
# Demonstrates that Step 0.5 of harness-sprint correctly aborts a new sprint
# when a graduated regression criterion fails.

set -uo pipefail

FIXTURE=tests/fixture-project
REGRESSION_FILE="$FIXTURE/.harness/regression/regression.json"
DEPENDENT_FILE="$FIXTURE/.harness/dependent.txt"  # the file the regression criterion checks

# Pre-condition: regression.json has at least one entry whose verification_command
# tests for the existence of $DEPENDENT_FILE.
python -c "
import json
d = json.load(open('$REGRESSION_FILE'))
assert len(d['tasks']) >= 1, 'regression.json must have a graduated criterion'
" || exit 1

# 1. Confirm the regression criterion currently passes.
test -f "$DEPENDENT_FILE" || { echo "FAIL: dependent file missing before test"; exit 1; }

# 2. Break the dependent file (move it aside; do not delete — we will restore).
mv "$DEPENDENT_FILE" "$DEPENDENT_FILE.bak"

# 3. Simulate Step 0.5: read regression.json, run each verification_command, expect non-zero exit.
ABORT_DETECTED=0
while read -r CMD; do
  if ! eval "$CMD" >/dev/null 2>&1; then
    ABORT_DETECTED=1
    echo "[regression abort] task failed verification: $CMD"
  fi
done < <(python -c "
import json
d = json.load(open('$REGRESSION_FILE'))
for t in d['tasks']:
    if t.get('verification_command'):
        print(t['verification_command'])
")

# 4. Restore the dependent file.
mv "$DEPENDENT_FILE.bak" "$DEPENDENT_FILE"

# 5. Confirm Step 0.5 logic detected the abort condition.
if [ "$ABORT_DETECTED" -eq 1 ]; then
  echo "PASS: regression abort triggered as expected"
  exit 0
else
  echo "FAIL: no regression failures detected — Step 0.5 logic broken"
  exit 1
fi
````

**Criterion 10 (backward compatibility audit) — example of the README/docs sentence pattern:**

```markdown
The fixture project at `tests/fixture-project/` is a self-contained harness
instance. It runs only against its own `.harness/` directory; the parent
trine-eval/.harness/ is never read or modified during verification. The
verification script is offline-capable: no Anthropic API key, no Docker, no
Playwright. External-service-dependent runtime paths (Batch API HTTP submission,
Playwright MCP invocation, edge-case rate aggregation across a multi-sprint
fixture) are explicitly out of scope and deferred to Sprint 12. Each such path
is guarded in the verification script with an `if external_service_available`
check that prints `[SKIP] Sprint 12: <reason>` when the service is absent.
```

## Out of Scope

- **Batch API HTTP submission against a live `ANTHROPIC_API_KEY`** — Sprint 12. Verifying that a single batch POST replaces N synchronous calls requires a real API key, which is environment-dependent and not appropriate for a verification sprint that should run cleanly offline. The Sprint 8 protocol (trigger condition, result-shape preservation invariant) is verified at the markdown/JSON level here; HTTP runtime is Sprint 12.
- **Playwright MCP invocation against a real `web-app` project** — Sprint 12. Requires a separate `web-app` fixture (with rendered UI, viewport-specific layout, etc.) that is non-trivial to build and out of scope for runtime verification of the seven other gaps. The Sprint 10 conditional protocol (`evaluator_tools.playwright: "auto"`, `project_type == "web-app"` guard, Visual Design fallback to curl) is verified at the markdown level here; live invocation is Sprint 12.
- **Edge-case pass rate aggregation across a multi-sprint test fixture** — Sprint 12. The Sprint 10 `## Edge Case Criteria` slot is verified to exist and to be optional in this sprint; cross-sprint aggregation logic in `harness-summary` will be exercised when the Sprint 12 fixture project declares edge-case criteria across multiple sprints.
- **`thinking.profile` runtime dispatch** — protocol-level check is Criterion 8 here (frontmatter declarations are present); the actual dispatch into per-message `thinking` metadata is observable only via the live API client, which is Sprint 12.
- **Recursive invocation of `/harness-sprint` from inside the verification script** — by design. The script orchestrates each runtime path by direct file operations and explicit shell commands; it does not invoke the harness recursively. This avoids infinite-loop risk and keeps verification reproducible.
- **Modifying any of Sprints 1–10's contracts, evals, or tasks.json** — append-only rule from `rules/harness-conventions.md`. Sprint 11 is purely additive.
- **Updating the eval-harness rubric** — the rubric is unchanged. Sprint 11 verifies existing protocol; it does not introduce new dimensions.

## Technical Notes

- **Verification ≠ recursive harness invocation.** The cleanest way to test whether a runtime path produces the expected on-disk artifacts is to call the underlying primitive directly (write a transcript JSON, write a trial eval file, run the regression check) — not to recursively invoke `/harness-sprint`. The verification script encodes each primitive as a self-contained shell or Python operation and asserts the output. This is the same pattern the gap-closure plan's Verification section uses ("manually break a file that a graduated criterion depends on, then run /harness-sprint" — but the script automates the orchestration).

- **Fixture project is intentionally minimal.** `tests/fixture-project/.harness/` contains exactly what's needed to exercise the trial loop, sandbox, regression gate, and transcript writing — one config, one contract, one tasks.json, one regression.json with a single graduated entry, one set of three trial eval files. No agent files, no skill files, no rubric — those are inherited from the parent trine-eval plugin via Claude Code's plugin system. This keeps the fixture under 200 lines total and reviewable in one sitting.

- **Why split Sprint 11 from Sprint 12.** Internal runtime hookups (trial loop, sandbox, regression abort, transcript writing, `verified_via_command` audit) operate on local files and produce deterministic verification. External-service hookups (Batch API, Playwright) require network, credentials, and a non-trivial `web-app` fixture. Bundling both into one sprint creates a "this sprint cannot run in CI" liability and makes the contract too large to review. Splitting at the offline/online boundary keeps Sprint 11 reproducible and runnable on any machine.

- **The `verified_via_command` audit script is the first concrete adversarial-hygiene enforcement.** Sprint 10 added the rule (no fabrication) and the schema slot (`criteria_audit` array). Sprint 11's Criterion 7 adds the *enforcement*: a script that detects mismatches between claimed `verified_via_command: true` flags and actual `tool_calls` entries. This closes the loop on Gap 10's runtime hookup.

- **Sprint 11 should produce a graduated regression entry as a side-effect.** The fixture's `regression.json` will contain at least one entry, and the regression-abort verification (Criterion 5) is the first time the harness exercises a non-empty regression suite end-to-end. The Sprint 11 eval should append at least one Sprint-11-graduated entry to the *parent* trine-eval `regression.json` if any of the Sprint 11 success criteria saturate (this is the standard saturation-graduation flow from `harness-summary`). However, since this is a one-shot verification sprint, saturation across 3+ consecutive sprints will not occur within Sprint 11 alone — graduation will land at Sprint 12 or later.

- **Pass@3 expected value for the deterministic fixture.** The fixture's verification command should be **deterministically PASS** (e.g., `true` or `test -f tests/fixture-project/.harness/dependent.txt`) so all three trials report 1.0 and pass@3 = pass^3 = 1.0. This verifies the trial-loop file naming and pass@k formula application, but it does not exercise the consistency-gap measurement (where pass@k > pass^k). Exercising the gap requires a non-deterministic command, which is hard to make reproducible — the verification script should optionally include a non-deterministic mode (`bash tests/verify-runtime-hookups.sh nondet-trial`) that runs `[ $((RANDOM % 2)) -eq 0 ]` as the verification command and confirms the harness-summary output matches the observed pass rate within ±0.001 tolerance.

- **Activation steps for the user.** Once this contract is reviewed and accepted: (1) append a Sprint 11 entry to `.harness/sprints.json` with `dependencies: [10]`; (2) rename `.harness/contracts/sprint-11-draft.md` to `.harness/contracts/sprint-11.md`; (3) run `/harness-sprint 11`. The standard contract-build-eval cycle then takes over — the Generator implements the fixture project and verification script, the Evaluator grades against this contract, and saturated criteria from the previous 10 sprints become regression-graduation candidates as the audit script runs against existing transcripts.

---

**Task taxonomy handoff:** Once this contract is approved by the Evaluator, a sibling `.harness/contracts/sprint-11.tasks.json` is emitted (guarded by `config.taxonomy.emit_tasks_json`, default `true`). It contains one JSON entry per criterion above — 9 deterministic + 3 LLM-judge + 3 Should-NOT gates = 15 entries — with stable `task_id`s, `grader_type`, `weight`, `is_gate`, `verification_command`, and `rubric_dimension`. Sprint 12 (Batch API + Playwright + multi-sprint edge-case fixture) will key off this JSON as it expands the verification scope to external services.
