# Sprint 04 Contract: Context Engineering and Structured State

## What I Will Build

Add structured JSON state tracking alongside the markdown progress log, add compaction guidance to generator and evaluator agents for surviving long sessions, expand hooks to cover key lifecycle events (session start, pre-eval, post-eval), and improve session resumption in the sprint workflow.

## Success Criteria

### Deterministic (code-verifiable)

1. **Sprint-workflow references feature_list.json** [weight: 10%]: `skills/sprint-workflow/SKILL.md` references a `feature_list.json` or structured JSON state file for machine-readable sprint tracking. Verify: `grep -ci 'feature_list.json\|sprint-state.json\|structured.*json\|json.*state' skills/sprint-workflow/SKILL.md` >= 1.

2. **Hooks file has multiple events** [weight: 8%]: `hooks/hooks.json` defines hooks for at least 3 distinct lifecycle events (not just Stop). Verify: count distinct `"event"` values in the JSON file >= 3.

3. **Generator has compaction guidance** [weight: 8%]: `agents/generator.md` contains instructions about surviving context compaction in long sessions. Verify: `grep -ci 'compact\|context.*limit\|context.*window\|progress.*file\|persist.*state' agents/generator.md` >= 1.

4. **Evaluator has compaction guidance** [weight: 8%]: `agents/evaluator.md` contains instructions about context management or compaction. Verify: `grep -ci 'compact\|context.*limit\|context.*window\|progress.*file' agents/evaluator.md` >= 1.

5. **Harness-kickoff creates JSON state file** [weight: 8%]: `skills/harness-kickoff/SKILL.md` includes instructions to create a structured JSON state file during initialization. Verify: `grep -ci 'feature_list\|sprint-state\|state.*json' skills/harness-kickoff/SKILL.md` >= 1.

### LLM-as-judge (requires reading comprehension)

6. **JSON state file schema is well-defined** [weight: 12%]: The sprint-workflow or harness-kickoff skill defines the JSON schema for the state file, including at minimum: (a) list of sprints with status, (b) current sprint number, and (c) per-sprint pass/fail results. PASS requires all three fields.

7. **Compaction guidance is actionable** [weight: 12%]: The generator and evaluator compaction instructions explain: (a) what information to persist externally before compaction (progress files, state JSON, key decisions), (b) what to re-read after compaction to restore context, and (c) that JSON is preferred over markdown for structured data because models are less likely to corrupt it. PASS requires all three points across the two agent files (they can be split between generator and evaluator).

8. **Hooks cover meaningful lifecycle events** [weight: 12%]: The hooks configuration includes at least: (a) a session-start hook that reads progress/state, (b) a post-eval or post-sprint hook that updates state, and the existing (c) Stop hook. Each hook has a clear purpose documented in its description field. PASS requires all three.

9. **Session resumption is robust** [weight: 12%]: The sprint-workflow skill's session resumption section references the JSON state file (not just progress.md and git log), checks for partially-completed evaluation rounds, and can determine the exact resumption point (which step within which sprint). PASS requires all three capabilities.

10. **JSON and markdown serve distinct purposes** [weight: 10%]: The system clearly distinguishes when to use JSON (machine-readable state, sprint status, pass/fail data) vs markdown (human-readable progress, prose notes, session logs). This distinction must be documented in at least one file. PASS requires the distinction to be explicit, not merely implied by file choices.

## Should-NOT Criteria

1. **Should NOT remove existing Stop hook**: The existing Stop hook that appends to progress.md must remain. Verify: `grep -c 'Stop' hooks/hooks.json` >= 1.

2. **Should NOT remove session resumption section from sprint-workflow**: The existing "Session Resumption" section must remain. Verify: `grep -c 'Session Resumption\|Resumption' skills/sprint-workflow/SKILL.md` >= 1.

## Reference Solutions

**Criterion 6 — JSON state schema:**
```json
{
  "current_sprint": 2,
  "sprints": [
    {
      "number": 1,
      "title": "...",
      "status": "pass",
      "rounds": 2,
      "criteria_passed": 8,
      "criteria_total": 10,
      "weighted_score": 85
    }
  ],
  "last_updated": "2026-04-12T14:30:00Z"
}
```

