# Sprint 09 Contract: Tasks.json Emission — Schema Port and Back-fill (Phase 1.5)

## Revision History

- **Rev 1 (2026-06-01):** Three fixes applied per Evaluator Round 1 review.
  1. B3 (BLOCKING): Parenthesized LHS of uniqueness check — `([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)` — to prevent jq exit 5 "Cannot index array with string 'tasks'" error.
  2. B7 (BLOCKING): Same parenthesization fix applied to the sprint-08.tasks.json uniqueness check.
  3. B9 (ADVISORY): Changed command from `jq '.taxonomy.emit_tasks_json'` to `jq -e '.taxonomy.emit_tasks_json == true'` so exit code 0 unambiguously means the field is literally `true` (not `null`); updated PASS condition wording accordingly.

## What I Will Build

Port the `## Task Taxonomy: sprint-NN.tasks.json` section from the published v0.3.3
plugin cache into the in-repo `plugins/trine-eval/skills/sprint-contract/SKILL.md`,
adapting `grader_type` from the cached 2-way enum (`deterministic | llm-judge`) to the
repo's 3-way split (`behavioral | structural | llm-judge`). Add `"taxonomy":
{"emit_tasks_json": true}` to `.harness/config.json`. Back-fill the two most recent
approved sprint contracts as machine-readable JSON: `.harness/contracts/sprint-07.tasks.json`
(15 entries: 11 success + 4 Should-NOT gates) and `.harness/contracts/sprint-08.tasks.json`
(19 entries: 13 success + 6 Should-NOT gates), by mechanical transcription from those
markdown contracts.

## Success Criteria

Each criterion must be independently testable. Be specific enough that pass/fail is
unambiguous. Tag each criterion as `behavioral` (execution-verified), `structural`
(artifact-inspected), or `llm-judge` (reading-comprehension). Weights must sum to 100%
across all success criteria.

**Behavioral coverage:** The two `tasks.json` back-fill files are fully machine-parseable
JSON artifacts. Behavioral criteria use `jq` invocations against those files — exit code
and output are the observable. Every `jq` command in B1–B9 is shell-executable: a command
is run, an exit code and a specific output value are observed, and PASS/FAIL is determined
from those observables. This is "execution-verified" per the 3-way grader split definition,
paralleling the Sprint 8 precedent for `jq`-based behavioral criteria. Total behavioral
weight: 63%.

### Behavioral (execution-verified)

1. **sprint-07.tasks.json parses as valid JSON and contains exactly 15 entries** [weight: 8%]:
   Run `jq 'empty' .harness/contracts/sprint-07.tasks.json` and assert exit code 0 (valid JSON).
   Then run `jq '.tasks | length' .harness/contracts/sprint-07.tasks.json` and assert output
   equals `15`. PASS when both conditions hold (exit 0 for `jq empty`, output `15` for length check).

2. **sprint-07.tasks.json: every entry carries all 7 required fields** [weight: 8%]:
   Run:
   ```
   jq '[.tasks[] | select(has("task_id") and has("criterion") and has("grader_type") and has("weight") and has("is_gate") and has("verification_command") and has("rubric_dimension"))] | length' .harness/contracts/sprint-07.tasks.json
   ```
   and assert the output equals the total entry count (15). PASS when the filtered count
   equals 15 — no entry is missing any of the 7 required fields.

3. **sprint-07.tasks.json: task_id uniqueness, is_gate semantics, and weight sum** [weight: 8%]:
   Run `jq '([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)' .harness/contracts/sprint-07.tasks.json`
   and assert output is `true` (all task_ids are unique).
   Then run `jq '[.tasks[] | select(.is_gate == false) | .weight] | add' .harness/contracts/sprint-07.tasks.json`
   and assert output equals `100` (non-gate criteria weights sum to 100).
   Then run `jq '[.tasks[] | select(.is_gate == true) | .weight] | add' .harness/contracts/sprint-07.tasks.json`
   and assert output equals `0` (gate criteria each have weight 0; sum is 0). PASS when all
   three assertions hold.

4. **sprint-07.tasks.json: grader_type enum is 3-way** [weight: 6%]:
   Run:
   ```
   jq '[.tasks[].grader_type] | unique | .[]' .harness/contracts/sprint-07.tasks.json
   ```
   and assert every printed value is one of `"behavioral"`, `"structural"`, or `"llm-judge"`.
   No value may be `"deterministic"` or any other string. PASS when the unique set is a
   non-empty subset of `{"behavioral", "structural", "llm-judge"}`.

5. **sprint-08.tasks.json parses as valid JSON and contains exactly 19 entries** [weight: 8%]:
   Run `jq 'empty' .harness/contracts/sprint-08.tasks.json` and assert exit code 0.
   Then run `jq '.tasks | length' .harness/contracts/sprint-08.tasks.json` and assert output
   equals `19`. PASS when both conditions hold.

6. **sprint-08.tasks.json: every entry carries all 7 required fields** [weight: 8%]:
   Run:
   ```
   jq '[.tasks[] | select(has("task_id") and has("criterion") and has("grader_type") and has("weight") and has("is_gate") and has("verification_command") and has("rubric_dimension"))] | length' .harness/contracts/sprint-08.tasks.json
   ```
   and assert the output equals 19 (total entry count). PASS when the filtered count equals 19.

7. **sprint-08.tasks.json: task_id uniqueness, is_gate semantics, and weight sum** [weight: 7%]:
   Run `jq '([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)' .harness/contracts/sprint-08.tasks.json`
   and assert `true`.
   Run `jq '[.tasks[] | select(.is_gate == false) | .weight] | add' .harness/contracts/sprint-08.tasks.json`
   and assert `100`.
   Run `jq '[.tasks[] | select(.is_gate == true) | .weight] | add' .harness/contracts/sprint-08.tasks.json`
   and assert `0`. PASS when all three assertions hold.

8. **sprint-08.tasks.json: grader_type enum is 3-way** [weight: 6%]:
   Run:
   ```
   jq '[.tasks[].grader_type] | unique | .[]' .harness/contracts/sprint-08.tasks.json
   ```
   and assert every printed value is one of `"behavioral"`, `"structural"`, or `"llm-judge"`.
   No value may be `"deterministic"`. PASS when the unique set is a non-empty subset of
   `{"behavioral", "structural", "llm-judge"}`.

9. **config.json carries `taxonomy.emit_tasks_json: true`** [weight: 4%]:
   Run `jq -e '.taxonomy.emit_tasks_json == true' .harness/config.json` and assert exit code 0
   and output `true`. The `-e` flag causes jq to exit non-zero when the expression evaluates to
   `false` or `null`, so exit 0 unambiguously means the field is literally `true` (not `null`).
   PASS when the command exits 0 and outputs `true`. Pre-sprint baseline: field absent, outputs
   `false` with exit code 1 — not a no-op.

### Structural (artifact-inspected)

10. **sprint-contract/SKILL.md contains the new `## Task Taxonomy` section heading** [weight: 5%]:
    Run:
    ```
    grep -c '^## Task Taxonomy' plugins/trine-eval/skills/sprint-contract/SKILL.md
    ```
    and assert count >= 1. Pre-sprint baseline is 0; the port must add this heading. PASS
    when count >= 1 (section is present).

