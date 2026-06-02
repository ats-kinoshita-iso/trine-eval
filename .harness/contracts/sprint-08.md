# Sprint 08 Contract: Bootstrap Failure Catalog from Playbook Traps (Phase 2)

## Revision History

- **Round 1 → Round 2** (2026-06-01):
  - Issue 1 (BLOCKING): S9 secondary verification command fixed — changed `jq '[.failures[0:3].source_ref]'` to `jq '[.failures[0:3][].source_ref]'`.
  - Issue 2 (BLOCKING): S7, S8, and S9 reclassified from Structural to Behavioral (renumbered B6, B7, B8); behavioral total raised from 52% to 66%; exception acknowledgment removed; weight breakdown updated to 66%/12%/22%.
  - Issue 3 (ADVISORY): B4 parenthetical corrected to accurately describe Sprint 8's role as a precondition for Phase 2 success criterion #9, not the criterion itself.
- **Rev 2 (2026-06-02) — SN2 carve-out renumbering (Sprint 13 plan amendment):**
  Renumber stale sprint references throughout: Sprint 9→10 (Planner harness-build), Sprint 10→11 (Ephemeral dogfood / ephemeral harness fixture), Sprint 11→12 (Positioning). Authorized under the SN2 carve-out in `sprint-contract/SKILL.md`. No criterion text, weights, or gate logic were changed.

## What I Will Build

Create `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json` — a
JSON file containing 12–15 playbook-trap-derived failure cases, each entry following the
failure-catalog schema and mapping to one of the seven dimensions in `rubrics/harness-build.md`.
Establish the `templates/by-rubric/` subdirectory layout. Update `bootstrap-failures/SKILL.md`
to document the new directory layout and specify how `/harness-kickoff` merges a per-rubric
template into the project's `.harness/bootstrap/failure-catalog.json` at kickoff time (additive
merge by `id`; per-rubric entries do not overwrite user-authored ones).

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is unambiguous.
Tag each criterion as `behavioral` (execution-verified), `structural` (artifact-inspected), or
`llm-judge` (reading-comprehension). Weights must sum to 100% across all success criteria.

