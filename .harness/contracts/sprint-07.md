# Sprint 07 Contract: harness-build Rubric (Phase 2)

## Revision History

**Rev 1 (2026-06-01) — Evaluator NEEDS REVISION addressed:**
1. **S6 broken grep** — Changed `'^- \`'` (single-quoted, BRE no-match) to `"^- \`"` (double-quoted, correctly returns 5 pre-sprint / 6 post-sprint).
2. **SN1 incorrect baseline** — Corrected count from 5 to 6 (Steps 1, 2, 2b, 3, 4, 5); tightened threshold from `>= 5` to `>= 6`.
3. **B1/B2 "behavioral" labeling advisory** — Retained "simulation behavioral" framing (option b); added explicit one-sentence acknowledgment to the Behavioral section header.

**Rev 2 (2026-06-02) — SN2 carve-out renumbering (Sprint 13 plan amendment):**
Renumber stale Out of Scope sprint references: Sprint 9→10 (Planner harness-build), Sprint 10→11 (Ephemeral dogfood), Sprint 11→12 (Positioning). Authorized under the SN2 carve-out in `sprint-contract/SKILL.md`. No criterion text, weights, or gate logic were changed.

## What I Will Build

Create `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` — a 7-dimension rubric for evaluating agent runtime harnesses against the "Playbook for Building Agent Harnesses" stages, including three UNCONDITIONAL hard-threshold gates (loop termination & bounds, sandboxing, governance placement). Register the new rubric as the sixth entry in `plugins/trine-eval/skills/eval-rubric/SKILL.md`'s Available Rubrics list. Update `plugins/trine-eval/skills/harness-kickoff/SKILL.md` so that Step 1 recognizes `harness-build` as a valid project type and routes to the new rubric.

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `behavioral` (execution-verified), `structural` (artifact-inspected), or `llm-judge` (reading-comprehension).
Weights must sum to 100% across all success criteria.

**Behavioral coverage:** This sprint produces only static markdown/JSON artifacts — a rubric file, a registry line, and a SKILL.md routing clause. No runnable binary, hook, or library function is introduced. Behavioral verification (invoking a skill and observing a state change) would require an end-to-end Claude Code agent run, which the Evaluator cannot execute deterministically from a shell command. Behavioral criteria are therefore minimal — see Technical Notes for full justification.

### Behavioral (execution-verified)

Note: B1 and B2 are "simulation behavioral" — the evaluator traces the documented procedure without invoking a shell command, as no shell-executable entry point exists for this sprint's deliverables (the kickoff skill executes only inside a Claude agent session).

1. **Rubric file is loadable by eval-rubric skill** [weight: 10%]: Simulate the eval-rubric skill's load sequence for `harness-build`: (a) read `.harness/config.json` (or a stub with `"rubric": "harness-build"`), (b) resolve the path `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md`, (c) read that file. The criterion PASSes when the file is present, parses as valid markdown (no read error), and its first heading confirms it is the harness-build rubric (not a placeholder stub). The evaluator must record the resolved path and first heading as evidence. This simulates the skill's runtime lookup without requiring a full Claude Code session.

2. **Kickoff routing step produces correct rubric assignment** [weight: 12%]: Simulate Step 1 and Step 2 of `harness-kickoff/SKILL.md` for a harness-build project: (a) read the updated SKILL.md, (b) follow the project-type detection branch for `harness-build`, (c) construct the `config.json` content that Step 2 would write. The criterion PASSes when the constructed JSON has `"project_type": "harness-build"` and `"rubric": "harness-build"`. The evaluator must quote the exact config.json template from SKILL.md that yields these values as evidence. This verifies the routing clause is present and correctly maps the project type to the rubric.

### Structural (artifact-inspected)

3. **Rubric file exists at correct path** [weight: 5%]: `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` exists. Verify: `Test-Path plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` returns True (PowerShell) or equivalent file-existence check.

4. **Rubric has exactly 7 dimensions** [weight: 8%]: The rubric file contains exactly 7 scored dimensions. Verify: count of level-3 headings (`###`) in `rubrics/harness-build.md` equals 7. Command: `grep -c '^### ' plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` == 7.