11. **sprint-contract/SKILL.md contains the 3-way `grader_type` enum** [weight: 4%]:
    Run:
    ```
    grep -c '"behavioral"' plugins/trine-eval/skills/sprint-contract/SKILL.md
    ```
    and assert count >= 1 AND run:
    ```
    grep -c '"structural"' plugins/trine-eval/skills/sprint-contract/SKILL.md
    ```
    assert count >= 1 AND run:
    ```
    grep -c '"llm-judge"' plugins/trine-eval/skills/sprint-contract/SKILL.md
    ```
    assert count >= 1 AND run:
    ```
    grep -c '"deterministic"' plugins/trine-eval/skills/sprint-contract/SKILL.md
    ```
    assert count == 0 (the cached 2-way `deterministic` term must NOT appear in the ported section).
    Pre-sprint baseline: `behavioral`=0, `structural`=0, `llm-judge`=0, `deterministic`=0.
    PASS when all four conditions hold (three additions present, one absence confirmed).

### LLM-as-judge (reading-comprehension)

12. **Schema port quality: the `## Task Taxonomy` section documents all 7 fields, when-to-emit
    timing, and the self-bootstrap handling** [weight: 15%]:
    Read `plugins/trine-eval/skills/sprint-contract/SKILL.md`'s new `## Task Taxonomy` section.
    PASS requires all of the following:
    (a) The section documents when to emit (after Evaluator writes `Status: APPROVED`, before
    IMPLEMENTATION mode begins) and references `config.taxonomy.emit_tasks_json` as the guard.
    (b) Field semantics are documented for all 7 required fields: `task_id`, `criterion`,
    `grader_type`, `weight`, `is_gate`, `verification_command`, `rubric_dimension`.
    (c) The `grader_type` enum is unambiguously stated as the 3-way set
    `"behavioral" | "structural" | "llm-judge"` — the cached term `"deterministic"` does not
    appear in the enum definition.
    (d) The `bucket` field is omitted, and the omission is documented with a brief rationale
    (e.g., "omitted pending port of `rules/harness-conventions.md`" or equivalent).
    (e) A JSON example is provided with at least one entry showing the 3-way `grader_type`
    value (either `"behavioral"` or `"structural"` — not `"deterministic"`).
    (f) A self-bootstrap note explains that sprint-09's own `tasks.json` is emitted
    post-implementation (after the schema lands in-repo), not at Step 1d — to avoid using
    the schema to document itself before it exists in-repo.

