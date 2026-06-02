# Sprint 13 Contract: Workflow-Step Port and Governance Hardening (Phase 1.6)

## Revision History

| Rev | Date | Change |
|-----|------|--------|
| 0 | 2026-06-02 | Initial draft |

## What I Will Build

(a) **Workflow-step port** — Port the missing sections from the cached `harness-sprint` SKILL.md (v0.3.3) into the in-repo `plugins/trine-eval/skills/sprint-workflow/SKILL.md` as additive subsections: Step 0.5 (regression gate), Step 1d (tasks.json emission point), Steps 3a–3e (pre-eval clean-state, evaluator dispatch, trial loop, batch API mode, transcript capture), and an `## Operational Notes` section (Evaluator Fallback, thinking.profile). The existing 6-step structure of the in-repo workflow (Steps 0, 1, 2, 3, 4, 5) is preserved byte-for-byte; the port is purely additive. Closes HK-0004 and the dangling references at `sprint-contract/SKILL.md` lines 74, 140, 142.

(b) **Council-check gates** — Add bidirectional governance-aware gates when `config.governance.enabled` is true: (b1) a pre-sprint warn-only gate in Step 0 that checks for `.council/sprint-prebrief/sprint-NN.json` and warns if missing; (b2) a post-sprint auto-trigger in Step 5 that invokes `/henkaten-council:council-autorun` when `config.governance.review_frequency == "every-sprint"`, respecting the existing andon-stop protocol. Closes HK-0003 by construction. Also amends Step 1d to advance `.harness/features.json` with any new sprint features at tasks.json emission time (DEC-0019 structural fix).

(c) **SN2 carve-out + stale-refs cleanup** — Formally amend `plugins/trine-eval/skills/sprint-contract/SKILL.md` to permit renumbering-only edits to approved markdown contracts under the SN2 carve-out, with a mandatory `## Revision History` block citing the plan-amendment commit. Apply the carve-out to fix stale Sprint 9/10/11 references in `.harness/contracts/sprint-07.md` and `.harness/contracts/sprint-08.md` per Scope Guardian #5a. Also apply DEC-0011's pending sprint-10.md awk-anchor fix (one-line correction changing `/^## Artifact 2/` to `/^### Artifact 2:/`).

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `behavioral` (execution-verified), `structural` (artifact-inspected), or `llm-judge` (reading-comprehension).
Weights must sum to 100% across all success criteria.

**Behavioral coverage:** Sprint 13 delivers additions to markdown files (SKILL.md updates, contract renumbering edits). The primary deliverable files are text artifacts, but many required properties are shell-verifiable via `grep` and `jq`. Following Sprint 9/10/11 precedents, `grep` invocations qualify as behavioral (not structural) when: (a) a shell command is run, (b) the expected output is a specific integer — not just non-zero, and (c) the pre-sprint baseline differs from the post-sprint expected value. The ported step text can be verified by counting section headings and key protocol keywords. The governance gate text, SN2 carve-out amendment, and stale-ref repairs are shell-verifiable. Behavioral coverage target: ≥ 60%. Full grader-split rationale in Technical Notes.

### Behavioral (execution-verified)

1. **Step 0.5 (regression gate) is present in sprint-workflow/SKILL.md** [weight: 8%]:
   Run `grep -c '## Step 0.5' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 1.
   Then run `grep -ci 'regression.*gate\|regression\.json\|regression\.enabled' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 3.
   Pre-sprint baseline: `grep -c '## Step 0.5' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 (section absent). Post-sprint: count >= 1 for heading, count >= 3 for key terms.
   PASS when both conditions hold.

2. **Step 1d (tasks.json emission point) is present in sprint-workflow/SKILL.md** [weight: 8%]:
   Run `grep -c '### 1d' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 1.
   Then run `grep -ci 'emit_tasks_json\|tasks\.json.*emit\|APPROVED.*tasks\|tasks.*APPROVED' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 2.
   Pre-sprint baseline: `grep -c '### 1d' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 (section absent). Post-sprint: both conditions met.
   PASS when both conditions hold.

3. **Steps 3c, 3d, and 3e are present in sprint-workflow/SKILL.md** [weight: 8%]:
   Run the following three greps and assert each returns count >= 1:
   ```
   grep -c '### 3c' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   grep -c '### 3d' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   grep -c '### 3e' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   ```
   Pre-sprint baseline: all three return 0 (the in-repo SKILL.md already has `### 3a` and `### 3b` — confirmed by `grep -n '### 3' plugins/trine-eval/skills/sprint-workflow/SKILL.md` returning lines 101 and 111 — but 3c, 3d, 3e are absent). Post-sprint: all three >= 1.
   PASS when all three conditions hold.
   Note for Evaluator: also confirm `### 3a` and `### 3b` remain present (count >= 1 each) as an additive integrity check.

4. **Operational Notes section is present in sprint-workflow/SKILL.md** [weight: 6%]:
   Run `grep -c '## Operational Notes' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 1.
   Then run each of the following and assert each >= 1:
   ```
   grep -ci 'Evaluator Fallback' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   grep -ci 'thinking\.profile' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   ```
   Pre-sprint baseline: `grep -c '## Operational Notes' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0. Post-sprint: all >= 1.
   PASS when all three conditions hold.