**Criterion 8 — Hooks structure:**
```json
{
  "hooks": [
    {
      "event": "SessionStart",
      "command": "...",
      "description": "Read progress state on session start"
    },
    {
      "event": "Stop",
      "command": "...",
      "description": "Append session timestamp to progress log"
    },
    {
      "event": "PostToolUse",
      "command": "...",
      "description": "Update sprint state after evaluation completes"
    }
  ]
}
```

## Out of Scope

- Changes to eval-summary (completed in Sprint 3)
- Changes to the planner agent
- Bootstrap from failures workflow (Sprint 5)
- Human calibration pathway (Sprint 5)

## Technical Notes

- The playbook recommends JSON over markdown for structured data because "models are less likely to inappropriately modify structured data"
- The state file complements (does not replace) progress.md — markdown stays for human-readable session notes
- Hooks must use valid shell commands that work on both Unix and Windows (via Git Bash)
- The `feature_list.json` name comes from Anthropic's "Effective Harnesses" post — but we can use `sprint-state.json` if it better describes the content

## Evaluator Review

**Status: APPROVED**

### Feedback

**Criterion 1 (Sprint-workflow references feature_list.json) [10%, deterministic]:**
Testable and specific. The grep pattern covers reasonable naming variants (feature_list.json, sprint-state.json, structured json, json state). The case-insensitive flag is appropriate. One minor note: the pattern `structured.*json` could false-positive on unrelated phrases like "structured JSON schema validation" in unrelated context, but in a file this small that risk is negligible. Acceptable as-is.

**Criterion 2 (Hooks file has multiple events) [8%, deterministic]:**
Testable. The verification method ("count distinct event values in the JSON file >= 3") is clear in intent but lacks a concrete command. Compare to Criterion 1 which gives an exact grep command. Suggest adding an explicit verification command, e.g., `grep -o '"event": "[^"]*"' hooks/hooks.json | sort -u | wc -l` >= 3, or parsing with jq. This is a minor gap -- the evaluator can construct a command from the description, but the other deterministic criteria set a higher bar by providing exact commands.

**Criterion 3 (Generator has compaction guidance) [8%, deterministic]:**
Testable. The grep pattern is broad enough to catch reasonable implementations. The pattern `persist.*state` could match existing content in unrelated contexts, but the current file has zero matches, so any match after implementation is attributable to this sprint. Acceptable.

**Criterion 4 (Evaluator has compaction guidance) [8%, deterministic]:**
Testable. Same grep-based approach as Criterion 3 with a slightly narrower pattern set (omits `persist.*state`). The current evaluator.md has zero matches. Acceptable.

**Criterion 5 (Harness-kickoff creates JSON state file) [8%, deterministic]:**
Testable. The grep pattern covers the expected terms. Current file has zero matches. Acceptable.

**Criterion 6 (JSON state file schema is well-defined) [12%, llm-judge]:**
Well-structured with three explicit sub-requirements (sprint list with status, current sprint number, per-sprint pass/fail). The reference solution provides a concrete example schema which is valuable for grader calibration. PASS threshold is clear: all three fields required. The reference solution goes beyond the minimum (includes `rounds`, `criteria_passed`, `criteria_total`, `weighted_score`, `last_updated`), but the criterion text only requires three fields -- the reference is guidance, not the bar. This is well-designed.

**Criterion 7 (Compaction guidance is actionable) [12%, llm-judge]:**
Three sub-requirements clearly stated: (a) what to persist before compaction, (b) what to re-read after, (c) JSON preferred over markdown rationale. The allowance that sub-requirements can be split across generator and evaluator files is a good practical design -- it avoids forcing redundant content. However, this split makes grading slightly more complex: the evaluator must read both files and track which sub-requirement each file covers. This is manageable but worth noting. No reference solution is provided for this criterion, which is a gap -- it is the second-highest weighted llm-judge criterion (tied with 6, 8, 9). However, the three sub-points are specific enough that a reference may not be strictly necessary.