13. **Back-fill transcription fidelity: spot-check 4 entries across sprint-07 and sprint-08
    tasks.json files** [weight: 13%]:
    Read `.harness/contracts/sprint-07.tasks.json` and `.harness/contracts/sprint-08.tasks.json`
    alongside the source markdown contracts. Spot-check at least 2 entries from each file:
    PASS requires for each spot-checked entry:
    (a) The `criterion` field verbatim-matches the corresponding criterion text in the markdown
    (no paraphrasing, no truncation).
    (b) The `weight` field matches the `[weight: N%]` integer in the markdown (for success
    criteria) or is `0` for Should-NOT gates.
    (c) The `is_gate` field is `true` for entries transcribed from the Should-NOT section and
    `false` for entries from the Success Criteria section.
    (d) The `verification_command` field is non-null for behavioral/structural entries and is
    a plausible shell command (not the word `null` as a string); it is `null` (JSON null) for
    llm-judge entries.
    (e) The `rubric_dimension` value is one of the 5 valid eval-harness rubric dimensions:
    `methodology_completeness`, `grading_architecture`, `generator_evaluator_separation`,
    `context_engineering`, `extensibility_aci`.

## Should-NOT Criteria

Gate criteria — any failure blocks the sprint regardless of score. These define behaviors
that must NOT occur. Graded PASS when the behavior is absent.

1. **Should NOT remove or rename any of the 7 existing named sections in
   sprint-contract/SKILL.md**: The sections "Negotiation Protocol", "Weighted Criteria",
   "Grader Types", "Negative (Should-NOT) Criteria", "Reference Solutions", "Guidelines for
   Good Criteria", and "No-Op Detection" must all remain present. Verify by running each of
   the following and asserting each returns >= 1:
   ```
   grep -c "^## Negotiation Protocol" plugins/trine-eval/skills/sprint-contract/SKILL.md
   grep -c "^## Weighted Criteria" plugins/trine-eval/skills/sprint-contract/SKILL.md
   grep -c "^## Grader Types" plugins/trine-eval/skills/sprint-contract/SKILL.md
   grep -c "^## Negative (Should-NOT) Criteria" plugins/trine-eval/skills/sprint-contract/SKILL.md
   grep -c "^## Reference Solutions" plugins/trine-eval/skills/sprint-contract/SKILL.md
   grep -c "^## Guidelines for Good Criteria" plugins/trine-eval/skills/sprint-contract/SKILL.md
   grep -c "^## No-Op Detection" plugins/trine-eval/skills/sprint-contract/SKILL.md
   ```
   (Pre-sprint baseline: each of the 7 headings appears exactly once. The port is additive;
   no existing section may be removed, renamed, or merged.)