5. **Pre-sprint governance warn-only gate (b1) is present in sprint-workflow/SKILL.md** [weight: 8%]:
   Run `grep -ci 'sprint-prebrief\|governance\.review_frequency\|warn.*missing\|missing.*prebrief' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 2.
   Then run `grep -ci 'WARN\|warn' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 1.
   Pre-sprint baseline: `grep -ci 'sprint-prebrief' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 (no governance gate text present). Post-sprint: first condition count >= 2, second >= 1.
   PASS when both conditions hold.

6. **Post-sprint auto-trigger gate (b2) is present in sprint-workflow/SKILL.md** [weight: 8%]:
   Run `grep -ci 'council-autorun\|henkaten-council.*council-autorun\|auto-trigger\|every-sprint' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 2.
   Then run `grep -ci 'andon.*stop\|andon.*halt\|andon-stop' plugins/trine-eval/skills/sprint-workflow/SKILL.md` and assert count >= 1 (the auto-trigger must reference the andon-stop protocol).
   Pre-sprint baseline: `grep -ci 'council-autorun' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0. Post-sprint: first condition count >= 2, second >= 1.
   PASS when both conditions hold.

7. **SN2 carve-out amendment is present in sprint-contract/SKILL.md** [weight: 8%]:
   Run `grep -ci 'SN2.*carve-out\|carve-out.*SN2\|renumbering-only\|renumbering.*edit\|Revision History.*carve' plugins/trine-eval/skills/sprint-contract/SKILL.md` and assert count >= 1.
   Then run `grep -ci 'plan-amendment.*commit\|amendment.*commit\|Revision History.*block' plugins/trine-eval/skills/sprint-contract/SKILL.md` and assert count >= 1.
   Pre-sprint baseline: `grep -ci 'SN2.*carve-out\|renumbering-only' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 0. Post-sprint: both >= 1.
   PASS when both conditions hold.

8. **Stale Sprint 9/10/11 references corrected to Sprint 10/11/12 in sprint-07.md** [weight: 6%]:
   Run `grep -c 'Sprint 10.*Planner harness-build\|Planner harness-build.*Sprint 10' .harness/contracts/sprint-07.md` and assert count >= 1.
   Run `grep -c 'Sprint 11.*Ephemeral\|Ephemeral.*Sprint 11' .harness/contracts/sprint-07.md` and assert count >= 1.
   Run `grep -c 'Sprint 12.*Positioning\|Positioning.*Sprint 12' .harness/contracts/sprint-07.md` and assert count >= 1.
   Pre-sprint baseline: sprint-07.md currently references "Sprint 9", "Sprint 10", "Sprint 11" in the Out of Scope section (lines 107-109 confirmed by grep). Post-sprint: references updated to Sprint 10, 11, 12 respectively.
   PASS when all three conditions hold.

9. **Stale references corrected in sprint-08.md and DEC-0011 awk-anchor fixed in sprint-10.md** [weight: 6%]:
   Run `grep -c 'Sprint 10.*Planner harness-build\|Planner.*Sprint 10' .harness/contracts/sprint-08.md` and assert count >= 1.
   Run `grep -c 'Sprint 11.*End-to-end\|End-to-end.*Sprint 11\|Sprint 11.*ephemeral' .harness/contracts/sprint-08.md` and assert count >= 1.
   Run `grep -c 'Sprint 12.*Positioning\|Positioning.*Sprint 12' .harness/contracts/sprint-08.md` and assert count >= 1.
   Run `grep -c '### Artifact 2:' .harness/contracts/sprint-10.md` and assert count >= 1 (confirms the awk anchor was corrected from `## Artifact 2` to `### Artifact 2:`).
   Pre-sprint baselines: sprint-08.md references "Sprint 9", "Sprint 10", "Sprint 11" similarly to sprint-07.md; sprint-10.md has `/^## Artifact 2/` (h2 anchor, wrong). Post-sprint: all updated.
   PASS when all four conditions hold.

### Structural (artifact-inspected)

10. **sprint-workflow/SKILL.md existing step headings are preserved unmodified** [weight: 4%]:
    Run the following and assert each returns the exact specified count:
    ```
    grep -c '^## Step 0:' plugins/trine-eval/skills/sprint-workflow/SKILL.md
    grep -c '^## Step 1:' plugins/trine-eval/skills/sprint-workflow/SKILL.md
    grep -c '^## Step 2:' plugins/trine-eval/skills/sprint-workflow/SKILL.md
    grep -c '^## Step 3:' plugins/trine-eval/skills/sprint-workflow/SKILL.md
    grep -c '^## Step 4:' plugins/trine-eval/skills/sprint-workflow/SKILL.md
    grep -c '^## Step 5:' plugins/trine-eval/skills/sprint-workflow/SKILL.md
    ```
    All six commands must return 1. Pre-sprint baseline: all six return 1 (Steps 0–5 present in the current file). Post-sprint: unchanged at 1 each.
    PASS when all six commands return exactly 1.

11. **sprint-contract/SKILL.md Task Taxonomy section remains unmodified** [weight: 4%]:
    Run `grep -c '## Task Taxonomy: sprint-NN.tasks.json' plugins/trine-eval/skills/sprint-contract/SKILL.md` and assert count == 1.
    Run `grep -c '"behavioral"\|"structural"\|"llm-judge"' plugins/trine-eval/skills/sprint-contract/SKILL.md` and assert count >= 3 (the 3-way enum examples are intact).
    Pre-sprint baseline: heading count = 1, enum count >= 3 (confirmed). Post-sprint: same.
    PASS when both conditions hold.

### LLM-as-judge (reading-comprehension)