**Criterion 8 (Hooks cover meaningful lifecycle events) [12%, llm-judge]:**
Three specific hooks required: (a) session-start that reads state, (b) post-eval/post-sprint that updates state, (c) existing Stop hook. Each must have a description field. The reference solution provides a concrete hooks JSON structure. Well-defined and testable. The "clear purpose documented in its description field" requirement adds a qualitative check that goes beyond structure -- good.

**Criterion 9 (Session resumption is robust) [12%, llm-judge]:**
Three sub-requirements: (a) references JSON state file, (b) checks for partially-completed evaluation rounds, (c) can determine exact resumption point (which step within which sprint). These are specific and independently verifiable by reading the sprint-workflow SKILL.md. The current Session Resumption section (lines 129-136) checks git log, contract existence, and eval results -- this sprint must extend it substantially. Well-scoped.

**Criterion 10 (JSON and markdown serve distinct purposes) [10%, llm-judge]:**
Requires the distinction to be "explicit, not merely implied." The "documented in at least one file" threshold is appropriately low -- it does not demand the distinction appear everywhere, just that it is stated somewhere. This is testable via reading comprehension. No reference solution, but the criterion is specific enough. Acceptable.

**Should-NOT Criteria:**
Both are well-formed gates with exact verification commands. SN1 checks the Stop hook survives. SN2 checks the Session Resumption section survives. Both baselines confirmed present in current files.

**Reference Solutions:**
Reference solutions are provided for Criteria 6 and 8. Criterion 6's reference is comprehensive (example JSON schema). Criterion 8's reference shows the hooks structure with three events. No reference for Criterion 7 (12% llm-judge) or Criterion 9 (12% llm-judge). The contract template guidance says to "prioritize LLM-judge criteria" for references. Having 2 of 5 llm-judge criteria with references is adequate given that Criteria 7, 9, and 10 have sufficiently specific sub-requirements to grade without a reference example.

**Weight distribution:**
Weights sum to 100%. Deterministic criteria total 42%, llm-judge criteria total 58%. The sprint-03 eval had a similar split (44% deterministic, 56% llm-judge). The distribution is reasonable: deterministic criteria verify that content exists, llm-judge criteria verify that content is meaningful.

**Out of Scope:**
Clearly delineated. Excludes eval-summary (completed Sprint 3), planner agent, bootstrap from failures (Sprint 5), and human calibration (Sprint 5). This properly scopes the sprint.

### Missing Criteria

1. **No criterion for cross-platform hook compatibility.** The Technical Notes state "Hooks must use valid shell commands that work on both Unix and Windows (via Git Bash)." This is a stated constraint with no corresponding success criterion. A deterministic check (e.g., verify hook commands do not use Windows-only or Unix-only constructs) would enforce this. This is a minor gap -- the builder could add hooks that only work on one platform and still pass all criteria. Severity: low, since the target platform uses Git Bash on Windows.

2. **No criterion for the state file actually being created by harness-kickoff at runtime.** Criterion 5 checks that the kickoff SKILL.md contains instructions to create the file. But there is no criterion verifying the instructions are correct enough that the file would actually be created (e.g., includes a file path, a write command or instruction, and the expected schema). This is partially covered by Criterion 6 (schema) but the connection between "kickoff mentions state.json" and "kickoff actually creates a well-formed state.json" has a gap. Severity: low, because the combination of Criteria 5 and 6 provides reasonable coverage.

### Approved Criteria

All 10 success criteria and both Should-NOT criteria are approved:

- **Criteria 1, 3, 4, 5:** Well-formed deterministic checks with exact grep commands, clear thresholds, and confirmed-zero baselines in the current files.
- **Criterion 2:** Approved with the minor note that an explicit verification command would improve consistency with other deterministic criteria.
- **Criteria 6, 8:** Strong llm-judge criteria with explicit sub-requirements and reference solutions.
- **Criteria 7, 9, 10:** Adequate llm-judge criteria with clear sub-requirements; grading is feasible without reference solutions.
- **SN1, SN2:** Properly scoped gate criteria with exact verification commands and confirmed baselines.