2. **Should NOT modify any prior sprint's approved markdown contract**: The content of
   `.harness/contracts/sprint-07.md` and `.harness/contracts/sprint-08.md` must be byte-for-byte
   identical to their content at HEAD before this sprint's implementation begins. Verify:
   ```
   git diff HEAD -- .harness/contracts/sprint-07.md
   git diff HEAD -- .harness/contracts/sprint-08.md
   ```
   Both commands must produce empty output (no diff). The back-fill produces NEW sibling
   `.tasks.json` files; the markdown source contracts are read-only.

3. **Should NOT regress Sprint 6 JIT annotations in harness-kickoff SKILL.md**: The six
   `<!-- Context scope at this step: ... -->` comment blocks added in Sprint 6 must remain
   intact. Verify:
   ```
   grep -c '<!-- Context scope at this step:' plugins/trine-eval/skills/harness-kickoff/SKILL.md
   ```
   assert count >= 6. (Pre-sprint baseline: 6 — Steps 1, 2, 2b, 3, 4, and 5.)

4. **Should NOT create an `examples/` directory at the repo root**: Phase 2's ephemeral
   constraint prohibits committing permanent example fixtures. Verify:
   ```
   test -d "examples"
   ```
   must return non-zero exit (ABSENT). (Pre-sprint baseline: ABSENT — confirmed.)

5. **Should NOT remove or alter the existing fields in `.harness/config.json`**: The fields
   `project_type`, `rubric`, `max_retries`, and `governance.enabled` must retain their
   current values after the `taxonomy` block is added. Verify:
   ```
   jq '.project_type == "eval-harness" and .rubric == "eval-harness" and .max_retries == 3 and .governance.enabled == true' .harness/config.json
   ```
   must output `true`. PASS when output is `true` and exit code is 0. (Pre-sprint baseline:
   `project_type: "eval-harness"`, `rubric: "eval-harness"`, `max_retries: 3`,
   `governance.enabled: true` — all confirmed present at current HEAD.)

## Reference Solutions

**Criterion 12 — Schema port quality (highest-weighted LLM-judge criterion):**

The following is the expected text of the `## Task Taxonomy: sprint-NN.tasks.json` section
as it should appear in `plugins/trine-eval/skills/sprint-contract/SKILL.md` after the port.
The Generator must produce a section of this structure and quality. Key requirements: 3-way
`grader_type` enum, all 7 field semantics documented, `bucket` omission noted, self-bootstrap
note present.

```markdown
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
      "verification_command": "jq '.tasks | length' .harness/contracts/sprint-09.tasks.json",
      "rubric_dimension": "methodology_completeness"
    },
    {
      "task_id": "s09-sn1",
      "criterion": "<Should-NOT criterion text>",
      "grader_type": "structural",
      "weight": 0,
      "is_gate": true,
      "verification_command": "grep -c '^## Negotiation Protocol' plugins/trine-eval/skills/sprint-contract/SKILL.md",
      "rubric_dimension": "grading_architecture"
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
  the markdown contract. The cached v0.3.3 schema used a 2-way `"deterministic" | "llm-judge"`
  enum; this repo adopted the 3-way split in commit 408e8a2. The term `"deterministic"` is
  not used.
- `weight` — The percentage weight from the markdown contract. Gate (Should-NOT) criteria
  use `0` — they are binary, not weighted.
- `is_gate` — `true` for Should-NOT gates, `false` for scored success criteria.
- `verification_command` — For behavioral and structural criteria, a runnable shell command
  whose exit code or stdout determines PASS/FAIL. For llm-judge criteria, `null`. The
  regression gate executes these commands directly.
- `rubric_dimension` — Which rubric dimension this criterion informs. Valid values for this
  project: `methodology_completeness`, `grading_architecture`, `generator_evaluator_separation`,
  `context_engineering`, `extensibility_aci`. Used by harness-summary for per-dimension
  rollups.

**Note on `bucket` field:** The cached v0.3.3 schema includes a `bucket` field (integer 1–3)
referencing `rules/harness-conventions.md`. That rules file is not present in this repo. The
`bucket` field is **omitted** from this ported schema pending a separate port of
`rules/harness-conventions.md`. The harness-summary skill treats missing-`bucket` as `1`
(the most conservative reading) for all entries that lack the field.

**Self-bootstrap note:** Sprint 09 is the sprint that ports this schema into the in-repo
SKILL.md. Sprint 09's own `tasks.json` is therefore emitted *after* the schema port lands
(during or after IMPLEMENTATION mode), not at Step 1d. This avoids using the schema to
describe itself before it exists in-repo. This is a one-time exception for the porting
sprint itself; from Sprint 10 onward, `tasks.json` emission resumes at Step 1d as normal.
```