12. **Ported step text quality: Steps 0.5, 1d, 3a–3e, and Operational Notes are complete, coherent, and additive** [weight: 22%]:
    Read the updated `plugins/trine-eval/skills/sprint-workflow/SKILL.md`. PASS requires ALL of the following:
    (a) **Step 0.5 (regression gate):** The section explains: (1) the 4 guard conditions under which Step 0.5 is a no-op (no `regression.json`, empty `tasks` array, `regression.enabled: false`, or auto-default), (2) the execution protocol (read file, run each verification_command verbatim, record PASS/FAIL, write run result to `.harness/regression/runs/`), (3) the Windows-bash invocation hazard or a clear note about platform-specific considerations, and (4) the `fail_fast` behavior (default true: abort sprint on any FAIL; false: warn and continue). The text must be specific enough that a Generator reading the workflow knows exactly when to skip the gate and what to do when it runs.
    (b) **Step 1d (tasks.json emission):** The section names: (1) the trigger condition (after `Status: APPROVED`, before IMPLEMENTATION mode), (2) the config guard (`config.taxonomy.emit_tasks_json`, default true), (3) the `sprint-contract/SKILL.md` cross-reference for schema and field semantics, and (4) the consequence of skipping emission (downstream synthesis weakens audit chain). Also includes the features.json advancement instruction (DEC-0019): when emit_tasks_json runs, also append any new sprint features from `sprints.json[sprint].features` to `.harness/features.json` (additive merge by feature id; no overwrites of existing entries).
    (c) **Steps 3c–3e (trial loop, batch API, transcript capture):** Step 3c clearly distinguishes the trial loop (independent trials at fixed code state) from the retry loop (bug-fix between rounds), with a table or clear prose explaining the `trials` config knob, file-naming convention (`-tT` suffix), and when trials > 1 differ from the default. Step 3d explains the batch API trigger conditions (both `batch.enabled == true` AND criterion count >= `batch.min_criteria`) and the invariant that the per-criterion file shape is byte-for-byte identical to the synchronous path. Step 3e explains the trailer extraction protocol (locate `## Transcript Trailer`, parse fenced JSON, write to `.harness/transcripts/`), the failure-tolerant posture (skip without failing eval if trailer missing), and the backward-compatibility stance.
    (d) **Operational Notes:** The `## Operational Notes` section contains at minimum: (1) an "Evaluator Fallback" subsection explaining when the main thread may author the eval (tool limitation only, not a feature), what a `## Process Note` disclosure must contain, and the rubric penalty for fallback evals (typically 3/5 on generator_evaluator_separation); and (2) a "thinking.profile" subsection documenting the three reserved values (`default`, `fast`, `thorough`) and their runtime translations.
    (e) **Additive integrity:** The new sections do not alter or paraphrase any of the existing 6-step bodies (Steps 0–5). The JIT context scope annotations (`<!-- Context scope at this step: -->`) in Steps 0, 1, 2, 3, 4, 5 remain intact. The Lazy Loading table and Session Resumption section are not modified.

13. **Council-gate wording quality: b1 and b2 gates are correct, complete, and respect the andon-stop protocol** [weight: 4%]:
    Read the governance-gate additions to `plugins/trine-eval/skills/sprint-workflow/SKILL.md`. PASS requires ALL of the following:
    (a) **b1 gate (pre-sprint warn):** The gate fires when `config.governance.enabled` is true AND `config.governance.review_frequency` is set (any value). It checks for `.council/sprint-prebrief/sprint-{NN}.json`. If the file is absent, the gate emits a WARN message identifying the missing file path. The gate does NOT block — it is warn-only. The gate is placed within Step 0 (before Step 0.5 regression gate).
    (b) **b2 gate (post-sprint auto-trigger):** The gate fires when `config.governance.enabled` is true AND `config.governance.review_frequency == "every-sprint"`. It invokes `/henkaten-council:council-autorun` as the final action of Step 5, after updating `progress.md`, `sprint-state.json`, and git checkpoint, but before reporting to the user. The gate text must state: if the council-autorun returns an andon halt or autonomy-floor breach, surface it to the user before offering the next sprint.
    (c) **Backward compatibility:** When `config.governance.enabled` is false or the `governance` key is absent from `config.json`, neither gate fires. A project without a governance config behaves identically to the current sprint-workflow SKILL.md.
    (d) **No blocking in b1:** The b1 gate must not introduce a `fail_fast` style abort — it is explicitly warn-only. Any wording that could be read as blocking (e.g., "halt if missing") is a FAIL for this sub-criterion.

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT alter the substantive body of any existing step in sprint-workflow/SKILL.md** (Steps 0, 1, 2, 3, 4, 5 and their existing subsections): The port is additive only — Step 0.5 is inserted after Step 0, Step 1d after Step 1c, Steps 3a–3e replace or augment the bare `## Step 3` body, and Operational Notes is appended at the end. No word of the existing step bodies (including the Lazy Loading table, Session Resumption section, and all `<!-- Context scope -->` annotations) may be changed.
   Verify:
   ```
   grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   ```
   assert count >= 5. Pre-sprint baseline: 5 (confirmed — sprint-workflow/SKILL.md has JIT annotations at Steps 0, 1, 2, 4, 5; Step 3 does not yet have the `<!-- Context scope at this step: -->` comment because it currently only has `### 3a` and `### 3b` stubs). The port adds the Step 3 comment as part of the ported `## Step 3: Evaluation` structure, so post-sprint count is >= 5. Post-sprint: must remain >= 5.
   Also verify:
   ```
   grep -c 'Lazy Loading' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   grep -c 'Session Resumption' plugins/trine-eval/skills/sprint-workflow/SKILL.md
   ```
   Both must return >= 1.

2. **Should NOT modify the Sprint 9 Task Taxonomy section in sprint-contract/SKILL.md**: The `## Task Taxonomy: sprint-NN.tasks.json` section ported in Sprint 9 must remain byte-for-byte intact except for the SN2 carve-out amendment (which is an additive section, not a modification of the Taxonomy section). Verify:
   ```
   grep -c '## Task Taxonomy: sprint-NN.tasks.json' plugins/trine-eval/skills/sprint-contract/SKILL.md
   ```
   assert count == 1 (heading unchanged).
   ```
   grep -c 'grader_type.*behavioral.*structural.*llm-judge\|"behavioral"\|"structural"' plugins/trine-eval/skills/sprint-contract/SKILL.md
   ```
   assert count >= 2 (3-way enum examples intact).