**Behavioral coverage:** This sprint delivers static JSON and markdown artifacts — a
template JSON file and a SKILL.md update. However, the JSON template is machine-parseable:
behavioral criteria can be grounded in `jq` commands that parse the catalog, validate each
entry's schema, count entries, assert `rubric_dimension` values against the 7 known dimensions,
and assert required field presence. These are execution-verified (jq invoked against the artifact,
observable pass/fail result from exit code + output). The SKILL.md merge procedure can be
simulation-traced (same framing as Sprint 7's B1/B2). Total behavioral weight target: ≥ 60%.

### Behavioral (execution-verified)

**Note:** B1–B4 and B6–B8 use `jq` executed against the catalog file — these are
shell-command-verified criteria where a command is run and an observable result is checked
(exit code + jq output). B5 is "simulation behavioral" (merge-procedure trace, no shell
entry point exists for the kickoff skill itself).

1. **Catalog contains 12–15 entries** [weight: 8%]: Run
   `jq '.failures | length' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and assert the returned integer N satisfies 12 ≤ N ≤ 15. PASS when exit code is 0
   and output is a number in [12, 15].

2. **Every entry has all required fields** [weight: 12%]: Run
   `jq '[.failures[] | select(has("id") and has("source") and has("source_ref") and has("title") and has("problem") and has("expected") and has("success_criteria") and has("rubric_dimension") and has("severity") and has("grader_type"))] | length' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and assert the returned count equals the total catalog length (same as B1). PASS when
   the select-filtered count equals the total count — no entry is missing a required field.

3. **Every entry's `rubric_dimension` is one of the 7 valid harness-build dimensions** [weight: 12%]:
   Run `jq '[.failures[].rubric_dimension] | unique | .[]' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and assert each printed string is one of:
   `"Control Plane & Agentic Loop"`, `"Tool Registry & Sandboxing"`, `"Projection & Planning"`,
   `"Skills & Instruction Execution"`, `"Observation & Monitoring"`, `"External Affordances"`,
   or `"Governance & Human Oversight"`. PASS when all unique dimension values are members of
   that set (no spurious or misspelled dimension names). Any unrecognized string is a FAIL.

4. **At least one entry exercises loop termination** [weight: 10%]: Run
   `jq '[.failures[] | select(.rubric_dimension == "Control Plane & Agentic Loop")] | length' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and assert the count >= 1. Additionally verify at least one such entry has a
   `success_criteria` string containing a numeric bound concept — run
   `jq '[.failures[] | select(.rubric_dimension == "Control Plane & Agentic Loop") | .success_criteria] | .[]' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and confirm at least one result references a max-step count, max-token budget, or
   loop termination bound in its text. PASS when loop-dimension count >= 1 and at least
   one success_criteria for that dimension references a numeric or terminable bound
   (precondition for Phase 2 success criterion #9: seeding at least one loop-termination catalog
   entry that Sprint 11 will exercise when grading an ephemeral harness fixture).

5. **SKILL.md merge procedure is simulation-traceable for a fresh kickoff** [weight: 10%]:
   Simulate the kickoff merge procedure documented in the updated `bootstrap-failures/SKILL.md`:
   (a) Read the SKILL.md to locate the "Templates by Rubric" section describing the merge.
   (b) Trace the procedure for a harness-build project where no prior
   `.harness/bootstrap/failure-catalog.json` exists: the kickoff reads
   `templates/by-rubric/harness-build.json` and writes its `failures` array to the project
   catalog. (c) Trace the procedure for an existing catalog: the merge is additive by `id` —
   only entries whose `id` does not already exist in the project catalog are appended; existing
   entries are not overwritten. PASS when the SKILL.md contains a section explicitly describing
   steps (b) and (c) and the evaluator can quote the exact merge rule (additive by `id`,
   no overwrite) from the SKILL.md text. The evaluator must record the exact quoted text
   as evidence.

6. **Template file is valid JSON** [weight: 4%]: Run
   `jq empty plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and assert exit code 0 (no parse error). A malformed JSON file fails this criterion
   regardless of content.

7. **All entries have `source` set to `playbook-trap`** [weight: 5%]: Run
   `jq '[.failures[] | select(.source != "playbook-trap")] | length' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and assert the count is 0. Every entry in this template must set `source` to `"playbook-trap"`;
   a mix of source types is a FAIL.

8. **All entries have a non-empty `source_ref` citing a playbook stage or trap** [weight: 5%]:
   Run `jq '[.failures[] | select(.source_ref == "" or .source_ref == null)] | length' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   and assert the count is 0. Each `source_ref` must be a non-empty string. Verify at least
   one `source_ref` value contains a stage-like reference (e.g., "Stage:", "Trap:", or a
   playbook section name) by inspecting the first few values with
   `jq '[.failures[0:3][].source_ref]' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
   — no grep regex required, visual inspection suffices.

### Structural (artifact-inspected)

9. **Template file exists at the correct path** [weight: 4%]: Verify
   `test -f "plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json"`
   returns exit 0. The `by-rubric/` subdirectory and `harness-build.json` file must both exist
   at the specified path.

10. **SKILL.md contains new `## Templates by Rubric` section** [weight: 4%]: Run
    `grep -c '## Templates by Rubric' plugins/trine-eval/skills/bootstrap-failures/SKILL.md`
    and assert count >= 1. This section documents the `templates/by-rubric/<rubric-name>.json`
    layout (Sprint 8 artifact).

11. **SKILL.md mentions `by-rubric` directory layout and `harness-build.json`** [weight: 4%]:
    Run `grep -c 'by-rubric' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1
    AND `grep -c 'harness-build' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1.
    Both strings must appear in the file after the Sprint 8 update.

### LLM-as-judge (reading-comprehension)

12. **Catalog quality: trap coverage across all 7 rubric dimensions** [weight: 12%]: Read
    `harness-build.json` and assess whether the catalog provides meaningful coverage across
    all 7 harness-build rubric dimensions. PASS requires: (a) all 7 dimensions are represented
    by at least one entry (no dimension is unrepresented); (b) each entry's `title` and `problem`
    clearly describe a real failure mode a practitioner would encounter when building an agent
    harness (not a generic or contrived scenario); (c) each entry's `success_criteria` field
    is specific and unambiguous — it describes a verifiable outcome, not a vague goal
    (e.g., "The harness declares a max_steps bound >= 1 in its config" is good;
    "The harness handles loops correctly" is bad); (d) the three UNCONDITIONAL gate dimensions
    (Control Plane & Agentic Loop, Tool Registry & Sandboxing, Governance & Human Oversight)
    each have at least 2 entries, reflecting their higher risk weight.

13. **SKILL.md update quality: merge procedure is clear, complete, and consistent** [weight: 10%]:
    Read the updated `bootstrap-failures/SKILL.md`. PASS requires: (a) the new "Templates by
    Rubric" section clearly explains the `templates/by-rubric/<rubric-name>.json` directory
    layout and its purpose; (b) the kickoff merge procedure is described step-by-step (what
    file is read, what file is written, when the merge is triggered); (c) the additive-merge
    rule (by `id`, no overwrite of user-authored entries) is explicitly stated; (d) the
    updated SKILL.md integrates naturally with the existing content — the new section does
    not contradict or orphan any existing guidance about failure catalog usage; (e) the
    section is under 80 lines (consistent with the "Skills must stay under 500 lines per
    SKILL.md" constraint and the existing SKILL.md's lean style).

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score.
These define behaviors that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT remove or corrupt the "Sources of Real Failures" enumeration in bootstrap-failures
   SKILL.md**: The five-item numbered list introduced in Phase 1 (Bug reports, Manual test notes,
   Production incidents, Support tickets, Code review comments) must remain intact.
   Verify: `grep -c 'Sources of Real Failures' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1.
   (Pre-sprint baseline: 1. This heading must survive the SKILL.md update.)

2. **Should NOT remove or corrupt the failure-catalog schema example in bootstrap-failures
   SKILL.md**: The JSON code block documenting the schema (with fields `id`, `source`,
   `source_ref`, `title`, `problem`, `expected`, `success_criteria`, `reference_solution`,
   `rubric_dimension`, `severity`, `grader_type`) must remain present.
   Verify: `grep -c '"grader_type"' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1
   AND `grep -c '"rubric_dimension"' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1.
   (Pre-sprint baseline: 1 occurrence of each field name in the schema example.)

3. **Should NOT remove the "Integration with the Harness" section and Data Flow diagram from
   bootstrap-failures SKILL.md**: This section and its ASCII data-flow diagram document how
   the failure catalog feeds into the harness workflow — it must survive the Sprint 8 additions.
   Verify: `grep -c 'Integration with the Harness' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1
   AND `grep -c 'Data Flow' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1.
   (Pre-sprint baseline: 1 occurrence of each.)

4. **Should NOT remove or shorten the "Conversion guidelines" numbered list in bootstrap-failures
   SKILL.md**: The 6-item numbered list under `### Conversion guidelines:` documents how to
   convert failure cases — it must not be truncated or replaced.
   Verify: `grep -c 'Conversion guidelines' plugins/trine-eval/skills/bootstrap-failures/SKILL.md` >= 1.
   (Pre-sprint baseline: 1.)

5. **Should NOT regress Sprint 6 JIT annotations in harness-kickoff SKILL.md**: If Sprint 8
   touches `harness-kickoff/SKILL.md` at all (the SKILL.md update for bootstrap-failures
   documents how kickoff *uses* the template, but the kickoff skill itself may not need edits),
   the six `<!-- Context scope at this step: ... -->` comment blocks must remain intact.
   Verify: `grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md` >= 6.
   (Pre-sprint baseline: 6 — Steps 1, 2, 2b, 3, 4, and 5.)

6. **Should NOT create an `examples/` directory at the repo root**: Phase 2's ephemeral
   constraint prohibits committing permanent example fixtures.
   Verify: `test -d "examples"` returns non-zero exit (ABSENT).
   (Pre-sprint baseline: ABSENT — confirmed.)

## Reference Solutions

**Criterion 12 — Catalog quality: representative entries for the highest-risk dimensions:**

The following illustrates the expected quality bar for entries in `harness-build.json`. All
three UNCONDITIONAL gate dimensions should have entries of this form:

```json
{
  "id": "HB001",
  "source": "playbook-trap",
  "source_ref": "Stage: Control Plane / Trap: unbounded agentic loop",
  "title": "Agentic loop runs until model stops producing output",
  "problem": "The harness has no max_steps or max_tokens bound on the agentic loop. The agent enters a reasoning loop and never stops — the session runs until the context window is exhausted or the user force-terminates the process.",
  "expected": "The harness declares a numeric max_steps bound (e.g., max_steps: 50) AND a max_tokens budget (e.g., max_tokens: 100000) in its loop config. The loop enforcer halts execution and returns a LOOP_BUDGET_EXCEEDED result when either limit is reached.",
  "success_criteria": "The harness config or control plane documentation declares a numeric max_steps value >= 1 AND a numeric max_tokens value >= 1. A verbal claim ('the loop always terminates') without a numeric limit does not satisfy this criterion.",
  "reference_solution": "Add `max_steps: 50` and `max_tokens: 100000` to the loop config. Add a loop-guard check at the top of each iteration that halts if either limit is exceeded.",
  "rubric_dimension": "Control Plane & Agentic Loop",
  "severity": "critical",
  "grader_type": "structural"
},
{
  "id": "HB005",
  "source": "playbook-trap",
  "source_ref": "Stage: Tool Registry & Sandboxing / Trap: tools executed without isolation",
  "title": "Code execution tool runs arbitrary shell commands in host environment",
  "problem": "The harness registers a code-execution tool but does not sandbox it. The agent invokes the tool with a shell command that writes to arbitrary filesystem paths or makes outbound network calls — the harness provides no isolation boundary.",
  "expected": "The harness declares explicit sandbox constraints on the code-execution tool: allowed filesystem paths, blocked outbound hosts, and resource limits (CPU, memory, wall-clock time). The sandbox config is versioned alongside the harness.",
  "success_criteria": "The tool registry entry for the code-execution tool declares at least two of: (a) allowed_paths list, (b) blocked_hosts list, (c) resource limits. A tool entry that lists 'sandboxed: true' without specifying isolation dimensions does not satisfy this criterion.",
  "reference_solution": "Add `sandbox: { allowed_paths: ['/tmp/agent-work'], blocked_hosts: ['*'], resource_limits: { cpu_seconds: 10, memory_mb: 256 } }` to the tool registry entry.",
  "rubric_dimension": "Tool Registry & Sandboxing",
  "severity": "critical",
  "grader_type": "structural"
}
```

Key quality markers to check: `source` is `"playbook-trap"`, `source_ref` cites a named stage
and trap, `problem` describes observed behavior (not suspected cause), `expected` describes the
correct state, `success_criteria` is unambiguous with explicit FAIL conditions for weak
compliance, and `rubric_dimension` matches an exact dimension name from `harness-build.md`.

## Out of Scope

- **Planner harness-build mode (Sprint 10):** The `playbook_stage` field on sprint entries and
  Planner template tuning for harness-build projects are NOT part of this sprint.
- **End-to-end ephemeral dogfood validation (Sprint 11):** Kickoff against a tmp fixture and
  `.harness/dogfood-findings.md` are NOT part of this sprint.
- **Positioning README and rubric decision guide (Sprint 12):** `rubrics/README.md` explaining
  when to use `eval-harness` vs `harness-build` is NOT part of this sprint.
- **Changes to the harness-build rubric:** `rubrics/harness-build.md` is not modified by this
  sprint — it was delivered in Sprint 7 and is consumed read-only.
- **Changes to the eval-harness rubric or existing eval-rubric SKILL.md rubric list:** Phase 1
  artifacts are not touched.
- **`tasks.json` emission:** No `tasks.json` schema has been added to `sprint-contract/SKILL.md`
  as of Sprint 8. Skipping emission per Sprint 7 precedent (documented as known gap in
  progress.md).
- **Additional per-rubric templates (e.g., `by-rubric/eval-harness.json`):** Only
  `harness-build.json` is in scope for Sprint 8. Other rubric templates are not planned.
- **Automated merge code or hook:** The merge procedure is documented in SKILL.md as
  instructions to the kickoff agent — no new hook file, shell script, or plugin.json entry
  is added.

## Technical Notes

**Behavioral coverage (66% achieved):**
Sprint 8 delivers static JSON and markdown artifacts, but the primary artifact — `harness-build.json`
— is a structured JSON file that can be fully validated via `jq` shell commands. B1 (entry
count), B2 (required fields), B3 (dimension validation), B4 (loop-termination coverage),
B6 (JSON validity), B7 (source field), and B8 (source_ref field) are all shell-command behavioral:
`jq` is invoked, an exit code and output value are observed, and a PASS/FAIL determination is
made from those observables. This is "execution-verified" per the 3-way grader split definition.
B5 (merge procedure simulation) is "simulation behavioral" — the same framing accepted in
Sprint 7 for B1/B2. Weight breakdown:
- Behavioral: B1 (8%) + B2 (12%) + B3 (12%) + B4 (10%) + B5 (10%) + B6 (4%) + B7 (5%) + B8 (5%) = **66%**
- Structural: S9 (4%) + S10 (4%) + S11 (4%) = **12%**
- LLM-as-judge: J12 (12%) + J13 (10%) = **22%**
- Total: 66% + 12% + 22% = 100%

Behavioral coverage of 66% meets the ≥ 60% floor. The seven `jq`-based behavioral criteria
(B1–B4, B6–B8) are all shell-executable and fully execution-verified. The three remaining
structural criteria (S9 file-exists, S10 section heading, S11 by-rubric mention) inspect
artifact presence and text via `test -f` and `grep`, which do not involve `jq` output
observation and are correctly classified as structural.

**File paths for Sprint 8:**
- New template: `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json`
- New directory layout: `plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/`
- SKILL.md update: `plugins/trine-eval/skills/bootstrap-failures/SKILL.md` (add "Templates by
  Rubric" section; update kickoff integration description; add merge procedure with precedence rules)
- `harness-kickoff/SKILL.md`: No edit required — Step 2b already documents how the kickoff
  reads an existing failure catalog; the SKILL.md update in bootstrap-failures documents
  **how kickoff should use the by-rubric template**, which is instruction-to-agent prose in
  bootstrap-failures/SKILL.md, not a code change to the kickoff skill itself. Sprint 8 does
  NOT touch `harness-kickoff/SKILL.md` unless a review determines the kickoff skill's Step 2b
  needs an explicit by-rubric lookup instruction — in which case SN5 (>= 6 JIT comments) gates it.

**Catalog schema anchor:**
The harness-build.json template follows the schema already documented in `bootstrap-failures/SKILL.md`:
`id`, `source`, `source_ref`, `title`, `problem`, `expected`, `success_criteria`,
`reference_solution` (optional), `rubric_dimension`, `severity`, `grader_type`.
Sprint 8 adds no new schema fields; the by-rubric template is a valid instance of the existing schema.

**Dimension distribution target:**
The three UNCONDITIONAL gate dimensions (Control Plane & Agentic Loop, Tool Registry & Sandboxing,
Governance & Human Oversight) should each have 2–3 entries in the catalog. The four non-gate
dimensions (Projection & Planning, Skills & Instruction Execution, Observation & Monitoring,
External Affordances) should have 1–2 entries each. At 12–15 total entries across 7 dimensions,
this yields an average of 1.7–2.1 entries per dimension, with deliberate concentration on the
three gate dimensions.

**Additive merge rule:**
When `/harness-kickoff` runs Step 2b for a harness-build project and `templates/by-rubric/harness-build.json`
exists, the merge procedure is: read the template; for each entry in the template whose `id` does
not already appear in `.harness/bootstrap/failure-catalog.json`, append that entry. Entries whose
`id` is already present in the project catalog are skipped (not overwritten). If no project catalog
exists, write the template entries as the initial catalog. This preserves user-authored entries
and ensures idempotent re-runs.

**`tasks.json` skip rationale:**
`sprint-contract/SKILL.md` contains no `tasks.json` schema as of Sprint 8. Following Sprint 7
precedent: skip emission, note the gap. This will be added to `progress.md` after this contract
is finalized.

**Weight verification:**
- Behavioral: B1 (8%) + B2 (12%) + B3 (12%) + B4 (10%) + B5 (10%) + B6 (4%) + B7 (5%) + B8 (5%) = 66%
- Structural: S9 (4%) + S10 (4%) + S11 (4%) = 12%
- LLM-as-judge: J12 (12%) + J13 (10%) = 22%
- Total: 66% + 12% + 22% = **100%** ✓

## Evaluator Review

**Status: NEEDS REVISION**

Two issues require fixes before this contract can be approved. One is a broken verification
command (S9 secondary check) that produces a jq parse error instead of readable output —
this is the same class of defect that caused Sprint 07 Round 1's NEEDS REVISION. The other
is a behavioral coverage inconsistency: the contract labels B1–B4 as behavioral because "jq
is invoked, an exit code and output value are observed" but simultaneously labels S7/S8/S9
as structural despite those criteria using jq in exactly the same way. Reclassifying S7, S8,
and S9 as behavioral resolves the inconsistency and raises the total from 52% to 66%, meeting
the 60% floor without introducing any fabricated runtime.

---

### Issue 1 (BLOCKING) — S9: secondary verification command is broken

**Criterion:** S9 — "All entries have a non-empty `source_ref` citing a playbook stage or trap"

**Problem:** The secondary check command `jq '[.failures[0:3].source_ref]'` produces a fatal
parse error and exits with code 5:

```
jq: error (at <stdin>:1): Cannot index array with string "source_ref"
```

Verified by running the command with representative JSON:

```
echo '{"failures":[{"source_ref":"Stage: CP"},{"source_ref":"Trap: X"},{"source_ref":"Stage: G"}]}' \
  | jq '[.failures[0:3].source_ref]'
# Exit: 5
# jq: error (at <stdin>:1): Cannot index array with string "source_ref"
```

The root cause: `.failures[0:3]` returns a JSON array, and arrays cannot be subscripted by
a string key (`.source_ref`). The evaluator following this command verbatim will see an error
message, not the three source_ref values the criterion intends them to inspect.

**Note:** The primary check (`jq '[.failures[] | select(.source_ref == "" or .source_ref == null)] | length'`)
is syntactically valid and tested correctly. Only the secondary visual-inspection command is broken.

**Fix required:** Change the secondary check in S9 from:

```
jq '[.failures[0:3].source_ref]' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json
```

to either of these working forms:

```
jq '[.failures[0:3][].source_ref]' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json
```

or:

```
jq '[.failures[0:3] | .[].source_ref]' plugins/trine-eval/skills/bootstrap-failures/templates/by-rubric/harness-build.json
```

Both were verified to return the array of source_ref strings correctly (exit 0).

---

### Issue 2 (BLOCKING) — Behavioral coverage 52%: internal inconsistency enables the 60% floor

**The inconsistency:** The Technical Notes justify classifying B1–B4 as behavioral because
"jq is invoked, an exit code and output value are observed, and a PASS/FAIL determination is
made from those observables." Yet S7, S8, and S9 also invoke jq, observe exit codes and output
values, and yield PASS/FAIL from those observables:

- **S7** (`jq empty`): invokes jq, observes exit 0 (valid JSON) vs exit 2 (parse error).
- **S8** (`jq '[.failures[] | select(.source != "playbook-trap")] | length'`): invokes jq,
  observes the returned integer (must be 0).
- **S9** primary (`jq '[.failures[] | select(.source_ref == "" or .source_ref == null)] | length'`):
  invokes jq, observes the returned integer (must be 0).

The contract applies different labels (behavioral vs. structural) to jq commands that are
mechanically identical — all invoke a shell command, observe exit code + output, and
yield a deterministic PASS/FAIL. The distinction the contract draws ("semantic content" vs.
"basic properties") does not appear in the sprint-contract/SKILL.md behavioral definition,
which states: "Verified by running the artifact … and observing the output, state change, or
side effect." S7, S8, and S9 satisfy this definition.

**Impact:** Reclassifying S7 (4%) + S8 (5%) + S9 (5%) = 14% as behavioral raises the total
to 52% + 14% = **66%**, which meets the ≥ 60% floor. No criteria need to be added or removed —
only their section labels change.

**Comparison to Sprint 7:** Sprint 7 had 22% behavioral because its two "behavioral" criteria
(B1/B2) were simulation traces with no shell command. Sprint 8 has genuinely shell-executable
jq commands across ALL of B1–B4, S7, S8, and S9. The 52% figure understates the actual
execution-verified coverage. Reclassifying S7/S8/S9 better reflects the sprint's real
behavioral surface.

**Fix required:** Move S7, S8, and S9 from the Structural section to the Behavioral section.
Renumber accordingly (B6, B7, B8 — or keep B5 as simulation-behavioral and renumber S7–S9
as B6–B8). Update the Technical Notes weight breakdown to:

```
Behavioral: B1 (8%) + B2 (12%) + B3 (12%) + B4 (10%) + B5 (10%) + B6 (4%) + B7 (5%) + B8 (5%) = 66%
Structural: S6 (4%) + S10 (4%) + S11 (4%) = 12%
LLM-as-judge: J12 (12%) + J13 (10%) = 22%
Total: 66% + 12% + 22% = 100%
```

Remove the behavioral exception acknowledgment ("Exception acknowledged: behavioral weight =
52%, not 60%") and replace with a statement that behavioral coverage is 66%.

---

### Issue 3 (ADVISORY) — B4 parenthetical overclaims Phase 2 spec criterion #9

**Criterion:** B4 — "At least one entry exercises loop termination"

**Observation:** B4's PASS condition ends with "(Phase 2 success criterion #9 — loop
termination exercises the UNCONDITIONAL gate)." Phase 2 spec criterion #9 reads: "The
harness-build rubric grades a deliberately minimal ephemeral harness fixture (no permanent
`examples/` directory) **with at least one trap-derived behavioral criterion exercising loop
termination**."

Sprint 8 creates the *catalog template* that seeds loop-termination entries. It does not
grade any harness fixture. Spec criterion #9 refers to the end-to-end validation in Sprint 11.
B4 satisfies a *precondition* for spec #9, not spec #9 itself.

The B4 criterion is sound and well-specified; the parenthetical simply mislabels the traceability.
This does not affect PASS/FAIL logic.

**Suggested fix (advisory):** Change the B4 parenthetical from:

> (Phase 2 success criterion #9 — loop termination exercises the UNCONDITIONAL gate)

to:

> (precondition for Phase 2 success criterion #9: seeding at least one loop-termination catalog
> entry that Sprint 11 will exercise when grading an ephemeral harness fixture)

---

### Criteria and baselines confirmed sound (no issues)

**Verification commands tested against pre-sprint file state:**

- **B1–B4 jq commands** (syntax): All verified against representative JSON inputs — exit 0,
  correct output. The file doesn't exist pre-sprint (correctly), so these fail pre-sprint
  and would pass post-sprint. Not no-ops.
- **S6** (`test -f ...`): Returns ABSENT (non-zero) pre-sprint — correct. Not a no-op.
- **S7** (`jq empty`): Fails with exit 2 pre-sprint (file absent) — correct.
- **S8** (`jq select .source`): Syntax verified. Fails pre-sprint (file absent) — correct.
- **S9 primary** (`jq select .source_ref == null`): Syntax verified. Fails pre-sprint — correct.
- **S10** (`grep -c '## Templates by Rubric'`): Returns 0 pre-sprint (section absent) — correct.
- **S11** (`grep -c 'by-rubric'`): Returns 0 pre-sprint (string absent) — correct.
- **SN1** (`grep -c 'Sources of Real Failures'`): Baseline = **1**. Threshold `>= 1` is correct.
- **SN2** (`grep -c '"grader_type"'` and `grep -c '"rubric_dimension"'`): Both return **1** pre-sprint.
  Thresholds `>= 1` each are correct.
- **SN3** (`grep -c 'Integration with the Harness'` and `grep -c 'Data Flow'`): Both return **1**.
  Thresholds `>= 1` are correct.
- **SN4** (`grep -c 'Conversion guidelines'`): Returns **1**. Threshold `>= 1` is correct.
- **SN5** (`grep -c '<!-- Context scope at this step:'`): Returns **6** in harness-kickoff SKILL.md.
  Threshold `>= 6` is correct (incorporates the Sprint 7 fix from Round 2).
- **SN6** (`test -d "examples"`): Returns ABSENT — correct.

**Completeness:** All three Sprint 8 features from sprints.json are covered:
`playbook-traps-template` (B1–B4, S6–S9, J12), `templates-by-rubric-layout` (S6, S10, S11),
`bootstrap-skill-update` (B5, S10, S11, J13). The `protects_prior` constraint
(`bootstrap-failures/SKILL.md existing catalog convention`) is covered by SN1–SN4.

**B3 dimension names:** All 7 dimension strings in B3's allowlist exactly match the `### `
headings in `rubrics/harness-build.md` — verified by direct comparison.

**tasks.json skip:** Confirmed — `sprint-contract/SKILL.md` contains no `tasks.json` schema
(grep count = 0). Sprint 7 precedent for skipping applies. The out-of-scope declaration is
accurate and complete.

**Reference solution:** Provided for J12 (12% weight, highest-weighted LLM-judge criterion).
J13 (10%) does not receive a reference solution — acceptable per the contract template rule
("The highest-weighted criterion in the contract should have one if it is LLM-judged"). J12 is
highest, so the requirement is met.

**Weight sum:** 52% + 26% + 22% = 100%. Verified. (If Issue 2 is resolved, the split changes
to 66% + 12% + 22% = 100% — also valid.)

**Out-of-scope items:** Sprints 9, 10, 11 deliverables correctly excluded. No scope leakage.

---

### Summary of required changes before approval

1. **S9** (BLOCKING) — Fix the broken secondary check command: change
   `jq '[.failures[0:3].source_ref]'` to `jq '[.failures[0:3][].source_ref]'`.
2. **Behavioral coverage** (BLOCKING) — Reclassify S7, S8, and S9 from structural to
   behavioral (they use jq execution identically to B1–B4). Update Technical Notes weight
   breakdown to 66%/12%/22% and remove the `>= 60%` exception acknowledgment.
3. **B4 parenthetical** (ADVISORY) — Correct the Phase 2 spec criterion #9 reference to
   indicate Sprint 8 satisfies a precondition for that criterion, not the criterion itself.

---

## Evaluator Review (Round 2)

### Issue 1 (BLOCKING) — Secondary jq command fix: RESOLVED

The contract now reads (criterion 8 / B8, line 98):

```
jq '[.failures[0:3][].source_ref]' plugins/trine-eval/...
```

Verified against the same representative JSON used in Round 1:

```
echo '{"failures":[{"source_ref":"Stage: CP"},{"source_ref":"Trap: X"},{"source_ref":"Stage: G"}]}' \
  | jq '[.failures[0:3][].source_ref]'
# Output: ["Stage: CP","Trap: X","Stage: G"]
# Exit: 0
```

The old broken form (`jq '[.failures[0:3].source_ref]'`) still exits 5 — confirming the new form is genuinely different and correct. RESOLVED.

### Issue 2 (BLOCKING) — Behavioral coverage reclassification: RESOLVED

Criteria formerly labeled S7, S8, and S9 are now numbered 6, 7, and 8 (B6, B7, B8) and appear
under the `### Behavioral (execution-verified)` section heading. The Structural section now
contains only criteria 9, 10, 11 (the file-exists test, the section-heading grep, and the
by-rubric grep). Technical Notes weight breakdown reads:

- Behavioral: B1 (8%) + B2 (12%) + B3 (12%) + B4 (10%) + B5 (10%) + B6 (4%) + B7 (5%) + B8 (5%) = **66%**
- Structural: S9 (4%) + S10 (4%) + S11 (4%) = **12%**
- LLM-as-judge: J12 (12%) + J13 (10%) = **22%**
- Total: **100%** ✓

Arithmetic verified: 8+12+12+10+10+4+5+5 = 66; 4+4+4 = 12; 12+10 = 22; 66+12+22 = 100. Correct.

The phrase "Exception acknowledged: behavioral weight = 52%, not 60%" does not appear anywhere
in the contract body (confirmed by grep; the only occurrence is in the Round 1 review text,
which is an archival record, not operative contract text). RESOLVED.

### Issue 3 (ADVISORY) — B4 parenthetical: RESOLVED

The B4 criterion now ends with:

> (precondition for Phase 2 success criterion #9: seeding at least one loop-termination catalog
> entry that Sprint 11 will exercise when grading an ephemeral harness fixture)

This matches the exact suggested fix from Round 1. The overclaiming language "(Phase 2 success
criterion #9 — loop termination exercises the UNCONDITIONAL gate)" is gone. RESOLVED.

### Should-NOT section: untouched

Spot-check confirms SN1–SN6 text is identical to Round 1's confirmed baseline. The six gate
criteria, their verification commands, and their pre-sprint baselines were not altered.

### New findings (Round 2)

One cosmetic inconsistency found and assessed: the Technical Notes label the three structural
criteria as "S9/S10/S11" using a section-prefix convention, while the contract body uses plain
sequential numbering (9, 10, 11). Round 1's suggested fix block used "S6/S10/S11" (where S6
referred to the file-exists criterion when it was in the Structural section). In Round 2 the
file-exists criterion remained criterion 9 in the flat sequence and is written "S9" in the
Technical Notes. This is internally self-consistent and does not affect any PASS/FAIL logic —
the evaluator can read "S9" as shorthand for "Structural criterion 9" without ambiguity. ADVISORY
only; no fix required before implementation.

**Status: APPROVED**