## Out of Scope

- **Back-fill for sprints 1–6**: Sprints 1–6 predate the 3-way grader split; back-filling
  requires per-criterion classification decisions that Phase 1.5 deliberately defers to a
  follow-up sprint.
- **`bucket` field port**: The `bucket` field from the cached v0.3.3 schema is OMITTED. A
  separate sprint will port `rules/harness-conventions.md` and reintroduce `bucket` when
  the rules file is available in-repo.
- **Arming the Step 0.5 regression gate**: Creating `.harness/regression/regression.json`
  is NOT in scope. The gate activates when harness-summary first graduates a criterion via
  saturation analysis.
- **Wiring `tasks.json` into Batch API submission**: Batch mode is not yet activated.
- **Porting the Authoring Checklist, Subagent-Driven Behavioral Verification, or
  trap-category enumeration** from the cached v0.3.3 SKILL.md: those are separate
  methodology sprint items.
- **Modifying any existing sprint contract markdown files**: `.harness/contracts/sprint-*.md`
  files are read-only inputs; only new sibling `.tasks.json` files are created.
- **Changes to eval-harness rubric, harness-build rubric, or any other skill file other than
  `sprint-contract/SKILL.md`**: This sprint's sole SKILL.md target is `sprint-contract/SKILL.md`.

## Technical Notes

**Self-bootstrap handling (option A selected):**
Sprint 09 ports the `tasks.json` schema into the in-repo SKILL.md. There is a chicken-and-egg
risk: the workflow's Step 1d requires the Generator to emit `sprint-09.tasks.json` using the
schema this sprint is porting. Option A is adopted: the Generator emits `sprint-09.tasks.json`
*after* the schema port has landed in-repo (during or after IMPLEMENTATION mode), not at Step
1d. This is cleaner because the audit chain then records sprint-09's `tasks.json` using the
canonical in-repo schema, not the cached v0.3.3 version. The orchestrator should expect
emission post-implementation rather than at Step 1d. This is a one-time bootstrap exception.

**Grader-type 3-way adaptation:**
The cached v0.3.3 `sprint-contract/SKILL.md` (lines 100–147) defines `grader_type` as a 2-way
enum: `"deterministic" | "llm-judge"`. The repo adopted a 3-way split in commit `408e8a2`:
`behavioral | structural | llm-judge`. The `deterministic` term is replaced by `behavioral` and
`structural`. The ported `## Task Taxonomy` section uses only the 3-way enum. The adaptation
reasoning is documented inline in the new section.