3. **Should NOT apply semantic edits to sprint-07.md or sprint-08.md beyond renumbering**: The SN2 carve-out permits ONLY renumbering of Sprint N references (9→10, 10→11, 11→12). No prose rewriting, no criterion text changes, no weight changes, no new sections. Verify that the diff is limited to line-level number substitutions:
   ```
   git diff HEAD -- .harness/contracts/sprint-07.md
   git diff HEAD -- .harness/contracts/sprint-08.md
   ```
   The diff must contain ONLY lines where "Sprint 9", "Sprint 10", or "Sprint 11" has been replaced by the corrected sprint number. Any addition, deletion, or other change is a FAIL.
   Note: The `## Revision History` block added to each file under the SN2 carve-out mandate is a permitted addition (it is the carve-out's required metadata).

4. **Should NOT modify `.harness/spec.md`**: The Phase 1, 1.5, 1.6, and 2 sections of spec.md are read-only for this sprint. Verify:
   ```
   git diff HEAD -- .harness/spec.md
   ```
   must produce empty output (no diff).

5. **Should NOT modify any prior sprint's eval results** (`.harness/evals/`): Eval files are append-only. Verify:
   ```
   git diff HEAD -- .harness/evals/
   ```
   must produce empty output (no diff). Pre-sprint baseline: all eval files committed and unmodified.

6. **Should NOT remove or alter the core config fields** in `.harness/config.json` (`project_type`, `rubric`, `max_retries`, `governance.enabled`): Verify:
   ```
   jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json
   ```
   must output `true`.

## Reference Solutions

**Criterion J12 — Ported step text quality (highest-weighted LLM-judge criterion, 22%):**

The following illustrates the required quality and structure for the ported Step 0.5 and Operational Notes additions in `plugins/trine-eval/skills/sprint-workflow/SKILL.md`. The exact prose may differ; the structural and content elements below must be present:

```markdown
## Step 0.5: Regression Gate

Before negotiating any new contract, verify that every previously graduated capability still
passes.

### Guard conditions — when Step 0.5 is a no-op

1. If `.harness/regression/regression.json` does **not** exist, skip this step entirely.
2. If `.harness/regression/regression.json` exists but its `tasks` array is empty, skip.
3. If `config.regression.enabled` is explicitly `false`, skip.
4. Otherwise (file exists with a non-empty `tasks` array, and `regression.enabled` is truthy
   or absent — the auto-default), execute the gate as described below.

### Execution

1. Read `.harness/regression/regression.json`.
2. For each entry in the `tasks` array:
   - Execute `task.verification_command` **verbatim** — do not paraphrase, reconstruct,
     or substitute variables. The exact string recorded in `regression.json` is what ran
     when the criterion was graduated; running the same command preserves the audit chain.
   - Record PASS if exit code is `0`, FAIL otherwise. Capture stdout, stderr, and exit code.

> **Windows-bash invocation hazard.** Do not invoke `task.verification_command` via
> `subprocess.run(['bash', '-c', cmd])`. On Windows with WSL installed, Python's PATH resolver
> picks `wsl bash` (no distros by default) and the command fails silently. Use either
> `subprocess.run(cmd, shell=True)` (cmd.exe; finds tools on PATH) or explicit
> `C:\Program Files\Git\bin\bash.exe`.

3. Write an aggregate results file to `.harness/regression/runs/run-<UTC-ISO8601>.json` with
   shape:
   ```json
   { "timestamp": "2026-06-02T18:45:00Z", "sprint_about_to_run": 13,
     "results": [
       { "task_id": "s07-c1", "graduated_from_sprint": 7,
         "verification_command": "...", "verdict": "PASS",
         "exit_code": 0, "stdout": "...", "stderr": "" }
     ] }
   ```
4. If any task's verdict is FAIL:
   - Read `config.regression.fail_fast` (default `true` when absent).
   - If `fail_fast` is true: **abort the sprint**. Print the failing `task_id`s along with
     their `graduated_from_sprint` origin.
   - If `fail_fast` is false: print a warning, note the regression in `progress.md`, continue.
5. If every task passes (or the step was skipped), continue to Step 1.

### Config defaults

- `config.regression.enabled` — default is *auto*: truthy when `regression.json` exists with
  a non-empty `tasks` array, falsy otherwise.
- `config.regression.fail_fast` — default `true`.

---

## Operational Notes

### Evaluator Fallback

The Evaluator subagent runs forked (`context: fork` in `agents/evaluator.md`) and writes its
eval markdown directly via the `Write` tool. This is the **default and preferred** path.

**When the fallback applies.** If the Evaluator subagent fails to write the eval file due to
a **tool limitation** (e.g., the agent's `tools:` frontmatter does not include `Write`), the
main thread may transcribe the eval markdown into `.harness/evals/sprint-{NN}-r{R}.md` so the
sprint can complete. This is an **escape valve, not a feature** — every fallback invocation is
a regression in Generator/Evaluator separation that must be flagged.

**How to flag a fallback eval.** When the main thread writes the eval, it must add a
`## Process Note` section near the top of the eval file disclosing:
- That the eval was authored by the main-thread orchestrator, not a forked Evaluator subagent
- The reason for the fallback (cite the specific tool limitation or dispatch failure)
- Which deterministic verification commands were run verbatim from the contract

**Rubric impact.** A sprint whose eval was written via fallback typically scores 3/5 on the
`generator_evaluator_separation` rubric dimension instead of 5/5.

### thinking.profile

`config.thinking.profile` is a per-installation knob that selects how the harness translates
`thinking: { type: adaptive, effort: ... }` declarations into runtime API parameters.

Reserved values:
- `"default"` → standard adaptive thinking. Each agent's frontmatter `effort: medium|high|max`
  maps to adaptive defaults. No override applied at the orchestrator layer.
- `"fast"` → no extended thinking. The orchestrator strips `thinking` from outgoing API
  requests regardless of frontmatter declaration. Trades accuracy for latency and cost.
- `"thorough"` → high-budget extended thinking. Forces a high `budget_tokens` on every
  thinking-enabled message. Trades latency and cost for highest reasoning quality.
```

**Key quality markers:** The Step 0.5 section covers all 4 guard conditions, the verbatim-execution mandate, the Windows hazard, the run file shape, and the fail_fast default. The Operational Notes section names both subsections (Evaluator Fallback and thinking.profile), explains the fallback as an escape valve (not a feature), specifies the `## Process Note` disclosure requirement, cites the rubric penalty, and lists all 3 thinking.profile reserved values with their translations.

## Out of Scope

- **Runtime dispatch wiring for synthetic-authoring detection (HK-0006):** The Sprint 12 vulnerability where B1 (simulation behavioral) cannot verify whether a real kickoff session dispatches the Planner correctly is NOT structurally closed by Sprint 13's workflow-step port. That requires a runtime audit hook. Deferred to a future sprint.
- **Arming regression.json with real graduated criteria:** The Step 0.5 port documents the regression gate; creating `.harness/regression/regression.json` with actual graduated entries requires harness-summary to first run saturation analysis. NOT in scope — the gate activates when harness-summary first graduates a criterion.
- **Sprints 1–8 tasks.json back-fill:** The Sprint 9 back-fill covered Sprints 7–8 only. Sprints 1–6 remain deferred (require per-criterion 3-way grader classification decisions). NOT in scope.
- **Live Batch API endpoint wiring (Step 3d):** The port documents the protocol; end-to-end submission against a live `/v1/messages/batches` endpoint is deferred (matches Sprint 9 posture).
- **Live transcript runtime extraction (Step 3e):** The port documents the protocol; runtime-instrumented transcript extraction against a live evaluator subagent is deferred (matches Sprint 9 posture).
- **Back-filling council session logs for Sprints 1–6:** Council infrastructure was not in place for those sprints. NOT in scope.
- **Modifying `.harness/sprints.json` or any already-approved Sprint 10, 11, 12 contracts** beyond the DEC-0011 awk-anchor fix to sprint-10.md.
- **Semantic edits to sprint-07.md or sprint-08.md** beyond renumbering Sprint 9→10, Sprint 10→11, Sprint 11→12 and adding the required `## Revision History` block.
- **tasks.json emission for Sprint 13:** Per the standard Step 1d protocol, `sprint-13.tasks.json` is emitted after contract approval and before IMPLEMENTATION mode. Listed here to clarify it is a Step 1d post-approval task, not an implementation deliverable.

## Technical Notes

**Grader-split rationale (behavioral % shown):**

Sprint 13 delivers text additions to five files: (a) `sprint-workflow/SKILL.md` (step port + governance gates), (b) `sprint-contract/SKILL.md` (SN2 carve-out amendment), (c) `sprint-07.md` (renumbering), (d) `sprint-08.md` (renumbering), (e) `sprint-10.md` (awk anchor fix). No runnable binary, hook listener, or library function is introduced.

Following Sprint 9/10/11/12 precedents for `grep` and `jq` invocations on text artifacts as behavioral:
- B1–B9: shell-command behavioral (`grep -c` on SKILL.md files, checking pre-sprint-absent sections). All pre-sprint baselines are 0 for the new sections. Post-sprint positive counts are non-trivially non-zero.
- S10–S11: structural (artifact-inspected at rest — preservation checks that must return the same value pre- and post-sprint, not proving new content).
- J12–J13: LLM-judge (reading comprehension — quality of ported text, correctness of governance gate wording).

Weight breakdown:
- Behavioral: B1 (8%) + B2 (8%) + B3 (8%) + B4 (6%) + B5 (8%) + B6 (8%) + B7 (8%) + B8 (6%) + B9 (6%) = **66%**
- Structural: S10 (4%) + S11 (4%) = **8%**
- LLM-as-judge: J12 (22%) + J13 (4%) = **26%**
- Total: 66% + 8% + 26% = **100%** ✓

Behavioral coverage: 66% >= 60% floor. Confirmed without needing a static-artifact exception.

**Why b2 auto-trigger is a text/protocol delivery in this sprint:**

The b2 auto-trigger in Step 5 is a workflow instruction that the harness orchestrator (running as a Claude Code session) will follow when it reads the updated `sprint-workflow/SKILL.md`. The trigger is behavioral in the sense that the orchestrator runs `/henkaten-council:council-autorun` — but the exercising of that live command requires a live council session, not a shell command from the evaluator. The criterion for b2 (B6) verifies that the protocol text is present and references the correct command; the runtime exercise is the next council-triggered sprint run. This matches Sprint 8's posture for Batch API (`thinking.profile` documented in Sprint 8; runtime hookup observed post-delivery) and Sprint 9's posture for transcript emission.

**Sprint 7/Sprint 12 static-artifact carve-out — not invoked:**

Sprint 13 achieves 66% behavioral coverage through B1–B9, which are shell-verifiable grep commands on files that did not contain the new sections pre-sprint. The static-artifact exception (invoked in Sprints 7 and 12) is NOT needed. All nine behavioral criteria qualify under the standard grep-as-behavioral precedent.

**SN2 carve-out policy boundary:**

The SN2 carve-out, introduced formally in Sprint 13, permits the following under a plan-amendment:
- Renumbering Sprint N references in approved markdown contracts (e.g., "Sprint 9" → "Sprint 10") when the plan was amended to insert a new sprint that shifted all subsequent sprint numbers.
- Adding a `## Revision History` block to the amended contract citing the plan-amendment commit and the date of renumbering.

The following remain FORBIDDEN even under the SN2 carve-out:
- Any change to criterion text, weights, grader type tags, Should-NOT gate text, or reference solutions.
- Adding, removing, or reordering criteria.
- Changing prose outside of sprint-number literals in scope (i.e., "Sprint N" renumberings).
- Applying the carve-out without a `## Revision History` block in the amended file.

The carve-out is encoded in `sprint-contract/SKILL.md` as a new subsection distinct from the existing `## Task Taxonomy` section (which remains untouched).

**DEC-0019 structural fix (features.json sync):**

DEC-0019 (deferred to Sprint 13 contract drafting) routes the recurring SG drift pattern where `features.json` is not updated at sprint completion. Sprint 13 addresses this by adding a features.json advancement step to the Step 1d instructions: when the Generator emits `sprint-{NN}.tasks.json`, it also appends any features listed in `sprints.json[sprint].features` to `.harness/features.json` (additive merge by feature id; no overwrites of existing entries). This is a protocol addition, not a SKILL.md behavior change — it closes the recurrence class that produced SG alerts in Sprints 10 and 12.

**Pre-sprint baselines (no-op detection — verified against current repo):**

| Command | Pre-sprint expected | Notes |
|---------|-------------------|-------|
| `grep -c '## Step 0.5' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B1 not a no-op |
| `grep -c '### 1d' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B2 not a no-op |
| `grep -c '### 3c' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B3 not a no-op |
| `grep -c '### 3d' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B3 not a no-op |
| `grep -c '### 3e' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B3 not a no-op |
| `grep -c '## Operational Notes' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B4 not a no-op |
| `grep -ci 'sprint-prebrief' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B5 not a no-op |
| `grep -ci 'council-autorun' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 0 | B6 not a no-op |
| `grep -ci 'SN2.*carve-out\|renumbering-only' plugins/trine-eval/skills/sprint-contract/SKILL.md` | 0 | B7 not a no-op |
| `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 5 | SN1 baseline confirmed (5 annotations in sprint-workflow SKILL.md; sprint-workflow differs from harness-kickoff SKILL.md which has 6) |
| `jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json` | true | SN6 baseline confirmed |
| `grep -c '^## Step 0:' plugins/trine-eval/skills/sprint-workflow/SKILL.md` | 1 | S10 baseline confirmed |
| `grep -c '## Task Taxonomy: sprint-NN.tasks.json' plugins/trine-eval/skills/sprint-contract/SKILL.md` | 1 | S11 baseline confirmed |

Evaluator should run all baseline checks before grading to confirm no-op-detection status.

**sprint-10.md awk-anchor fix scope:**

DEC-0011 flagged that sprint-10.md's B7 verification command uses `/^## Artifact 2/` as the awk anchor, but `planner.md` has `### Artifact 2:` (h3, not h2). The fix replaces the anchor with `/^### Artifact 2:/` (and adjusts the boundary pattern accordingly). This is a one-line renumbering/correction within the Revision History of sprint-10.md and falls under the SN2 carve-out. The `## Revision History` block in sprint-10.md is amended to record this fix with the plan-amendment commit reference.

**File paths for Sprint 13:**

- Modified (additive port): `plugins/trine-eval/skills/sprint-workflow/SKILL.md`
- Modified (additive amendment): `plugins/trine-eval/skills/sprint-contract/SKILL.md`
- Modified (renumbering-only, SN2 carve-out): `.harness/contracts/sprint-07.md`, `.harness/contracts/sprint-08.md`
- Modified (awk-anchor fix, SN2 carve-out): `.harness/contracts/sprint-10.md`
- Read-only inputs: `.harness/spec.md`, `.harness/sprints.json`, `.harness/config.json`, all eval files, `sprint-09.md`, `sprint-11.md`, `sprint-12.md`

**Council decision traceability:**

- DEC-0010: Plan amendment authorizing Sprint 13; includes (a) workflow-step port, (b) pre-sprint gate (b1), (c) SN2 carve-out + stale-refs cleanup.
- DEC-0011: Extends (b) to bidirectional gates (b1 pre-sprint + b2 post-sprint auto-trigger); routes DEC-0011 awk-anchor fix to Sprint 13 under SN2 carve-out.
- DEC-0012: Ratifies standard-work PROC-001/002/003; yokoten blocks on HK-0002/0003/0005. PROC-001 (Generator pre-flight verification-command checklist) applies to this contract.
- DEC-0019: Defers features.json-sync structural fix to Sprint 13 contract drafting. Resolved by Step 1d amendment in (b).

Sprints 9, 10, 11, 12 all PASS (per sprint-state.json). All four dependencies satisfied.

## Evaluator Review

**Round:** 1

### Verification Summary

All pre-sprint baselines were run directly against the current repo state. Commands and outputs follow.

**B1 baselines:**
- `grep -c '## Step 0.5' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓
- `grep -ci 'regression.*gate\|regression\.json\|regression\.enabled' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓

**B2 baselines:**
- `grep -c '### 1d' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓
- `grep -ci 'emit_tasks_json\|tasks\.json.*emit\|APPROVED.*tasks\|tasks.*APPROVED' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓

**B3 baselines:**
- `grep -c '### 3c' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓
- `grep -c '### 3d' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓
- `grep -c '### 3e' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓
- `grep -c '### 3a' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 1 (lines 101 and 111 confirmed for 3a and 3b)

**B4 baselines:**
- `grep -c '## Operational Notes' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓

**B5 baselines:**
- `grep -ci 'sprint-prebrief' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓
- `grep -ci 'WARN\|warn' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓

**B6 baselines:**
- `grep -ci 'council-autorun' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓
- `grep -ci 'andon.*stop\|andon.*halt\|andon-stop' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 0 ✓

**B7 baselines:**
- `grep -ci 'SN2.*carve-out\|renumbering-only' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 0 ✓
- `grep -ci 'plan-amendment.*commit\|amendment.*commit\|Revision History.*block' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 0 ✓

**B8 baselines (sprint-07.md):**
- `grep -c 'Sprint 10.*Planner harness-build\|Planner harness-build.*Sprint 10' .harness/contracts/sprint-07.md` → 0 ✓
- `grep -c 'Sprint 11.*Ephemeral\|Ephemeral.*Sprint 11' .harness/contracts/sprint-07.md` → 0 ✓
- `grep -c 'Sprint 12.*Positioning\|Positioning.*Sprint 12' .harness/contracts/sprint-07.md` → 0 ✓

**B9 baselines (sprint-08.md and sprint-10.md):**
- `grep -c 'Sprint 10.*Planner harness-build\|Planner.*Sprint 10' .harness/contracts/sprint-08.md` → 0 ✓
- `grep -c 'Sprint 11.*End-to-end\|End-to-end.*Sprint 11\|Sprint 11.*ephemeral' .harness/contracts/sprint-08.md` → 0 ✓
- `grep -c 'Sprint 12.*Positioning\|Positioning.*Sprint 12' .harness/contracts/sprint-08.md` → 0 ✓
- `grep -c '### Artifact 2:' .harness/contracts/sprint-10.md` → 0 ✓

**S10 baselines:** All six step headings return 1 each (`^## Step 0:` through `^## Step 5:`) ✓

**S11 baselines:**
- `grep -c '## Task Taxonomy: sprint-NN.tasks.json' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 1 ✓
- `grep -c '"behavioral"\|"structural"\|"llm-judge"' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 4 (>= 2 required) ✓

**SN1 baselines:**
- `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/sprint-workflow/SKILL.md` → 5 ✓
  (Steps 0, 1, 2, 4, 5 — confirmed by line-level grep)
- `grep -c 'Lazy Loading' ...` → 1 ✓
- `grep -c 'Session Resumption' ...` → 1 ✓

**SN2 baseline:**
- `grep -c '## Task Taxonomy: sprint-NN.tasks.json' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 1 ✓
- `grep -c 'grader_type.*behavioral.*structural.*llm-judge\|"behavioral"\|"structural"' ...` → 4 (>= 2) ✓

**SN6 baseline:**
- `jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json` → true ✓

---

### Issues Found

#### Issue 1 (NON-BLOCKING, advisory) — SN1 explanation is factually inaccurate

**Location:** Should-NOT criterion 1, line 141.

**Problem:** The SN1 prose states: "Step 3 does not yet have the `<!-- Context scope at this step: -->` comment because it currently only has `### 3a` and `### 3b` stubs."

This is factually wrong. Step 3 already has a context scope annotation at line 98 of sprint-workflow/SKILL.md:

```
<!-- Context scope at Step 3: contracts/sprint-{NN}.md, config.json, rubric file (deferred until 3b) -->
```

The existing annotation uses "at Step 3:" (not "at this step:"), which is why `grep -c '<!-- Context scope at this step:'` returns 5 (not 6). The contract's count of 5 is correct; only the narrative explanation is wrong.

**Impact on grading:** None — the verification command and threshold are correct. The pre-sprint baseline of 5 is accurate. The SN1 gate functions correctly: any Generator that removes one of the 5 existing "at this step:" annotations would drop the count below 5 and trigger a FAIL. The incorrect prose could confuse a Generator into thinking Step 3 has no context annotation and that adding one is purely additive, when in fact it has one in a slightly different format.

**Recommended fix:** Change the parenthetical to: "(Sprint-workflow SKILL.md has 5 exact-match 'at this step:' annotations at Steps 0, 1, 2, 4, 5; Step 3 uses a variant format `<!-- Context scope at Step 3: ...-->` which is NOT matched by the grep. The port may add a new conformant annotation to Step 3 — post-sprint count must remain >= 5.)"

This issue is advisory only. It does not block approval.

---

#### Issue 2 (NON-BLOCKING, advisory) — B9: Sprint-08.md has stale Sprint 10 references outside Out of Scope that the PASS conditions do not check

**Location:** B9 criterion; sprint-08.md lines 68, 437, 450, 557.

**Problem:** Sprint-08.md contains four "Sprint 10" references outside its Out of Scope section (at B4's criterion text and multiple Technical Notes repetitions), all of which are stale because "Ephemeral dogfood validation" shifted from Sprint 10 to Sprint 11. Specifically:

- Line 68: `entry that Sprint 10 will exercise when grading an ephemeral harness fixture`
- Lines 437, 450, 557: Similar repetitions in Technical Notes

Under SN3, the diff MUST contain only renumbering-line substitutions — the gate does not exempt any section from the renumbering requirement. If the Generator renumbers only the Out of Scope section (lines 230–234) and misses lines 68/437/450/557, the SN3 diff check will FAIL because those lines still say "Sprint 10" when they should say "Sprint 11".

However, B9's PASS conditions (checking for "Sprint 10 Planner harness-build", "End-to-end Sprint 11", "Sprint 12 Positioning") only verify three specific patterns from the Out of Scope section. They do not verify that lines 68/437/450/557 were also corrected. A Generator that fixes only Out of Scope would PASS B9 but FAIL SN3.

This is a potential false-positive on B9 when SN3 catches the partial renumbering. The evaluation will still be correct overall (SN3 catches the regression), but B9 gives a misleading PASS.

**Recommended fix:** Add a fourth PASS condition to B9: `grep -c 'Sprint 11.*ephemeral harness fixture\|ephemeral harness fixture.*Sprint 11' .harness/contracts/sprint-08.md >= 1` — this confirms the non-Out-of-Scope "Sprint 10 will exercise when grading an ephemeral harness fixture" references (lines 68, 437, 450, 557) were also renumbered.

This issue is advisory. The SN3 gate provides the backstop. The contract remains testable and correct in its ultimate verdict.

---

#### Issue 3 (NON-BLOCKING, advisory) — J12 reference solution covers only sub-criteria (a) and (d); (b)(c)(e) have no reference anchors

**Location:** Reference Solutions section (J12 at 22%).

**Problem:** J12 has five sub-criteria: (a) Step 0.5, (b) Step 1d, (c) Steps 3c–3e, (d) Operational Notes, (e) additive integrity. The Reference Solution covers (a) and (d) completely. Sub-criteria (b), (c), and (e) have no reference examples. 

The sprint-contract/SKILL.md template says the highest-weighted LLM-judge criterion "should have" a reference solution — not that the reference must be exhaustive. The sub-criteria for (b)(c)(e) are detailed enough in J12's criterion text to anchor LLM judgment, and providing a complete reference for all five would make the contract unwieldy.

**Assessment:** This is acceptable. The J12 criterion text for (b)(c)(e) is specific enough (naming exact field names, protocol semantics, and config knobs) that two evaluators would likely reach the same verdict without a reference. The existing reference solution covers the two most complex sections.

This is advisory only.

---

### Criteria Confirmed Sound

- **B1–B9:** All behavioral criteria have correct pre-sprint baselines confirmed by command execution. All grep patterns execute without error on this platform. Post-sprint PASS conditions are unambiguous integers. No no-op criteria detected.
- **S10–S11:** Structural criteria have correct pre-sprint baselines. The preservation checks (step headings return exactly 1 each; taxonomy section count unchanged) are sound regression guards.
- **J12:** The criterion is specific with named protocol elements, config fields, and behavioral requirements for each sub-section. The partial reference solution anchors the most complex subsections.
- **J13:** The four-part council gate wording quality check is specific and self-contained. The warn-only constraint (no `fail_fast`-style abort) is clearly stated in (d) as an explicit FAIL condition.
- **SN1–SN6:** All gate commands run without error. Pre-sprint baselines match reality. SN3 (git diff check) correctly limits renumbering scope. SN4 and SN5 (spec.md and eval files read-only) are standard protection gates.
- **Weight sum:** 66% + 8% + 26% = 100% ✓
- **Behavioral coverage:** 66% ≥ 60% floor ✓
- **Reference solution completeness:** J12 (highest-weighted LLM-judge, 22%) has a reference solution as required. ✓
- **Deliverable coverage:**
  - (a) Workflow-step port: B1 (Step 0.5), B2 (Step 1d), B3 (Steps 3c/3d/3e), B4 (Operational Notes), J12 (quality) ✓
  - (b1) Pre-sprint warn-only gate: B5 (presence + warn language), J13 (b1 correctness including no-block constraint) ✓
  - (b2) Post-sprint auto-trigger: B6 (presence + andon-stop reference), J13 (b2 correctness) ✓
  - (c) SN2 carve-out: B7 (carve-out amendment in sprint-contract SKILL.md) ✓
  - (c) Stale-refs cleanup: B8 (sprint-07.md renumbering), B9 (sprint-08.md renumbering + sprint-10.md awk anchor fix) ✓
- **Protected files coverage:** SN1 (sprint-workflow existing steps), SN2 (sprint-contract Task Taxonomy), SN3 (sprint-07.md/sprint-08.md), SN4 (spec.md), SN5 (eval files), SN6 (config.json core fields) ✓
- **No-op detection:** All behavioral criteria confirmed non-no-op by pre-sprint baseline verification ✓
- **Grader-type tagging:** All criteria correctly tagged. The grep-as-behavioral precedent is correctly invoked with citation to Sprint 9/10/11 precedent and the three qualifying conditions ✓
- **Sprint 7/12 static-artifact carve-out:** Correctly noted as NOT invoked (66% behavioral coverage achieved without it) ✓
- **DEC-0011 awk-anchor fix scope:** The fix (B9 check 4) correctly targets `### Artifact 2:` which matches planner.md's actual heading (`### Artifact 2: .harness/sprints.json` at line 28). Pre-sprint count of 0 confirmed; post-sprint count of >= 1 will be achieved by correcting the awk anchor text in sprint-10.md ✓

---

### Summary

Three advisory issues were found, none blocking:

1. **(Advisory)** SN1 prose incorrectly states "Step 3 does not yet have a `<!-- Context scope at this step: -->` comment." Step 3 has a context annotation in a slightly different format ("at Step 3:"). The gate command and threshold are correct; only the narrative is wrong.
2. **(Advisory)** B9's PASS conditions do not verify that sprint-08.md's non-Out-of-Scope "Sprint 10" references (lines 68, 437, 450, 557) were renumbered. SN3 provides the backstop but B9 gives a partial pass signal. Consider adding a fourth grep check.
3. **(Advisory)** J12 reference solution covers only sub-criteria (a) and (d); (b)(c)(e) have no explicit reference. The detailed criterion text is sufficient compensation.

No blocking issues found. All verification commands execute correctly. All pre-sprint baselines match contract claims. Weight sum and behavioral coverage floor are satisfied.

**Status: APPROVED**