5. **Rubric has exactly 3 UNCONDITIONAL hard-threshold gates** [weight: 8%]: The rubric's Hard Thresholds section contains entries for loop termination/bounds, sandboxing, and governance. Verify: `grep -ci 'loop.*terminat\|terminat.*loop\|max.*step\|max.*token\|agentic.*bound' plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` >= 1 AND `grep -ci 'sandbox\|isolat' plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` >= 1 AND `grep -ci 'governance\|human.*review\|approval.*path\|escalat' plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` >= 1.

6. **Rubric is registered as sixth entry in eval-rubric SKILL.md** [weight: 7%]: The Available Rubrics list in `plugins/trine-eval/skills/eval-rubric/SKILL.md` now contains exactly 6 entries, with `harness-build` as one of them. Verify: `grep -c "^- \`" plugins/trine-eval/skills/eval-rubric/SKILL.md` == 6 AND `grep -c 'harness-build' plugins/trine-eval/skills/eval-rubric/SKILL.md` >= 1.

7. **Kickoff SKILL.md contains harness-build project type** [weight: 5%]: The updated harness-kickoff SKILL.md names `harness-build` as a recognizable project type (in Step 1's detection list or type prompt). Verify: `grep -c 'harness-build' plugins/trine-eval/skills/harness-kickoff/SKILL.md` >= 1.

8. **Rubric has a Hard Thresholds section** [weight: 5%]: The rubric file contains a `## Hard Thresholds` heading with the word "UNCONDITIONAL" or equivalent strong gate language. Verify: `grep -c '## Hard Thresholds' plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` >= 1 AND `grep -ci 'unconditional\|automatic.*fail\|blocks.*regardless\|hard.fail' plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md` >= 1.

### LLM-as-judge (reading-comprehension)

9. **Rubric dimensions align to playbook stages** [weight: 15%]: The 7 rubric dimensions must collectively cover the nine stages of the agent-harness playbook plus the cross-cutting governance principle. PASS requires: (a) at least 5 of the following stage themes are addressable by one of the 7 dimensions: control plane / agentic loop, tool registry, projection / planning, skills / instruction execution, sandbox, observation / monitoring, external affordances, governance; (b) each dimension has a clear 1-5 scale with distinct and meaningful descriptions (not just "level 1 is bad, level 5 is good"); (c) dimension weights are explicitly stated and sum to 100%.

10. **Hard-threshold gates are truly UNCONDITIONAL** [weight: 15%]: The three hard-threshold gates (loop termination & bounds, sandboxing, governance placement) must be written as UNCONDITIONAL blockers — i.e., the rubric must state that failing any of these three gates causes automatic sprint failure regardless of the weighted score. PASS requires: (a) all three gate concepts are present in the Hard Thresholds section, (b) each gate's failure condition is stated without a score-based escape hatch (e.g., "cannot be waived," "regardless of weighted score," or "automatic FAIL"), and (c) each gate defines what the harness MUST have documented (not just a score threshold) — e.g., "the harness must document a max-step or max-token bound; absence of this document causes automatic FAIL."

11. **Kickoff routing is non-ambiguous and integrated** [weight: 10%]: After reading the updated `harness-kickoff/SKILL.md`, an evaluator must be able to confirm that: (a) `harness-build` appears as an explicit project type option in Step 1's type-detection list (alongside the existing types), (b) Step 2's `config.json` template maps `harness-build` to `"rubric": "harness-build"` or the mapping is otherwise unambiguous (e.g., a routing table or comment), and (c) the new routing clause does not regress or obscure the existing project type options (`web-app`, `rag-system`, `cli-tool`, `api-service`, `eval-harness`).

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT regress Sprint 6 JIT annotations in harness-kickoff SKILL.md**: The six `<!-- Context scope at this step: ... -->` comment blocks added in Sprint 6 must remain intact in `harness-kickoff/SKILL.md`. Verify: `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` >= 6. (Sprint 6 baseline: 6 such comments present — one per Step 1, Step 2, Step 2b, Step 3, Step 4, and Step 5.)

2. **Should NOT remove or rename any of the existing 5 rubric entries in eval-rubric SKILL.md**: The Available Rubrics list must retain all five original entries (`web-app`, `rag-system`, `cli-tool`, `api-service`, `eval-harness`) with their original names. Verify: `grep -c 'web-app\|rag-system\|cli-tool\|api-service\|eval-harness' plugins/trine-eval/skills/eval-rubric/SKILL.md` >= 5. (Each name must still be present — a rename would reduce this count.)

3. **Should NOT remove the "Context Retrieval Principles" section from harness-kickoff SKILL.md**: This section, added in Sprint 6, documents the JIT/lazy-loading philosophy for the skill. Verify: `grep -c 'Context Retrieval Principles' plugins/trine-eval/skills/harness-kickoff/SKILL.md` >= 1.

4. **Should NOT create an `examples/` directory at the repo root**: Phase 2's ephemeral constraint prohibits committing permanent example fixtures. Verify: `Test-Path examples` returns False (PowerShell) or equivalent absence check on the repo root `examples/` directory.

## Reference Solutions

**Criterion 10 — Unconditional hard-threshold gates:**

The following illustrates the required gate encoding in `harness-build.md`. All three gates must appear in a `## Hard Thresholds` section with language of this strength:

```markdown
## Hard Thresholds

The following three gates are UNCONDITIONAL. Failing any gate causes **automatic sprint FAIL**
regardless of the weighted dimension score. No score-based waiver applies.

- **Loop Termination & Bounds (UNCONDITIONAL):** The harness under evaluation MUST have a
  documented maximum step count OR maximum token budget on its agentic loop. A harness with
  no documented loop bound causes automatic FAIL for this gate. A verbal claim that "the loop
  always terminates" without an enforced numeric limit does not satisfy this gate.

- **Sandboxing (UNCONDITIONAL):** The harness MUST declare that code execution is sandboxed —
  with explicit filesystem, network, or process isolation. Absence of any sandboxing declaration
  causes automatic FAIL. A harness that executes arbitrary tool calls in the host environment
  without isolation does not satisfy this gate.

- **Governance Placement (UNCONDITIONAL):** The harness MUST document a human-review or
  out-of-band approval path for agentic decisions that escalate (irreversible actions, external
  side effects, money movement, or destructive operations). Absence of any documented escalation
  path causes automatic FAIL for this gate.
```

**Criterion 9 — Dimension-to-stage alignment (partial reference):**

The 7 dimensions should map roughly to the following themes (exact names may differ):
1. Control Plane & Agentic Loop — covers loop design, termination, max-step bounds
2. Tool Registry & Safety — covers tool definitions, sandboxing, side-effect declaration
3. Projection & Planning — covers how the harness decomposes tasks, state management
4. Skills & Instruction Execution — covers prompt engineering, skill definitions, instruction quality
5. Observation & Monitoring — covers logging, eval hooks, transcript capture
6. External Affordances — covers outbound integrations, API calls, data retrieval
7. Governance — covers escalation paths, human review, irreversibility checks

## Out of Scope

- **Bootstrap failure catalog (Sprint 8):** The `templates/by-rubric/harness-build.json` playbook-traps template is NOT part of this sprint. Sprint 8 delivers that artifact.
- **Planner harness-build mode (Sprint 10):** The `playbook_stage` field on sprint entries and Planner template tuning for harness-build projects are NOT part of this sprint.
- **Ephemeral dogfood validation (Sprint 11):** End-to-end kickoff against a tmp fixture and `.harness/dogfood-findings.md` are NOT part of this sprint.
- **Positioning README and rubric decision guide (Sprint 12):** `plugins/trine-eval/skills/eval-rubric/rubrics/README.md` explaining when to use `eval-harness` vs `harness-build` is NOT part of this sprint.
- **Changes to the eval-harness rubric:** The existing `rubrics/eval-harness.md` file is not modified by this sprint.
- **New hooks or config schema fields:** No harness-lifecycle hooks or config schema changes are part of this sprint.

## Technical Notes

**Behavioral coverage justification (below 60%):**
Sprint 7 delivers three static artifacts: (1) `rubrics/harness-build.md` — a new markdown file, (2) an updated list entry in `eval-rubric/SKILL.md` — a markdown edit, (3) a project-type detection clause in `harness-kickoff/SKILL.md` — a markdown edit. None of these introduce a runnable binary, hook listener, library function, or standalone CLI. The closest behavioral surface is the kickoff skill's routing logic, but that skill executes inside a Claude Code agent session and cannot be triggered by a deterministic shell command from the evaluator. B1 and B2 are "simulation behavioral" criteria — the evaluator reads the skill instructions and traces through the documented steps to verify the routing outcome — rather than shell-command behavioral. Total behavioral weight: 22%. The remaining 78% is split between structural (33%) and llm-judge (40%+), which is appropriate for a documentation-only sprint.

**File paths:**
- New rubric: `plugins/trine-eval/skills/eval-rubric/rubrics/harness-build.md`
- Registry update: `plugins/trine-eval/skills/eval-rubric/SKILL.md` (add sixth bullet to Available Rubrics)
- Kickoff update: `plugins/trine-eval/skills/harness-kickoff/SKILL.md` (add `harness-build` to Step 1 detection list and Step 2 config template)

**Hard-threshold encoding:**
The three UNCONDITIONAL gates (Architect A3) must appear in a `## Hard Thresholds` section that explicitly uses language like "UNCONDITIONAL," "automatic FAIL," or "regardless of weighted score." Score-based waivers (e.g., "if scored 3 or above elsewhere") are prohibited for these three gates. The gates verify documentation presence, not implementation quality — the harness is FAIL if the required document does not exist; it is not sufficient to score 4/5 on the dimension.

**Rubric structure:**
The harness-build rubric follows the same format as existing rubrics in `rubrics/`: a prose header, `## Dimensions and Weights` with a level-3 heading per dimension, a score table (1-5 scale), a `## Hard Thresholds` section, and a `## Testing Tools` section. The 7 dimensions cover the playbook's nine stages plus governance by grouping related stages (e.g., Tool Registry + Sandboxing into one dimension; Governance as a standalone dimension).

**Kickoff Step 1 update scope:**
Only Step 1's type-detection list and Step 2's `config.json` template need updating. The JIT context scope comments, the "Context Retrieval Principles" section, and all other content must remain unchanged (protected by SN1 and SN3).

**Weight verification:**
- Behavioral: B1 (10%) + B2 (12%) = 22%
- Structural: S3 (5%) + S4 (8%) + S5 (8%) + S6 (7%) + S7 (5%) + S8 (5%) = 38%
- LLM-as-judge: J9 (15%) + J10 (15%) + J11 (10%) = 40%
- Total: 22% + 38% + 40% = 100%

## Evaluator Review

**Status: NEEDS REVISION**

Three issues require fixes before the contract can be approved. One is a definitive broken verification command (S6) that would cause a false FAIL. One is a factually incorrect baseline count in a Should-NOT gate (SN1) that weakens regression protection. One is a labeling inconsistency (B1/B2 as "behavioral") that, while defensible, requires an explicit acknowledgment in the contract to prevent future grader confusion. Details follow.

---

### Issue 1 (BLOCKING) — S6: verification command is broken

**Criterion:** S6 — "Rubric is registered as sixth entry in eval-rubric SKILL.md"

**Problem:** The grep pattern `'^- \`'` (single-quoted with backslash-escaped backtick) returns 0 matches and exit code 1 on this platform, even though the file contains 5 lines matching `^- `` (unescaped backtick). Verified by running both forms:

```
grep -c '^- \`' eval-rubric/SKILL.md   # returns 0, exit 1  ← BROKEN
grep -c "^- \`" eval-rubric/SKILL.md   # returns 5, exit 0  ← CORRECT
```

In bash, the single-quoted form passes `\`` literally to the regex engine; the backslash-backtick sequence is not a valid BRE escape, so it matches nothing. After Sprint 7 delivers the sixth entry, the command will still return 0 and the evaluator will mark S6 FAIL regardless of correct implementation.

**Fix required:** Change the verification command in S6 from:

```
grep -c '^- \`' plugins/trine-eval/skills/eval-rubric/SKILL.md
```

to:

```
grep -c "^- \`" plugins/trine-eval/skills/eval-rubric/SKILL.md
```

(double-quoted pattern, where `\`` is correctly interpreted as a literal backtick by the shell before passing `^- `` to grep). Alternatively use `grep -c '^- ` ` (single-quoted, no backslash). Either form currently returns 5 and will return 6 post-sprint.

---

### Issue 2 (BLOCKING) — SN1: baseline count is factually wrong, threshold too weak

**Criterion:** SN1 — "Should NOT regress Sprint 6 JIT annotations in harness-kickoff SKILL.md"

**Problem:** The contract states "(Sprint 6 baseline: 5 such comments present — one per Step 1 through Step 5)" and sets the threshold at `>= 5`. The actual count is **6**, not 5. Verified:

```
grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md
# returns 6
```

The six comments are at Steps 1, 2, 2b, 3, 4, and 5. Step 2b has its own scope comment. The contract's parenthetical is wrong, and the `>= 5` threshold is therefore too weak: a Generator that removes Step 2b's scope comment would reduce the count to 5, still satisfy `>= 5`, and SN1 would PASS — but a real regression occurred.

**Fix required:** Update the SN1 note and threshold to reflect the true baseline:

```
Verify: grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md >= 6.
(Sprint 6 baseline: 6 such comments present — one per Step 1, Step 2, Step 2b, Step 3, Step 4, and Step 5.)
```

---

### Issue 3 (NON-BLOCKING, advisory) — B1/B2 labeled "behavioral" but are structurally graded

**Criteria:** B1 and B2

**Observation:** The Technical Notes correctly explain these are "simulation behavioral" — the evaluator reads the skill instructions and traces through the documented steps rather than running a shell command. This is honest and accurate. However, in the harness methodology, "behavioral (execution-verified)" means a shell command invocation exercises the behavior. B1 and B2 do not meet this bar: B1 is equivalent to S3 (file exists) plus a first-heading grep; B2 is a careful reading of the SKILL.md routing prose.

The static-artifact justification is genuinely sound for this sprint — there is no runnable harness-kickoff binary, and the kickoff skill executes only inside a Claude agent session which cannot be triggered deterministically by the evaluator. The justification in Technical Notes is correct.

However, calling these criteria "behavioral" risks training future evaluators to accept "I read the code and traced the logic" as behavioral verification. The 3-way grader split methodology defines behavioral as execution-verified. Calling B1 and B2 "structural" (artifact-inspected) would be more precise and would avoid the definitional drift.

**Suggested fix:** Relabel B1 and B2 as structural criteria, absorb them into the S-block (renumbering S3–S8 accordingly), and update the Technical Notes to state that this sprint has 0% behavioral coverage by the execution-verified definition, with the full justification already provided. This does not change any threshold or weight — it is a labeling correction that makes future contract reviews cleaner.

This is advisory only (not blocking). If the Generator prefers to retain the "simulation behavioral" framing as an acknowledged exception, the contract should add one sentence to the behavioral header: "Note: B1 and B2 are 'simulation behavioral' — the evaluator traces the documented procedure without invoking a shell command, as no shell-executable entry point exists for this sprint's deliverables."

---

### Criteria confirmed sound (no issues)

- **S3** (file existence, Test-Path): correct path, correct command.
- **S4** (7 `###` headings): the count of `###` works correctly if — and only if — the Generator follows the same rubric format convention as existing rubrics (one `###` per dimension, no `###` inside Hard Thresholds or Testing Tools). This is consistent with the template described in Technical Notes and the existing `eval-harness.md` pattern (which uses 5 `###` headings for 5 dimensions and `##` for Hard Thresholds/Testing Methods). Sound, but the Generator must be aware.
- **S5** (3 UNCONDITIONAL gates): multi-grep approach is correct; three separate grep conditions cover loop termination, sandboxing, and governance independently.
- **S7** (harness-build in kickoff SKILL.md): simple grep, correct.
- **S8** (Hard Thresholds section + UNCONDITIONAL language): two-part grep, sound.
- **SN2** (`web-app\|rag-system\|cli-tool\|api-service\|eval-harness` with `\|`): uses GNU grep BRE alternation, which works on this platform. Verified returning 5 on current file. Not POSIX-portable but functionally correct here.
- **SN3** (Context Retrieval Principles): baseline verified at 1. Threshold `>= 1` is correct.
- **SN4** (no `examples/` directory): Test-Path absence check is sound.
- **J9** (dimension-to-stage alignment): rubric with concrete stage themes and explicit 1-5 scale requirement is well-specified. Reference solution (partial) provided.
- **J10** (hard-threshold gates UNCONDITIONAL): three-part PASS requirement is specific. Reference solution is complete and strong. This is the right criterion to anchor.
- **J11** (kickoff routing non-ambiguous): three-part requirement covering explicit option list, config.json template mapping, and non-regression of existing project types is concrete and testable by reading.
- **Weight sum**: 22% + 38% + 40% = 100%. Verified.
- **Static-artifact justification**: Genuinely sound. The kickoff skill's routing logic is prose instructions to a model — there is no `harness-kickoff --type harness-build` CLI invocation the evaluator can run. The B1/B2 simulation approach is the correct workaround, with the labeling advisory above.
- **Completeness**: All three Sprint 7 features from sprints.json (`harness-build-rubric`, `rubric-registration`, `kickoff-project-type`) are covered. Phase 2 scope from spec.md is correctly addressed. Out-of-scope items (sprints 8–11 deliverables) are explicitly excluded. No missing features.
- **Reference solution**: Provided for J10 (highest-weighted LLM-judge criterion at 15%, tied with J9 — acceptable choice per contract review instructions). The reference solution is concrete and illustrates exactly the language strength required.

---

### Summary of required changes before approval

1. **S6** — Fix the broken backtick-escaped grep pattern. Change `'^- \`'` to `"^- \`"` (double-quoted).
2. **SN1** — Correct the baseline count from 5 to 6 and tighten the threshold from `>= 5` to `>= 6`.
3. **B1/B2** (advisory) — Either relabel as structural or add an explicit "simulation behavioral" acknowledgment sentence to the behavioral section header.

Issues 1 and 2 must be fixed. Issue 3 is advisory.

## Evaluator Review (Round 2)

**Status: APPROVED**

### Verification of Round 1 Issues

All three issues raised in Round 1 have been addressed. Verification commands were run independently.

**Issue 1 (BLOCKING — S6 broken grep): RESOLVED**

The S6 verification command (line 38) now uses double-quoted pattern:
```
grep -c "^- \`" plugins/trine-eval/skills/eval-rubric/SKILL.md
```
This correctly returns 5 today (pre-sprint baseline). Verified by running the command against the live file — exit 0, count 5. Post-sprint, when the sixth rubric entry is added, it will return 6 and the `== 6` check will pass correctly.

**Issue 2 (BLOCKING — SN1 baseline count): RESOLVED**

SN1 (line 57) now reads `>= 6` with the parenthetical corrected to: "(Sprint 6 baseline: 6 such comments present — one per Step 1, Step 2, Step 2b, Step 3, Step 4, and Step 5.)" Verified by running `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` — returns 6. The threshold now correctly matches the actual baseline; a Generator that removes any single scope comment (including Step 2b's) will cause SN1 to fail.

**Issue 3 (ADVISORY — B1/B2 labeling): RESOLVED**

The Behavioral section header (lines 23-25) now contains the explicit acknowledgment sentence: "Note: B1 and B2 are 'simulation behavioral' — the evaluator traces the documented procedure without invoking a shell command, as no shell-executable entry point exists for this sprint's deliverables (the kickoff skill executes only inside a Claude agent session)." This satisfies option b from the Round 1 advisory and prevents future grader confusion about what "behavioral" means in this sprint context.

### No New Issues Introduced

The revision history block at the top of the file (lines 4-8) accurately summarizes what was changed and why. The weight totals, all other criterion text, and the reference solutions are unchanged from Round 1. The Revision History block itself is informational only and does not affect any grading logic.