**No-op check for S10 and S11:**
Pre-sprint baselines confirmed by running grep against the current in-repo SKILL.md:
- `grep -c '^## Task Taxonomy' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 0 (pre-sprint)
- `grep -c '"behavioral"' plugins/trine-eval/skills/sprint-contract/SKILL.md` → 0 (pre-sprint)
These criteria are not no-ops: they fail pre-sprint and will pass post-sprint.

**No-op check for B9:**
`jq '.taxonomy.emit_tasks_json' .harness/config.json` → `null` pre-sprint (field absent).
Not a no-op: the criterion requires `true`, which only holds post-sprint.

**tasks.json file structure:**
Both back-fill files use the top-level structure `{"sprint": NN, "tasks": [...]}`, matching
the cached v0.3.3 schema example.

**Back-fill entry counts:**
- sprint-07.tasks.json: 11 success criteria (B1–B2, S3–S8, J9–J11) + 4 Should-NOT gates
  (SN1–SN4) = 15 entries.
- sprint-08.tasks.json: 13 success criteria (B1–B8, S9–S11, J12–J13) + 6 Should-NOT gates
  (SN1–SN6) = 19 entries.

**rubric_dimension mapping approach:**
The 5 valid values for the eval-harness rubric are `methodology_completeness`,
`grading_architecture`, `generator_evaluator_separation`, `context_engineering`,
`extensibility_aci`. Assignment is by topic alignment:
- Criteria about rubric structure, hard thresholds, and grading hierarchy → `grading_architecture`
- Criteria about kickoff routing, step integration, catalog merge → `methodology_completeness`
- Criteria about contract isolation, generator-evaluator boundary → `generator_evaluator_separation`
- Criteria about JIT annotations, SKILL.md procedures → `context_engineering`
- Criteria about extension patterns (by-rubric layout, new rubric registration) → `extensibility_aci`

**SKILL.md line count:**
The in-repo SKILL.md has 86 lines pre-sprint (confirmed by `wc -l`). The spec references "87
lines" — this is a close approximation; the port is additive regardless. The new `## Task
Taxonomy` section adds approximately 50–60 lines, keeping the total well under the 500-line
per-SKILL.md constraint.

**Weight verification:**
- Behavioral: B1 (8%) + B2 (8%) + B3 (8%) + B4 (6%) + B5 (8%) + B6 (8%) + B7 (7%) + B8 (6%) + B9 (4%) = 63%
- Structural: S10 (5%) + S11 (4%) = 9%
- LLM-as-judge: J12 (15%) + J13 (13%) = 28%
- Total: 63% + 9% + 28% = **100%** ✓
- Behavioral coverage: 63% ≥ 60% floor ✓

## Evaluator Review

**Status: NEEDS REVISION**

Two issues require fixes before this contract can be approved. Both are broken `jq` verification commands of the same class — they exit with code 5 and produce "Cannot index array with string 'tasks'" errors, meaning they would FAIL post-implementation for the wrong reason. One advisory item tightens ambiguous wording in B9.

---

### Issue 1 (BLOCKING) — B3: task_id uniqueness command is broken

**Criterion:** B3 — "sprint-07.tasks.json: task_id uniqueness, is_gate semantics, and weight sum"

**Problem:** The first assertion in B3 uses:
```
jq '[.tasks[].task_id] | length == ([ .tasks[].task_id] | unique | length)' .harness/contracts/sprint-07.tasks.json
```
This command exits with code 5 and produces:
```
jq: error (at sprint-07.tasks.json:0): Cannot index array with string "tasks"
```
Verified by running the command with representative JSON. The root cause: `[.tasks[].task_id]` creates an array, which is then piped to `length == ([ .tasks[].task_id] | unique | length)`. The second sub-expression `[ .tasks[].task_id]` receives the array on its left (not the original document), and an array has no `.tasks` key — hence the type error.

The weight-sum and gate-semantics sub-commands in B3 are syntactically correct and tested successfully. Only the uniqueness sub-command is broken.

**Verified broken:**
```
python: subprocess.run(['jq', '[.tasks[].task_id] | length == ([ .tasks[].task_id] | unique | length)', fname])
→ exit:5, stderr: Cannot index array with string "tasks"
```

**Fix required:** Replace the broken uniqueness check with the parenthesized form:
```
jq '([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)' .harness/contracts/sprint-07.tasks.json
```
Verified working: returns `true` for unique ids, `false` for duplicates, exit 0 in both cases.

---

### Issue 2 (BLOCKING) — B7: same broken pattern in sprint-08.tasks.json check

**Criterion:** B7 — "sprint-08.tasks.json: task_id uniqueness, is_gate semantics, and weight sum"

**Problem:** B7 uses the same broken uniqueness command pattern:
```
jq '[.tasks[].task_id] | length == ([.tasks[].task_id] | unique | length)' .harness/contracts/sprint-08.tasks.json
```
Same failure mode as B3 — exit code 5, "Cannot index array with string 'tasks'" error.

**Fix required:** Same correction as B3 — wrap the LHS in parentheses:
```
jq '([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)' .harness/contracts/sprint-08.tasks.json
```

---

### Issue 3 (ADVISORY) — B9: exit code condition is ambiguous

**Criterion:** B9 — "config.json carries `taxonomy.emit_tasks_json: true`"

**Problem:** The verification command `jq '.taxonomy.emit_tasks_json' .harness/config.json` exits 0 both when the field is present (`true`) and when the field is absent (`null`). The pre-sprint baseline outputs `null` with exit code 0:
```
jq '.taxonomy.emit_tasks_json' .harness/config.json → null (exit 0)
```
The criterion description says "assert output is `true` (exit code 0)" — a grader who reads "exit code 0" as the primary condition could misinterpret the pre-sprint `null` output as PASS. The output check (`true`) is the operative condition; exit code 0 is satisfied by both states and should not be cited as an independent assertion.

**Suggested fix (advisory):** Tighten the PASS condition wording to: "PASS when the command outputs `true` (not `null`, not `false`). Note that the field's absence causes `null` output with exit code 0 — exit code alone does not distinguish `true` from `null`."

Alternatively, use `jq -e '.taxonomy.emit_tasks_json' .harness/config.json` with the `-e` flag, which exits non-zero when the output is `false` or `null`, making the exit code condition unambiguous (pre-sprint: exit 1; post-sprint: exit 0).

This is advisory because a careful grader will read "outputs `true`" and correctly FAIL pre-sprint. It becomes blocking only if the PASS condition is later restated as "exit code 0."

---

### Pre-implementation baselines confirmed

All pre-sprint baselines were run independently against the current tree:

- **S10** (`grep -c '^## Task Taxonomy'` in sprint-contract/SKILL.md): returns **0** (exit 1). Not a no-op. ✓
- **S11** (`grep -c '"behavioral"'` in sprint-contract/SKILL.md): returns **0** (exit 1). Not a no-op. ✓
- **S11** (`grep -c '"structural"'`): **0** (exit 1). Not a no-op. ✓
- **S11** (`grep -c '"llm-judge"'`): **0** (exit 1). Not a no-op. ✓
- **S11** (`grep -c '"deterministic"'`): **0** (exit 1). Pre-sprint baseline correct; the term is absent. ✓
- **B9** (`jq '.taxonomy.emit_tasks_json'`): outputs `null` (exit 0). Fails criterion (output ≠ `true`). Not a no-op. ✓
- **SN1** (7 sections): all 7 present at count 1 each. Baseline confirmed. ✓
- **SN2** (`git diff HEAD` on sprint-07.md and sprint-08.md): empty output. Markdown contracts are byte-for-byte unchanged. ✓
- **SN3** (`grep -c '<!-- Context scope at this step:'`): returns **6** (exit 0). Threshold `>= 6` correct. ✓
- **SN4** (`test -d "examples"`): exit 1 (directory absent). Baseline correct. ✓
- **SN5** (`jq '.project_type == ...'`): outputs `true`. Baseline confirmed. ✓

### Entry count verification

Manually counted criteria from sprint-07.md and sprint-08.md:
- **Sprint 07**: 11 success criteria (B1–B2, S3–S8, J9–J11) + 4 Should-NOT gates (SN1–SN4) = **15 entries** ✓
- **Sprint 08**: 13 success criteria (B1–B8, S9–S11, J12–J13) + 6 Should-NOT gates (SN1–SN6) = **19 entries** ✓

Both counts in the contract are factually correct.

### Self-bootstrap deferral adjudication

Option A is the correct call. The chicken-and-egg risk is real: the canonical schema only lands in-repo during this sprint's implementation, so emitting sprint-09.tasks.json at Step 1d would use the cached v0.3.3 schema (with the 2-way `grader_type` enum), not the 3-way schema this sprint is porting. Option A defers emission until post-implementation so the audit record uses the canonical in-repo schema from the start. The contract's Technical Notes section flags this explicitly (paragraph "Self-bootstrap handling (option A selected)") and the Reference Solution repeats the note — the orchestrator has sufficient warning. This is a sound one-time exception; no structural change required.

### Behavioral coverage confirmed

Behavioral weight arithmetic: 8+8+8+6+8+8+7+6+4 = **63%** ≥ 60% floor. ✓

The `jq`-based behavioral classification for B1–B9 is consistent with Sprint 8 precedent (where jq-invoked commands were reclassified from structural to behavioral in Round 2). No re-classification opportunity found.

### Weight sum confirmed

63% + 9% + 28% = **100%** ✓

### Reference solution confirmed present

Provided for J12 (15% weight, highest-weighted LLM-judge criterion). ✓

### Out-of-scope items confirmed complete

Sprints 1–6 back-fill, `bucket` field port, regression.json arming, Batch API wiring — all explicitly excluded. No scope leakage. ✓

---

### Summary of required changes before approval

1. **B3** (BLOCKING) — Fix the uniqueness check: change `[.tasks[].task_id] | length == ([ .tasks[].task_id] | unique | length)` to `([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)`.
2. **B7** (BLOCKING) — Same fix as B3 but for the sprint-08.tasks.json check.
3. **B9** (ADVISORY) — Tighten wording to clarify the output check (`true`, not `null`) is the operative condition; exit code 0 alone is insufficient. Consider adding `-e` flag to jq command.

## Evaluator Review (Round 2)

**Status: APPROVED**

### Verification Results

All three R1 issues verified as correctly resolved:

**B3 — task_id uniqueness command (was BLOCKING):** The operative criterion text at line 53 now reads `jq '([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)' .harness/contracts/sprint-07.tasks.json`. Live test:
- `echo '{"tasks":[{"task_id":"a"},{"task_id":"b"}]}' | jq '([.tasks[].task_id] | length) == ([.tasks[].task_id] | unique | length)'` → `true`, exit 0. RESOLVED.

**B7 — sprint-08.tasks.json same fix (was BLOCKING):** The operative criterion text at line 83 now reads the same parenthesized form against the sprint-08 path. Same live test pattern → `true`, exit 0. RESOLVED.

**B9 — command changed to `jq -e '.taxonomy.emit_tasks_json == true'` (was ADVISORY):** Line 100 now uses `jq -e '.taxonomy.emit_tasks_json == true'` with explicit semantics documented (lines 101–104). Live tests:
- `echo '{}' | jq -e '.taxonomy.emit_tasks_json == true'` → `false`, exit 1 (field absent). PASS condition correctly NOT met.
- `echo '{"taxonomy":{"emit_tasks_json":true}}' | jq -e '.taxonomy.emit_tasks_json == true'` → `true`, exit 0. PASS condition correctly met.
RESOLVED.

### R1 Review Block Integrity

The Round 1 `## Evaluator Review` block (lines 401–527) is fully intact and unmodified. The R2 block is appended below it as required.

### Other Criterion Text

No criterion text outside B3, B7, and B9 changed. All other criteria (B1–B2, B4–B6, B8, S10–S11, J12–J13, SN1–SN5) are word-for-word identical to the original contract text.

### Advisory Note

The Technical Notes section (line 365) and the R1 review prose (lines 460–468, 483) still reference the old `jq '.taxonomy.emit_tasks_json'` form in descriptive/historical context — this is correct and intentional. Those passages document the pre-fix baseline behavior; the operative criterion command at line 100 is the only location that matters for grading, and it is correctly updated.

### Contract Readiness

All weights sum to 100% (63% behavioral + 9% structural + 28% llm-judge). Behavioral coverage is 63% ≥ 60% floor. Reference solution for J12 is present. Gate criteria are well-formed. The contract is implementation-ready.
